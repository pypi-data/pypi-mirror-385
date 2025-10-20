import pytest
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import RequestFactory

from django_admin_audit.middleware import AdminAuditMiddleware
from django_admin_audit.models import AdminAuditLog


def _make_request(path="/admin/app/model/1/change/"):
    factory = RequestFactory()
    request = factory.post(path)
    return request


@pytest.mark.django_db
def test_admin_log_entry_creates_audit_record(settings):
    user_model = get_user_model()
    user = user_model.objects.create_superuser("admin", "admin@example.com", "password")

    request = _make_request()
    request.user = user
    middleware = AdminAuditMiddleware(lambda req: None)
    middleware.process_request(request)

    user.first_name = "Alice"
    user.save()

    content_type = ContentType.objects.get_for_model(user_model)

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=content_type.pk,
        object_id=str(user.pk),
        object_repr=str(user),
        action_flag=CHANGE,
        change_message="Changed first name.",
    )

    audit = AdminAuditLog.objects.get()
    assert audit.user == user
    assert audit.path == "/admin/app/model/1/change/"
    assert audit.method == "POST"
    assert audit.change_message == "Changed first name."
    assert audit.content_type == content_type
    assert audit.can_revert is True
    assert audit.before_snapshot["fields"]["first_name"] == ""
    assert audit.after_snapshot["fields"]["first_name"] == "Alice"

    middleware.process_response(request, HttpResponse())


@pytest.mark.django_db
def test_revert_change_restores_previous_state(settings):
    user_model = get_user_model()
    user = user_model.objects.create_superuser("admin", "admin@example.com", "password")

    request = _make_request()
    request.user = user
    middleware = AdminAuditMiddleware(lambda req: None)
    middleware.process_request(request)

    original_first_name = user.first_name
    user.first_name = "Changed"
    user.save()

    content_type = ContentType.objects.get_for_model(user_model)

    LogEntry.objects.log_action(
        user_id=user.pk,
        content_type_id=content_type.pk,
        object_id=str(user.pk),
        object_repr=str(user),
        action_flag=CHANGE,
        change_message="Changed first name.",
    )

    audit = AdminAuditLog.objects.latest("timestamp")
    assert audit.can_revert

    user.first_name = "Another"
    user.save()

    reverted, message = audit.revert()
    assert reverted
    user.refresh_from_db()
    assert user.first_name == original_first_name

    middleware.process_response(request, HttpResponse())


@pytest.mark.django_db
def test_revert_addition_deletes_object(settings):
    user_model = get_user_model()
    admin_user = user_model.objects.create_superuser("admin", "admin@example.com", "password")

    request = _make_request("/admin/app/model/add/")
    request.user = admin_user
    middleware = AdminAuditMiddleware(lambda req: None)
    middleware.process_request(request)

    new_user = user_model.objects.create_user("jane", "jane@example.com", "password")
    content_type = ContentType.objects.get_for_model(user_model)

    LogEntry.objects.log_action(
        user_id=admin_user.pk,
        content_type_id=content_type.pk,
        object_id=str(new_user.pk),
        object_repr=str(new_user),
        action_flag=ADDITION,
        change_message="Added user.",
    )

    audit = AdminAuditLog.objects.latest("timestamp")
    assert audit.can_revert
    reverted, _ = audit.revert()
    assert reverted
    assert not user_model.objects.filter(pk=new_user.pk).exists()

    middleware.process_response(request, HttpResponse())


@pytest.mark.django_db
def test_revert_deletion_recreates_object(settings):
    user_model = get_user_model()
    admin_user = user_model.objects.create_superuser("admin", "admin@example.com", "password")
    victim = user_model.objects.create_user("victim", "victim@example.com", "password")
    victim_pk = victim.pk

    request = _make_request("/admin/app/model/delete/")
    request.user = admin_user
    middleware = AdminAuditMiddleware(lambda req: None)
    middleware.process_request(request)

    victim.delete()

    content_type = ContentType.objects.get_for_model(user_model)
    LogEntry.objects.log_action(
        user_id=admin_user.pk,
        content_type_id=content_type.pk,
        object_id=str(victim_pk),
        object_repr="victim",
        action_flag=DELETION,
        change_message="Deleted user.",
    )

    audit = AdminAuditLog.objects.latest("timestamp")
    assert audit.can_revert
    reverted, _ = audit.revert()
    assert reverted
    assert user_model.objects.filter(pk=victim_pk).exists()

    middleware.process_response(request, HttpResponse())
