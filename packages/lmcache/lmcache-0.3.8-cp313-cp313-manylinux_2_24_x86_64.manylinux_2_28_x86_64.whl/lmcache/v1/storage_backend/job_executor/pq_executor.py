# SPDX-License-Identifier: Apache-2.0
# Standard
from concurrent.futures import Future
from typing import Any, Awaitable, Callable
import asyncio
import itertools

# First Party
from lmcache.v1.storage_backend.job_executor.base_executor import BaseJobExecutor

_SENTINEL = object()


class AsyncPQExecutor(BaseJobExecutor):
    """Execute async functions with a priority queue and using event loop"""

    def __init__(self, loop: asyncio.AbstractEventLoop, max_workers: int = 4):
        max_size = 0  # infinite
        self.loop = loop
        self._queue: asyncio.PriorityQueue[
            tuple[
                int,
                int,
                Callable[..., Awaitable[Any]] | object,
                Any,
                dict[str, Any],
                asyncio.Future[Any] | None,
            ]
        ] = asyncio.PriorityQueue(maxsize=max_size)
        self._counter = itertools.count()
        self.max_workers = max_workers
        # we don't use asyncio.create_task so that PQ executor can be invoked
        # from sync code
        self._workers: list[Future] = [
            asyncio.run_coroutine_threadsafe(self._worker(), loop)
            for _ in range(max_workers)
        ]
        self._closed = False

    async def submit_job(
        self,
        fn: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        # Assign highest priority by default
        priority = kwargs.pop("priority", 0)
        done: asyncio.Future[Any] = self.loop.create_future()
        await self._queue.put((priority, next(self._counter), fn, args, kwargs, done))
        return await done

    async def _worker(self):
        while True:
            item = await self._queue.get()
            # Detect sentinel both as raw object and wrapped tuple
            if item is _SENTINEL or (
                isinstance(item, tuple) and len(item) >= 3 and item[2] is _SENTINEL
            ):
                self._queue.task_done()
                break

            _, _, fn, args, kwargs, done = item
            try:
                result = await fn(*args, **kwargs)
                done.set_result(result)
            except Exception as e:
                done.set_exception(e)
            finally:
                # decrement task count
                # join needs to wait until task count is zero
                self._queue.task_done()

    async def _shutdown_async(self, wait: bool = True) -> None:
        self._closed = True
        # Enqueue comparable sentinel tuples with the highest priority value so
        # that outstanding work drains before shutdown signals are consumed.
        # Use a very large integer to satisfy the typed queue's expected int priority
        sentinel_priority = 2**31 - 1
        for _ in range(self.max_workers):
            await self._queue.put(
                (sentinel_priority, next(self._counter), _SENTINEL, None, {}, None)
            )
        if wait:
            await self._queue.join()
            await asyncio.gather(
                *[asyncio.wrap_future(fut, loop=self.loop) for fut in self._workers],
                return_exceptions=True,
            )

    def shutdown(self, wait: bool = True) -> None:
        future = asyncio.run_coroutine_threadsafe(self._shutdown_async(wait), self.loop)
        if wait:
            # Propagate exceptions if any
            future.result()


class AsyncPQThreadPoolExecutor(AsyncPQExecutor):
    """Execute sync functions with a priority queue and using threadpool"""

    def __init__(self, loop: asyncio.AbstractEventLoop, max_workers: int = 4):
        max_size = 0  # infinite
        self.loop = loop
        self._queue: asyncio.PriorityQueue[
            tuple[
                int,
                int,
                Callable[..., Any] | object,
                Any,
                dict[str, Any],
                asyncio.Future[Any] | None,
            ]
        ] = asyncio.PriorityQueue(maxsize=max_size)
        self._counter = itertools.count()
        self.max_workers = max_workers
        self._workers = []
        for _ in range(max_workers):
            self._workers.append(
                asyncio.run_coroutine_threadsafe(self._worker(), self.loop)
            )
        self._closed = False

    async def _worker(self):
        while True:
            item = await self._queue.get()
            # Detect sentinel both as raw object and wrapped tuple
            if item is _SENTINEL or (
                isinstance(item, tuple) and len(item) >= 3 and item[2] is _SENTINEL
            ):
                self._queue.task_done()
                break

            _, _, fn, args, kwargs, done = item
            try:
                result = await asyncio.to_thread(fn, *args, **kwargs)
                done.set_result(result)
            except Exception as e:
                done.set_exception(e)
            finally:
                # decrement task count
                # join needs to wait until task count is zero
                self._queue.task_done()

    async def _shutdown_async(self, wait: bool = True) -> None:
        self._closed = True
        # Enqueue comparable sentinel tuples with the highest priority value so
        # that outstanding work drains before shutdown signals are consumed.
        # Use a very large integer to satisfy the typed queue's expected int priority
        sentinel_priority = 2**31 - 1
        for _ in range(self.max_workers):
            await self._queue.put(
                (sentinel_priority, next(self._counter), _SENTINEL, None, {}, None)
            )
        if wait:
            await self._queue.join()
            await asyncio.gather(
                *[asyncio.wrap_future(fut, loop=self.loop) for fut in self._workers],
                return_exceptions=True,
            )

    def shutdown(self, wait: bool = True) -> None:
        future = asyncio.run_coroutine_threadsafe(self._shutdown_async(wait), self.loop)
        if wait:
            # Propagate exceptions if any
            future.result()
