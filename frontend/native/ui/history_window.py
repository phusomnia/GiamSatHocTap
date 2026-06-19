from __future__ import annotations

from datetime import datetime

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget, QPushButton, QHBoxLayout

from src.SharedKernel.persistence.StudySessionRepo import StudySessionRepo
from frontend.native.utils.config import ACCENT, CARD, NAVY, TEXT, MUTED, NAVY_LIGHT


class HistoryPage(QWidget):
    def __init__(self, database: StudySessionRepo) -> None:
        super().__init__()
        self._database = database
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QGridLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)

        top = QHBoxLayout()
        self.summary_label = QLabel(self)
        self.summary_label.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: white; padding: 10px 12px;"
        )

        self.refresh_btn = QPushButton("Refresh", self)
        self.refresh_btn.setStyleSheet(
            f"background-color: {ACCENT}; border: none; border-radius: 10px;"
            f" padding: 8px 18px; font-size: 13px; font-weight: 700; color: white;"
        )
        self.refresh_btn.clicked.connect(self.refresh)

        top.addWidget(self.summary_label, 1)
        top.addWidget(self.refresh_btn)
        top.addStretch()

        self.figure = Figure(figsize=(10, 6), facecolor=NAVY)
        self.canvas = FigureCanvas(self.figure)

        layout.addLayout(top, 0, 0)
        layout.addWidget(self.canvas, 1, 0)

        self.setStyleSheet(f"background-color: {NAVY}; color: {TEXT};")

    def refresh(self) -> None:
        stats = self._database.get_stats_summary()
        daily = self._database.get_daily_scores(14)
        sessions = self._database.get_recent(14)

        self.summary_label.setText(
            f"Total sessions: {stats['total_sessions']} | "
            f"Average focus score: {stats['avg_focus_score']:.1f} | "
            f"Total time: {stats['total_duration_seconds'] // 60}m"
        )

        self.figure.clear()
        daily_ax = self.figure.add_subplot(2, 1, 1)
        dur_ax = self.figure.add_subplot(2, 1, 2)

        daily_ax.set_facecolor(CARD)
        dur_ax.set_facecolor(CARD)

        if daily:
            dates = [d["date"][5:] for d in daily]
            scores = [d["avg_focus_score"] for d in daily]
            daily_ax.plot(dates, scores, color=ACCENT, marker="o", linewidth=2)
            daily_ax.fill_between(range(len(dates)), scores, alpha=0.15, color=ACCENT)
        else:
            daily_ax.text(
                0.5, 0.5, "No data available", ha="center", va="center", color=TEXT,
                transform=daily_ax.transAxes,
            )
        daily_ax.set_title("Average Focus Score by Day", color=TEXT, fontweight="bold")
        daily_ax.tick_params(axis="x", rotation=30, colors=TEXT)
        daily_ax.tick_params(axis="y", colors=TEXT)
        daily_ax.set_ylim(0, 105)
        daily_ax.grid(alpha=0.2)

        if sessions:
            labels = [
                s.start_time.strftime("%m/%d")[:5] if s.start_time else ""
                for s in sessions[-10:]
            ]
            durations = [s.duration / 60.0 for s in sessions[-10:]]
            dur_ax.bar(range(len(durations)), durations, color=ACCENT, width=0.6)
            dur_ax.set_xticks(range(len(labels)))
            dur_ax.set_xticklabels(labels)
        else:
            dur_ax.text(
                0.5, 0.5, "No data available", ha="center", va="center", color=TEXT,
                transform=dur_ax.transAxes,
            )
        dur_ax.set_title("Session Duration (minutes)", color=TEXT, fontweight="bold")
        dur_ax.tick_params(axis="x", rotation=30, colors=TEXT)
        dur_ax.tick_params(axis="y", colors=TEXT)
        dur_ax.grid(alpha=0.2, axis="y")

        self.figure.tight_layout()
        self.canvas.draw_idle()
