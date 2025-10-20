import os
from pathlib import Path
import time
from datetime import datetime
import json
import itertools
import asyncio
import aiosqlite
import aiofiles
from aiorwlock import RWLock
from contextlib import asynccontextmanager

from ..misc import alocking
from .. import logging
from ..nodegraph_holder_base import NodeGraphHolderBase
from ..attribute_serialization import serialize_attributes, deserialize_attributes
from ..worker_message_processor_client import WorkerControlClient
from ..hardware_resources import HardwareResources
from ..invocationjob import Invocation, InvocationJob, Requirements
from ..environment_resolver import EnvironmentResolverArguments
from ..broadcasting import create_broadcaster
from ..simple_worker_pool import SimpleWorkerPool
from ..timestamp import global_timestamp_int
from ..nethelpers import get_broadcast_addr_for, all_interfaces
from ..worker_metadata import WorkerMetadata
from ..taskspawn import TaskSpawn
from ..basenode import BaseNode
from ..exceptions import *
from ..node_dataprovider_base import NodeDataProvider
from ..basenode_serialization import NodeSerializerBase, IncompatibleDeserializationMethod, FailedToDeserialize
from ..enums import WorkerState, WorkerPingState, TaskState, InvocationState, WorkerType, \
    SchedulerMode, TaskGroupArchivedState, SpawnStatus
from .. import aiosqlite_overlay
from ..ui_protocol_data import TaskData, TaskDelta, IncompleteInvocationLogData, InvocationLogData

from ..net_messages.address import DirectAddress, AddressChain
from ..net_messages.message_processor import MessageProcessorBase
from ..scheduler_config_provider_base import SchedulerConfigProviderBase
from ..worker_pool_message_processor import WorkerPoolMessageProcessor

from .data_access import DataAccess
from .scheduler_component_base import SchedulerComponentBase
from .pinger import Pinger
from .ping_producer_base import PingProducerBase
from .task_processor import TaskProcessor
from .ui_state_accessor import UIStateAccessor

from typing import Optional, Any, Callable, Tuple, List, Iterable, Union, Dict, Set


