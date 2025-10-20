from __future__ import annotations

import logging
from functools import lru_cache
from importlib import import_module
from typing import Any, Callable

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver

from .conf import app_settings
from .context import get_context
from .models import AdminAuditLog
from .snapshots import get_snapshots

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_extra_context_callable() -> Callable[[LogEntry], dict] | None:
    dotted_path = app_settings.extra_context_callable
    if not dotted_path:
        return None
    module_path, _, attr = dotted_path.rpartition(".")
    if not module_path:
        raise ValueError("EXTRA_CONTEXT_CALLABLE must be a dotted path")
    module = import_module(module_path)
    return getattr(module, attr)


@receiver(post_save, sender=LogEntry)
def create_audit_log(sender, instance: LogEntry, created: bool, **kwargs):
    if not app_settings.enabled or not created:
        return

    context = get_context()
    extra_context: dict[str, Any] = {}

    callable_ = _load_extra_context_callable()
    if callable_:
        try:
            value = callable_(instance) or {}
            if not isinstance(value, dict):
                raise TypeError(
                    "EXTRA_CONTEXT_CALLABLE must return a mapping compatible with JSONField"
                )
            extra_context = value
        except Exception:  # pragma: no cover - do not break admin flow
            logger.exception("django-admin-audit: extra context callable failed")

    before = {}
    after = {}
    can_revert = False
    if instance.content_type and instance.object_id:
        key = (
            instance.content_type.app_label,
            instance.content_type.model,
            str(instance.object_id),
        )
        snapshot_data = get_snapshots(key)
        before = snapshot_data.get("before", {})
        after = snapshot_data.get("after", {})

    action_flag = instance.action_flag
    if action_flag == ADDITION and instance.object_id:
        can_revert = True
    elif action_flag == CHANGE and before:
        can_revert = True
    elif action_flag == DELETION and before:
        can_revert = True

    payload = dict(
        user=instance.user,
        action_flag=action_flag,
        object_id=instance.object_id or "",
        object_repr=instance.object_repr,
        content_type=instance.content_type,
        change_message=instance.get_change_message(),
        path=context.path if context else "",
        method=context.method if context else "",
        ip_address=context.ip_address if context else None,
        user_agent=context.user_agent or "" if context else "",
        headers=context.headers if context else {},
        extra=extra_context,
        before_snapshot=before,
        after_snapshot=after,
        snapshot_schema_version=1,
        can_revert=can_revert,
    )
    if context:
        payload["request_id"] = context.request_id

    AdminAuditLog.objects.create(**payload)
