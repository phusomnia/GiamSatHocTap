from .FaceState import FaceState

class ExpressionFSM:
    EYE_CLOSE_THRESHOLD = 0.20
    MOUTH_OPEN_THRESHOLD = 0.5
    LOOKING_LEFT_THRESHOLD = -25.0
    LOOKING_RIGHT_THRESHOLD = 25.0
    LOOKING_DOWN_THRESHOLD = -20.0
    ABSENT_FRAMES = 90

    REQUIRED_FRAMES = 4

    def __init__(self):
        self.state = FaceState.NORMAL
        self.counter = 0
        self.absent_counter = 0

    def update(self, metrics=None):
        if metrics is None:
            return self._process_no_face()
        return self._process_face(metrics)

    def _process_face(self, metrics):
        target_state = self._determine_target_state(metrics)
        self.absent_counter = 0
        if target_state == self.state:
            self.counter = 0
            return self.state
        self.counter += 1
        if self.counter >= self.REQUIRED_FRAMES:
            self.state = target_state
            self.counter = 0
        return self.state

    def _process_no_face(self):
        self.absent_counter += 1
        if self.absent_counter >= self.ABSENT_FRAMES:
            return self._transition_to(FaceState.ABSENT)
        return self.state

    def _determine_target_state(self, metrics):
        is_turning = (
            metrics.yaw is not None
            and (
                metrics.yaw < self.LOOKING_LEFT_THRESHOLD
                or metrics.yaw > self.LOOKING_RIGHT_THRESHOLD
            )
        )
        if not is_turning and metrics.mar > self.MOUTH_OPEN_THRESHOLD:
            return FaceState.YAWNING
        if not is_turning and metrics.ear < self.EYE_CLOSE_THRESHOLD:
            return FaceState.EYES_CLOSED
        if metrics.pitch is not None and metrics.pitch < self.LOOKING_DOWN_THRESHOLD:
            return FaceState.LOOKING_DOWN
        if metrics.yaw is not None and metrics.yaw < self.LOOKING_LEFT_THRESHOLD:
            return FaceState.LOOKING_LEFT
        if metrics.yaw is not None and metrics.yaw > self.LOOKING_RIGHT_THRESHOLD:
            return FaceState.LOOKING_RIGHT
        return FaceState.NORMAL

    def _transition_to(self, target_state):
        if target_state == self.state:
            self.counter = 0
            return self.state
        self.counter += 1
        if self.counter >= self.REQUIRED_FRAMES:
            self.state = target_state
            self.counter = 0
        return self.state

    def reset(self):
        self.state = FaceState.NORMAL
        self.counter = 0
        self.absent_counter = 0