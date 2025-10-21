"""Configuration management for the AISentinel Python SDK."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

LOGGER = logging.getLogger(__name__)

_DEFAULTS: Dict[str, Any] = {
    "base_url": "https://api.aisentinel.ai",
    "token": None,
    "environment": "production",
    "tenant_id": None,
    "cache_ttl_seconds": 300,
    "rulepack_cache_dir": str(Path.home() / ".aisentinel" / "rulepacks"),
    "offline_mode_enabled": True,
    "log_level": "INFO",
}


class ConfigError(ValueError):
    """Raised when configuration loading fails."""


@dataclass
class SDKConfig:
    """Runtime configuration for the AISentinel SDK."""

    base_url: str
    token: Optional[str] = None
    environment: str = "production"
    tenant_id: Optional[str] = None
    cache_ttl_seconds: int = 300
    rulepack_cache_dir: str = field(
        default_factory=lambda: _DEFAULTS["rulepack_cache_dir"]
    )
    offline_mode_enabled: bool = True
    log_level: str = "INFO"
    extra: Dict[str, Any] = field(default_factory=dict)
    tenant_overrides: Dict[str, "SDKConfig"] = field(default_factory=dict, repr=False)

    @classmethod
    def load(
        cls,
        *,
        file_path: Optional[Path | str] = None,
        env_prefix: str = "AISENTINEL_",
        overrides: Optional[Mapping[str, Any]] = None,
    ) -> "SDKConfig":
        """Load configuration from defaults, optional file, environment, and overrides."""

        config_data: Dict[str, Any] = dict(_DEFAULTS)
        if file_path:
            file_values = cls._read_file(Path(file_path))
            config_data.update(file_values)
        env_values = cls._read_env(prefix=env_prefix)
        config_data.update(env_values)
        if overrides:
            config_data.update({k: v for k, v in overrides.items() if v is not None})
        cls._normalise(config_data)
        cls._validate(config_data)
        tenant_overrides = cls._extract_tenant_overrides(config_data)
        extra = {
            k: v
            for k, v in config_data.items()
            if k
            not in {
                "base_url",
                "token",
                "environment",
                "tenant_id",
                "cache_ttl_seconds",
                "rulepack_cache_dir",
                "offline_mode_enabled",
                "log_level",
                "tenants",
            }
        }
        config = cls(
            base_url=config_data["base_url"],
            token=config_data.get("token"),
            environment=config_data.get("environment", "production"),
            tenant_id=config_data.get("tenant_id"),
            cache_ttl_seconds=int(config_data.get("cache_ttl_seconds", 300)),
            rulepack_cache_dir=config_data.get(
                "rulepack_cache_dir", _DEFAULTS["rulepack_cache_dir"]
            ),
            offline_mode_enabled=bool(config_data.get("offline_mode_enabled", True)),
            log_level=str(config_data.get("log_level", "INFO")),
            extra=extra,
        )
        config.tenant_overrides = tenant_overrides
        return config

    @classmethod
    def _read_file(cls, path: Path) -> Any:
        if not path.exists():
            raise ConfigError(f"Configuration file not found: {path}")
        try:
            with path.open("r", encoding="utf-8") as handle:
                contents = handle.read().strip()
        except OSError as exc:  # pragma: no cover - IO failure
            raise ConfigError(
                f"Failed to read configuration file {path}: {exc}"
            ) from exc
        if not contents:
            return {}
        try:
            data = json.loads(contents)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON configuration in {path}: {exc}") from exc
        return data

    @classmethod
    def _read_env(cls, prefix: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            short_key = key[len(prefix) :].lower()
            if short_key in {"cache_ttl_seconds"}:
                try:
                    data[short_key] = int(value)
                except ValueError:
                    raise ConfigError(
                        f"Environment variable {key} must be an integer"
                    ) from None
            elif short_key in {"offline_mode_enabled"}:
                data[short_key] = value.lower() in {"true", "1", "yes"}
            else:
                data[short_key] = value
        return data

    @classmethod
    def _normalise(cls, data: Dict[str, Any]) -> None:
        environment = data.get("environment")
        if environment is None and data.get("base_url", "").startswith(
            "http://localhost"
        ):
            data["environment"] = "development"

    @classmethod
    def _validate(cls, data: Mapping[str, Any]) -> None:
        base_url = data.get("base_url")
        if not base_url:
            raise ConfigError("base_url is required for AISentinel SDK configuration")
        if not isinstance(data.get("cache_ttl_seconds", 0), int):
            raise ConfigError("cache_ttl_seconds must be an integer")

    @classmethod
    def _extract_tenant_overrides(cls, data: Dict[str, Any]) -> Dict[str, "SDKConfig"]:
        tenant_configs: Dict[str, SDKConfig] = {}
        raw = data.get("tenants")
        if not isinstance(raw, dict):
            return tenant_configs
        for tenant_id, tenant_data in raw.items():
            merged: Dict[str, Any] = dict(_DEFAULTS)
            merged.update({k: v for k, v in data.items() if k in _DEFAULTS})
            if isinstance(tenant_data, Mapping):
                merged.update(tenant_data)
            merged["tenant_id"] = tenant_id
            cls._validate(merged)
            tenant_configs[tenant_id] = SDKConfig(
                base_url=merged["base_url"],
                token=merged.get("token"),
                environment=merged.get(
                    "environment", data.get("environment", "production")
                ),
                tenant_id=tenant_id,
                cache_ttl_seconds=int(
                    merged.get("cache_ttl_seconds", data.get("cache_ttl_seconds", 300))
                ),
                rulepack_cache_dir=merged.get(
                    "rulepack_cache_dir",
                    data.get("rulepack_cache_dir", _DEFAULTS["rulepack_cache_dir"]),
                ),
                offline_mode_enabled=bool(
                    merged.get(
                        "offline_mode_enabled", data.get("offline_mode_enabled", True)
                    )
                ),
                log_level=str(merged.get("log_level", data.get("log_level", "INFO"))),
            )
        return tenant_configs

    def for_tenant(self, tenant_id: str) -> "SDKConfig":
        """Return a tenant specific configuration if available."""
        return self.tenant_overrides.get(tenant_id, self)


__all__ = ["SDKConfig", "ConfigError"]
