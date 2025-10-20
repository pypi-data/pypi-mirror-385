from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from django.apps import apps
from django.db.models.signals import post_save, pre_delete, pre_save

from .context import get_context


SnapshotKey = Tuple[str, str, str]


@dataclass
class Snapshot:
    pk: Any
    data: Dict[str, Any]

    def to_payload(self) -> Dict[str, Any]:
        return {
            "pk": str(self.pk) if self.pk is not None else None,
            **self.data,
        }


def _context_store() -> Dict[str, Dict[SnapshotKey, Snapshot]]:
    ctx = get_context()
    if not ctx:
        return {}
    if "snapshots" not in ctx.extra:
        ctx.extra["snapshots"] = {"before": {}, "after": {}}
    return ctx.extra["snapshots"]


def _key_for_instance(instance) -> SnapshotKey:
    meta = instance._meta
    pk = getattr(instance, meta.pk.attname, None)
    if pk is None:
        pk = ""
    return meta.app_label, meta.model_name, str(pk)


def _default_manager(instance):
    return instance.__class__._default_manager


def _serialize_instance(instance):
    opts = instance._meta
    fields: Dict[str, Any] = {}
    m2m: Dict[str, list] = {}

    for field in opts.concrete_fields:
        fields[field.name] = field.value_to_string(instance)

    if instance.pk is not None:
        for field in opts.many_to_many:
            try:
                related = field.value_from_object(instance)
            except TypeError:
                continue
            if hasattr(related, "values_list"):
                values = list(related.values_list("pk", flat=True))
            else:
                values = list(related)
            m2m[field.name] = [str(value) for value in values]

    return {"fields": fields, "many_to_many": m2m}


def _load_existing(instance):
    manager = _default_manager(instance)
    meta = instance._meta
    pk = getattr(instance, meta.pk.attname)
    if pk is None:
        return None
    try:
        current = manager.get(pk=pk)
    except instance.__class__.DoesNotExist:
        return None
    return Snapshot(pk=pk, data=_serialize_instance(current))


def _capture_after(instance):
    meta = instance._meta
    pk = getattr(instance, meta.pk.attname)
    if pk is None:
        return None
    return Snapshot(pk=pk, data=_serialize_instance(instance))


def store_before(instance):
    store = _context_store()
    if not store:
        return
    key = _key_for_instance(instance)
    before = _load_existing(instance)
    if before:
        store["before"][key] = before


def store_after(instance):
    store = _context_store()
    if not store:
        return
    key = _key_for_instance(instance)
    after = _capture_after(instance)
    if after:
        store["after"][key] = after


def store_delete(instance):
    store = _context_store()
    if not store:
        return
    key = _key_for_instance(instance)
    before = _load_existing(instance)
    if before:
        store["before"][key] = before


def get_snapshots(key: SnapshotKey) -> Dict[str, Dict[str, Any]]:
    store = _context_store()
    if not store:
        return {}
    result = {}
    before = store["before"].get(key)
    after = store["after"].get(key)
    if before:
        result["before"] = before.to_payload()
    if after:
        result["after"] = after.to_payload()
    return result


def connect_signals():
    # Avoid connecting multiple times during tests.
    if getattr(connect_signals, "_connected", False):
        return

    def _should_track(instance):
        meta = instance._meta
        model_label = f"{meta.app_label}.{meta.model_name}"
        return model_label != "django_admin_audit.adminauditlog"

    def pre_save_handler(sender, instance, **kwargs):
        if _should_track(instance):
            store_before(instance)

    def post_save_handler(sender, instance, **kwargs):
        if _should_track(instance):
            store_after(instance)

    def pre_delete_handler(sender, instance, **kwargs):
        if _should_track(instance):
            store_delete(instance)

    for model in apps.get_models():
        if model._meta.label_lower == "django_admin_audit.adminauditlog":
            continue
        pre_save.connect(pre_save_handler, sender=model, weak=False)
        post_save.connect(post_save_handler, sender=model, weak=False)
        pre_delete.connect(pre_delete_handler, sender=model, weak=False)

    connect_signals._connected = True