class SchedulerCore(NodeGraphHolderBase):
    __next_unique_session_key = 0

    @classmethod
    def _next_unique_session_key(cls) -> int:
        """
        just a helper that returns globally unique integers.
        could use uuid, but this seems more straightforward and easier to debug

        """
        key = cls.__next_unique_session_key
        cls.__next_unique_session_key += 1
        return key

    def __init__(self, *,
                 scheduler_config_provider: SchedulerConfigProviderBase,
                 node_data_provider: NodeDataProvider,
                 node_serializers: List[NodeSerializerBase],
                 message_processor_factory: Callable[["SchedulerCore", List[DirectAddress]], MessageProcessorBase],
                 legacy_task_protocol_factory: Callable[["SchedulerCore"], asyncio.StreamReaderProtocol],
                 ui_protocol_factory: Callable[["SchedulerCore"], asyncio.StreamReaderProtocol],
                 data_access: DataAccess,
                 ping_producers: Iterable[PingProducerBase],
                 ):
        """
        TODO: add a docstring

        :param scheduler_config_provider:
        """
        self.__node_data_provider: NodeDataProvider = node_data_provider
        if len(node_serializers) < 1:
            raise ValueError('at least one serializer must be provided!')
        self.__node_serializers = list(node_serializers)
        self.__logger = logging.get_logger('scheduler')
        self.__logger.info('loading core plugins')
        self.__node_objects: Dict[int, BaseNode] = {}
        self.__node_objects_locks: Dict[int, RWLock] = {}
        self.__node_objects_creation_locks: Dict[int, asyncio.Lock] = {}
        self.__config_provider: SchedulerConfigProviderBase = scheduler_config_provider

        # this lock will prevent tasks from being reported cancelled and done at the same exact time should that ever happen
        # this lock is overkill already, but we can make it even more overkill by using set of locks for each invoc id
        # which would be completely useless now cuz sqlite locks DB as a whole, not even a single table, especially not just parts of table
        self.__invocation_reporting_lock = asyncio.Lock()

        self.__all_components = None
        self.__started_event = asyncio.Event()

        self.__db_path = scheduler_config_provider.main_database_location()
        if not self.__db_path.startswith('file:'):  # if schema is used - we do not modify the db uri in any way
            self.__db_path = os.path.realpath(os.path.expanduser(self.__db_path))
        self.__logger.debug(f'starting scheduler with database: {self.__db_path}')
        self.data_access: DataAccess = data_access
        ##

        self.__use_external_log = self.__config_provider.external_log_location() is not None
        self.__external_log_location: Optional[Path] = self.__config_provider.external_log_location()
        if self.__use_external_log:
            external_log_path = Path(self.__use_external_log)
            if external_log_path.exists() and external_log_path.is_file():
                external_log_path.unlink()
            if not external_log_path.exists():
                external_log_path.mkdir(parents=True)
            if not os.access(self.__external_log_location, os.X_OK | os.W_OK):
                raise RuntimeError('cannot write to external log location provided')

        self.__pinger: Pinger = Pinger(self, ping_producers=list(ping_producers))
        self.task_processor: TaskProcessor = TaskProcessor(self)
        self.ui_state_access: UIStateAccessor = UIStateAccessor(self)

        self.__message_processor_addresses = []
        self.__ui_address = None
        self.__legacy_command_server_address = None

        legacy_server_ip, legacy_server_port = self.__config_provider.legacy_server_address()  # TODO: this CAN be None
        for message_server_ip, message_server_port in self.__config_provider.server_message_addresses():
            self.__message_processor_addresses.append(DirectAddress.from_host_port(message_server_ip, message_server_port))
        self.__legacy_command_server_address = (legacy_server_ip, legacy_server_port)

        self.__ui_address = self.__config_provider.server_ui_address()

        self.__stop_event = asyncio.Event()
        self.__server_closing_task = None
        self.__cleanup_tasks = None

        self.__legacy_command_server = None
        self.__message_processor: Optional[MessageProcessorBase] = None
        self.__ui_server = None
        self.__ui_server_coro_args = {'protocol_factory': lambda: ui_protocol_factory(self), 'host': self.__ui_address[0], 'port': self.__ui_address[1], 'backlog': 16}
        self.__legacy_server_coro_args = {'protocol_factory': lambda: legacy_task_protocol_factory(self), 'host': legacy_server_ip, 'port': legacy_server_port, 'backlog': 16}
        self.__message_processor_factory = message_processor_factory

        self.__do_broadcasting = self.__config_provider.broadcast_interval() is not None
        self.__broadcasting_interval = self.__config_provider.broadcast_interval() or 0
        self.__broadcasting_servers = []

        self.__worker_pool = None
        self.__worker_pool_helpers_minimal_idle_to_ensure = self.__config_provider.scheduler_helpers_minimal()

        self.__event_loop = asyncio.get_running_loop()
        assert self.__event_loop is not None, 'Scheduler MUST be created within working event loop, in the main thread'

    @property
    def config_provider(self) -> SchedulerConfigProviderBase:
        return self.__config_provider

    def get_event_loop(self):
        return self.__event_loop

    def node_data_provider(self) -> NodeDataProvider:
        return self.__node_data_provider

    def db_uid(self) -> int:
        """
        unique id that was generated on creation for the DB currently in use

        :return: 64 bit unsigned int
        """
        return self.data_access.db_uid

    def wake(self):
        """
        scheduler may go into DORMANT mode when he things there's nothing to do
        in that case wake() call exits DORMANT mode immediately
        if wake is not called on some change- eventually scheduler will check it's shit and will decide to exit DORMANT mode on it's own, it will just waste some time first
        if currently not in DORMANT mode - nothing will happen

        :return:
        """
        self.task_processor.wake()
        self.__pinger.wake()

    def poke_task_processor(self):
        """
        kick that lazy ass to stop it's waitings and immediately perform another processing iteration
        this is not connected to wake, __sleep and DORMANT mode,
        this is just one-time kick
        good to perform when task was changed somewhere async, outside of task_processor

        :return:
        """
        self.task_processor.poke()

    def poke_pinger(self):
        self.__pinger.poke()

    def _component_changed_mode(self, component: SchedulerComponentBase, mode: SchedulerMode):
        if component == self.task_processor and mode == SchedulerMode.DORMANT:
            self.__logger.info('task processor switched to DORMANT mode')
            self.__pinger.sleep()

    def message_processor(self) -> MessageProcessorBase:
        """
        get scheduler's main message processor
        """
        return self.__message_processor

    async def get_node_type_and_name_by_id(self, node_id: int) -> (str, str):
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT "type", "name" FROM "nodes" WHERE "id" = ?', (node_id,)) as nodecur:
                node_row = await nodecur.fetchone()
        if node_row is None:
            raise RuntimeError(f'node with given id {node_id} does not exist')
        return node_row['type'], node_row['name']

    @asynccontextmanager
    async def node_object_by_id_for_reading(self, node_id: int):
        async with self.get_node_lock_by_id(node_id).reader_lock:
            yield await self._get_node_object_by_id(node_id)

    @asynccontextmanager
    async def node_object_by_id_for_writing(self, node_id: int):
        async with self.get_node_lock_by_id(node_id).writer_lock:
            yield await self._get_node_object_by_id(node_id)

    async def _get_node_object_by_id(self, node_id: int) -> BaseNode:
        """
        When accessing node this way - be aware that you SHOULD ensure your access happens within a lock
        returned by get_node_lock_by_id.
        If you don't want to deal with that - use scheduler's wrappers to access nodes in a safe way
        (lol, wrappers are not implemented)

        :param node_id:
        :return:
        """
        if node_id in self.__node_objects:
            return self.__node_objects[node_id]
        async with self.__get_node_creation_lock_by_id(node_id):
            # in case by the time we got here and the node was already created
            if node_id in self.__node_objects:
                return self.__node_objects[node_id]
            # if no - need to create one after all
            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                async with con.execute('SELECT * FROM "nodes" WHERE "id" = ?', (node_id,)) as nodecur:
                    node_row = await nodecur.fetchone()
                if node_row is None:
                    raise RuntimeError('node id is invalid')

                node_type = node_row['type']
                if not self.__node_data_provider.has_node_factory(node_type):
                    raise RuntimeError('node type is unsupported')

                if node_row['node_object'] is not None:
                    try:
                        for serializer in self.__node_serializers:
                            try:
                                node_object = await serializer.deserialize_async(self.__node_data_provider, node_row['node_object'], node_row['node_object_state'])
                                break
                            except IncompatibleDeserializationMethod as e:
                                self.__logger.warning(f'deserialization method failed with {e} ({serializer})')
                                continue
                        else:
                            raise FailedToDeserialize(f'node entry {node_id} has unknown serialization method')
                        node_object.set_parent(self, node_id)
                        self.__node_objects[node_id] = node_object
                        return self.__node_objects[node_id]
                    except FailedToDeserialize:
                        if self.__config_provider.ignore_node_deserialization_failures():
                            pass  # ignore errors, recreate node
                        else:
                            raise

                newnode = self.__node_data_provider.node_factory(node_type)(node_row['name'])
                newnode.set_parent(self, node_id)

                self.__node_objects[node_id] = newnode
                node_data, state_data = await self.__node_serializers[0].serialize_async(newnode)
                await con.execute('UPDATE "nodes" SET node_object = ?, node_object_state = ? WHERE "id" = ?',
                                  (node_data, state_data, node_id))
                await con.commit()

                return newnode

    def get_node_lock_by_id(self, node_id: int) -> RWLock:
        """
        All read/write operations for a node should be locked within a per node rw lock that scheduler maintains.
        Usually you do NOT have to be concerned with this.
        But in cases you get the node object with functions like get_node_object_by_id.
        it is your responsibility to ensure data is locked when accessed.
        Lock is not part of the node itself.

        :param node_id: node id to get lock to
        :return: rw lock for the node
        """
        if node_id not in self.__node_objects_locks:
            self.__node_objects_locks[node_id] = RWLock(fast=True)  # read about fast on github. the points is if we have awaits inside critical section - it's safe to use fast
        return self.__node_objects_locks[node_id]

    def __get_node_creation_lock_by_id(self, node_id: int) -> asyncio.Lock:
        """
        This lock is for node creation/deserialization sections ONLY
        """
        if node_id not in self.__node_objects_creation_locks:
            self.__node_objects_creation_locks[node_id] = asyncio.Lock()
        return self.__node_objects_creation_locks[node_id]

    async def get_task_attributes(self, task_id: int) -> Tuple[Dict[str, Any], Optional[EnvironmentResolverArguments]]:
        """
        get tasks, atributes and it's enviroment resolver's attributes

        :param task_id:
        :return:
        """
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT attributes, environment_resolver_data FROM tasks WHERE "id" = ?', (task_id,)) as cur:
                res = await cur.fetchone()
            if res is None:
                raise RuntimeError('task with specified id was not found')
            env_res_args = None
            if res['environment_resolver_data'] is not None:
                env_res_args = await EnvironmentResolverArguments.deserialize_async(res['environment_resolver_data'])
            return await deserialize_attributes(res['attributes']), env_res_args

    async def get_task_fields(self, task_id: int) -> Dict[str, Any]:
        """
        returns information about the given task, excluding thicc fields like attributes or env resolver
        for those - use get_task_attributes

        :param task_id:
        :return:
        """
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT "id", "name", parent_id, children_count, active_children_count, "state", paused, '
                                   '"node_id", split_level, priority, "dead" FROM tasks WHERE "id" == ?', (task_id,)) as cur:
                res = await cur.fetchone()
            if res is None:
                raise RuntimeError('task with specified id was not found')
            return dict(res)

    async def task_name_to_id(self, name: str) -> List[int]:
        """
        get the list of task ids that have specified name

        :param name:
        :return:
        """
        async with self.data_access.data_connection() as con:
            async with con.execute('SELECT "id" FROM "tasks" WHERE "name" = ?', (name,)) as cur:
                return list(x[0] for x in await cur.fetchall())

    async def get_task_invocation_serialized(self, task_id: int) -> Optional[bytes]:
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT work_data FROM tasks WHERE "id" = ?', (task_id,)) as cur:
                res = await cur.fetchone()
            if res is None:
                raise RuntimeError('task with specified id was not found')
            return res[0]

    async def worker_id_from_address(self, addr: str) -> Optional[int]:
        async with self.data_access.data_connection() as con:
            async with con.execute('SELECT "id" FROM workers WHERE last_address = ?', (addr,)) as cur:
                ret = await cur.fetchone()
        if ret is None:
            return None
        return ret[0]

    async def get_worker_state(self, wid: int, con: Optional[aiosqlite.Connection] = None) -> WorkerState:
        if con is None:
            async with self.data_access.data_connection() as con:
                async with con.execute('SELECT "state" FROM "workers" WHERE "id" = ?', (wid,)) as cur:
                    res = await cur.fetchone()
        else:
            async with con.execute('SELECT "state" FROM "workers" WHERE "id" = ?', (wid,)) as cur:
                res = await cur.fetchone()
        if res is None:
            raise ValueError(f'worker with given wid={wid} was not found')
        return WorkerState(res[0])

    async def get_task_invocation(self, task_id: int):
        data = await self.get_task_invocation_serialized(task_id)
        if data is None:
            return None
        return await InvocationJob.deserialize_async(data)

    async def get_invocation_worker(self, invocation_id: int) -> Optional[AddressChain]:
        async with self.data_access.data_connection() as con:
            async with con.execute(
                    'SELECT workers.last_address '
                    'FROM invocations LEFT JOIN workers '
                    'ON invocations.worker_id == workers.id '
                    'WHERE invocations.id == ?', (invocation_id,)) as cur:
                res = await cur.fetchone()
        if res is None:
            return None
        return AddressChain(res[0])

    async def get_invocation_state(self, invocation_id: int) -> Optional[InvocationState]:
        async with self.data_access.data_connection() as con:
            async with con.execute(
                    'SELECT state FROM invocations WHERE id == ?', (invocation_id,)) as cur:
                res = await cur.fetchone()
        if res is None:
            return None
        return InvocationState(res[0])

    def stop(self):
        async def _server_closer():
            # for server in self.__broadcasting_servers:
            #     server.wait_closed()
            # ensure all components stop first
            await self.__pinger.wait_till_stops()
            await self.task_processor.wait_till_stops()
            await self.__worker_pool.wait_till_stops()
            await self.__ui_server.wait_closed()
            if self.__legacy_command_server is not None:
                self.__legacy_command_server.close()
                await self.__legacy_command_server.wait_closed()
            self.__logger.debug('stopping message processor...')
            self.__message_processor.stop()
            await self.__message_processor.wait_till_stops()
            self.__logger.debug('message processor stopped')

        async def _db_cache_writeback():
            await self.__pinger.wait_till_stops()
            await self.task_processor.wait_till_stops()
            await self.__server_closing_task
            await self._save_all_cached_nodes_to_db()
            await self.data_access.write_back_cache()

        if self.__stop_event.is_set():
            self.__logger.error('cannot double stop!')
            return  # no double stopping
        if not self.__started_event.is_set():
            self.__logger.error('cannot stop what is not started!')
            return
        self.__logger.info('STOPPING SCHEDULER')
        # for server in self.__broadcasting_servers:
        #     server.close()
        self.__stop_event.set()  # this will stop things including task_processor
        self.__pinger.stop()
        self.task_processor.stop()
        self.ui_state_access.stop()
        self.__worker_pool.stop()
        self.__server_closing_task = asyncio.create_task(_server_closer())  # we ensure worker pool stops BEFORE server, so workers have chance to report back
        self.__cleanup_tasks = [asyncio.create_task(_db_cache_writeback())]
        if self.__ui_server is not None:
            self.__ui_server.close()

    def _stop_event_wait(self):  # TODO: this is currently being used by ui proto to stop long connections, but not used in task proto, but what if it'll also get long living connections?
        return self.__stop_event.wait()

    async def start(self):
        # prepare
        async with self.data_access.data_connection() as con:
            # we play it the safest for now:
            # all workers set to UNKNOWN state, all active invocations are reset, all tasks in the middle of processing are reset to closest waiting state
            con.row_factory = aiosqlite.Row
            await con.execute('UPDATE "tasks" SET "state" = ? WHERE "state" IN (?, ?)',
                              (TaskState.READY.value, TaskState.IN_PROGRESS.value, TaskState.INVOKING.value))
            await con.execute('UPDATE "tasks" SET "state" = ? WHERE "state" = ?',
                              (TaskState.WAITING.value, TaskState.GENERATING.value))
            await con.execute('UPDATE "tasks" SET "state" = ? WHERE "state" = ?',
                              (TaskState.WAITING.value, TaskState.WAITING_BLOCKED.value))
            await con.execute('UPDATE "tasks" SET "state" = ? WHERE "state" = ?',
                              (TaskState.POST_WAITING.value, TaskState.POST_GENERATING.value))
            await con.execute('UPDATE "tasks" SET "state" = ? WHERE "state" = ?',
                              (TaskState.POST_WAITING.value, TaskState.POST_WAITING_BLOCKED.value))
            await con.execute('UPDATE "invocations" SET "state" = ? WHERE "state" = ?', (InvocationState.FINISHED.value, InvocationState.IN_PROGRESS.value))
            # for now invoking invocation are invalidated by deletion (here and in task_processor)
            await con.execute('DELETE FROM invocations WHERE "state" = ?', (InvocationState.INVOKING.value,))
            await con.execute('UPDATE workers SET "ping_state" = ?', (WorkerPingState.UNKNOWN.value,))
            await con.execute('UPDATE "workers" SET "state" = ?, session_key = ?', (WorkerState.UNKNOWN.value, None))
            await con.commit()

            # update volatile mem cache:
            async with con.execute('SELECT "id", last_seen, last_checked, ping_state FROM workers') as worcur:
                async for row in worcur:
                    self.data_access.mem_cache_workers_state[row['id']] = {k: row[k] for k in dict(row)}

        # start
        loop = asyncio.get_event_loop()
        self.__legacy_command_server = await loop.create_server(**self.__legacy_server_coro_args)
        self.__ui_server = await loop.create_server(**self.__ui_server_coro_args)
        # start message processor

        self.__message_processor = self.__message_processor_factory(self, self.__message_processor_addresses)
        await self.__message_processor.start()
        worker_pool_message_proxy_address = (self.__message_processor_addresses[0].split(':', 1)[0], None)  # use same ip as scheduler's message processor, but default port
        self.__worker_pool = SimpleWorkerPool(WorkerType.SCHEDULER_HELPER,
                                        minimal_idle_to_ensure=self.__worker_pool_helpers_minimal_idle_to_ensure,
                                        scheduler_address=self.server_message_address(DirectAddress(worker_pool_message_proxy_address[0])),
                                        message_proxy_address=worker_pool_message_proxy_address,
                                        message_processor_factory=WorkerPoolMessageProcessor,
                                        )
        await self.__worker_pool.start()
        #
        # broadcasting
        if self.__do_broadcasting:
            # need to start a broadcaster for each interface from union of message and ui addresses
            for iface_addr in all_interfaces()[1:]:  # skipping first, as first is localhost
                broadcast_address = get_broadcast_addr_for(iface_addr)
                if broadcast_address is None:  # broadcast not supported
                    continue
                broadcast_data = {}
                if direct_address := {x.split(':', 1)[0]: x for x in self.__message_processor_addresses}.get(iface_addr):
                    broadcast_data['message_address'] = str(direct_address)
                if iface_addr == self.__ui_address[0] or self.__ui_address[0] == '0.0.0.0':
                    broadcast_data['ui'] = ':'.join(str(x) for x in (iface_addr, self.__ui_address[1]))
                if iface_addr == self.__legacy_command_server_address[0] or self.__legacy_command_server_address[0] == '0.0.0.0':
                    broadcast_data['worker'] = ':'.join(str(x) for x in (iface_addr, self.__legacy_command_server_address[1]))
                self.__broadcasting_servers.append(
                    (
                        broadcast_address,
                        await create_broadcaster(
                            'lifeblood_scheduler',
                            json.dumps(broadcast_data),
                            ip=broadcast_address,
                            broadcast_interval=self.__broadcasting_interval
                        )
                    )
                )

        await self.task_processor.start()
        await self.__pinger.start()
        await self.ui_state_access.start()
        # run
        self.__all_components = \
            asyncio.gather(self.task_processor.wait_till_stops(),
                           self.__pinger.wait_till_stops(),
                           self.ui_state_access.wait_till_stops(),
                           self.__legacy_command_server.wait_closed(),  # TODO: shit being waited here below is very unnecessary
                           self.__ui_server.wait_closed(),
                           self.__worker_pool.wait_till_stops())

        self.__started_event.set()
        # print information
        self.__logger.info('scheduler started')
        self.__logger.info(
            'scheduler listening on:\n'
            '  message processors:\n'
            + '\n'.join((f'    {addr}' for addr in self.__message_processor_addresses)) +
            '\n'
            '  ui servers:\n'
            f'    {":".join(str(x) for x in self.__ui_address)}\n'
            '  legacy command servers:\n'
            f'    {":".join(str(x) for x in self.__legacy_command_server_address)}'
        )
        self.__logger.info(
            'broadcasting enabled for:\n'
            + '\n'.join((f'    {info[0]}' for info in self.__broadcasting_servers))
        )

    async def wait_till_starts(self):
        return await self.__started_event.wait()

    async def wait_till_stops(self):
        await self.__started_event.wait()
        assert self.__all_components is not None
        await self.__all_components
        await self.__server_closing_task
        for task in self.__cleanup_tasks:
            await task

    async def _save_all_cached_nodes_to_db(self):
        self.__logger.info('saving nodes to db')
        for node_id in self.__node_objects:
            await self.save_node_to_database(node_id)
            self.__logger.debug(f'node {node_id} saved to db')

    def is_started(self):
        return self.__started_event.is_set()

    def is_stopping(self) -> bool:
        """
        True if stopped or in process of stopping
        """
        return self.__stop_event.is_set()

    #
    # helper functions
    #

    async def reset_invocations_for_worker(self, worker_id: int, con: aiosqlite_overlay.ConnectionWithCallbacks, also_update_resources=True) -> bool:
        """

        :param worker_id:
        :param con:
        :param also_update_resources:
        :return: need commit?
        """
        assert con.in_transaction, 'expectation failure'

        async with con.execute('SELECT * FROM invocations WHERE "worker_id" = ? AND "state" == ?',
                               (worker_id, InvocationState.IN_PROGRESS.value)) as incur:
            all_invoc_rows = await incur.fetchall()  # we don't really want to update db while reading it
        need_commit = False
        for invoc_row in all_invoc_rows:  # mark all (probably single one) invocations
            need_commit = True
            self.__logger.warning("fixing unresponsive invocation %d for worker %d" % (invoc_row['id'], worker_id))
            await con.execute('UPDATE invocations SET "state" = ? WHERE "id" = ?',
                              (InvocationState.FINISHED.value, invoc_row['id']))
            await con.execute('UPDATE tasks SET "state" = ? WHERE "id" = ?',
                              (TaskState.READY.value, invoc_row['task_id']))
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, TaskDelta(invoc_row['task_id'], state=TaskState.READY))  # ui event
        if also_update_resources:
            also_need_commit = await self._update_worker_resouce_usage(worker_id, connection=con)
            need_commit = need_commit or also_need_commit
        return need_commit

    #
    # invocation consistency checker
    async def invocation_consistency_checker(self):
        """
        both scheduler and woker might crash at any time. so we need to check that
        worker may crash working on a task (
        :return:
        """
        pass

    #
    # callbacks

    #
    # worker reports done task
    async def task_done_reported(self, task: Invocation, stdout: str, stderr: str):
        """
        scheduler comm protocols should call this when a task is done
         TODO: this is almost the same code as for task_cancel_reported, maybe unify?
        """
        for attempt in range(120):  # TODO: this should be configurable
            # if invocation is super fast - this may happen even before submission is completed,
            # so we might need to wait a bit
            try:
                return await self.__task_done_reported_inner(task, stdout, stderr)
            except NeedToRetryLater:
                self.__logger.debug('attempt %d to report invocation %d done notified it needs to wait', attempt, task.invocation_id())
                await asyncio.sleep(0.5)  # TODO: this should be configurable
                continue
        else:
            self.__logger.error(f'out of attempts trying to report done invocation {task.invocation_id()}, probably something is not right with the state of the database')

    async def __task_done_reported_inner(self, task: Invocation, stdout: str, stderr: str):
        """

        """
        async with self.__invocation_reporting_lock, \
                self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            self.__logger.debug('task finished reported %s code %s', repr(task), task.exit_code())
            # sanity check
            async with con.execute('SELECT "state" FROM invocations WHERE "id" = ?', (task.invocation_id(),)) as cur:
                invoc = await cur.fetchone()
                if invoc is None:
                    self.__logger.error('reported task has non existing invocation id %d' % task.invocation_id())
                    return
                if invoc['state'] == InvocationState.INVOKING.value:  # means _submitter has not yet finished, we should wait
                    raise NeedToRetryLater()
                elif invoc['state'] != InvocationState.IN_PROGRESS.value:
                    self.__logger.warning(f'reported task for a finished invocation. assuming that worker failed to cancel task previously and ignoring invocation results. (state={invoc["state"]})')
                    return
            await con.execute('UPDATE invocations SET "state" = ?, "return_code" = ?, "runtime" = ? WHERE "id" = ?',
                              (InvocationState.FINISHED.value, task.exit_code(), task.running_time(), task.invocation_id()))
            async with con.execute('SELECT * FROM invocations WHERE "id" = ?', (task.invocation_id(),)) as incur:
                invocation = await incur.fetchone()
            assert invocation is not None

            await con.execute('UPDATE workers SET "state" = ? WHERE "id" = ?',
                              (WorkerState.IDLE.value, invocation['worker_id']))
            await self._update_worker_resouce_usage(invocation['worker_id'], connection=con)  # remove resource usage info
            tasks_to_wait = []
            if not self.__use_external_log:
                await con.execute('UPDATE invocations SET "stdout" = ?, "stderr" = ? WHERE "id" = ?',
                                  (stdout, stderr, task.invocation_id()))
            else:
                await con.execute('UPDATE invocations SET "log_external" = 1 WHERE "id" = ?',
                                  (task.invocation_id(),))
                tasks_to_wait.append(asyncio.create_task(self._save_external_logs(task.invocation_id(), stdout, stderr)))

            self.data_access.clear_invocation_progress(task.invocation_id())

            ui_task_delta = TaskDelta(invocation['task_id'])  # for ui event
            ui_task_delta.progress = None
            if task.finished_needs_retry():  # max retry count will be checked by task processor
                await con.execute('UPDATE tasks SET "state" = ?, "work_data_invocation_attempt" = "work_data_invocation_attempt" + 1 WHERE "id" = ?',
                                  (TaskState.READY.value, invocation['task_id']))
                ui_task_delta.state = TaskState.READY  # for ui event
            elif task.finished_with_error():
                state_details = json.dumps({'message': f'see invocation #{invocation["id"]} log for details',
                                            'happened_at': TaskState.IN_PROGRESS.value,
                                            'type': 'invocation'})
                await con.execute('UPDATE tasks SET "state" = ?, "state_details" = ? WHERE "id" = ?',
                                  (TaskState.ERROR.value,
                                   state_details,
                                   invocation['task_id']))
                ui_task_delta.state = TaskState.ERROR  # for ui event
                ui_task_delta.state_details = state_details  # for ui event
            else:
                await con.execute('UPDATE tasks SET "state" = ? WHERE "id" = ?',
                                  (TaskState.POST_WAITING.value, invocation['task_id']))
                ui_task_delta.state = TaskState.POST_WAITING  # for ui event

            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, ui_task_delta)  # ui event
            await con.commit()
            if len(tasks_to_wait) > 0:
                await asyncio.wait(tasks_to_wait)
        self.wake()
        self.poke_task_processor()

    async def _save_external_logs(self, invocation_id, stdout, stderr):
        logbasedir = self.__external_log_location / 'invocations' / f'{invocation_id}'
        try:
            if not logbasedir.exists():
                logbasedir.mkdir(exist_ok=True)
            async with aiofiles.open(logbasedir / 'stdout.log', 'w') as fstdout, \
                    aiofiles.open(logbasedir / 'stderr.log', 'w') as fstderr:
                await asyncio.gather(fstdout.write(stdout),
                                     fstderr.write(stderr))
        except OSError:
            self.__logger.exception('error happened saving external logs! Ignoring this error')

    #
    # worker reports canceled task
    async def task_cancel_reported(self, task: Invocation, stdout: str, stderr: str):
        """
        scheduler comm protocols should call this when a task is cancelled
        """
        for attempt in range(120):  # TODO: this should be configurable
            # if invocation is super fast - this may happen even before submission is completed,
            # so we might need to wait a bit
            try:
                return await self.__task_cancel_reported_inner(task, stdout, stderr)
            except NeedToRetryLater:
                self.__logger.debug('attempt %d to report invocation  %d cancelled notified it needs to wait', attempt, task.invocation_id())
                await asyncio.sleep(0.5)  # TODO: this should be configurable
                continue
        else:
            self.__logger.error(f'out of attempts trying to report cancel invocation {task.invocation_id()}, probably something is not right with the state of the database')

    async def __task_cancel_reported_inner(self, task: Invocation, stdout: str, stderr: str):
        async with self.__invocation_reporting_lock, \
                self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            self.__logger.debug('task cancelled reported %s', repr(task))
            # sanity check
            async with con.execute('SELECT "state" FROM invocations WHERE "id" = ?', (task.invocation_id(),)) as cur:
                invoc = await cur.fetchone()
                if invoc is None:
                    self.__logger.error('reported task has non existing invocation id %d' % task.invocation_id())
                    return
                if invoc['state'] == InvocationState.INVOKING.value:  # means _submitter has not yet finished, we should wait
                    raise NeedToRetryLater()
                elif invoc['state'] != InvocationState.IN_PROGRESS.value:
                    self.__logger.warning(f'reported task for a finished invocation. assuming that worker failed to cancel task previously and ignoring invocation results. (state={invoc["state"]})')
                    return
            await con.execute('UPDATE invocations SET "state" = ?, "runtime" = ? WHERE "id" = ?',
                              (InvocationState.FINISHED.value, task.running_time(), task.invocation_id()))
            async with con.execute('SELECT * FROM invocations WHERE "id" = ?', (task.invocation_id(),)) as incur:
                invocation = await incur.fetchone()
            assert invocation is not None

            self.data_access.clear_invocation_progress(task.invocation_id())

            await con.execute('UPDATE workers SET "state" = ? WHERE "id" = ?',
                              (WorkerState.IDLE.value, invocation['worker_id']))
            await self._update_worker_resouce_usage(invocation['worker_id'], connection=con)  # remove resource usage info
            tasks_to_wait = []
            if not self.__use_external_log:
                await con.execute('UPDATE invocations SET "stdout" = ?, "stderr" = ? WHERE "id" = ?',
                                  (stdout, stderr, task.invocation_id()))
            else:
                await con.execute('UPDATE invocations SET "log_external" = 1, "stdout" = null, "stderr" = null WHERE "id" = ?',
                                  (task.invocation_id(),))
                tasks_to_wait.append(asyncio.create_task(self._save_external_logs(task.invocation_id(), stdout, stderr)))
            await con.execute('UPDATE tasks SET "state" = ? WHERE "id" = ?',
                              (TaskState.READY.value, invocation['task_id']))
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, TaskDelta(invocation['task_id'], state=TaskState.READY, progress=None))  # ui event
            await con.commit()
            if len(tasks_to_wait) > 0:
                await asyncio.wait(tasks_to_wait)
        self.__logger.debug(f'cancelling task done {repr(task)}')
        self.wake()
        self.poke_task_processor()

    #
    # add new worker to db
    async def add_worker(
            # TODO: WorkerResources (de)serialization
            # TODO: Worker actually passing new WorkerResources on hello
            self, addr: str, worker_type: WorkerType, worker_resources: HardwareResources,  # TODO: all resource should also go here
            *,
            assume_active: bool = True,
            worker_metadata: WorkerMetadata):
        """
        this is called by network protocol handler when worker reports being up to the scheduler
        """
        self.__logger.debug(f'worker reported added: {addr}')
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('BEGIN IMMEDIATE')  # important to have locked DB during all this state change
            # logic for now:
            #  - search for same last_address, same hwid
            #  - if no - search for first entry (OFF or UNKNOWN) with same hwid, ignore address
            #    - in this case also delete addr from DB if exists
            async with con.execute('SELECT "id", state FROM "workers" WHERE "last_address" == ? AND hwid == ?', (addr, worker_resources.hwid)) as worcur:
                worker_row = await worcur.fetchone()
            if worker_row is None:
                # first ensure that there is no entry with the same address
                await con.execute('UPDATE "workers" SET "last_address" = ? WHERE "last_address" == ?', (None, addr))
                async with con.execute('SELECT "id", state FROM "workers" WHERE hwid == ? AND '
                                       '(state == ? OR state == ?)', (worker_resources.hwid,
                                                                      WorkerState.OFF.value, WorkerState.UNKNOWN.value)) as worcur:
                    worker_row = await worcur.fetchone()
            if assume_active:
                ping_state = WorkerPingState.WORKING.value
                state = WorkerState.IDLE.value
            else:
                ping_state = WorkerPingState.OFF.value
                state = WorkerState.OFF.value

            tstamp = global_timestamp_int()
            if worker_row is not None:
                await self.reset_invocations_for_worker(worker_row['id'], con=con, also_update_resources=False)  # we update later
                await con.execute('UPDATE "workers" SET '
                                  'hwid=?, '
                                  'last_seen=?, ping_state=?, state=?, worker_type=?, '
                                  'last_address=?  '
                                  'WHERE "id"=?',
                                  (worker_resources.hwid,
                                   tstamp, ping_state, state, worker_type.value,
                                   addr,
                                   worker_row['id']))
                # async with con.execute('SELECT "id" FROM "workers" WHERE last_address=?', (addr,)) as worcur:
                #     worker_id = (await worcur.fetchone())['id']
                worker_id = worker_row['id']
                self.data_access.mem_cache_workers_state[worker_id].update({'last_seen': tstamp,
                                                                            'last_checked': tstamp,
                                                                            'ping_state': ping_state,
                                                                            'worker_id': worker_id})
                # await con.execute('UPDATE tmpdb.tmp_workers_states SET '
                #                   'last_seen=?, ping_state=? '
                #                   'WHERE worker_id=?',
                #                   (tstamp, ping_state, worker_id))
            else:
                async with con.execute('INSERT INTO "workers" '
                                       '(hwid, '
                                       'last_address, last_seen, ping_state, state, worker_type) '
                                       'VALUES '
                                       '(?, ?, ?, ?, ?, ?)',
                                       (worker_resources.hwid, addr, tstamp, ping_state, state, worker_type.value)) as insworcur:
                    worker_id = insworcur.lastrowid
                self.data_access.mem_cache_workers_state[worker_id] = {'last_seen': tstamp,
                                                                       'last_checked': tstamp,
                                                                       'ping_state': ping_state,
                                                                       'worker_id': worker_id}
                # await con.execute('INSERT INTO tmpdb.tmp_workers_states '
                #                   '(worker_id, last_seen, ping_state) '
                #                   'VALUES '
                #                   '(?, ?, ?)',
                #                   (worker_id, tstamp, ping_state))

            # set new worker's unique session key
            await con.execute(
                'UPDATE "workers" SET session_key = ? WHERE "id" == ?',
                (self._next_unique_session_key(), worker_id)
            )

            resource_fields: Tuple[str, ...] = tuple(x.name for x in self.__config_provider.hardware_resource_definitions())
            # device_type_names = tuple(x.name for x in self.__config_provider.hardware_device_type_definitions())
            device_type_resource_fields: Dict[str, Tuple[str, ...]] = {x.name: tuple(r.name for r in x.resources) for x in self.__config_provider.hardware_device_type_definitions()}
            # in case worker_resources contain dev_types not known to config - they will be ignored
            devices_to_register = []
            # checks
            for field in resource_fields:
                if field not in worker_resources:
                    self.__logger.warning(f'worker (hwid:{worker_resources.hwid}) does not declare expected resource "{field}", assume value=0')
            for res_name, _ in worker_resources.items():
                if res_name not in resource_fields:
                    self.__logger.warning(f'worker (hwid:{worker_resources.hwid}) declares resource "{res_name}" unknown to the scheduler, ignoring')
            for dev_type, dev_name, dev_res in worker_resources.devices():
                if dev_type not in device_type_resource_fields:
                    self.__logger.warning(f'worker (hwid:{worker_resources.hwid}) declares device type "{dev_type}" unknown to the scheduler, ignoring')
                    continue
                devices_to_register.append((dev_type, dev_name, {res_name: res_val for res_name, res_val in dev_res.items() if res_name in device_type_resource_fields[dev_type]}))

            # TODO: note that below sql breaks if there are no resource_fields (which is an unlikely config, but not impossible)
            await con.execute('INSERT INTO resources '
                              '(hwid, ' +
                              ', '.join(f'{field}, total_{field}' for field in resource_fields) +
                              ') '
                              'VALUES (?' + ', ?' * (2 * len(resource_fields)) + ') '
                                                                                 'ON CONFLICT(hwid) DO UPDATE SET ' +
                              ', '.join(f'"{field}"=excluded.{field}, "total_{field}"=excluded.total_{field}' for field in resource_fields)
                              ,
                              (worker_resources.hwid,
                               *(x for field in resource_fields for x in (
                                   (worker_resources[field].value, worker_resources[field].value) if field in worker_resources else (0, 0))  # TODO: do NOT invent defaults here, only set known fields, like in dev code below
                                 ))
                              )

            for dev_type, dev_name, dev_res in sorted(devices_to_register, key=lambda x: (x[0], x[1])):  # sort by (deva_type, dev_name) to ensure some consistent order

                dev_type_table_name = f'hardware_device_type__{dev_type}'
                if dev_res:
                    await con.execute(
                        f'INSERT INTO "{dev_type_table_name}" '
                        f'(hwid, hw_dev_name, ' +
                        ', '.join(f'res__{field}' for field, _ in dev_res.items()) +
                        ') '
                        'VALUES (?, ?' + ', ?' * (len(dev_res)) + ') '
                                                                  'ON CONFLICT(hwid,"hw_dev_name") DO UPDATE SET ' +
                        ', '.join(f'"res__{field}"=excluded.res__{field}' for field in dev_res)
                        ,
                        (worker_resources.hwid, dev_name,
                         *(res_val.value for _, res_val in dev_res.items())
                         )
                    )
                else:
                    await con.execute(
                        f'INSERT INTO "{dev_type_table_name}" '
                        f'(hwid, hw_dev_name) ' +
                        'VALUES (?, ?) '
                        'ON CONFLICT(hwid,"hw_dev_name") DO NOTHING'
                        ,
                        (worker_resources.hwid, dev_name)
                    )

            await self._update_worker_resouce_usage(worker_id, hwid=worker_resources.hwid, connection=con)  # used resources are inited to none
            self.data_access.set_worker_metadata(worker_resources.hwid, worker_metadata)
            await con.commit()
        self.__logger.debug(f'finished worker reported added: {addr}')
        self.poke_task_processor()
        self.poke_pinger()

    # TODO: add decorator that locks method from reentry or smth
    #  potentially a worker may report done while this works,
    #  or when scheduler picked worker and about to run this, which will lead to inconsistency warning
    #  NOTE!: so far it's always called from a STARTED transaction, so there should not be reentry possible
    #  But that is not enforced right now, easy to make mistake
    async def _update_worker_resouce_usage(self, worker_id: int, resources: Optional[Requirements] = None, *, hwid=None, connection: aiosqlite.Connection) -> bool:
        """
        updates resource information based on new worker resources usage
        as part of ongoing transaction
        Note: con SHOULD HAVE STARTED TRANSACTION, otherwise it might be not safe to call this

        :param worker_id:
        :param hwid: if hwid of worker_id is already known - provide it here to skip extra db query. but be SURE it's correct!
        :param connection: opened db connection. expected to have Row as row factory
        :return: if commit is needed on connection (if db set operation happened)
        """
        assert connection.in_transaction, 'expectation failure'

        resource_fields = tuple(x.name for x in self.__config_provider.hardware_resource_definitions())
        device_type_names = tuple(x.name for x in self.__config_provider.hardware_device_type_definitions())

        workers_resources = self.data_access.mem_cache_workers_resources
        if hwid is None:
            async with connection.execute('SELECT "hwid" FROM "workers" WHERE "id" == ?', (worker_id,)) as worcur:
                hwid = (await worcur.fetchone())['hwid']

        # calculate available resources NOT counting current worker_id
        async with connection.execute(f'SELECT '
                                      f'{", ".join(resource_fields)}, '
                                      f'{", ".join("total_" + x for x in resource_fields)} '
                                      f'FROM resources WHERE hwid == ?', (hwid,)) as rescur:
            available_res = dict(await rescur.fetchone())
        available_dev_type_to_ids: Dict[str, Dict[int, Dict[str, Union[int, float, str]]]] = {}
        current_available_dev_type_to_ids: Dict[str, Set[int]] = {}
        for dev_type in device_type_names:
            dev_type_table_name = f'hardware_device_type__{dev_type}'
            async with connection.execute(
                    f'SELECT * FROM "{dev_type_table_name}" WHERE hwid == ?',
                    (hwid,)) as rescur:
                all_dev_rows = [dict(x) for x in await rescur.fetchall()]
            available_dev_type_to_ids[dev_type] = {
                x['dev_id']: {k[len('res__'):]: v for k, v in x.items() if k.startswith('res__')}  # resource cols start with res__
                for x in all_dev_rows
            }  # note, these are ALL devices, with "available" 0 and 1 values, we don't *trust* "available", we recalc them below, just like with non-total res
            current_available_dev_type_to_ids[dev_type] = {x['dev_id'] for x in all_dev_rows if x['available']}  # now this counts available to check later if anything changed
        current_available = {k: v for k, v in available_res.items() if not k.startswith('total_')}
        available_res = {k[len('total_'):]: v for k, v in available_res.items() if k.startswith('total_')}  # start with full total res

        for wid, res in workers_resources.items():
            if wid == worker_id:
                continue  # SKIP worker_id currently being set
            if res.get('hwid') != hwid:
                continue
            # recalc actual available resources based on cached worker_resources
            for field in resource_fields:
                if field not in res.get('res', {}):
                    continue
                available_res[field] -= res['res'][field]
            # recalc actual available devices based on cached worker_resources
            for dev_type in device_type_names:
                if dev_type not in res.get('dev', {}):
                    continue
                for dev_id in res['dev'][dev_type]:
                    available_dev_type_to_ids[dev_type].pop(dev_id)
        ##

        # now choose proper amount of resources to pick
        if resources is None:
            workers_resources[worker_id] = {'hwid': hwid}  # remove resource usage info
        else:
            workers_resources[worker_id] = {'res': {}, 'dev': {}}
            for field in resource_fields:
                if field not in resources.resources:
                    continue
                if available_res[field] < resources.resources[field].min:
                    raise NotEnoughResources(f'{field}: {resources.resources[field].min} out of {available_res[field]}')
                # so we take preferred amount of resources (or minimum if pref not set), but no more than available
                # if preferred is lower than min - it's ignored
                workers_resources[worker_id]['res'][field] = min(available_res[field],
                                                                 max(resources.resources[field].pref, resources.resources[field].min))
                available_res[field] -= workers_resources[worker_id]['res'][field]

            selected_devs: Dict[str, List[int]] = {}  # dev_type to list of dev_ids of that type that are picked
            for dev_type, dev_reqs in resources.devices.items():
                if dev_reqs.min == 0 and dev_reqs.pref == 0:  # trivial check
                    continue
                if dev_type not in available_dev_type_to_ids:
                    if dev_reqs.min > 0:
                        raise NotEnoughResources(f'device "{dev_type}" missing')  # this shouldn't happen - this whole func is only called when resources are checked
                    else:
                        continue
                for dev_id, dev_res in available_dev_type_to_ids[dev_type].items():
                    # now we check if dev fits requirements
                    is_good = True
                    for req_name, req_val in dev_reqs.resources.items():  # we ignore pref in current logic - devices are always taken full
                        if req_name not in dev_res:
                            raise NotEnoughResources(f'device "{dev_type}" does not have requested resource "{req_name}"')  # this also should not happen
                        if dev_res[req_name] < req_val.min:
                            is_good = False
                            break
                    if is_good:
                        selected_devs.setdefault(dev_type, []).append(dev_id)
                        if len(selected_devs[dev_type]) >= max(dev_reqs.min, dev_reqs.pref):
                            # we selected enough devices of this type
                            break
                # now remove selected from available
                for dev_id in selected_devs.get(dev_type, []):
                    available_dev_type_to_ids[dev_type].pop(dev_id)
                # sanity check
                if dev_reqs.min > 0 and len(selected_devs[dev_type]) < dev_reqs.min:
                    raise NotEnoughResources(f'device "{dev_type}: cannot select {dev_reqs.min} out of {len(selected_devs[dev_type])}')
            workers_resources[worker_id]['dev'] = selected_devs

            workers_resources[worker_id]['hwid'] = hwid  # just to ensure it was not overriden

        self.__logger.debug(f'updating resources {hwid} with {available_res} against {current_available}')
        self.__logger.debug(workers_resources)

        available_res_didnt_change = available_res == current_available
        available_devs_didnt_change = all(set(available_dev_type_to_ids[dev_type].keys()) == current_available_dev_type_to_ids[dev_type] for dev_type in device_type_names)
        if available_res == current_available and available_devs_didnt_change:  # nothing needs to be updated
            return False

        if not available_res_didnt_change:
            await connection.execute(f'UPDATE resources SET {", ".join(f"{k}={v}" for k, v in available_res.items())} WHERE hwid == ?', (hwid,))
        if not available_devs_didnt_change:
            for dev_type in device_type_names:  # TODO: only update affected tables
                dev_type_table_name = f'hardware_device_type__{dev_type}'
                await connection.execute(f'UPDATE "{dev_type_table_name}" SET "available"=0 WHERE hwid==?', (hwid,))
                await connection.executemany(f'UPDATE "{dev_type_table_name}" SET "available"=1 WHERE dev_id==?', ((x,) for x in available_dev_type_to_ids[dev_type].keys()))
        return True

    #
    #
    async def update_invocation_progress(self, invocation_id: int, progress: float):
        """
        report progress update on invocation that is being worked on
        there are not too many checks here, as progress report is considered non-vital information,
        so if such message comes after invocation is finished - it's not big deal
        """
        prev_progress = self.data_access.get_invocation_progress(invocation_id)
        self.data_access.set_invocation_progress(invocation_id, progress)
        if prev_progress != progress:
            task_id = None
            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                async with con.execute('SELECT task_id FROM invocations WHERE "state" == ? AND "id" == ?',
                                       (InvocationState.IN_PROGRESS.value, invocation_id,)) as cur:
                    task_id_row = await cur.fetchone()
                    if task_id_row is not None:
                        task_id = task_id_row['task_id']
            if task_id is not None:
                self.ui_state_access.scheduler_reports_task_updated(TaskDelta(task_id, progress=progress))

    #
    # worker reports it being stopped
    async def worker_stopped(self, addr: str):
        """

        :param addr:
        :return:
        """
        self.__logger.debug(f'worker reported stopped: {addr}')
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('BEGIN IMMEDIATE')
            async with con.execute('SELECT id, hwid from "workers" WHERE "last_address" = ?', (addr,)) as worcur:
                worker_row = await worcur.fetchone()
            if worker_row is None:
                self.__logger.warning(f'unregistered worker reported "stopped": {addr}, ignoring')
                await con.rollback()
                return
            wid = worker_row['id']
            hwid = worker_row['hwid']
            # print(wid)

            # we ensure there are no invocations running with this worker
            async with con.execute('SELECT "id", task_id, state FROM invocations WHERE worker_id = ? AND ("state" = ? OR "state" = ?)',
                                   (wid, InvocationState.IN_PROGRESS.value, InvocationState.INVOKING.value)) as invcur:
                invocations = await invcur.fetchall()

            await con.execute('UPDATE workers SET "state" = ?, session_key = ? WHERE "id" = ?', (WorkerState.OFF.value, None, wid))
            for invocation_row in invocations:
                invocation_state = InvocationState(invocation_row['state'])
                # we do NOT touch invoking invocations and tasks -
                # if they are still invoking - submission process is still going,
                # and it itself will cancel those invocations
                if invocation_state == InvocationState.IN_PROGRESS:
                    await con.execute('UPDATE invocations SET state = ? WHERE "id" = ?', (InvocationState.FINISHED.value, invocation_row["id"]))
                    await con.execute('UPDATE tasks SET state = ? WHERE "id" = ?', (TaskState.READY.value, invocation_row["task_id"]))
            await self._update_worker_resouce_usage(wid, hwid=hwid, connection=con)  # oh wait, it happens right here, still an assert won't hurt
            del self.data_access.mem_cache_workers_resources[wid]  # remove from cache  # TODO: ENSURE resources were already unset for this wid
            if len(invocations) > 0:
                con.add_after_commit_callback(self.ui_state_access.scheduler_reports_tasks_updated, [TaskDelta(x["task_id"], state=TaskState.READY) for x in invocations])  # ui event
            await con.commit()
        self.__logger.debug(f'finished worker reported stopped: {addr}')

    #
    # protocol related commands
    #
    #
    # cancel invocation
    async def cancel_invocation(self, invocation_id: str):
        self.__logger.debug(f'canceling invocation {invocation_id}')
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT * FROM "invocations" WHERE "id" = ?', (invocation_id,)) as cur:
                invoc = await cur.fetchone()
            if invoc is None or invoc['state'] != InvocationState.IN_PROGRESS.value:
                return
            async with con.execute('SELECT "last_address" FROM "workers" WHERE "id" = ?', (invoc['worker_id'],)) as cur:
                worker = await cur.fetchone()
        if worker is None:
            self.__logger.error('inconsistent worker ids? how?')
            return
        addr = AddressChain(worker['last_address'])

        # the logic is:
        # - we send the worker a signal to cancel invocation
        # - later worker sends task_cancel_reported, and we are happy
        # - but worker might be overloaded, broken or whatever and may never send it. and it can even finish task and send task_done_reported, witch we need to treat
        with WorkerControlClient.get_worker_control_client(addr, self.message_processor()) as client:  # type: WorkerControlClient
            await client.cancel_task()  # TODO: cannot blindly cancel whatever "current" task is, must provide invocation ID we are cancelling

        # oh no, we don't do that, we wait for worker to report task canceled.  await con.execute('UPDATE invocations SET "state" = ? WHERE "id" = ?', (InvocationState.FINISHED.value, invocation_id))

    #
    #
    async def cancel_invocation_for_task(self, task_id: int):
        self.__logger.debug(f'canceling invocation for task {task_id}')
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT "id" FROM "invocations" WHERE "task_id" = ? AND state = ?', (task_id, InvocationState.IN_PROGRESS.value)) as cur:
                invoc = await cur.fetchone()
        if invoc is None:
            return
        return await self.cancel_invocation(invoc['id'])

    #
    #
    async def cancel_invocation_for_worker(self, worker_id: int):
        self.__logger.debug(f'canceling invocation for worker {worker_id}')
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('SELECT "id" FROM "invocations" WHERE "worker_id" == ? AND state == ?', (worker_id, InvocationState.IN_PROGRESS.value)) as cur:
                invoc = await cur.fetchone()
        if invoc is None:
            return
        return await self.cancel_invocation(invoc['id'])

    #
    #
    async def force_set_node_task(self, task_id: int, node_id: int):
        self.__logger.debug(f'forcing task {task_id} to node {node_id}')
        try:
            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                await con.execute('BEGIN IMMEDIATE')
                await con.execute('PRAGMA FOREIGN_KEYS = on')
                async with con.execute('SELECT "state" FROM tasks WHERE "id" == ?', (task_id,)) as cur:
                    row = await cur.fetchone()
                if row is None:
                    self.__logger.warning(f'failed to force task node: task {task_id} not found')
                    await con.rollback()
                    return

                state = TaskState(row['state'])
                new_state = None
                if state in (TaskState.WAITING, TaskState.READY, TaskState.POST_WAITING):
                    new_state = TaskState.WAITING
                elif state == TaskState.DONE:
                    new_state = TaskState.DONE
                # if new_state was not set - means state was invalid
                if new_state is None:
                    self.__logger.warning(f'changing node of a task in state {state.name} is not allowed')
                    await con.rollback()
                    raise ValueError(f'changing node of a task in state {state.name} is not allowed')

                await con.execute('UPDATE tasks SET "node_id" = ?, "state" = ? WHERE "id" = ?', (node_id, new_state.value, task_id))
                con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, TaskDelta(task_id, node_id=node_id))  # ui event
                # reset blocking too
                await self.data_access.reset_task_blocking(task_id, con=con)
                await con.commit()
        except aiosqlite.IntegrityError:
            self.__logger.error(f'could not set task {task_id} to node {node_id} because of database integrity check')
            raise DataIntegrityError() from None
        else:
            self.wake()
            self.poke_task_processor()

    #
    # force change task state
    async def force_change_task_state(self, task_ids: Union[int, Iterable[int]], state: TaskState):
        """
        forces task into given state.
        obviously a task cannot be forced into certain states, like IN_PROGRESS, GENERATING, POST_GENERATING
        :param task_ids:
        :param state:
        :return:
        """
        if state in (TaskState.IN_PROGRESS, TaskState.GENERATING, TaskState.POST_GENERATING):
            self.__logger.error(f'cannot force task {task_ids} into state {state}')
            return
        if isinstance(task_ids, int):
            task_ids = [task_ids]
        query = 'UPDATE tasks SET "state" = %d WHERE "id" = ?' % state.value
        # print('beep')
        async with self.data_access.data_connection() as con:
            for task_id in task_ids:
                await con.execute('BEGIN IMMEDIATE')
                async with con.execute('SELECT "state" FROM tasks WHERE "id" = ?', (task_id,)) as cur:
                    cur_state = await cur.fetchone()
                    if cur_state is None:
                        await con.rollback()
                        continue
                    cur_state = TaskState(cur_state[0])
                if cur_state in (TaskState.IN_PROGRESS, TaskState.GENERATING, TaskState.POST_GENERATING):
                    self.__logger.warning(f'forcing task out of state {cur_state} is not allowed')
                    await con.rollback()
                    continue

                await con.execute(query, (task_id,))
                # just in case we also reset blocking
                await self.data_access.reset_task_blocking(task_id, con=con)
                con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, TaskDelta(task_id, state=state))  # ui event
                await con.commit()  # TODO: this can be optimized into a single transaction
        # print('boop')
        self.wake()
        self.poke_task_processor()

    #
    # change task's paused state
    async def set_task_paused(self, task_ids_or_group: Union[int, Iterable[int], str], paused: bool):
        if isinstance(task_ids_or_group, str):
            async with self.data_access.data_connection() as con:
                await con.execute('UPDATE tasks SET "paused" = ? WHERE "id" IN (SELECT "task_id" FROM task_groups WHERE "group" = ?)',
                                  (int(paused), task_ids_or_group))
                ui_task_ids = await self.ui_state_access._get_group_tasks(task_ids_or_group)  # ui event
                con.add_after_commit_callback(self.ui_state_access.scheduler_reports_tasks_updated, [TaskDelta(ui_task_id, paused=paused) for ui_task_id in ui_task_ids])  # ui event
                await con.commit()
            self.wake()
            self.poke_task_processor()
            return
        if isinstance(task_ids_or_group, int):
            task_ids_or_group = [task_ids_or_group]
        query = 'UPDATE tasks SET "paused" = %d WHERE "id" = ?' % int(paused)
        async with self.data_access.data_connection() as con:
            await con.executemany(query, ((x,) for x in task_ids_or_group))
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_tasks_updated, [TaskDelta(ui_task_id, paused=paused) for ui_task_id in task_ids_or_group])  # ui event
            await con.commit()
        self.wake()
        self.poke_task_processor()

    async def add_task_group(self, task_group_name: str, creator: str, *, allow_name_change_to_make_unique: bool = False, priority: float = 50.0, user_data: Optional[bytes] = None) -> Tuple[bool, str]:
        """
        returns True if group was created, False if it already exists
        """
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('BEGIN IMMEDIATE')
            base_task_group_name = task_group_name
            counter = 1
            while True:
                async with con.execute('SELECT 1 FROM task_group_attributes WHERE "group" == ?', (task_group_name,)) as cur:
                    if (await cur.fetchone()) is not None:
                        if allow_name_change_to_make_unique:
                            task_group_name = f'{base_task_group_name} {counter}'
                            counter += 1
                            continue
                        else:
                            return False, ''
                    break

            await con.execute(
                'INSERT INTO task_group_attributes '
                '("group", "ctime", "state", "creator", priority, user_data) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (
                    task_group_name,
                    global_timestamp_int(),
                    TaskGroupArchivedState.NOT_ARCHIVED.value,
                    creator,
                    priority,
                    bytes(user_data) if user_data is not None else None,
                )
            )
            await con.commit()
        return True, task_group_name

    async def get_task_group_user_data(self, task_group_name: str) -> Optional[bytes]:
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute(
                    'SELECT user_data FROM task_group_attributes WHERE "group" == ?',
                    (task_group_name,)
            ) as cur:
                row = await cur.fetchone()
        if row is None:
            raise NoSuchGroupError(task_group_name)
        return bytes(row['user_data']) if row['user_data'] is not None else None

    #
    # change task group archived state
    @alocking('scheduler.task_group_deletion')
    async def set_task_group_archived(self, task_group_name: str, state: TaskGroupArchivedState = TaskGroupArchivedState.ARCHIVED) -> None:
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('UPDATE task_group_attributes SET state=? WHERE "group"==?', (state.value, task_group_name))  # this triggers all task deadness | 2, so potentially it can be long, beware
            # task's dead field's 2nd bit is set, but we currently do not track it
            # so no event needed
            await con.commit()
            if state == TaskGroupArchivedState.NOT_ARCHIVED:
                self.poke_task_processor()  # unarchived, so kick task processor, just in case
                return
            # otherwise - it's archived
            # now all tasks belonging to that group should be set to dead|2
            # we need to make sure to cancel all running invocations for those tasks
            # at this point tasks are archived and won't be processed,
            # so we only expect concurrent changes due to already running _submitters and _awaiters,
            # like INVOKING->IN_PROGRESS
            async with con.execute('SELECT "id" FROM invocations '
                                   'INNER JOIN task_groups ON task_groups.task_id == invocations.task_id '
                                   'WHERE task_groups."group" == ? AND invocations.state == ?',
                                   (task_group_name, InvocationState.INVOKING.value)) as cur:
                invoking_invoc_ids = set(x['id'] for x in await cur.fetchall())
            async with con.execute('SELECT "id" FROM invocations '
                                   'INNER JOIN task_groups ON task_groups.task_id == invocations.task_id '
                                   'WHERE task_groups."group" == ? AND invocations.state == ?',
                                   (task_group_name, InvocationState.IN_PROGRESS.value)) as cur:
                active_invoc_ids = tuple(x['id'] for x in await cur.fetchall())
                # i sure use a lot of fetchall where it's much more natural to iterate cursor
                # that is because of a fear of db locking i got BEFORE switching to WAL, when iterating connection was randomly crashing other connections not taking timeout into account at all.

        # note at this point we might have some invoking_invocs_id, but at this point some of them
        # might already have been set to in-progress and even got into active_invoc_ids list

        # first - cancel all in-progress invocations
        for inv_id in active_invoc_ids:
            await self.cancel_invocation(inv_id)

        # now since we dont have the ability to safely cancel running _submitter task - we will just wait till
        # invoking invocations change state
        # sure it's a bit bruteforce
        # but a working solution for now
        if len(invoking_invoc_ids) == 0:
            return
        async with self.data_access.data_connection() as con:
            while len(invoking_invoc_ids) > 0:
                # TODO: this forever while doesn't seem right
                #  in average case it should basically never happen at all
                #  only in case of really bad buggy network connections an invocation can get stuck on INVOKING
                #  but there are natural timeouts in _submitter that will switch it from INVOKING eventually
                #  the only question is - do we want to just stay in this function until it's resolved? UI's client is single thread, so it will get stuck waiting
                con.row_factory = aiosqlite.Row
                async with con.execute('SELECT "id",state FROM invocations WHERE state!={} AND "id" IN ({})'.format(
                        InvocationState.IN_PROGRESS.value,
                        ','.join(str(x) for x in invoking_invoc_ids))) as cur:
                    changed_state_ones = await cur.fetchall()

                for oid, ostate in ((x['id'], x['state']) for x in changed_state_ones):
                    if ostate == InvocationState.IN_PROGRESS.value:
                        await self.cancel_invocation(oid)
                    assert oid in invoking_invoc_ids
                    invoking_invoc_ids.remove(oid)
                await asyncio.sleep(0.5)

    async def __cancel_invocations_for_tasks(self, con: aiosqlite_overlay.ConnectionWithCallbacks, task_ids: Set[int]):
        if not task_ids:
            return

        async with con.execute(
                'SELECT "id" FROM invocations '
                f'WHERE task_id IN ({",".join(str(x) for x in task_ids)})'
        ) as cur:
            invoc_ids = [x['id'] for x in await cur.fetchall()]

        for inv_id in invoc_ids:
            await self.cancel_invocation(inv_id)

    @staticmethod
    async def __has_nonfinished_invocations_for_tasks(con: aiosqlite_overlay.ConnectionWithCallbacks, task_ids: Set[int]) -> bool:
        if not task_ids:
            return False

        async with con.execute(
                'SELECT COUNT(*) as cnt FROM invocations '
                f'WHERE state != ? AND task_id IN ({",".join(str(x) for x in task_ids)})',
                (InvocationState.FINISHED.value,)
        ) as cur:
            return (await cur.fetchone())['cnt'] != 0

    @staticmethod
    async def __remove_tasks_not_fully_present_in_splits(con: aiosqlite_overlay.ConnectionWithCallbacks, task_ids: Set[int], split_ids: Set[int]) -> bool:
        smth_changed = False
        async with con.execute(
                f'WITH tmp AS (SELECT * FROM tasks WHERE "id" IN ({",".join(str(x) for x in task_ids)})) '
                'SELECT id, "split_id", "split_count" FROM task_splits '
                'INNER JOIN tmp ON  task_splits.task_id == tmp.id OR (task_splits.origin_task_id == tmp.id AND task_splits.split_element == 0)'
        ) as cur:
            rows = await cur.fetchall()
        split_id_counts = {}
        for row in rows:
            split_id = row['split_id']
            if split_id not in split_id_counts:
                split_id_counts[split_id] = 0
            split_id_counts[split_id] += 1

        for row in rows:
            split_id = row['split_id']
            # +1 cuz we expect full group to have split_count splitted tasks + 1 origin task
            if row['split_count'] + 1 == split_id_counts[split_id]:
                # means full group, remember to purge
                if row['split_id'] not in split_ids:
                    split_ids.add(row['split_id'])
                    smth_changed = True
                # and skip
                continue
            if row['id'] in task_ids:
                task_ids.remove(row['id'])
                smth_changed = True
        return smth_changed

    @staticmethod
    async def __remove_tasks_not_fully_present_in_with_parental_tree(con: aiosqlite_overlay.ConnectionWithCallbacks, task_ids: Set[int]) -> bool:
        smth_changed = False
        async with con.execute(
                f'WITH tmp AS (SELECT * FROM tasks WHERE "id" IN ({",".join(str(x) for x in task_ids)})) '
                'SELECT tasks.id as pid, tasks.parent_id, tasks.children_count, tmp.id as cid FROM tasks '
                'INNER JOIN tmp ON tasks.id == tmp.parent_id OR tasks.id == tmp.id '
                'WHERE tasks.children_count != 0'
        ) as cur:
            rows = await cur.fetchall()
        pid_counts = {}
        for row in rows:
            pid = row['pid']
            if pid not in pid_counts:
                pid_counts[pid] = 0
            pid_counts[pid] += 1

        for row in rows:
            pid = row['pid']
            # +1 cuz we expect full group to have children_count children tasks + 1 parent task
            if row['children_count'] + 1 == pid_counts[pid]:
                # and skip
                continue
            if row['cid'] in task_ids:
                task_ids.remove(row['cid'])
                smth_changed = True
        return smth_changed

    @alocking('scheduler.task_group_deletion')
    async def delete_task_group(self, task_group_name: str, also_delete_orphaned_tasks: bool = True):
        """
        deletes task group named task_group_name.
        If also_delete_orphaned_tasks is True - then also delete all tasks that will have no
        task groups left as a result of this group deletion.

        Note, affected tasks will be archived first, all running invocations belonging to these
        tasks will be force stopped, which may take time.
        The method will not return until all operations are completed,
        but this may not (and will not) be completed in a single transaction, so other components
        may see intermediate states of things, such as orphaned archived tasks waiting to be deleted
        """
        self.__logger.debug('removing task group "%s"', task_group_name)
        if not also_delete_orphaned_tasks:
            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                await con.execute('PRAGMA FOREIGN_KEYS = on')
                await self.data_access.delete_task_group(task_group_name, con=con)
                await con.commit()
                self.__logger.debug('task group "%s" removal: group removed', task_group_name)
            self.__logger.debug('task group "%s" removal: done', task_group_name)
            return

        assert also_delete_orphaned_tasks

        task_ids_to_purge: Set[int] = set()
        split_ids_to_purge: Set[int] = set()

        # everything will be done in an iterative loop
        # to ensure the whole deletion is done in a single transaction,
        # while all running invocations are still cancelled between transaction attempts

        do_wait_a_bit = False
        while True:
            something_changed_this_iteration = False
            # if it's not first attempt - wait a bit
            if do_wait_a_bit:
                self.__logger.debug('task group "%s" removal: waiting for affected invocations to be cancelled', task_group_name)
                await asyncio.sleep(0.5)
            do_wait_a_bit = True

            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                await con.execute('PRAGMA FOREIGN_KEYS = on')
                # ensure that no invocations are running
                if await self.__has_nonfinished_invocations_for_tasks(con, task_ids_to_purge):
                    continue

                await self.data_access.begin_immediate_transaction(con=con)
                # Ensure again that no invocations running, go back to waiting if there are
                if await self.__has_nonfinished_invocations_for_tasks(con, task_ids_to_purge):
                    await con.rollback()
                    continue

                # only now, within a transaction we once again reselect all tasks
                # and make sure no invocations are running.
                # Only this way we can be sure there are no changes made between transactions,
                # while we wait for invocation cancellation

                old_task_ids_to_purge = set(task_ids_to_purge)
                old_split_ids_to_purge = set(split_ids_to_purge)

                # remember which tasks will become orphaned to delete
                async with con.execute(
                        'SELECT "id" FROM tasks '
                        'INNER JOIN task_groups ON task_groups.task_id == tasks.id '
                        'GROUP BY tasks."id" HAVING COUNT("group") == 1 AND "group" == ?',
                        (task_group_name,)
                ) as cur:
                    task_ids_to_purge = {x['id'] for x in await cur.fetchall()}
                split_ids_to_purge = set()

                # we must exclude ones that participate in splits with tasks not to be deleted
                while await self.__remove_tasks_not_fully_present_in_splits(con, task_ids_to_purge, split_ids_to_purge):
                    pass  # loop will ensure we propagate tasks through the whole split tree

                # also exclude partial parents-children. delete whole family only, so noone wants to get revenge later
                while await self.__remove_tasks_not_fully_present_in_with_parental_tree(con, task_ids_to_purge):
                    pass  # loop will ensure we propagate tasks through the whole family tree

                if task_ids_to_purge != old_task_ids_to_purge or split_ids_to_purge != old_split_ids_to_purge:
                    something_changed_this_iteration = True
                    self.__logger.debug('task group "%s" removal: updated intermediate list of tasks to be removed with the group: %s', task_group_name, task_ids_to_purge)

                # do NOT delete group until we are sure no tasks are left in it

                if something_changed_this_iteration:
                    await con.executemany(
                        'UPDATE tasks SET "dead" = "dead" | 2 '
                        'WHERE "id" == ?',
                        ((x,) for x in task_ids_to_purge)
                    )
                    self.__logger.debug('task group "%s" removal: orphaned tasks set archived', task_group_name)

                    # Ensure once again that no invocations running with possible task_ids updated, go back to waiting if there are
                    if await self.__has_nonfinished_invocations_for_tasks(con, task_ids_to_purge):
                        await con.commit()
                        await self.__cancel_invocations_for_tasks(con, task_ids_to_purge)
                        self.__logger.debug('task group "%s" removal: orphaned task invocations cancellations sent', task_group_name)
                        continue
                self.__logger.debug('task group "%s" removal: all invocations done, proceeding with removal', task_group_name)
                self.__logger.debug('task group "%s" removal: tasks to be removed with the group: %s', task_group_name, task_ids_to_purge)

                # remove ALL invocations related to tasks
                # TODO: delete external logs if any
                await con.executemany(
                    'DELETE FROM invocations '
                    'WHERE task_id == ?',
                    ((x,) for x in task_ids_to_purge)
                )
                self.__logger.debug('task group "%s" removal: invocations removed', task_group_name)

                # remove all splits
                await con.executemany(
                    'DELETE FROM task_splits '
                    'WHERE split_id == ?',
                    ((x,) for x in split_ids_to_purge)
                )
                self.__logger.debug('task group "%s" removal: task splits removed', task_group_name)

                # finally, remove all tasks
                await con.executemany(
                    'DELETE FROM tasks '
                    'WHERE "id" == ?',
                    ((x,) for x in task_ids_to_purge)
                )
                self.__logger.debug('task group "%s" removal: tasks removed', task_group_name)

                # only delete group if it is empty after all deletions
                # check if there are any tasks left in the group
                # TODO: allow deleting groups with tasks that still belong to at least one OTHER group
                async with con.execute(
                        'SELECT COUNT(*) as cnt FROM task_groups '
                        'WHERE "group" == ?',
                        (task_group_name,)
                ) as cur:
                    still_has_tasks = (await cur.fetchone())['cnt'] > 0
                if still_has_tasks:
                    self.__logger.debug('task group "%s" removal: task group cannot be removed as there are tasks left in it', task_group_name)
                else:
                    await self.data_access.delete_task_group(task_group_name, con=con)
                    self.__logger.debug('task group "%s" removal: task group removed', task_group_name)

                await con.commit()
                break
        self.__logger.debug('task group "%s" removal: done', task_group_name)

    async def set_task_group_priority(self, task_group: str, priority: float) -> float:
        await self.data_access.set_task_group_priority(task_group, priority)
        return priority  # for now there is no restrictions on priority, so return same

    #
    # set task name
    async def set_task_name(self, task_id: int, new_name: str):
        async with self.data_access.data_connection() as con:
            await con.execute('UPDATE tasks SET "name" = ? WHERE "id" = ?', (new_name, task_id))
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, TaskDelta(task_id, name=new_name))  # ui event
            await con.commit()

    #
    # set task groups
    async def set_task_groups(self, task_id: int, group_names: Iterable[str]):
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('BEGIN IMMEDIATE')
            async with con.execute('SELECT "group" FROM task_groups WHERE "task_id" = ?', (task_id,)) as cur:
                all_groups = set(x['group'] for x in await cur.fetchall())
            group_names = set(group_names)
            groups_to_set = group_names - all_groups
            groups_to_del = all_groups - group_names
            print(task_id, groups_to_set, groups_to_del, all_groups, group_names)

            for group_name in groups_to_set:
                await con.execute('INSERT INTO task_groups (task_id, "group") VALUES (?, ?)', (task_id, group_name))
                await con.execute('INSERT OR IGNORE INTO task_group_attributes ("group", "ctime") VALUES (?, ?)', (group_name, global_timestamp_int()))
            for group_name in groups_to_del:
                await con.execute('DELETE FROM task_groups WHERE task_id = ? AND "group" = ?', (task_id, group_name))
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_tasks_removed_from_group, [task_id], groups_to_del)  # ui event
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_groups_changed, groups_to_set)  # ui event
            #
            # ui event
            if len(groups_to_set) > 0:
                async with con.execute(
                        'SELECT tasks.id, tasks.parent_id, tasks.children_count, tasks.active_children_count, tasks.state, tasks.state_details, tasks.paused, tasks.node_id, '
                        'tasks.node_input_name, tasks.node_output_name, tasks.name, tasks.split_level, tasks.work_data_invocation_attempt, '
                        'task_splits.origin_task_id, task_splits.split_id, invocations."id" as invoc_id '
                        'FROM "tasks" '
                        'LEFT JOIN "task_splits" ON tasks.id=task_splits.task_id '
                        'LEFT JOIN "invocations" ON tasks.id=invocations.task_id AND invocations.state = ? '
                        'WHERE tasks."id" == ?',
                        (InvocationState.IN_PROGRESS.value, task_id)) as cur:
                    task_row = await cur.fetchone()
                if task_row is not None:
                    progress = self.data_access.get_invocation_progress(task_row['invoc_id'])
                    con.add_after_commit_callback(
                        self.ui_state_access.scheduler_reports_task_added,
                        TaskData(task_id, task_row['parent_id'], task_row['children_count'], task_row['active_children_count'], TaskState(task_row['state']),
                                 task_row['state_details'], bool(task_row['paused']), task_row['node_id'], task_row['node_input_name'], task_row['node_output_name'],
                                 task_row['name'], task_row['split_level'], task_row['work_data_invocation_attempt'], progress,
                                 task_row['origin_task_id'], task_row['split_id'], task_row['invoc_id'], group_names),
                        groups_to_set
                    )  # ui event
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_updated, TaskDelta(task_id, groups=group_names))  # ui event
            #
            #
            await con.commit()

    #
    # update task attributes
    async def update_task_attributes(self, task_id: int, attributes_to_update: dict, attributes_to_delete: set):
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('BEGIN IMMEDIATE')
            async with con.execute('SELECT "attributes" FROM tasks WHERE "id" = ?', (task_id,)) as cur:
                row = await cur.fetchone()
            if row is None:
                self.__logger.warning(f'update task attributes for {task_id} failed. task id not found.')
                await con.commit()
                return
            attributes = await deserialize_attributes(row['attributes'])
            attributes.update(attributes_to_update)
            for name in attributes_to_delete:
                if name in attributes:
                    del attributes[name]
            await con.execute('UPDATE tasks SET "attributes" = ? WHERE "id" = ?', (await serialize_attributes(attributes),
                                                                                   task_id))
            await con.commit()

    #
    # set environment resolver
    async def set_task_environment_resolver_arguments(self, task_id: int, env_res: Optional[EnvironmentResolverArguments]):
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            await con.execute('UPDATE tasks SET "environment_resolver_data" = ? WHERE "id" = ?',
                              (await env_res.serialize_async() if env_res is not None else None,
                               task_id))
            await con.commit()

    #
    # node stuff
    async def set_node_name(self, node_id: int, node_name: str) -> str:
        """
        rename node. node_name may undergo validation and change. final node name that was set is returned
        :param node_id: node id
        :param node_name: proposed node name
        :return: actual node name set
        """
        async with self.data_access.data_connection() as con:
            await con.execute('UPDATE "nodes" SET "name" = ? WHERE "id" = ?', (node_name, node_id))
            if node_id in self.__node_objects:
                self.__node_objects[node_id].set_name(node_name)
            await con.commit()
            self.ui_state_access.bump_graph_update_id()
        return node_name

    #
    # reset node's stored state
    async def wipe_node_state(self, node_id):
        async with self.data_access.data_connection() as con:
            await con.execute('UPDATE "nodes" SET node_object = NULL WHERE "id" = ?', (node_id,))
            if node_id in self.__node_objects:
                # TODO: this below may be not safe (at least not proven to be safe yet, but maybe). check
                del self.__node_objects[node_id]  # it's here to "protect" operation within db transaction. TODO: but a proper __node_object lock should be in place instead
            await con.commit()
            self.ui_state_access.bump_graph_update_id()  # not sure if needed - even number of inputs/outputs is not part of graph description
        self.wake()

    #
    # copy nodes
    async def duplicate_nodes(self, node_ids: Iterable[int]) -> Dict[int, int]:
        """
        copies given nodes, including connections between given nodes,
        and returns mapping from given node_ids to respective new copies

        :param node_ids:
        :return:
        """
        old_to_new = {}
        for nid in node_ids:
            async with self.node_object_by_id_for_reading(nid) as node_obj:
                node_obj: BaseNode
                node_type, node_name = await self.get_node_type_and_name_by_id(nid)
                new_id = await self.add_node(node_type, f'{node_name} copy')
                async with self.node_object_by_id_for_writing(new_id) as new_node_obj:
                    node_obj.copy_ui_to(new_node_obj)
                    old_to_new[nid] = new_id

        # now copy connections
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            node_ids_str = f'({",".join(str(x) for x in node_ids)})'
            async with con.execute(f'SELECT * FROM node_connections WHERE node_id_in IN {node_ids_str} AND node_id_out IN {node_ids_str}') as cur:
                all_cons = await cur.fetchall()
        for nodecon in all_cons:
            assert nodecon['node_id_in'] in old_to_new
            assert nodecon['node_id_out'] in old_to_new
            await self.add_node_connection(old_to_new[nodecon['node_id_out']], nodecon['out_name'], old_to_new[nodecon['node_id_in']], nodecon['in_name'])
        return old_to_new
        # TODO: NotImplementedError("recheck and needs testing")

    #
    #
    # node reports it's interface was changed. not sure why it exists
    async def node_reports_changes_needs_saving(self, node_id):
        assert node_id in self.__node_objects, 'this may be caused by race condition with node deletion'
        await self.save_node_to_database(node_id)

    #
    # save node to database.
    async def save_node_to_database(self, node_id):
        """
        save node with given node_id to database
        if node is not in our list of nodes - we assume it was not touched, not changed, so no saving needed

        :param node_id:
        :return:
        """
        # TODO: introduce __node_objects lock? or otherwise secure access
        #  why? this happens on ui_update, which can happen cuz of request from viewer.
        #  while node processing happens in a different thread, so this CAN happen at the same time with this
        #  AND THIS IS BAD! (potentially) if a node has changing internal state - this can save some inconsistent snapshot of node state!
        #  this works now only cuz scheduler_ui_protocol does the locking for param settings
        node_object = self.__node_objects[node_id]
        if node_object is None:
            self.__logger.error('node_object is None while')
            return
        node_data, state_data = await self.__node_serializers[0].serialize_async(node_object)
        async with self.data_access.data_connection() as con:
            await con.execute('UPDATE "nodes" SET node_object = ?, node_object_state = ? WHERE "id" = ?',
                              (node_data, state_data, node_id))
            await con.commit()

    #
    # set worker groups
    async def set_worker_groups(self, worker_hwid: int, groups: List[str]):
        groups = set(groups)
        async with self.data_access.data_connection() as con:
            await con.execute('BEGIN IMMEDIATE')  # start transaction straight away
            async with con.execute('SELECT "group" FROM worker_groups WHERE worker_hwid == ?', (worker_hwid,)) as cur:
                existing_groups = set(x[0] for x in await cur.fetchall())
            to_delete = existing_groups - groups
            to_add = groups - existing_groups
            if len(to_delete):
                await con.execute(f'DELETE FROM worker_groups WHERE worker_hwid == ? AND "group" IN ({",".join(("?",) * len(to_delete))})', (worker_hwid, *to_delete))
            if len(to_add):
                await con.executemany(f'INSERT INTO worker_groups (worker_hwid, "group") VALUES (?, ?)',
                                      ((worker_hwid, x) for x in to_add))
            await con.commit()

    #
    # change node connection callback
    async def change_node_connection(self, node_connection_id: int, new_out_node_id: Optional[int], new_out_name: Optional[str],
                                     new_in_node_id: Optional[int], new_in_name: Optional[str]):
        parts = []
        vals = []
        if new_out_node_id is not None:
            parts.append('node_id_out = ?')
            vals.append(new_out_node_id)
        if new_out_name is not None:
            parts.append('out_name = ?')
            vals.append(new_out_name)
        if new_in_node_id is not None:
            parts.append('node_id_in = ?')
            vals.append(new_in_node_id)
        if new_in_name is not None:
            parts.append('in_name = ?')
            vals.append(new_in_name)
        if len(vals) == 0:  # nothing to do
            return
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            vals.append(node_connection_id)
            await con.execute(f'UPDATE node_connections SET {", ".join(parts)} WHERE "id" = ?', vals)
            await con.commit()
        self.wake()
        self.ui_state_access.bump_graph_update_id()

    #
    # add node connection callback
    async def add_node_connection(self, out_node_id: int, out_name: str, in_node_id: int, in_name: str) -> int:
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('INSERT OR REPLACE INTO node_connections (node_id_out, out_name, node_id_in, in_name) VALUES (?,?,?,?)',  # INSERT OR REPLACE here (and not OR ABORT or smth) to ensure lastrowid is set
                                   (out_node_id, out_name, in_node_id, in_name)) as cur:
                ret = cur.lastrowid
            await con.commit()
            self.wake()
            self.ui_state_access.bump_graph_update_id()
            return ret

    #
    # remove node connection callback
    async def remove_node_connection(self, node_connection_id: int):
        try:
            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                await con.execute('PRAGMA FOREIGN_KEYS = on')
                await con.execute('DELETE FROM node_connections WHERE "id" = ?', (node_connection_id,))
                await con.commit()
                self.ui_state_access.bump_graph_update_id()
        except aiosqlite.IntegrityError as e:
            self.__logger.error(f'could not remove node connection {node_connection_id} because of database integrity check')
            raise DataIntegrityError() from None

    #
    # add node
    async def add_node(self, node_type: str, node_name: str) -> int:
        if not self.__node_data_provider.has_node_factory(node_type):  # preliminary check
            raise RuntimeError(f'unknown node type: "{node_type}"')

        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            async with con.execute('INSERT INTO "nodes" ("type", "name") VALUES (?,?)',
                                   (node_type, node_name)) as cur:
                ret = cur.lastrowid
            await con.commit()
            self.ui_state_access.bump_graph_update_id()
            return ret

    async def apply_node_settings(self, node_id: int, settings_name: str):
        async with self.node_object_by_id_for_writing(node_id) as node_object:
            settings = self.__node_data_provider.node_settings(node_object.type_name(), settings_name)
            async with self.node_object_by_id_for_writing(node_id) as node:  # type: BaseNode
                await asyncio.get_event_loop().run_in_executor(None, node.apply_settings, settings)

    async def remove_node(self, node_id: int):
        try:
            async with self.data_access.data_connection() as con:
                con.row_factory = aiosqlite.Row
                await con.execute('PRAGMA FOREIGN_KEYS = on')
                await con.execute('DELETE FROM "nodes" WHERE "id" = ?', (node_id,))
                await con.commit()
                self.ui_state_access.bump_graph_update_id()
        except aiosqlite.IntegrityError as e:
            self.__logger.error(f'could not remove node {node_id} because of database integrity check')
            raise DataIntegrityError('There are invocations (maybe achieved ones) referencing this node') from None

    #
    # query connections
    async def get_node_input_connections(self, node_id: int, input_name: Optional[str] = None):
        return await self.get_node_connections(node_id, True, input_name)

    async def get_node_output_connections(self, node_id: int, output_name: Optional[str] = None):
        return await self.get_node_connections(node_id, False, output_name)

    async def get_node_connections(self, node_id: int, query_input: bool = True, name: Optional[str] = None):
        if query_input:
            nodecol = 'node_id_in'
            namecol = 'in_name'
        else:
            nodecol = 'node_id_out'
            namecol = 'out_name'
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            if name is None:
                async with con.execute('SELECT * FROM node_connections WHERE "%s" = ?' % (nodecol,),
                                       (node_id,)) as cur:
                    return [dict(x) for x in await cur.fetchall()]
            else:
                async with con.execute('SELECT * FROM node_connections WHERE "%s" = ? AND "%s" = ?' % (nodecol, namecol),
                                       (node_id, name)) as cur:
                    return [dict(x) for x in await cur.fetchall()]

    #
    # spawning new task callback
    async def spawn_tasks(self, newtasks: Union[Iterable[TaskSpawn], TaskSpawn], con: Optional[aiosqlite_overlay.ConnectionWithCallbacks] = None) -> Union[Tuple[SpawnStatus, Optional[int]], Tuple[Tuple[SpawnStatus, Optional[int]], ...]]:
        """

        :param newtasks:
        :param con:
        :return:
        """

        async def _inner_shit() -> Tuple[Tuple[SpawnStatus, Optional[int]], ...]:
            result = []
            new_tasks = []
            current_timestamp = global_timestamp_int()
            assert len(newtasks) > 0, 'expectations failure'
            if not con.in_transaction:  # IF this is called from multiple async tasks with THE SAME con - this may cause race conditions
                await con.execute('BEGIN IMMEDIATE')
            for newtask in newtasks:
                if newtask.source_invocation_id() is not None:
                    async with con.execute('SELECT node_id, task_id FROM invocations WHERE "id" = ?',
                                           (newtask.source_invocation_id(),)) as incur:
                        invocrow = await incur.fetchone()
                        assert invocrow is not None
                        node_id: int = invocrow['node_id']
                        parent_task_id: int = invocrow['task_id']
                elif newtask.forced_node_task_id() is not None:
                    node_id, parent_task_id = newtask.forced_node_task_id()
                else:
                    self.__logger.error('ERROR CREATING SPAWN TASK: Malformed source')
                    result.append((SpawnStatus.FAILED, None))
                    continue

                # internal order is not inherited from parent.
                #  reasoning: nothing solid really.
                #  internal order is more to distinguish similar tasks, and children
                #  should be distinguishable among themselves, but not from parent
                try:
                    async with con.execute(
                            'INSERT INTO tasks ("name", "attributes", "parent_id", "state", "node_id", "node_output_name", "environment_resolver_data", "priority_tie_order") VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                            (
                                newtask.name(),
                                await serialize_attributes(newtask._attributes()),  # TODO: run dumps in executor
                                parent_task_id,
                                TaskState.SPAWNED.value if newtask.create_as_spawned() else TaskState.WAITING.value,
                                node_id,
                                newtask.node_output_name(),
                                newtask.environment_arguments().serialize() if newtask.environment_arguments() is not None else None,
                                newtask.internal_order(),
                            )
                    ) as newcur:
                        new_id = newcur.lastrowid
                except aiosqlite.IntegrityError:
                    result.append((SpawnStatus.FAILED, None))
                    continue

                # Groups
                all_groups = set()
                extra_group_names = list(newtask.extra_group_names())
                if parent_task_id is not None:  # inherit all parent's groups
                    # check and inherit parent's environment wrapper arguments
                    if newtask.environment_arguments() is None:
                        await con.execute('UPDATE tasks SET environment_resolver_data = (SELECT environment_resolver_data FROM tasks WHERE "id" == ?) WHERE "id" == ?',
                                          (parent_task_id, new_id))

                    # inc children count happens in db trigger
                    # inherit groups
                    async with con.execute('SELECT "group" FROM task_groups WHERE "task_id" = ?', (parent_task_id,)) as gcur:
                        extra_group_names += [x['group'] for x in await gcur.fetchall()]
                elif len(extra_group_names) == 0:  # parent_task_id is None and no extra groups provided
                    # in this case we create a default group for the task.
                    # task should not be left without groups at all - otherwise it will be impossible to find in UI
                    extra_group_names.append('{name}#{id:d}'.format(name=newtask.name(), id=new_id))
                    #
                if extra_group_names:
                    all_groups.update(extra_group_names)
                    for group in extra_group_names:
                        async with con.execute('SELECT "group" FROM task_group_attributes WHERE "group" == ?', (group,)) as gcur:
                            need_create = await gcur.fetchone() is None
                        if not need_create:
                            continue
                        await con.execute('INSERT INTO task_group_attributes ("group", "ctime") VALUES (?, ?)',
                                          (group, current_timestamp))
                        # TODO: a warning or smth here, cuz we create a group with not enough data specified
                        if newtask.default_priority() is not None:
                            await con.execute('UPDATE task_group_attributes SET "priority" = ? WHERE "group" = ?',
                                              (newtask.default_priority(), group))
                    await con.executemany('INSERT INTO task_groups ("task_id", "group") VALUES (?, ?)',
                                          zip(itertools.repeat(new_id, len(extra_group_names)), extra_group_names))
                    con.add_after_commit_callback(self.ui_state_access.scheduler_reports_task_groups_changed, extra_group_names)  # ui event
                result.append((SpawnStatus.SUCCEEDED, new_id))
                new_tasks.append(TaskData(new_id, parent_task_id, 0, 0,
                                          TaskState.SPAWNED if newtask.create_as_spawned() else TaskState.WAITING, '',
                                          False, node_id, 'main', newtask.node_output_name(), newtask.name(), 0, 0, None, None, None, None,
                                          all_groups))

            # callbacks for ui events
            con.add_after_commit_callback(self.ui_state_access.scheduler_reports_tasks_added, new_tasks)
            return tuple(result)

        return_single = False
        if isinstance(newtasks, TaskSpawn):
            newtasks = (newtasks,)
            return_single = True
        if len(newtasks) == 0:
            return ()
        if con is not None:
            stuff = await _inner_shit()
        else:
            async with self.data_access.data_connection() as con:
                await con.execute('PRAGMA foreign_keys=on')  # TODO: this should be made DEFAULT !
                con.row_factory = aiosqlite.Row
                stuff = await _inner_shit()
                await con.commit()
        self.wake()
        self.poke_task_processor()
        return stuff[0] if return_single else stuff

    #
    async def node_name_to_id(self, name: str) -> List[int]:
        """
        get the list of node ids that have specified name
        :param name:
        :return:
        """
        async with self.data_access.data_connection() as con:
            async with con.execute('SELECT "id" FROM "nodes" WHERE "name" = ?', (name,)) as cur:
                return list(x[0] for x in await cur.fetchall())

    #
    async def get_invocation_metadata(self, task_id: int) -> Dict[int, List[IncompleteInvocationLogData]]:
        """
        get task's log metadata - meaning which nodes it ran on and how
        :param task_id:
        :return: dict[node_id -> list[IncompleteInvocationLogData]]
        """
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            logs = {}
            self.__logger.debug(f'fetching log metadata for {task_id}')
            async with con.execute('SELECT "id", node_id, runtime, worker_id, state, return_code from "invocations" WHERE "state" != ? AND "task_id" == ?',
                                   (InvocationState.INVOKING.value, task_id)) as cur:
                async for entry in cur:
                    node_id = entry['node_id']
                    logs.setdefault(node_id, []).append(IncompleteInvocationLogData(
                        entry['id'],
                        entry['worker_id'],
                        entry['runtime'],  # TODO: this should be set to active run time if invocation is running
                        InvocationState(entry['state']),
                        entry['return_code']
                    ))
            return logs

    async def get_log(self, invocation_id: int) -> Optional[InvocationLogData]:
        """
        get logs for given task, node and invocation ids

        returns a dict of node_id

        :param invocation_id:
        :return:
        """
        async with self.data_access.data_connection() as con:
            con.row_factory = aiosqlite.Row
            self.__logger.debug(f"fetching for {invocation_id}")
            async with con.execute('SELECT "id", task_id, worker_id, node_id, state, return_code, log_external, runtime, stdout, stderr '
                                   'FROM "invocations" WHERE "id" = ?',
                                   (invocation_id,)) as cur:
                rawentry = await cur.fetchone()  # should be exactly 1 or 0
            if rawentry is None:
                return None

            entry: InvocationLogData = InvocationLogData(rawentry['id'],
                                                         rawentry['worker_id'],
                                                         rawentry['runtime'],
                                                         rawentry['task_id'],
                                                         rawentry['node_id'],
                                                         InvocationState(rawentry['state']),
                                                         rawentry['return_code'],
                                                         rawentry['stdout'] or '',
                                                         rawentry['stderr'] or '')
            if entry.invocation_state == InvocationState.IN_PROGRESS:
                async with con.execute('SELECT last_address FROM workers WHERE "id" = ?', (entry.worker_id,)) as worcur:
                    workrow = await worcur.fetchone()
                if workrow is None:
                    self.__logger.error('Worker not found during log fetch! this is not supposed to happen! Database inconsistent?')
                else:
                    try:
                        with WorkerControlClient.get_worker_control_client(AddressChain(workrow['last_address']), self.message_processor()) as client:  # type: WorkerControlClient
                            stdout, stderr = await client.get_log(invocation_id)
                        if not self.__use_external_log:
                            await con.execute('UPDATE "invocations" SET stdout = ?, stderr = ? WHERE "id" = ?',  # TODO: is this really needed? if it's never really read
                                              (stdout, stderr, invocation_id))
                            await con.commit()
                        # TODO: maybe add else case? save partial log to file?
                    except ConnectionError:
                        self.__logger.warning('could not connect to worker to get freshest logs')
                    else:
                        entry.stdout = stdout
                        entry.stderr = stderr

            elif entry.invocation_state == InvocationState.FINISHED and rawentry['log_external'] == 1:
                logbasedir = self.__external_log_location / 'invocations' / f'{invocation_id}'
                stdout_path = logbasedir / 'stdout.log'
                stderr_path = logbasedir / 'stderr.log'
                try:
                    if stdout_path.exists():
                        async with aiofiles.open(stdout_path, 'r') as fstdout:
                            entry.stdout = await fstdout.read()
                except IOError:
                    self.__logger.exception(f'could not read external stdout log for {invocation_id}')
                try:
                    if stderr_path.exists():
                        async with aiofiles.open(stderr_path, 'r') as fstderr:
                            entry.stderr = await fstderr.read()
                except IOError:
                    self.__logger.exception(f'could not read external stdout log for {invocation_id}')

        return entry

    def server_address(self) -> Tuple[str, int]:
        if self.__legacy_command_server_address is None:
            raise RuntimeError('cannot get listening address of a non started server')
        return self.__legacy_command_server_address

    def server_message_address(self, to: AddressChain) -> AddressChain:
        if self.__message_processor is None:
            raise RuntimeError('cannot get listening address of a non started server')

        return self.message_processor().listening_address(to)

    def server_message_addresses(self) -> Tuple[AddressChain, ...]:
        if self.__message_processor is None:
            raise RuntimeError('cannot get listening address of a non started server')

        return self.message_processor().listening_addresses()
