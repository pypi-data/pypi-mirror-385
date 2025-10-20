from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from django.conf import settings


@dataclass
class AppSettings:
    enabled: bool = True
    admin_path_prefixes: Sequence[str] = field(default_factory=lambda: ("/admin",))
    capture_headers: Sequence[str] = field(default_factory=tuple)
    ignore_ips: Sequence[str] = field(default_factory=tuple)
    anonymize_ips: bool = False
    extra_context_callable: str | None = None

    def __post_init__(self):
        # Normalize prefixes to always start with a slash and exclude trailing slashes.
        self.admin_path_prefixes = tuple(
            f"/{prefix.lstrip('/')}" for prefix in self.admin_path_prefixes
        )
        self.capture_headers = tuple(header.upper() for header in self.capture_headers)
        self.ignore_ips = tuple(self.ignore_ips)


class SettingsProxy:
    prefix = "ADMIN_AUDIT_"

    def __init__(self):
        self.defaults = AppSettings()

    def _setting(self, name: str, default):
        return getattr(settings, f"{self.prefix}{name}", default)

    @property
    def enabled(self) -> bool:
        return bool(self._setting("ENABLED", self.defaults.enabled))

    @property
    def admin_path_prefixes(self) -> Sequence[str]:
        prefixes = self._setting(
            "ADMIN_PATH_PREFIXES", self.defaults.admin_path_prefixes
        )
        return tuple(f"/{prefix.lstrip('/')}" for prefix in prefixes)

    @property
    def capture_headers(self) -> Sequence[str]:
        headers = self._setting("CAPTURE_HEADERS", self.defaults.capture_headers)
        return tuple(header.upper().replace("-", "_") for header in headers)

    @property
    def ignore_ips(self) -> Sequence[str]:
        return tuple(self._setting("IGNORE_IPS", self.defaults.ignore_ips))

    @property
    def anonymize_ips(self) -> bool:
        return bool(self._setting("ANONYMIZE_IPS", self.defaults.anonymize_ips))

    @property
    def extra_context_callable(self) -> str | None:
        return self._setting(
            "EXTRA_CONTEXT_CALLABLE", self.defaults.extra_context_callable
        )

    def as_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "admin_path_prefixes": list(self.admin_path_prefixes),
            "capture_headers": list(self.capture_headers),
            "ignore_ips": list(self.ignore_ips),
            "anonymize_ips": self.anonymize_ips,
            "extra_context_callable": self.extra_context_callable,
        }


app_settings = SettingsProxy()
