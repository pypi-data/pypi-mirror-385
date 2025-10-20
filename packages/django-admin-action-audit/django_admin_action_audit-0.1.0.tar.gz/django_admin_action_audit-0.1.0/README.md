# django-admin-audit

`django-admin-audit` is a reusable Django application that records actions in
the Django admin along with request metadata (IP address, headers, user agent,
and more). It plugs into Django's built-in admin logging so you can enrich
existing audit trails without modifying your admin classes.

## Features

- Stores a normalized audit log for each admin action with optional request
  metadata.
- Middleware-based request capture that supports IP anonymisation and header
  whitelisting.
- Extensible hook for supplying extra JSON-serialisable context per action.
- Ships with Django admin integration so logs are browsable immediately.
- Superuser-only undo action that can revert additions, changes, and deletions
  when snapshots are available.

## Installation

```bash
pip install django-admin-action-audit
```

Then add the app and middleware to your Django settings:

```python
INSTALLED_APPS = [
    # ...
    "django_admin_audit",
]

MIDDLEWARE = [
    # ...
    "django_admin_audit.middleware.AdminAuditMiddleware",
]
```

## Configuration

Customise the behaviour via the following optional settings (prefixed with
`ADMIN_AUDIT_`):

| Setting | Default | Description |
| ------- | ------- | ----------- |
| `ENABLED` | `True` | Toggle the audit log without uninstalling the app. |
| `ADMIN_PATH_PREFIXES` | `("/admin",)` | Path prefixes that should be considered admin traffic. |
| `CAPTURE_HEADERS` | `()` | Iterable of HTTP headers to store alongside each log entry. |
| `IGNORE_IPS` | `()` | Iterable of IP addresses to exclude from logging (e.g. health checks). |
| `ANONYMIZE_IPS` | `False` | Replace the last IPv4 octet with `0` for basic anonymisation. |
| `EXTRA_CONTEXT_CALLABLE` | `None` | Dotted path to a callable returning additional JSON-serialisable data per `LogEntry`. |

### Reverting admin actions

`django-admin-audit` records before/after snapshots for admin activity so that
superusers can undo selected log entries from the _Admin Audit Log_ changelist.
The undo admin action honours the following rules:

- **Additions**: removes the newly created object.
- **Changes**: restores previously persisted field values.
- **Deletions**: recreates the deleted object using the stored snapshot.

Snapshots are captured automatically for models managed through the Django
admin while the audit middleware is active. If a snapshot is incomplete (for
example, the object was already gone before the request), the entry is marked
as non-revertible.

### Providing extra context

Create a callable that accepts the `LogEntry` instance and returns a dictionary.
The dictionary is stored in the `extra` JSON field.

```python
# myproject/audit.py
def admin_extra_context(log_entry):
    return {"session_key": getattr(log_entry.user, "last_login_session", None)}

# settings.py
ADMIN_AUDIT_EXTRA_CONTEXT_CALLABLE = "myproject.audit.admin_extra_context"
```

## Database migrations

This package ships with migrations. Run them after installation:

```bash
python manage.py migrate django_admin_audit
```

## Running the tests

The test suite uses `pytest` and `pytest-django`:

```bash
pip install -e .[test]
pytest
```

## Releasing

1. Update `django_admin_audit/__init__.py` with the new version.
2. Build the distribution: `python -m build`.
3. Upload to TestPyPI first, then PyPI via `twine upload`.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
