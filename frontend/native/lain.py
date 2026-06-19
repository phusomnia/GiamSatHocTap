from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from PyQt5.QtWidgets import QApplication

from src.SharedKernel.persistence.StudySessionRepo import StudySessionRepo
from src.SharedKernel.persistence.SessionManager import SessionManager
from frontend.native.ui.dashboard import Dashboard
from frontend.native.utils.config import DB_PATH


def main() -> int:
    app = QApplication(sys.argv)
    db = StudySessionRepo(DB_PATH)
    session_manager = SessionManager(db)
    dashboard = Dashboard(db=db, session_manager=session_manager)
    dashboard.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
