"""Top-level package for django-admin-audit."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("django-admin-audit")
except PackageNotFoundError:  # pragma: no cover - package metadata absent in dev installs
    __version__ = "0.1.0"

default_app_config = "django_admin_audit.apps.DjangoAdminAuditConfig"

__all__ = ["__version__"]
