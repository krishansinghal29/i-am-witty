from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyUnitOfWork:
    """Commit-as-you-go unit of work over a single request ``AsyncSession``.

    Deliberately avoids explicit ``session.begin()``: SQLAlchemy autobegins a
    transaction on first use, and ``commit``/``rollback`` end whatever is
    active. This lets a service read, ``rollback`` to release that read
    transaction before external network calls, then open a fresh atomic write
    block via ``transaction`` without risking "a transaction is already begun".
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        try:
            yield
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
