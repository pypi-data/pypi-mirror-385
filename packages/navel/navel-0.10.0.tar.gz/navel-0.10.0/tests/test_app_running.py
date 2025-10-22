import navel
import pytest


def test_robot_run():
    async def mock_app(robot):
        return isinstance(robot, navel.Robot)

    with navel.Robot() as rob:
        res = rob.run(mock_app)

    assert res


def test_run_raises_outside_context():
    async def mock_app(robot):
        pass

    rob = navel.Robot()

    with pytest.raises(RuntimeError):
        rob.run(mock_app)


def test_navel_run():
    async def mock_app(robot):
        return isinstance(robot, navel.Robot)

    res = navel.run(mock_app)

    assert res
