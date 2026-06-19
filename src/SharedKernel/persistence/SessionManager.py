from datetime import datetime
from typing import Optional

from ...Features.VoxelStream_Module.models.StudySession import StudySession
from .StudySessionRepo import StudySessionRepo
from ...Features.VoxelStream_Module.services.FocusAnalyzer import FocusAnalyzer
from ...Features.VoxelStream_Module.services.FaceState import FaceState


class SessionManager:
    def __init__(self, db: StudySessionRepo):
        self.db = db
        self.analyzer = FocusAnalyzer()
        self._session: Optional[StudySession] = None
        self._is_running = False

    def start(self):
        self.analyzer.reset()
        self._session = StudySession(start_time=datetime.now())
        self._is_running = True

    def update(self, state: FaceState):
        if not self._is_running:
            return
        self.analyzer.update(state)

    def stop(self) -> Optional[StudySession]:
        if not self._is_running:
            return self._session
        now = datetime.now()
        self._session.end_time = now
        self._session.duration = int(
            (now - self._session.start_time).total_seconds()
        )
        summary = self.analyzer.get_summary()
        self._session.focus_score = summary["focus_score"]
        self._session.distraction_count = summary["distraction_count"]
        self._session.yawn_count = summary["yawn_count"]
        self._session.eye_close_count = summary["eye_close_count"]
        self._session.looking_left_count = summary["looking_left_count"]
        self._session.looking_right_count = summary["looking_right_count"]
        self._session.looking_down_count = summary["looking_down_count"]
        self._session.absent_count = summary["absent_count"]
        self.db.save(self._session)
        self._is_running = False
        return self._session

    def is_running(self) -> bool:
        return self._is_running

    def get_current_stats(self) -> dict:
        if not self._is_running or not self._session:
            return {}
        elapsed = int(
            (datetime.now() - self._session.start_time).total_seconds()
        )
        return {"elapsed_seconds": elapsed, **self.analyzer.get_summary()}
