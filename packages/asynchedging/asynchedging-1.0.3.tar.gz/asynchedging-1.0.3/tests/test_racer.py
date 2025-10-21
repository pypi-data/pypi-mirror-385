import asyncio

import pytest

from asynchedging import AllTasksFailedError, hedge, race

pytestmark = pytest.mark.asyncio


async def _ok(val: str, delay: float = 0.0) -> str:
    if delay:
        await asyncio.sleep(delay)
    return val


async def _fail(delay: float = 0.0) -> str:
    if delay:
        await asyncio.sleep(delay)
    raise RuntimeError("boom")


def _accept_non_empty(s: str) -> bool:
    return bool(s.strip())


# All tasks fail which should raise AllTasksFailedError
async def test_race_all_fail_raises_with_errors():
    with pytest.raises(AllTasksFailedError) as exc:
        await race([(_fail(0.05), 0.0), (_fail(0.01), 0.0)])

    assert isinstance(exc.value.errors, list)
    assert len(exc.value.errors) == 2


# Total timeout occurs before any task can complete
# Total timeout is set to 0.1, but both tasks will take at least 1 second to complete
async def test_race_total_timeout():
    with pytest.raises(TimeoutError):
        await race([(_ok("A", 1.0), 0.0), (_ok("B", 1.2), 0.0)], total_timeout_s=0.1)


# Race with multiple factories and explicit delays
# The fastest task should win
async def test_race_multiple_factories_with_stagger():
    # backup1 is the fastest despite starting later
    # all three tasks start before the first completes
    coros_with_delays = [
        (_ok("primary", 1.0), 0.0),
        (_ok("backup1", 0.4), 0.4),
        (_ok("backup2", 0.8), 0.4),
    ]
    result, info = await race(coros_with_delays)
    assert info.started_count == 3
    assert result == "backup1"
    assert info.index == 1

    # backup1 is the fastest despite starting later
    # only primary and backup1 start before the first completes
    coros_with_delays = [
        (_ok("primary", 1.0), 0.0),
        (_ok("backup1", 0.4), 0.4),
        (_ok("backup2", 0.8), 1.0),
    ]
    result, info = await race(coros_with_delays)
    assert info.started_count == 2
    assert result == "backup1"
    assert info.index == 1


# Only accepts non-empty results
# First task is fast but returns empty
# Second task is slightly slower but returns non-empty
# We expect the second task to be the winner
async def test_race_respects_accept_predicate():
    # First returns empty, second returns non-empty
    coros_with_delays = [(_ok("", 0.05), 0.0), (_ok("ok", 0.06), 0.0)]
    result, info = await race(coros_with_delays, accept=_accept_non_empty)
    assert result == "ok"
    assert info.index == 1


async def test_hedge_single_factory_replication_requires_delays():
    # Single factory replicated with explicit delays
    counts = {"runs": 0}

    async def factory():
        counts["runs"] += 1
        return await _ok("X", 0.2)

    result, info = await hedge(factory, delays_s=(0.25, 0.75))
    assert result == "X"
    # Ensure at least the first task started before completion
    assert info.started_count == 1
    # Ensure the factory was invoked at least once
    assert counts["runs"] == 1


# edge case: hedge starts a replica but it is cancelled before it can start
async def test_hedge_replica_cancelled_before_start():
    counts = {"runs": 0}

    async def factory():
        counts["runs"] += 1
        return await _ok("Y", 0.2)

    result, info = await hedge(factory, delays_s=(0.5, 1.0))
    assert result == "Y"
    # Ensure only the first task started before completion
    assert info.started_count == 1
    # Ensure the factory was invoked only once
    assert counts["runs"] == 1
