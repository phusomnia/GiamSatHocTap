from enum import Enum

from .FaceState import FaceState


class FocusLevel(Enum):
    FOCUSING = "FOCUSING"
    DISTRACTED = "DISTRACTED"
    DROWSY = "DROWSY"
    LOST_FOCUS = "LOST_FOCUS"

_FOCUS_STATES = {FaceState.NORMAL, FaceState.LOOKING_LEFT, FaceState.LOOKING_RIGHT}


class FocusAnalyzer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.focus_percentage = 100.0
        self.total_frames = 0
        self.focusing_frames = 0
        self.distraction_count = 0
        self.yawn_count = 0
        self.eye_close_count = 0
        self.looking_left_count = 0
        self.looking_right_count = 0
        self.looking_down_count = 0
        self.absent_count = 0
        self._previous_state = FaceState.NORMAL

    def update(self, state: FaceState):
        self.total_frames += 1
        if state in _FOCUS_STATES:
            self.focusing_frames += 1

        self.focus_percentage = (
            (self.focusing_frames / self.total_frames) * 100.0
            if self.total_frames > 0
            else 100.0
        )

        if state != self._previous_state:
            self._on_transition(state)
            self._previous_state = state

    def _on_transition(self, state: FaceState):
        if state == FaceState.EYES_CLOSED:
            self.eye_close_count += 1
            self.distraction_count += 1
        elif state == FaceState.YAWNING:
            self.yawn_count += 1
        elif state == FaceState.LOOKING_LEFT:
            self.looking_left_count += 1
        elif state == FaceState.LOOKING_RIGHT:
            self.looking_right_count += 1
        elif state == FaceState.LOOKING_DOWN:
            self.looking_down_count += 1
            self.distraction_count += 1
        elif state == FaceState.ABSENT:
            self.absent_count += 1
            self.distraction_count += 1

    @staticmethod
    def derive_focus_level(state: FaceState) -> FocusLevel:
        if state in _FOCUS_STATES:
            return FocusLevel.FOCUSING
        if state in (FaceState.EYES_CLOSED, FaceState.YAWNING):
            return FocusLevel.DROWSY
        return FocusLevel.LOST_FOCUS

    def get_summary(self) -> dict:
        return {
            "focus_score": self.focus_percentage,
            "focus_percentage": self.focus_percentage,
            "focus_level": self.derive_focus_level(self._previous_state).value,
            "distraction_count": self.distraction_count,
            "yawn_count": self.yawn_count,
            "eye_close_count": self.eye_close_count,
            "looking_left_count": self.looking_left_count,
            "looking_right_count": self.looking_right_count,
            "looking_down_count": self.looking_down_count,
            "absent_count": self.absent_count,
        }
