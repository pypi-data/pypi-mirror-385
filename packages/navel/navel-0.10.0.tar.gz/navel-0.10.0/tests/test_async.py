import asyncio

import navel


class MockClient:
    executed = False

    @navel.task
    async def mock_task(self):
        self.executed = True
        return True


def test_sync_execution():
    client = MockClient()

    res = client.mock_task()

    assert client.executed
    assert res


def test_async_execution():
    client = MockClient()

    async def run_task(c):
        c.mock_task()

    asyncio.run(run_task(client))

    assert client.executed


def test_is_task_and_returns():
    client = MockClient()
    is_task = False
    res = False

    async def run_task(c):
        nonlocal is_task
        nonlocal res
        tsk = c.mock_task()
        is_task = isinstance(tsk, asyncio.Task)
        res = await tsk

    asyncio.run(run_task(client))

    assert is_task
    assert res
