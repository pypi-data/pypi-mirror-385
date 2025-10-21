from __future__ import annotations

import asyncio
import signal
from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from aiotaskqueue.router import TaskRouter
    from aiotaskqueue.tasks import TaskDefinition


def utc_now() -> datetime:
    return datetime.now(tz=UTC)


def extract_tasks(
    tasks: TaskRouter | Sequence[TaskDefinition[Any, Any]],
) -> Sequence[TaskDefinition[Any, Any]]:
    from aiotaskqueue.router import TaskRouter  # noqa: PLC0415

    if isinstance(tasks, TaskRouter):
        return tuple(tasks.tasks.values())
    return tasks


INJECTED: Any = object()


class ShutdownManager:
    def __init__(self) -> None:
        self._callbacks: list[Callable[[], Any]] = []
        self.event: Final = asyncio.Event()

        signal.signal(
            signal.SIGTERM,
            lambda signalnum, handler: self.shutdown(),  # noqa: ARG005
        )
        signal.signal(
            signal.SIGINT,
            lambda signalnum, handler: self.shutdown(),  # noqa: ARG005
        )

    def shutdown(self) -> None:
        self.event.set()


class TaskManager:
    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[object]] = set()

    def add(self, *tasks: asyncio.Task[Any]) -> None:
        for task in tasks:
            self._tasks.add(task)

    async def wait_for_completion(self) -> None:
        while self._tasks:
            done, _ = await asyncio.wait(self._tasks)
            for task in done:
                self._tasks.remove(task)

    async def cancel(self) -> None:
        for task in self._tasks:
            task.cancel()
        await self.wait_for_completion()


async def run_until_stopped(
    func: Callable[[], Awaitable[None]],
    interval: timedelta,
    stop: asyncio.Event,
) -> None:
    stop_task = asyncio.create_task(stop.wait())
    while True:
        await func()
        sleep_task = asyncio.create_task(asyncio.sleep(interval.total_seconds()))
        await asyncio.wait({stop_task, sleep_task}, return_when=asyncio.FIRST_COMPLETED)
        if stop.is_set():
            return
