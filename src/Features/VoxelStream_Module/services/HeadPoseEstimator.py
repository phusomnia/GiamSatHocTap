import math
import numpy as np

class HeadPoseEstimator:
    def estimate(self, transform_matrix: np.ndarray):
        R = transform_matrix[:3, :3]
        sy = math.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
        singular = sy < 1e-6
        if not singular:
            pitch = math.degrees(math.atan2(R[2, 1], R[2, 2]))
            yaw = math.degrees(math.atan2(-R[2, 0], sy))
            roll = math.degrees(math.atan2(R[1, 0], R[0, 0]))
        else:
            pitch = math.degrees(math.atan2(-R[1, 2], R[1, 1]))
            yaw = math.degrees(math.atan2(-R[2, 0], sy))
            roll = 0.0
        return pitch, yaw, roll
