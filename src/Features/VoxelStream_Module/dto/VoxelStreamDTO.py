from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class SessionResponse(BaseModel):
    id: int
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: int = 0
    focus_score: float = 100.0
    distraction_count: int = 0
    yawn_count: int = 0
    eye_close_count: int = 0
    looking_left_count: int = 0
    looking_right_count: int = 0
    looking_down_count: int = 0
    absent_count: int = 0


class StatsSummary(BaseModel):
    total_sessions: int = 0
    total_duration_seconds: int = 0
    avg_focus_score: float = 100.0
    total_distractions: int = 0
    total_yawns: int = 0
    total_eye_closes: int = 0
    total_looking_left: int = 0
    total_looking_right: int = 0
    total_looking_down: int = 0
    total_absent: int = 0


class DailyScore(BaseModel):
    date: str
    avg_focus_score: float
    total_duration_seconds: int


class SessionStats(BaseModel):
    elapsed_seconds: int = 0
    focus_score: float = 100.0
    distraction_count: int = 0
    yawn_count: int = 0
    eye_close_count: int = 0
    looking_left_count: int = 0
    looking_right_count: int = 0
    looking_down_count: int = 0
    absent_count: int = 0
