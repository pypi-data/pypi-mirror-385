from __future__ import annotations

from contextlib import AsyncExitStack
from pathlib import Path
from types import TracebackType

import anyio
from wiredb import Room as _Room, RoomManager, ServerWire as _ServerWire


class ServerWire(_ServerWire):
    def __init__(self, *, directory: Path | str) -> None:
        super().__init__()
        self._directory = anyio.Path(directory)

    @property
    def room_manager(self) -> RoomManager:
        return self._room_manager

    async def __aenter__(self) -> ServerWire:
        async with AsyncExitStack() as exit_stack:
            self._task_group = await exit_stack.enter_async_context(create_task_group())
            self._room_manager = await exit_stack.enter_async_context(RoomManager())
            self._exit_stack = exit_stack.pop_all()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        return await self._exit_stack.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self, id: str):
        server_send_stream, client_receive_stream = create_memory_object_stream[bytes](max_buffer_size=math.inf)
        client_send_stream, server_receive_stream = create_memory_object_stream[bytes](max_buffer_size=math.inf)
        channel = Memory(server_send_stream, server_receive_stream, id)
        room = await self._room_manager.get_room(id)
        self._task_group.start_soon(self._serve, room, channel)
        return client_send_stream, client_receive_stream

    async def _serve(self, room: Room, channel: Memory):
        async with (
            channel.send_stream as channel.send_stream,
            channel.receive_stream as channel.receive_stream
        ):
            await room.serve(channel)


class Room(_Room):
    def __init__(self, directory: Path | str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._directory = anyio.Path(directory)
        self.doc.observe(...)

    async def start(self, *, task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
        async with create_task_group() as tg:
            await self._directory.mkdir(exist_ok=True)
            await tg.start(self._write_file)
            await super().start(task_status=task_status)

    async def _write_file(self, *, task_status: TaskStatus[None] = TASK_STATUS_IGNORED):
        async with await open_file(self._directory / self._id) as f:
            task_status.started()
            async for message in self._file_receive_stream:
                f.write(message)
