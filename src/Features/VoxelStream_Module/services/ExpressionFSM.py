from src.VortexRAG.FaceState import FaceState

"""
Optimaztion 1: hysteresis + dwell frames
"""
class ExpressionFSM:
    EYE_CLOSE_THRESHOLD = 0.20
    MOUTH_OPEN_THRESHOLD = 0.03

    REQUIRED_FRAMES = 4

    def __init__(self):
        self.state = FaceState.NORMAL
        self.counter = 0

    def update(self, metrics):
        target_state = FaceState.NORMAL

        if metrics.mar > self.MOUTH_OPEN_THRESHOLD:
            target_state = FaceState.YAWNING

        elif metrics.ear < self.EYE_CLOSE_THRESHOLD:
            target_state = FaceState.EYES_CLOSED

        if target_state == self.state:
            self.counter = 0
            return self.state

        self.counter += 1

        if self.counter >= self.REQUIRED_FRAMES:
            self.state = target_state
            self.counter = 0

        return self.state