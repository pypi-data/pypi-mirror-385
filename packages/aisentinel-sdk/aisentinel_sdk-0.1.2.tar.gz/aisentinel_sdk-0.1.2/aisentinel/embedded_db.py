"""Embedded SQLite database for AISentinel governance data."""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

LOGGER = logging.getLogger(__name__)


class MigrationError(RuntimeError):
    """Raised when a database migration fails."""


@dataclass(frozen=True)
class ReportRecord:
    """Represents a stored governance report."""

    report_id: str
    tenant_id: Optional[str]
    report_type: str
    payload: Dict[str, Any]
    created_at: float


@dataclass(frozen=True)
class MetricRecord:
    """Represents a stored governance metric."""

    metric_id: int
    name: str
    value: float
    labels: Dict[str, str]
    recorded_at: float


class EmbeddedDatabase:
    """SQLite backed storage for audit reports, violations, and metrics.

    The database automatically initialises its schema and performs migrations
    using SQLite's ``user_version`` pragma. All operations are guarded by a
    re-entrant lock to ensure thread safety for multi-agent deployments.
    """

    _SCHEMA_VERSION = 1

    def __init__(self, path: Path | str):
        self._path = Path(path)
        if self._path.parent and not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._connection = sqlite3.connect(
            self._path,
            detect_types=sqlite3.PARSE_DECLTYPES,
            check_same_thread=False,
        )
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._initialize()

    def _initialize(self) -> None:
        """Initialise the database schema if required."""
        with self._cursor() as cursor:
            cursor.execute("PRAGMA user_version")
            row = cursor.fetchone()
            current_version = row[0] if row else 0
        if current_version > self._SCHEMA_VERSION:
            raise MigrationError(
                f"Database version {current_version} is newer than supported "
                f"schema version {self._SCHEMA_VERSION}."
            )
        if current_version == self._SCHEMA_VERSION:
            return
        LOGGER.debug(
            "Applying migrations to embedded database from version %s to %s",
            current_version,
            self._SCHEMA_VERSION,
        )
        try:
            self._apply_migrations(current_version)
        except Exception as exc:  # pragma: no cover - defensive branch
            LOGGER.exception("Failed to apply database migrations")
            raise MigrationError("Failed to apply migrations") from exc

    def close(self) -> None:
        """Close the underlying SQLite connection."""
        with self._lock:
            self._connection.close()

    @contextmanager
    def _cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        with self._lock:
            cursor = self._connection.cursor()
            try:
                yield cursor
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise
            finally:
                cursor.close()

    def _apply_migrations(self, current_version: int) -> None:
        with self._cursor() as cursor:
            if current_version < 1:
                cursor.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS reports (
                        id TEXT PRIMARY KEY,
                        tenant_id TEXT,
                        report_type TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        created_at REAL NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS violations (
                        id TEXT PRIMARY KEY,
                        report_id TEXT NOT NULL,
                        rule_id TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        details TEXT,
                        created_at REAL NOT NULL,
                        FOREIGN KEY(report_id) REFERENCES reports(id)
                    );

                    CREATE TABLE IF NOT EXISTS metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        value REAL NOT NULL,
                        labels TEXT,
                        recorded_at REAL NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS preflight_cache (
                        hash TEXT PRIMARY KEY,
                        decision TEXT NOT NULL,
                        created_at REAL NOT NULL
                    );
                    """
                )
                cursor.execute(f"PRAGMA user_version = {self._SCHEMA_VERSION}")

    @staticmethod
    def _json_dumps(data: Dict[str, Any] | List[Any]) -> str:
        return json.dumps(data, sort_keys=True)

    @staticmethod
    def _json_loads(payload: str) -> Any:
        return json.loads(payload)

    def store_report(
        self,
        report_id: str,
        report_type: str,
        payload: Dict[str, Any],
        tenant_id: str | None = None,
        created_at: Optional[float] = None,
    ) -> None:
        """Persist a governance report."""
        created_at = created_at or time.time()
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO reports(id, tenant_id, report_type, payload, created_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    tenant_id,
                    report_type,
                    self._json_dumps(payload),
                    created_at,
                ),
            )

    def fetch_reports(
        self,
        limit: int = 50,
        tenant_id: Optional[str] = None,
        report_type: Optional[str] = None,
    ) -> List[ReportRecord]:
        """Retrieve stored reports sorted by creation time descending."""
        query = "SELECT id, tenant_id, report_type, payload, created_at FROM reports"
        params: List[Any] = []
        filters: List[str] = []
        if tenant_id:
            filters.append("tenant_id = ?")
            params.append(tenant_id)
        if report_type:
            filters.append("report_type = ?")
            params.append(report_type)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
        return [
            ReportRecord(
                report_id=row[0],
                tenant_id=row[1],
                report_type=row[2],
                payload=self._json_loads(row[3]),
                created_at=row[4],
            )
            for row in rows
        ]

    def store_violation(
        self,
        violation_id: str,
        report_id: str,
        rule_id: str,
        severity: str,
        details: Dict[str, Any],
        created_at: Optional[float] = None,
    ) -> None:
        """Persist a governance violation record."""
        created_at = created_at or time.time()
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO violations(id, report_id, rule_id, severity, details, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    violation_id,
                    report_id,
                    rule_id,
                    severity,
                    self._json_dumps(details),
                    created_at,
                ),
            )

    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        recorded_at: Optional[float] = None,
    ) -> None:
        """Record a numerical metric."""
        recorded_at = recorded_at or time.time()
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO metrics(name, value, labels, recorded_at)
                VALUES(?, ?, ?, ?)
                """,
                (name, value, self._json_dumps(labels or {}), recorded_at),
            )

    def fetch_metrics(
        self,
        name: Optional[str] = None,
        since: Optional[float] = None,
    ) -> List[MetricRecord]:
        """Fetch recorded metrics."""
        query = "SELECT id, name, value, labels, recorded_at FROM metrics"
        params: List[Any] = []
        filters: List[str] = []
        if name:
            filters.append("name = ?")
            params.append(name)
        if since:
            filters.append("recorded_at >= ?")
            params.append(since)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY recorded_at DESC"
        with self._cursor() as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
        return [
            MetricRecord(
                metric_id=row[0],
                name=row[1],
                value=row[2],
                labels=self._json_loads(row[3]) if row[3] else {},
                recorded_at=row[4],
            )
            for row in rows
        ]

    def cache_preflight_decision(
        self, cache_hash: str, decision: Dict[str, Any]
    ) -> None:
        """Store a cached preflight decision for offline use."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO preflight_cache(hash, decision, created_at)
                VALUES(?, ?, ?)
                """,
                (cache_hash, self._json_dumps(decision), time.time()),
            )

    def get_cached_preflight_decision(
        self, cache_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a cached preflight decision if available."""
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT decision FROM preflight_cache WHERE hash = ?",
                (cache_hash,),
            )
            row = cursor.fetchone()
        if not row:
            return None
        loaded = self._json_loads(row[0])
        return loaded if isinstance(loaded, dict) else None

    def purge_preflight_cache(self, older_than: float) -> int:
        """Remove cached decisions older than the supplied timestamp."""
        with self._cursor() as cursor:
            cursor.execute(
                "DELETE FROM preflight_cache WHERE created_at < ?",
                (older_than,),
            )
            return cursor.rowcount


__all__ = ["EmbeddedDatabase", "ReportRecord", "MetricRecord", "MigrationError"]
