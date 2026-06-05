from __future__ import annotations

from contextlib import AbstractAsyncContextManager
from typing import Protocol


class UnitOfWork(Protocol):
    """Transaction boundary shared by every repository in a request.

    All request-scoped repositories operate over the same underlying session,
    so committing the unit of work persists their writes atomically. Services
    own this boundary: read-then-external-then-write flows (e.g. ``complete_task``)
    call ``rollback`` to release the read transaction before any network call,
    then wrap the multi-table write in ``transaction``.
    """

    def transaction(self) -> AbstractAsyncContextManager[None]:
        """Atomic scope: commit on clean exit, roll back on exception."""
        ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
