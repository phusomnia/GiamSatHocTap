"""Session scoring service for attention tracking."""

from __future__ import annotations

from datetime import datetime

from FocusMonitor.models.session import FocusMetrics, FocusStateSnapshot, SessionRecord


class FocusService:
    """Accumulate time-based metrics and derive a focus score."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Reset the active session counters."""

        self._start_time: datetime | None = None
        self._last_update: datetime | None = None
        self._last_focus_active = False
        self._metrics = FocusMetrics()

    def start(self, start_time: datetime | None = None) -> None:
        """Start a new session."""

        self.reset()
        self._start_time = start_time or datetime.now()
        self._last_update = self._start_time

    def update(self, snapshot: FocusStateSnapshot, current_time: datetime | None = None) -> None:
        """Update the metrics using the latest analysis snapshot."""

        if self._start_time is None:
            return

        now = current_time or datetime.now()
        if self._last_update is None:
            self._last_update = now
            return

        delta_seconds = max((now - self._last_update).total_seconds(), 0.0)
        self._last_update = now
        self._last_focus_active = snapshot.focus_active
        self._metrics.total_time += delta_seconds

        if snapshot.focus_active:
            self._metrics.focus_time += delta_seconds
        else:
            self._metrics.lost_time += delta_seconds

        if snapshot.drowsy:
            self._metrics.drowsy_time += delta_seconds

    def stop(self, end_time: datetime | None = None) -> SessionRecord:
        """Finalize the session and return the persisted model."""

        if self._start_time is None:
            raise RuntimeError("The session has not been started.")

        final_end_time = end_time or datetime.now()
        if self._last_update is not None and final_end_time > self._last_update:
            delta_seconds = (final_end_time - self._last_update).total_seconds()
            self._metrics.total_time += delta_seconds
            if self._last_focus_active:
                self._metrics.focus_time += delta_seconds
            else:
                self._metrics.lost_time += delta_seconds
            self._last_update = final_end_time

        session = SessionRecord(
            start_time=self._start_time,
            end_time=final_end_time,
            focus_time=self._metrics.focus_time,
            lost_time=self._metrics.lost_time,
            focus_score=self._metrics.focus_score,
        )
        self.reset()
        return session

    @property
    def metrics(self) -> FocusMetrics:
        """Return the current in-memory metrics snapshot."""

        return self._metrics
