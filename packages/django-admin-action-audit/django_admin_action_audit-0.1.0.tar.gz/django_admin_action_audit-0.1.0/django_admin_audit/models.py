from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class AdminAuditLog(models.Model):
    """Persistent record of admin site actions with request metadata."""

    ACTION_ADD = 1
    ACTION_CHANGE = 2
    ACTION_DELETE = 3

    ACTION_CHOICES = (
        (ACTION_ADD, _("Addition")),
        (ACTION_CHANGE, _("Change")),
        (ACTION_DELETE, _("Deletion")),
    )

    id = models.BigAutoField(primary_key=True)
    request_id = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text=_("Correlation id for the request")
    )
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="admin_audit_logs",
    )
    action_flag = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    object_id = models.CharField(max_length=255, blank=True)
    object_repr = models.CharField(max_length=200)
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.SET_NULL
    )
    change_message = models.TextField(blank=True)
    path = models.CharField(max_length=255, blank=True)
    method = models.CharField(max_length=10, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    headers = models.JSONField(default=dict, blank=True)
    extra = models.JSONField(default=dict, blank=True)
    before_snapshot = models.JSONField(default=dict, blank=True)
    after_snapshot = models.JSONField(default=dict, blank=True)
    snapshot_schema_version = models.PositiveSmallIntegerField(default=1)
    can_revert = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Admin Audit Log")
        verbose_name_plural = _("Admin Audit Logs")
        ordering = ("-timestamp",)

    def __str__(self) -> str:
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} {self.get_action_flag_display()} {self.object_repr}"

    def get_target_model(self):
        if not self.content_type:
            return None
        return self.content_type.model_class()

    def revert(self):
        if not self.can_revert:
            raise ValueError("This audit entry is not revertible.")
        model = self.get_target_model()
        if not model:
            raise ValueError("Target model no longer available.")

        manager = model._default_manager
        pk_field = model._meta.pk
        pk_value = pk_field.to_python(self.object_id) if self.object_id else None
        if pk_value is None:
            pk_value = self.before_snapshot.get("pk") or self.after_snapshot.get("pk")
        if pk_value is not None:
            pk_value = pk_field.to_python(pk_value)
        if self.action_flag == self.ACTION_ADD:
            try:
                obj = manager.get(pk=pk_value)
            except model.DoesNotExist:
                return False, "Object already deleted."
            obj.delete()
            return True, "Addition reverted by deleting object."
        if self.action_flag == self.ACTION_CHANGE:
            if not self.before_snapshot:
                return False, "No snapshot available to revert change."
            try:
                obj = manager.get(pk=pk_value)
            except model.DoesNotExist:
                return False, "Object no longer exists."
            self._apply_field_values(obj, self.before_snapshot)
            obj.save()
            self._apply_many_to_many(obj, self.before_snapshot)
            return True, "Change reverted to previous values."
        if self.action_flag == self.ACTION_DELETE:
            if not self.before_snapshot:
                return False, "No snapshot available to restore deletion."
            data = self.before_snapshot
            obj = model()
            self._apply_field_values(obj, data, include_pk=True)
            pk_attr = pk_field.attname
            pk_to_restore = data.get("pk", pk_value)
            pk_to_restore = pk_field.to_python(pk_to_restore)
            setattr(obj, pk_attr, pk_to_restore)
            obj.save(force_insert=True)
            self._apply_many_to_many(obj, data)
            return True, "Deletion reverted by recreating object."
        return False, "Unsupported action."

    def _apply_field_values(self, obj, snapshot, include_pk=False):
        model = obj.__class__
        fields = snapshot.get("fields", {})
        for name, value in fields.items():
            field = model._meta.get_field(name)
            if field.many_to_many:
                continue
            if field.primary_key and not include_pk:
                continue
            if value in (None, "") and getattr(field, "null", False):
                python_value = None
            else:
                python_value = field.to_python(value)
            setattr(obj, field.attname, python_value)

    def _apply_many_to_many(self, obj, snapshot):
        model = obj.__class__
        m2m_values = snapshot.get("many_to_many", {})
        for name, value_list in m2m_values.items():
            field = model._meta.get_field(name)
            if not field.many_to_many:
                continue
            rel_field = field.target_field
            parsed_values = [rel_field.to_python(value) for value in value_list]
            getattr(obj, name).set(parsed_values)
