"""History and statistics window backed by matplotlib charts."""

from __future__ import annotations

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QLabel, QMainWindow, QWidget

from FocusMonitor.database.sqlite_manager import SQLiteManager
from FocusMonitor.services.statistics_service import StatisticsService
from FocusMonitor.utils.constants import ACCENT, CARD, NAVY, TEXT


class HistoryWindow(QMainWindow):
    """Show historical study-session metrics and charts."""

    def __init__(self, database: SQLiteManager, statistics_service: StatisticsService) -> None:
        super().__init__()
        self._database = database
        self._statistics_service = statistics_service
        self.setWindowTitle("Focus History")
        self.setMinimumSize(980, 680)
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Create the labels and chart container."""

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        self.summary_label = QLabel(central_widget)
        self.summary_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.summary_label.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: white; padding: 10px 12px;"
        )

        self.figure = Figure(figsize=(10, 6), facecolor=NAVY)
        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.summary_label, 0, 0)
        layout.addWidget(self.canvas, 1, 0)

        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {NAVY};
                color: {TEXT};
            }}
            QWidget {{
                background-color: {NAVY};
                color: {TEXT};
            }}
            """
        )

    def refresh(self) -> None:
        """Load the sessions from SQLite and redraw charts."""

        sessions = self._database.fetch_sessions()
        summary = self._statistics_service.build_summary(sessions)
        self.summary_label.setText(
            f"Total sessions: {summary.total_sessions} | Average focus score: {summary.average_focus_score:.1f}%"
        )

        self.figure.clear()
        daily_axis = self.figure.add_subplot(2, 1, 1)
        duration_axis = self.figure.add_subplot(2, 1, 2)

        daily_axis.set_facecolor(CARD)
        duration_axis.set_facecolor(CARD)

        if summary.daily_labels:
            daily_axis.plot(summary.daily_labels, summary.daily_focus_scores, color=ACCENT, marker="o")
        else:
            daily_axis.text(0.5, 0.5, "No data available", ha="center", va="center", color=TEXT)
        daily_axis.set_title("Average Focus Score by Day", color=TEXT)
        daily_axis.tick_params(axis="x", rotation=30, colors=TEXT)
        daily_axis.tick_params(axis="y", colors=TEXT)
        daily_axis.grid(alpha=0.2)

        if summary.session_labels:
            duration_axis.bar(summary.session_labels, summary.focus_durations, color=ACCENT)
        else:
            duration_axis.text(0.5, 0.5, "No data available", ha="center", va="center", color=TEXT)
        duration_axis.set_title("Focus Time per Session (minutes)", color=TEXT)
        duration_axis.tick_params(axis="x", rotation=30, colors=TEXT)
        duration_axis.tick_params(axis="y", colors=TEXT)
        duration_axis.grid(alpha=0.2, axis="y")

        self.figure.tight_layout()
        self.canvas.draw_idle()
