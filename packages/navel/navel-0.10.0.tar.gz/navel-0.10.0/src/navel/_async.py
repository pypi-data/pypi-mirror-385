import asyncio
from functools import wraps
from warnings import warn


class AsyncRunner:
    def __init__(self):
        self._active = False
        self._tasks = None

    def __enter__(self):
        if is_async():
            raise RuntimeError(
                'An event loop is running. Did you mean to use "async with"?'
            )
        self._tasks = None

        self.open()

        return self

    async def __aenter__(self):
        self._tasks = set()

        self.open()

        return self

    def open(self):
        self._active = True

    def __exit__(self, a, b, c):
        self.close()

    async def __aexit__(self, a, b, c):
        while self._tasks:
            await self._tasks.pop()

        self.close()

    def close(self):
        self._active = False

    def run(self, app):
        warn(
            "Function .run() is deprecated and will be removed in a future version. Please check the getting started guide for the recommended way to start coroutines.",
            DeprecationWarning,
            stacklevel=2,
        )
        if self._active:
            return asyncio.run(app(self))
        else:
            raise RuntimeError('App must be run inside a "with" block.')


def runner_task(func):
    """Wrapper to make coroutines "runnable".

    Returns a task if event loop is running, otherwise runs it synchronously.
    """

    @wraps(func)
    def wrapped(self: AsyncRunner, *args, **kwargs):

        if self._tasks is None:
            if is_async():
                raise RuntimeError("Sync function called from async context.")
            return asyncio.run(func(self, *args, **kwargs))
        else:
            if not is_async():
                raise RuntimeError("Async function called from sync context.")
            _task = asyncio.create_task(func(self, *args, **kwargs))
            self._tasks.add(_task)
            _task.add_done_callback(self._tasks.discard)

            return _task

    return wrapped


def is_async():
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return False

    return True
