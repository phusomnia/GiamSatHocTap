from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class StudySession:
    id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: int = 0
    focus_score: float = 100.0
    distraction_count: int = 0
    yawn_count: int = 0
    eye_close_count: int = 0
    looking_left_count: int = 0
    looking_right_count: int = 0
    looking_down_count: int = 0
    absent_count: int = 0
