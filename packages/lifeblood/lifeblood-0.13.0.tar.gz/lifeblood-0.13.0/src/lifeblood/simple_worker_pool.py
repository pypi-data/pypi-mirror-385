import sys
import errno
import asyncio
import shutil
import tempfile
import time
import itertools
from pathlib import Path
from types import MappingProxyType
from .config import get_config, Config
from .defaults import message_proxy_port
from .pulse_checker import PulseChecker
from .process_utils import create_worker_process, send_stop_signal_to_worker

from .logging import get_logger
from .nethelpers import get_addr_to, get_localhost
from .enums import WorkerState, WorkerType, ProcessPriorityAdjustment
from .net_messages.message_processor import MessageProcessorBase
from .net_messages.address import AddressChain, DirectAddress

from typing import Callable, Tuple, Dict, List, Optional


class ProcData:
    __slots__ = {'process', 'id', 'state', 'state_entering_time', 'start_time', 'sent_term_signal'}

    def __init__(self, process: asyncio.subprocess.Process, id: int):
        self.process = process
        self.id = id
        self.state: WorkerState = WorkerState.OFF
        self.state_entering_time = 0
        self.start_time = time.time()
        self.sent_term_signal = False


class SimpleWorkerPool:  # TODO: split base class, make this just one of implementations
    def __init__(self, worker_type: WorkerType = WorkerType.STANDARD, *,
                 minimal_total_to_ensure=0, minimal_idle_to_ensure=0, maximum_total=256,
                 idle_timeout=10, worker_suspicious_lifetime=4, housekeeping_interval: float = 10,
                 idle_timeout_boost: float = 0.0,
                 priority=ProcessPriorityAdjustment.NO_CHANGE,
                 scheduler_address: AddressChain,
                 message_proxy_address: Optional[Tuple[Optional[str], Optional[int]]] = None,
                 config: Optional[Config] = None,
                 message_processor_factory: Callable[["SimpleWorkerPool", List[Tuple[str, int]]], MessageProcessorBase],
                 ):
        """
        manages a pool of workers.
        :param worker_type: workers are created of given type
        :param minimal_total_to_ensure:  at minimum this amount of workers will always be upheld
        :param minimal_idle_to_ensure:  at minimum this amount of IDLE or OFF(as we assume they are OFF only while they are booting up) workers will always be upheld
        :param scheduler_address: force created workers to use this scheduler address
        """
        # local helper workers' pool
        self.__worker_pool: Dict[asyncio.Future, ProcData] = {}
        self.__workers_to_merge: List[ProcData] = []
        self.__pool_task = None
        self.__message_proxy: Optional[MessageProcessorBase] = None
        self.__message_processor_factory = message_processor_factory
        self.__stop_event = asyncio.Event()
        self.__server_closer_waiter = None
        self.__poke_event = asyncio.Event()
        self.__logger = get_logger(self.__class__.__name__.lower())
        self.__ensure_minimum_total = minimal_total_to_ensure
        self.__ensure_minimum_idle = minimal_idle_to_ensure
        self.__maximum_total = maximum_total
        self.__worker_type = worker_type
        self.__idle_timeout = idle_timeout  # after this amount of idling worker will be stopped if total count is above minimum
        self.__idle_timeout_boost_interval = idle_timeout_boost  # every time any worker changes state - this time is to be waited before idle prunning
        self.__idle_timeout_boost_start_time = 0.0
        self.__housekeeping_interval = housekeeping_interval
        self.__worker_priority = priority
        self.__scheduler_address = scheduler_address
        self.__worker_config = config or get_config('worker')
        self.__worker_config_dir: Optional[Path] = None

        # workers are not created as singleshot, so lifetime of less then this should be considered a sign of possible error
        self.__suspiciously_short_process_time = worker_suspicious_lifetime

        self.__pulse_checker = None

        self.__id_to_procdata: Dict[int, ProcData] = {}
        self.__next_wid = 0

        # this __message_proxy_address is not correct until start() is called
        self.__message_proxy_address = message_proxy_address

        self.__poke_event.set()
        self.__stopped = False

    async def start(self):
        if self.__pool_task is not None and not self.__pool_task.done():
            return

        # actual __message_proxy_address will be set after open port is found
        default_address = get_addr_to(self.__scheduler_address.split_address()[0])
        if self.__message_proxy_address is None:
            proxy_addr, proxy_port = default_address, message_proxy_port()
        else:
            proxy_addr, proxy_port = self.__message_proxy_address
            if proxy_addr is None:
                proxy_addr = default_address
            if proxy_port is None:
                proxy_port = message_proxy_port()

        localhost = get_localhost()
        if proxy_addr != localhost:
            # NOTE: ordering MATTERS, we always use localhost last, supplementary. worker creation below relies on this order
            proxy_addresses = (proxy_addr, localhost)
        else:
            proxy_addresses = (proxy_addr,)
        for i in range(1024):  # somewhat big, but not too big
            self.__message_proxy = self.__message_processor_factory(self, [(addr, proxy_port) for addr in proxy_addresses])  # TODO: config for other arguments
            try:
                await self.__message_proxy.start()
                break
            except OSError as e:
                if e.errno != errno.EADDRINUSE:
                    raise
                proxy_port += 1
                continue
        else:
            raise RuntimeError(f'could not find an opened port in range [{message_proxy_port()}-{proxy_port}]!')
        self.__message_proxy_address = DirectAddress.from_host_port(proxy_addr, proxy_port)

        self.__pool_task = asyncio.create_task(self.local_worker_pool_manager())

        self.__pulse_checker = PulseChecker(self.__scheduler_address, self.__message_proxy, interval=10, maximum_misses=10)
        self.__pulse_checker.add_pulse_fail_callback(self._on_pulse_fail)
        await self.__pulse_checker.start()

        # create config file for workers
        self.__worker_config_dir = Path(tempfile.mkdtemp('lifeblood_worker_temp_config'))
        self.__worker_config.save_as_copy(self.__worker_config_dir / 'config.toml', collapse_overrides=True)

        self.__logger.debug(f'worker pool message protocol listening on {self.__message_proxy.listening_addresses()}')

    def stop(self):
        async def _server_closer():
            self.__pulse_checker.stop()
            await self.__pulse_checker
            await self.__pool_task  # ensure local manager is stopped before closing server. here it will ensure all workers are terminated
            self.__message_proxy.stop()
            await self.__message_proxy.wait_till_stops()
            self.__logger.info('message processor stopped')

        if self.__stopped:
            return
        self.__stop_event.set()  # stops local_worker_pool_manager
        self.__server_closer_waiter = asyncio.create_task(_server_closer())  # server will be closed here
        if self.__worker_config_dir is not None and not self.__worker_config_dir.exists():
            shutil.rmtree(self.__worker_config_dir)
            self.__worker_config_dir = None
        self.__stopped = True

    def __await__(self):
        return self.wait_till_stops().__await__()

    async def wait_till_stops(self):
        if self.__pool_task is None:
            return
        await self.__stop_event.wait()
        await self.__server_closer_waiter

    def is_stopping(self) -> bool:
        """
        True if worker pool is stopped or in process of stopping
        """
        return self.__stop_event.is_set()

    def is_pool_closed(self) -> bool:
        """
        True if main task has finished
        """
        return self.__pool_task.done()

    async def add_worker(self):
        if self.__stopped:
            self.__logger.warning('add_worker called after stop()')
            return
        # below we count all Worker processes, including those that are being awaited after terminate signal was called
        #  so it's not just "active" ones that we count
        if len(self.__id_to_procdata) + len(self.__workers_to_merge) >= self.__maximum_total:
            self.__logger.warning(f'maximum worker limit reached ({self.__maximum_total})')
            return

        # NOTE: last address is localhost, if localhost is listened to
        # NOTE: worker will re-normalize address (as long as it's reachable), so we don't need to do that
        pool_address = self.__message_proxy.listening_addresses()[-1]
        args = [sys.executable, '-m', 'lifeblood.launch',
                '--loglevel', 'DEBUG',
                'worker',
                '--type', self.__worker_type.name,
                '--priority', self.__worker_priority.name,
                '--no-loop',
                '--id', str(self.__next_wid),
                '--pool-address', str(pool_address),
                '--override-config-path', str(self.__worker_config_dir),
                '--scheduler-address',
                AddressChain.join_address((
                    pool_address,
                    self.__scheduler_address
                 ))]

        self.__workers_to_merge.append(ProcData(await create_worker_process(args), self.__next_wid))
        self.__logger.debug(f'adding new worker (id: {self.__next_wid}) to the pool, total: {len(self.__workers_to_merge) + len(self.__worker_pool)}')
        self.__next_wid += 1
        self.__poke_event.set()

    def list_workers(self):
        return MappingProxyType(self.__id_to_procdata)

    def set_minimum_total_workers(self, minimum_total: int):
        self.__ensure_minimum_total = minimum_total

    def set_minimum_idle_workers(self, minimum_idle: int):
        self.__ensure_minimum_idle = minimum_idle

    def set_maximum_workers(self, maximum: int):
        self.__maximum_total = maximum

    def total_active_worker_count(self):
        return len([k for k, v in self.__id_to_procdata.items()
                    if not v.sent_term_signal])

    def idle_active_worker_count(self):
        return len([k for k, v in self.__id_to_procdata.items()
                    if v.state in (WorkerState.IDLE, WorkerState.OFF) and not v.sent_term_signal])  # consider OFF ones as IDLEs that just boot up

    def should_prune_idles(self) -> bool:
        return time.time() - self.__idle_timeout_boost_start_time >= self.__idle_timeout_boost_interval

    #
    # local worker pool manager
    async def local_worker_pool_manager(self):
        """
        this task is responsible for local worker management.
        kill them if aborted
        :return:
        """
        async def _wait_and_reset_event(event: asyncio.Event, timeout):
            await asyncio.sleep(timeout)
            event.clear()

        stop_waiter = asyncio.create_task(self.__stop_event.wait())
        poke_waiter = asyncio.create_task(self.__poke_event.wait())
        no_adding_workers = asyncio.Event()
        wait_event_task = None
        try:
            while True:
                done, pending = await asyncio.wait(
                    itertools.chain(self.__worker_pool.keys(), (stop_waiter, poke_waiter)),
                    timeout=min(self.__housekeeping_interval, self.__idle_timeout),
                    return_when=asyncio.FIRST_COMPLETED
                )
                time_to_stop = False
                if wait_event_task is not None and wait_event_task.done():
                    wait_event_task = None

                for x in done:
                    if x == stop_waiter:
                        time_to_stop = True
                        self.__logger.info('stopping worker pool...')
                        if not poke_waiter.done():
                            poke_waiter.cancel()
                        break
                    elif x == poke_waiter:
                        self.__poke_event.clear()
                        poke_waiter = asyncio.create_task(self.__poke_event.wait())
                        continue
                    # if not those 2 - x must be a process awaiting task
                    if (span := time.time() - self.__worker_pool[x].start_time) < self.__suspiciously_short_process_time:
                        self.__logger.warning(f'worker died within suspicious time threshold: {span}s. pausing worker creation for a bit')
                        if wait_event_task is None:
                            no_adding_workers.set()
                            wait_event_task = asyncio.create_task(_wait_and_reset_event(no_adding_workers, 5))
                    wid = self.__worker_pool[x].id
                    del self.__worker_pool[x]
                    del self.__id_to_procdata[wid]

                    self.__logger.debug(f'removing finished worker from the pool, total: {len(self.__workers_to_merge) + len(self.__worker_pool)}')
                if time_to_stop:
                    break
                for procdata in self.__workers_to_merge:
                    self.__worker_pool[asyncio.create_task(procdata.process.wait())] = procdata
                    self.__id_to_procdata[procdata.id] = procdata

                self.__workers_to_merge.clear()

                # check for idle workers
                idle_guys = self.idle_active_worker_count()
                total_guys = self.total_active_worker_count()
                if self.should_prune_idles() and idle_guys > self.__ensure_minimum_idle and total_guys > self.__ensure_minimum_total:
                    max_to_kill = min(idle_guys - self.__ensure_minimum_idle, total_guys - self.__ensure_minimum_total)
                    self.__logger.debug(f'cleaning up. max {max_to_kill} workers to kill')
                    # if we above minimum - we can kill some idle ones
                    now = time.time()
                    for procdata in self.__worker_pool.values():
                        if max_to_kill <= 0:
                            break
                        if procdata.state != WorkerState.IDLE or now - procdata.state_entering_time < self.__idle_timeout or procdata.sent_term_signal:
                            self.__logger.debug(f'not killing (id: {procdata.id}): not idle enough')
                            continue
                        try:
                            self.__logger.debug(f'enforcing limits: terminating worker (id: {procdata.id})')
                            send_stop_signal_to_worker(procdata.process)
                            procdata.sent_term_signal = True
                        except ProcessLookupError:
                            # probability is low, but this can happen. though if this happens often - something is wrong
                            self.__logger.warning("tried kill some idle workers, but it was already dead")
                        else:
                            max_to_kill -= 1
                            self.__poke_event.set()  # poke ourselves to clean up finished processes

                # ensure the ensure
                if not no_adding_workers.is_set():
                    just_added = 0
                    if total_guys < self.__ensure_minimum_total:
                        for _ in range(self.__ensure_minimum_total - total_guys):
                            await self.add_worker()
                            just_added += 1  # cuz add_worker will not add to __id_to_procdata or __worker_pool - we do on next iteration

                    if idle_guys + just_added < self.__ensure_minimum_idle:
                        for _ in range(self.__ensure_minimum_idle - idle_guys - just_added):
                            await self.add_worker()
                else:
                    self.__logger.debug('temporarily not adding workers')

            # debug logging
            self.__logger.debug(f'at pool closing, before cleanup: total workers: {len(self.__worker_pool)}, idle: {len([k for k, v in self.__id_to_procdata.items() if v.state in (WorkerState.IDLE, WorkerState.OFF)])}')
            # more verbose debug:
            if True:
                for wid, procdata in self.__id_to_procdata.items():
                    self.__logger.debug(f'worker id {wid}, pid {procdata.process.pid}: {procdata.state}')
        except asyncio.CancelledError:
            self.__logger.info('cancelled! stopping worker pool...')
            raise
        finally:
            async def _proc_waiter(proc: asyncio.subprocess.Process):
                try:
                    await asyncio.wait_for(proc.wait(), timeout=10)
                    self.__logger.debug(f'{proc.pid} has gracefully ended with {await proc.wait()}')
                except asyncio.TimeoutError:
                    self.__logger.warning('worker ignored SIGINT. killing instead.')
                    proc.kill()
                    await proc.wait()
                except Exception as e:
                    self.__logger.exception('very unexpected exception. pretending like it hasn\'t happened')

            # cleanup
            wait_tasks = []
            for procdata in itertools.chain(self.__worker_pool.values(), self.__workers_to_merge):
                try:
                    self.__logger.debug(f'sending SIGTERM to {procdata.process.pid}')
                    send_stop_signal_to_worker(procdata.process)
                except ProcessLookupError:
                    continue
                wait_tasks.append(_proc_waiter(procdata.process))
            await asyncio.gather(*wait_tasks)
            await asyncio.gather(*self.__worker_pool.keys())  # since all processes are killed now - this SHOULD take no time at all

            self.__logger.info('worker pool stopped')
        # tidyup
        for fut in self.__worker_pool:
            if not fut.done():
                fut.cancel()

    #
    # callbacks
    async def _on_pulse_fail(self):
        self.stop()

    #
    # callbacks from protocol
    async def _worker_state_change(self, worker_id: int, state: WorkerState):
        if worker_id not in self.__id_to_procdata:
            self.__logger.warning(f'reported state {state} for worker {worker_id} that DOESN\'T BELONG TO US')
            return

        self.__logger.debug(f'worker (id: {worker_id}) reported state={state}')
        if self.__id_to_procdata[worker_id].state != state:
            self.__id_to_procdata[worker_id].state = state
            now = time.time()
            self.__id_to_procdata[worker_id].state_entering_time = now
            self.__idle_timeout_boost_start_time = now
            self.__poke_event.set()
