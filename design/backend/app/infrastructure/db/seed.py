"""Compatibility wrapper for the reference data seeder.

Prefer:

    uv run python -m app.infrastructure.db.seed_reference_data
"""

from __future__ import annotations

import asyncio

from app.infrastructure.db.seed_reference_data import main


if __name__ == "__main__":
    asyncio.run(main())

