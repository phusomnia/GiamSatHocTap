"""Statistics preparation for the focus-monitoring history view."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Iterable, Sequence

from FocusMonitor.models.session import SessionRecord


@dataclass(slots=True)
class StatisticsSummary:
    """Aggregated statistics used by the history dashboard."""

    total_sessions: int
    average_focus_score: float
    daily_labels: list[str]
    daily_focus_scores: list[float]
    session_labels: list[str]
    focus_durations: list[float]


class StatisticsService:
    """Transform raw sessions into chart-friendly aggregates."""

    def build_summary(self, sessions: Sequence[SessionRecord]) -> StatisticsSummary:
        """Return the metrics needed by the history window."""

        ordered_sessions = sorted(sessions, key=lambda session: session.start_time)
        total_sessions = len(ordered_sessions)
        average_focus_score = self._average([session.focus_score for session in ordered_sessions])
        daily_map = self._daily_scores(ordered_sessions)

        return StatisticsSummary(
            total_sessions=total_sessions,
            average_focus_score=average_focus_score,
            daily_labels=list(daily_map.keys()),
            daily_focus_scores=list(daily_map.values()),
            session_labels=[session.start_time.strftime("%d/%m %H:%M") for session in ordered_sessions],
            focus_durations=[session.focus_time / 60.0 for session in ordered_sessions],
        )

    @staticmethod
    def _average(values: Iterable[float]) -> float:
        """Compute the arithmetic mean of a sequence of numbers."""

        collected = list(values)
        if not collected:
            return 0.0
        return sum(collected) / len(collected)

    @staticmethod
    def _daily_scores(sessions: Sequence[SessionRecord]) -> OrderedDict[str, float]:
        """Group sessions by day and average their focus scores."""

        grouped: OrderedDict[str, list[float]] = OrderedDict()
        for session in sessions:
            label = session.start_time.strftime("%d/%m/%Y")
            grouped.setdefault(label, []).append(session.focus_score)

        averaged: OrderedDict[str, float] = OrderedDict()
        for label, values in grouped.items():
            averaged[label] = sum(values) / len(values)
        return averaged
