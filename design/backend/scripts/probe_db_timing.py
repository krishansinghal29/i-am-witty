"""Measure DB round-trip latency + Neon cold-start for the start_task path.

Run: PYTHONPATH=. .venv/bin/python scripts/probe_db_timing.py
"""
from __future__ import annotations

import asyncio
import time

from sqlalchemy import text

from app.infrastructure.db.engine import get_engine


async def main() -> None:
    engine = get_engine()

    # First connection = TCP + TLS + (possibly) Neon compute wake-up.
    t = time.perf_counter()
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    print(f"[first connect + SELECT 1]   {time.perf_counter() - t:6.2f}s  (incl. Neon wake + TLS)")

    # Warm round trips: one query each, sequential — mirrors start_task's reads.
    async with engine.connect() as conn:
        rtts = []
        for _ in range(8):
            t = time.perf_counter()
            await conn.execute(text("SELECT 1"))
            rtts.append(time.perf_counter() - t)
        avg = sum(rtts) / len(rtts)
        print(f"[warm SELECT 1 x8]           avg {avg*1000:6.1f}ms  min {min(rtts)*1000:.1f}ms  max {max(rtts)*1000:.1f}ms")
        print(f"  -> start_task does ~6 reads + 2 txns; est sequential DB cost ~= {avg*10*1000:.0f}ms+")

    # A representative transaction: BEGIN ... COMMIT round trips.
    t = time.perf_counter()
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    print(f"[begin+select+commit txn]    {(time.perf_counter()-t)*1000:6.1f}ms")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
