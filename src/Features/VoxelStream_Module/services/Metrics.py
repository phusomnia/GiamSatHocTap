class FaceMetrics:
    def __init__(
        self,
        left_ear,
        right_ear,
        mar
    ):
        self.left_ear = left_ear
        self.right_ear = right_ear
        self.mar = mar
        self.pitch = None
        self.yaw = None
        self.roll = None

    @property
    def ear(self):
        return (
            self.left_ear +
            self.right_ear
        ) / 2