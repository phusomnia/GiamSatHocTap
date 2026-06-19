"""SQLite persistence manager for study sessions."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

from FocusMonitor.models.session import SessionRecord


class SQLiteManager:
    """Create, persist and query study sessions in SQLite."""

    def __init__(self, database_path: str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with row access by name."""

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        """Create the study sessions table if it does not exist."""

        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    focus_time REAL NOT NULL,
                    lost_time REAL NOT NULL,
                    focus_score REAL NOT NULL
                )
                """
            )
            connection.commit()

    def save_session(self, session: SessionRecord) -> int:
        """Insert a study session and return the generated row id."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO study_sessions (start_time, end_time, focus_time, lost_time, focus_score)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session.start_time.isoformat(),
                    session.end_time.isoformat(),
                    session.focus_time,
                    session.lost_time,
                    session.focus_score,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def fetch_sessions(self) -> list[SessionRecord]:
        """Return all saved sessions ordered by newest first."""

        with self._connect() as connection:
            cursor = connection.execute(
                """
                SELECT id, start_time, end_time, focus_time, lost_time, focus_score
                FROM study_sessions
                ORDER BY start_time DESC
                """
            )
            rows = cursor.fetchall()

        sessions: list[SessionRecord] = []
        for row in rows:
            sessions.append(
                SessionRecord(
                    id=int(row["id"]),
                    start_time=datetime.fromisoformat(row["start_time"]),
                    end_time=datetime.fromisoformat(row["end_time"]),
                    focus_time=float(row["focus_time"]),
                    lost_time=float(row["lost_time"]),
                    focus_score=float(row["focus_score"]),
                )
            )
        return sessions
