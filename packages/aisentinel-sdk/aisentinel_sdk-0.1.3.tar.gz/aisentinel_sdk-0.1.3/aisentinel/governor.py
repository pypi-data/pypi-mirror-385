"""AISentinel Governor SDK with caching and offline capabilities."""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import requests

from .config import SDKConfig
from .embedded_db import EmbeddedDatabase
from .offline_mode import OfflineModeManager

LOGGER = logging.getLogger(__name__)


def _json_default(value: Any) -> str:
    return str(value)


class RulepackCache:
    """Local TTL based cache for rulepacks."""

    def __init__(
        self,
        cache_dir: Path,
        ttl_seconds: int,
        database: Optional[EmbeddedDatabase] = None,
    ) -> None:
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._ttl = ttl_seconds
        self._db = database
        self._lock = threading.RLock()
        self._metrics: Dict[str, int] = {
            "hits": 0,
            "misses": 0,
            "expired": 0,
            "writes": 0,
        }

    def _record_metric(self, name: str) -> None:
        with self._lock:
            self._metrics[name] = self._metrics.get(name, 0) + 1
        if self._db:
            self._db.record_metric(
                name="rulepack_cache",
                value=1,
                labels={"event": name},
            )

    def _path_for(self, rulepack_id: str, version: str) -> Path:
        safe_id = rulepack_id.replace("/", "_")
        safe_version = version.replace("/", "_")
        return self._cache_dir / f"{safe_id}__{safe_version}.json"

    def get(
        self,
        rulepack_id: str,
        *,
        version: Optional[str] = None,
        fetcher: Callable[[], Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Retrieve a rulepack, fetching it if required."""
        target_version = version or "latest"
        path = self._path_for(rulepack_id, target_version)
        with self._lock:
            if path.exists():
                age = time.time() - path.stat().st_mtime
                if self._ttl <= 0 or age <= self._ttl:
                    self._record_metric("hits")
                    with path.open("r", encoding="utf-8") as handle:
                        cached = json.load(handle)
                        if isinstance(cached, dict):
                            return cached
                        else:
                            # Invalid cache, remove it
                            path.unlink(missing_ok=True)
                self._record_metric("expired")
                path.unlink(missing_ok=True)
        self._record_metric("misses")
        data = fetcher()
        fetched_version = str(data.get("version", target_version))
        path = self._path_for(rulepack_id, fetched_version)
        with self._lock:
            with path.open("w", encoding="utf-8") as handle:
                json.dump(data, handle)
            self._record_metric("writes")
        return data

    def get_metrics(self) -> Dict[str, int]:
        with self._lock:
            return dict(self._metrics)


class Governor:
    """AISentinel Governor with offline and caching support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        *,
        config: Optional[SDKConfig] = None,
        database_path: Optional[str | Path] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        overrides: Dict[str, Any] = {}
        if base_url is not None:
            overrides["base_url"] = base_url
        if token is not None:
            overrides["token"] = token
        self.config = config or SDKConfig.load(overrides=overrides)
        LOGGER.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
        self.session = session or requests.Session()
        self.session.headers.setdefault("Content-Type", "application/json")
        if self.config.token:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.config.token}"}
            )
        db_path = Path(
            database_path
            or self.config.extra.get(
                "database_path", Path.home() / ".aisentinel" / "governor.sqlite3"
            )
        )
        self._db = EmbeddedDatabase(db_path)
        self._rulepack_cache = RulepackCache(
            Path(self.config.rulepack_cache_dir),
            self.config.cache_ttl_seconds,
            self._db,
        )
        self._offline_manager = (
            OfflineModeManager() if self.config.offline_mode_enabled else None
        )
        self._lock = threading.RLock()

    @property
    def base_url(self) -> str:
        return self.config.base_url.rstrip("/")

    def _decision_hash(self, candidate: Dict[str, Any], state: Dict[str, Any]) -> str:
        payload = json.dumps(
            {"candidate": candidate, "state": state},
            sort_keys=True,
            default=_json_default,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _cache_decision(
        self, candidate: Dict[str, Any], state: Dict[str, Any], decision: Dict[str, Any]
    ) -> None:
        cache_hash = self._decision_hash(candidate, state)
        self._db.cache_preflight_decision(cache_hash, decision)

    def _load_cached_decision(
        self, candidate: Dict[str, Any], state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        cache_hash = self._decision_hash(candidate, state)
        return self._db.get_cached_preflight_decision(cache_hash)

    def _record_metric(
        self, name: str, value: float, labels: Optional[Dict[str, str]] = None
    ) -> None:
        self._db.record_metric(name=name, value=value, labels=labels or {})

    def preflight(
        self,
        candidate: Dict[str, Any],
        state: Dict[str, Any],
        *,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Check if a candidate action is allowed."""
        if self._offline_manager and not self._offline_manager.is_online():
            cached = self._load_cached_decision(candidate, state)
            if cached is not None:
                cached.setdefault("offline", True)
                cached.setdefault("cached", True)
                self._record_metric("preflight_offline_hit", 1)
                return cached
            self._record_metric("preflight_offline_miss", 1)
            safe_candidate = json.loads(json.dumps(candidate, default=_json_default))
            safe_state = json.loads(json.dumps(state, default=_json_default))

            def _enqueue_preflight() -> None:
                self.preflight(safe_candidate, safe_state, tenant_id=tenant_id)
                return None

            self._offline_manager.enqueue(_enqueue_preflight, description="preflight")
            return {
                "allowed": False,
                "offline": True,
                "reasons": ["Offline mode active; decision deferred"],
                "alternatives": [],
            }
        tenant_config = self.config.for_tenant(tenant_id) if tenant_id else self.config
        data = {"candidate": candidate, "context_state": state}
        # Use per-request headers to avoid mutating the shared session headers and
        # leaking tenant tokens across requests.
        headers = dict(self.session.headers)
        if tenant_config.token and tenant_config.token != self.config.token:
            headers.update({"Authorization": f"Bearer {tenant_config.token}"})
        response = self.session.post(
            f"{tenant_config.base_url.rstrip('/')}/preflight",
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        decision = response.json()
        if isinstance(decision, dict):
            self._cache_decision(candidate, state, decision)
            self._record_metric("preflight_online", 1)
            return decision
        else:
            raise ValueError(f"Invalid response format from server: {decision}")

    def guarded_execute(
        self,
        tool_fn: Callable,
        candidate: Dict[str, Any],
        state: Dict[str, Any],
        *,
        require_approval: bool = False,
        tenant_id: Optional[str] = None,
    ) -> Any:
        """Execute a tool function if allowed, otherwise return alternatives."""
        decision = self.preflight(candidate, state, tenant_id=tenant_id)
        if decision.get("allowed"):
            return tool_fn(**candidate.get("args", {}))
        if decision.get("requires_approval"):
            if require_approval and decision.get("alternatives"):
                return {
                    "error": "Requires approval",
                    "alternatives": decision["alternatives"],
                }
            return {
                "error": "Requires approval",
                "reasons": decision.get("reasons", []),
                "alternatives": decision.get("alternatives", []),
            }
        return {
            "error": "Blocked",
            "reasons": decision.get("reasons", []),
            "alternatives": decision.get("alternatives", []),
        }

    def fetch_rulepack(
        self,
        rulepack_id: str,
        *,
        version: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve a rulepack leveraging the local cache when possible."""

        def _download() -> Dict[str, Any]:
            tenant_config = (
                self.config.for_tenant(tenant_id) if tenant_id else self.config
            )
            params = {"version": version} if version else None
            # Use per-request headers to avoid mutating the shared session headers and
            # leaking tenant tokens across requests.
            headers = dict(self.session.headers)
            if tenant_config.token and tenant_config.token != self.config.token:
                headers.update({"Authorization": f"Bearer {tenant_config.token}"})
            response = self.session.get(
                f"{tenant_config.base_url.rstrip('/')}/rulepacks/{rulepack_id}",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            if isinstance(result, dict):
                return result
            else:
                raise ValueError(f"Invalid rulepack format from server: {result}")

        return self._rulepack_cache.get(rulepack_id, version=version, fetcher=_download)

    def get_cache_metrics(self) -> Dict[str, int]:
        """Return rulepack cache metrics."""
        return self._rulepack_cache.get_metrics()


__all__ = ["Governor"]
