from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from ...Features.VoxelStream_Module.models.StudySession import StudySession
from .CrudORM import CrudORM


class StudySessionRepo(CrudORM[StudySession]):
    TABLE_NAME = "study_sessions"

    def __init__(self, db_path: str = "focus_monitor.db"):
        super().__init__(db_path)

    @classmethod
    def _model_class(cls):
        return StudySession

    def save(self, session: StudySession) -> int:
        if session.id is None:
            return self.insert(session)
        self.update(session)
        return session.id

    def get_all(self, order_by: str = "start_time DESC") -> List[StudySession]:
        return super().get_all(order_by=order_by)

    def get_by_date_range(
        self, start: datetime, end: datetime
    ) -> List[StudySession]:
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM study_sessions "
                "WHERE start_time >= ? AND start_time <= ? "
                "ORDER BY start_time DESC",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
            return [self._row_to_model(row) for row in rows]

    def get_recent(self, days: int = 7) -> List[StudySession]:
        start = datetime.now() - timedelta(days=days)
        return self.get_by_date_range(start, datetime.now())

    def get_stats_summary(self) -> dict:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COUNT(*) as total_sessions,
                    COALESCE(SUM(duration), 0) as total_duration,
                    COALESCE(AVG(focus_score), 100.0) as avg_focus_score,
                    COALESCE(SUM(distraction_count), 0) as total_distractions,
                    COALESCE(SUM(yawn_count), 0) as total_yawns,
                    COALESCE(SUM(eye_close_count), 0) as total_eye_closes,
                    COALESCE(SUM(looking_left_count), 0) as total_looking_left,
                    COALESCE(SUM(looking_right_count), 0) as total_looking_right,
                    COALESCE(SUM(looking_down_count), 0) as total_looking_down,
                    COALESCE(SUM(absent_count), 0) as total_absent
                FROM study_sessions
                """
            ).fetchone()

            return {
                "total_sessions": row[0],
                "total_duration_seconds": row[1],
                "avg_focus_score": round(row[2], 1),
                "total_distractions": row[3],
                "total_yawns": row[4],
                "total_eye_closes": row[5],
                "total_looking_left": row[6],
                "total_looking_right": row[7],
                "total_looking_down": row[8],
                "total_absent": row[9],
            }

    def get_daily_scores(self, days: int = 7) -> List[dict]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    date(start_time) as day,
                    AVG(focus_score) as avg_score,
                    SUM(duration) as total_duration
                FROM study_sessions
                GROUP BY date(start_time)
                ORDER BY day DESC
                LIMIT ?
                """,
                (days,),
            ).fetchall()
            return [
                {
                    "date": row[0],
                    "avg_focus_score": round(row[1] or 0, 1),
                    "total_duration_seconds": row[2] or 0,
                }
                for row in rows
            ]
