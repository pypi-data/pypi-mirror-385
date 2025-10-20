import struct
import asyncio
import pickle
import json

from . import logging
from .taskspawn import TaskSpawn
from .enums import SpawnStatus, WorkerState
from .scheduler.scheduler_core import SchedulerCore

from typing import Optional, Tuple


class SchedulerTaskProtocol(asyncio.StreamReaderProtocol):
    def __init__(self, scheduler: SchedulerCore, limit=2**16):
        self.__logger = logging.get_logger('scheduler')
        self.__timeout = 300.0
        self.__reader = asyncio.StreamReader(limit=limit)
        self.__scheduler = scheduler
        self.__saved_references = []
        super(SchedulerTaskProtocol, self).__init__(self.__reader, self.connection_cb)

    async def connection_cb(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        # there is a bug in py <=3.8, callback task can be GCd
        # see https://bugs.python.org/issue46309
        # so we HAVE to save a reference to self somewhere
        self.__saved_references.append(asyncio.current_task())

        #
        #
        # commands

        async def comm_ping():  # if command == b'ping'
            # when worker pings scheduler - scheduler returns the state it thinks the worker is in
            addr = await read_string()
            wid = await self.__scheduler.worker_id_from_address(addr)
            if wid is None:
                state = WorkerState.UNKNOWN
            else:
                state = await self.__scheduler.get_worker_state(wid)
            writer.write(struct.pack('>I', state.value))

        async def comm_pulse():  # elif command == b'pulse':
            writer.write(b'\1')

        async def comm__pulse3way_():  # WARNING: this is for tests only!
            writer.write(b'\1')
            await writer.drain()
            await reader.readexactly(1)
            writer.write(b'\2')

        #
        # commands used mostly by lifeblood_connection/lifeblood_client
        #
        # spawn a child task for task being processed
        async def comm_spawn():  # elif command == b'spawn':
            tasksize = struct.unpack('>Q', await reader.readexactly(8))[0]
            taskspawn: TaskSpawn = TaskSpawn.deserialize(await reader.readexactly(tasksize))
            ret: Tuple[SpawnStatus, Optional[int]] = await self.__scheduler.spawn_tasks(taskspawn)
            writer.write(struct.pack('>I?Q', ret[0].value, ret[1] is not None, 0 if ret[1] is None else ret[1]))

        async def comm_add_task_group():  # command == 'addtaskgroup'
            name: str = await read_string()
            creator: str = await read_string()
            priority, user_data_size = struct.unpack('>dQ', await reader.readexactly(16))
            user_data: Optional[bytes] = None if user_data_size == 0 else await reader.readexactly(user_data_size)
            added, name = await self.__scheduler.add_task_group(
                name,
                creator,
                allow_name_change_to_make_unique=True,
                priority=priority,
                user_data=user_data,
            )
            writer.write(struct.pack('>?', added))
            await write_string(name)

        async def comm_node_name_to_id():  # elif command == b'nodenametoid':
            nodename = await read_string()
            self.__logger.debug(f'got {nodename}')
            ids = await self.__scheduler.node_name_to_id(nodename)
            self.__logger.debug(f'sending {ids}')
            writer.write(struct.pack('>' + 'Q'*(1+len(ids)), len(ids), *ids))

        async def comm_update_task_attributes():  # elif command == b'tupdateattribs':  # note - this one is the same as in scheduler_ui_protocol...
            task_id, update_data_size, strcount = struct.unpack('>QQQ', await reader.readexactly(24))
            attribs_to_update = await asyncio.get_event_loop().run_in_executor(None, pickle.loads, await reader.readexactly(update_data_size))
            attribs_to_delete = set()
            for _ in range(strcount):
                attribs_to_delete.add(await read_string())
            await self.__scheduler.update_task_attributes(task_id, attribs_to_update, attribs_to_delete)
            writer.write(b'\1')

        async def comm_get_task_state():  # elif command == b'gettaskstate':
            task_id = struct.unpack('>Q', await reader.readexactly(8))[0]
            fields_dict = await self.__scheduler.get_task_fields(task_id)
            data = await asyncio.get_event_loop().run_in_executor(None, str.encode,
                                                                  await asyncio.get_event_loop().run_in_executor(None, json.dumps, fields_dict),
                                                                  'UTF-8')
            writer.write(struct.pack('>Q', len(data)))
            writer.write(data)

        async def comm_task_name_to_id():  # elif command == b'tasknametoid':
            taskname = await read_string()
            self.__logger.debug(f'got {taskname}')
            ids = await self.__scheduler.task_name_to_id(taskname)
            self.__logger.debug(f'sending {ids}')
            writer.write(struct.pack('>' + 'Q'*(1+len(ids)), len(ids), *ids))

        #
        commands = {'ping': comm_ping,
                    'pulse': comm_pulse,
                    '_pulse3way_': comm__pulse3way_,  # WARNING: this is for tests only!
                    'spawn': comm_spawn,
                    'addtaskgroup': comm_add_task_group,
                    'nodenametoid': comm_node_name_to_id,
                    'tupdateattribs': comm_update_task_attributes,
                    'gettaskstate': comm_get_task_state,
                    'tasknametoid': comm_task_name_to_id,
                    }
        #
        #

        async def read_string() -> str:
            strlen = struct.unpack('>Q', await reader.readexactly(8))[0]
            if strlen == 0:
                return ''
            return (await reader.readexactly(strlen)).decode('UTF-8')

        async def write_string(s: str):
            b = s.encode('UTF-8')
            writer.write(struct.pack('>Q', len(b)))
            writer.write(b)

        try:
            # TODO: see same todo in worker_task_protocol
            prot = await asyncio.wait_for(reader.readexactly(4), self.__timeout)
            if prot != b'\0\0\0\0':
                raise NotImplementedError()

            while True:
                try:
                    command: str = await read_string()
                except asyncio.IncompleteReadError:  # no command sent, connection closed
                    self.__logger.debug('connection closed')
                    break
                self.__logger.debug(f'scheduler got command: {command}')

                if command in commands:
                    await commands[command]()

                #
                # if conn is closed - result will be b'', but in mostl likely totally impossible case it can be unfinished command.
                # so lets just catch all
                elif reader.at_eof():
                    self.__logger.debug('connection closed')
                    return
                else:
                    raise NotImplementedError()
                await writer.drain()

        except asyncio.exceptions.TimeoutError as e:
            self.__logger.warning(f'connection timeout happened ({self.__timeout}s).')
        except ConnectionResetError as e:
            self.__logger.exception('connection was reset. disconnected %s', e)
        except ConnectionError as e:
            self.__logger.exception('connection error. disconnected %s', e)
        except Exception as e:
            self.__logger.exception('unknown error. disconnected %s', e)
            raise
        finally:
            writer.close()
            await writer.wait_closed()
            # according to the note in the beginning of the function - now reference can be cleared
            self.__saved_references.remove(asyncio.current_task())


class SchedulerTaskClient:
    def write_string(self, s: str):
        b = s.encode('UTF-8')
        self.__writer.write(struct.pack('>Q', len(b)))
        self.__writer.write(b)

    def __init__(self, ip: str, port: int):
        self.__logger = logging.get_logger('worker')
        self.__conn_task = asyncio.open_connection(ip, port)
        self.__reader = None  # type: Optional[asyncio.StreamReader]
        self.__writer = None  # type: Optional[asyncio.StreamWriter]

    async def __aenter__(self) -> "SchedulerTaskClient":
        await self._ensure_conn_open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        self.__writer.close()
        await self.__writer.wait_closed()

    async def _ensure_conn_open(self):
        if self.__reader is not None:
            return
        self.__reader, self.__writer = await self.__conn_task
        self.__writer.write(b'\0\0\0\0')

    async def ping(self, my_address: str) -> WorkerState:
        """
        remind scheduler about worker's existence and get back what he thinks of us

        :param my_address: address of this worker used to register at scheduler
        :return: worker state that scheduler thinks a worker with given address has
        """
        await self._ensure_conn_open()
        self.write_string('ping')
        try:
            self.write_string(my_address)
            await self.__writer.drain()
            return WorkerState(struct.unpack('>I', await self.__reader.readexactly(4))[0])
        except ConnectionResetError as e:
            self.__logger.error('ping failed. %s', e)
            raise

    async def pulse(self) -> None:
        """
        just ping the scheduler and get back a response, check if it's alive
        check pulse sorta

        :return:
        """
        await self._ensure_conn_open()
        self.write_string('pulse')
        try:
            await self.__writer.drain()
            await self.__reader.readexactly(1)
        except ConnectionResetError as e:
            self.__logger.error('pulse check failed. %s', e)
            raise

    async def _pulse3way_(self):
        """
        FOR TESTS ONLY
        """
        await self._ensure_conn_open()
        self.write_string('_pulse3way_')
        await self.__writer.drain()
        yield
        await self.__reader.readexactly(1)
        yield
        self.__writer.write(b'\1')
        await self.__writer.drain()
        await self.__reader.readexactly(1)

    async def spawn(self, taskspawn: TaskSpawn) -> Tuple[SpawnStatus, Optional[int]]:
        await self._ensure_conn_open()
        self.write_string('spawn')
        data_ser = await taskspawn.serialize_async()
        self.__writer.write(struct.pack('>Q', len(data_ser)))
        self.__writer.write(data_ser)
        await self.__writer.drain()
        status, is_null, val = struct.unpack('>I?Q', await self.__reader.readexactly(13))
        return SpawnStatus(status), None if is_null else val
