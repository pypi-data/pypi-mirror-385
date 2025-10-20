from django.contrib import admin, messages
from django.db import transaction

from .models import AdminAuditLog


@admin.action(description="Revert selected admin actions")
def revert_selected(modeladmin, request, queryset):
    if not request.user.is_superuser:
        modeladmin.message_user(
            request, "Only superusers can revert audit entries.", messages.ERROR
        )
        return

    success_count = 0
    for log in queryset:
        if not log.can_revert:
            modeladmin.message_user(
                request,
                f"{log} cannot be reverted.",
                level=messages.WARNING,
            )
            continue
        try:
            with transaction.atomic():
                reverted, message = log.revert()
        except Exception as exc:
            modeladmin.message_user(
                request, f"Failed to revert {log}: {exc}", level=messages.ERROR
            )
            continue
        if reverted:
            success_count += 1
            if message:
                modeladmin.message_user(request, message, level=messages.SUCCESS)
        else:
            modeladmin.message_user(
                request, f"Unable to revert {log}: {message}", level=messages.WARNING
            )

    if success_count:
        modeladmin.message_user(
            request, f"Successfully reverted {success_count} audit entries."
        )


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action_flag",
        "object_repr",
        "path",
        "ip_address",
        "can_revert",
    )
    list_filter = ("action_flag", "timestamp", "user", "can_revert")
    search_fields = ("object_repr", "change_message", "path", "ip_address")
    readonly_fields = (
        "timestamp",
        "request_id",
        "user",
        "action_flag",
        "object_id",
        "object_repr",
        "content_type",
        "change_message",
        "path",
        "method",
        "ip_address",
        "user_agent",
        "headers",
        "extra",
        "before_snapshot",
        "after_snapshot",
        "can_revert",
    )
    actions = [revert_selected]

    fieldsets = (
        (None, {"fields": ("timestamp", "request_id", "user", "action_flag")}),
        (
            "Object",
            {"fields": ("content_type", "object_id", "object_repr", "change_message")},
        ),
        (
            "Request Metadata",
            {
                "fields": (
                    "path",
                    "method",
                    "ip_address",
                    "user_agent",
                    "headers",
                    "extra",
                )
            },
        ),
        (
            "Snapshots",
            {
                "fields": (
                    "can_revert",
                    "before_snapshot",
                    "after_snapshot",
                )
            },
        ),
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            actions.pop("revert_selected", None)
        return actions
