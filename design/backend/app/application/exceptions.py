from __future__ import annotations


class ApplicationError(Exception):
    """Base for application-layer errors; mapped to HTTP status at the API edge."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class NotFoundError(ApplicationError):
    """A referenced resource does not exist or is not visible to the caller."""


class AccessDeniedError(ApplicationError):
    """The caller may not perform the action (e.g. premium tier required)."""


class PaywallRequiredError(ApplicationError):
    """The free daily limit is exhausted; the caller should surface the paywall."""


class ConflictError(ApplicationError):
    """The action conflicts with current state (e.g. attempt already completed)."""


class ValidationError(ApplicationError):
    """The request is structurally valid but semantically unacceptable."""
