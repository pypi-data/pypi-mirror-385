from __future__ import annotations

# system imports
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections.abc import Awaitable
from typing import TypeVar, AsyncGenerator, Any, Callable

# external imports
from rubicon.objc import ObjCClass
from maestral.daemon import MaestralProxy


T = TypeVar("T")


NSAppleScript = ObjCClass("NSAppleScript")


# ==== async calls =====================================================================

thread_pool_executor = ThreadPoolExecutor(10)


def create_task(awaitable: Awaitable[T]) -> asyncio.Task[T]:
    loop = asyncio.get_running_loop()
    return asyncio.ensure_future(awaitable, loop=loop)


def call_async(func: Callable, *args) -> Awaitable:
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(thread_pool_executor, func, *args)


def call_async_maestral(config_name: str, func_name: str, *args) -> Awaitable:
    def func(*inner_args):
        with MaestralProxy(config_name) as m:
            m_func = m.__getattr__(func_name)
            return m_func(*inner_args)

    loop = asyncio.get_running_loop()
    return loop.run_in_executor(thread_pool_executor, func, *args)


def generate_async_maestral(config_name: str, func_name: str, *args) -> AsyncGenerator:
    loop = asyncio.get_running_loop()
    queue: "asyncio.Queue[Any]" = asyncio.Queue(1)
    exception = None
    _END = object()

    def func(*inner_args):
        nonlocal exception
        with MaestralProxy(config_name) as m:
            m_func = m.__getattr__(func_name)
            generator = m_func(*inner_args)

            try:
                for res in generator:
                    asyncio.run_coroutine_threadsafe(queue.put(res), loop).result()
            except Exception as e:
                exception = e
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(_END), loop).result()

    async def yield_results():
        while True:
            next_item = await queue.get()
            if next_item is _END:
                break
            yield next_item
        if exception is not None:
            # the iterator has raised, propagate the exception
            raise exception

    thread_pool_executor.submit(func, *args)

    return yield_results()


# ==== system calls ====================================================================


def request_authorization_from_user_and_run(command: str) -> None:
    source = f'do shell script "{command}" with administrator privileges'

    script = NSAppleScript.alloc().initWithSource(source)
    res = script.executeAndReturnError(None)

    if res is None:
        raise RuntimeError(f"Could not run privileged command {command!r}")


def is_empty(dirname: str | os.PathLike[str]) -> bool:
    """Checks if a directory is empty."""

    exceptions = {".DS_Store"}
    n_exceptions = len(exceptions)

    children: list[os.DirEntry] = []

    try:
        with os.scandir(dirname) as sd_iter:
            while len(children) <= n_exceptions:
                children.append(next(sd_iter))
    except StopIteration:
        pass

    return all(child.name in exceptions for child in children)
