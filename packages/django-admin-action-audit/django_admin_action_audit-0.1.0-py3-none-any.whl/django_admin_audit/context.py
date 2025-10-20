"""Context helpers for capturing request metadata during admin actions."""

from __future__ import annotations

import contextvars
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import UUID, uuid4


@dataclass
class RequestContext:
    request_id: UUID = field(default_factory=uuid4)
    path: str = ""
    method: str = ""
    ip_address: str | None = None
    headers: Dict[str, Any] = field(default_factory=dict)
    user_agent: str | None = None
    extra: Dict[str, Any] = field(default_factory=dict)


_context_var: contextvars.ContextVar[RequestContext | None] = contextvars.ContextVar(
    "django_admin_audit_ctx", default=None
)


def set_context(ctx: RequestContext | None) -> None:
    _context_var.set(ctx)


def get_context() -> Optional[RequestContext]:
    return _context_var.get()


def clear_context() -> None:
    _context_var.set(None)
