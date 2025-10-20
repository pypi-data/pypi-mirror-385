from __future__ import annotations

from collections import OrderedDict

from django.utils.deprecation import MiddlewareMixin

from .conf import app_settings
from .context import RequestContext, clear_context, set_context


class AdminAuditMiddleware(MiddlewareMixin):
    """
    Middleware that captures request metadata for admin operations.

    The metadata is later combined with admin log entries by signal handlers to
    produce a consolidated audit trail.
    """

    def process_request(self, request):
        if not app_settings.enabled:
            return

        if not self._is_admin_path(request.path):
            clear_context()
            return

        ip_address = request.META.get("REMOTE_ADDR")
        if app_settings.ignore_ips and ip_address in app_settings.ignore_ips:
            clear_context()
            return

        headers = self._capture_headers(request)

        ctx = RequestContext(
            path=request.path,
            method=request.method,
            ip_address=self._normalize_ip(ip_address),
            headers=headers,
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )

        request.audit_context = ctx  # type: ignore[attr-defined]
        set_context(ctx)

    def process_response(self, request, response):
        clear_context()
        return response

    def process_exception(self, request, exception):
        clear_context()

    @staticmethod
    def _is_admin_path(path: str) -> bool:
        return any(path.startswith(prefix) for prefix in app_settings.admin_path_prefixes)

    @staticmethod
    def _capture_headers(request) -> dict:
        captured = OrderedDict()
        for header in app_settings.capture_headers:
            meta_key = f"HTTP_{header}"
            if meta_key in request.META:
                captured[header.replace("_", "-").title()] = request.META[meta_key]
        return captured

    @staticmethod
    def _normalize_ip(ip_address: str | None) -> str | None:
        if not ip_address:
            return None
        if app_settings.anonymize_ips:
            octets = ip_address.split(".")
            if len(octets) == 4:
                octets[-1] = "0"
                return ".".join(octets)
        return ip_address
