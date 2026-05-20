import math
from .Metrics import FaceMetrics

class Extractor:

    def distance(self, p1, p2):
        return math.sqrt(
            (p1.x - p2.x) ** 2 +
            (p1.y - p2.y) ** 2
        )

    def calc_ear(
        self,
        landmarks,
        p1, p2, p3,
        p4, p5, p6
    ):

        vert1 = self.distance(
            landmarks[p2],
            landmarks[p6]
        )

        vert2 = self.distance(
            landmarks[p3],
            landmarks[p5]
        )

        horizontal = self.distance(
            landmarks[p1],
            landmarks[p4]
        )

        if horizontal == 0:
            return 0

        return (
            vert1 + vert2
        ) / (2.0 * horizontal)

    def calc_mar(self, landmarks):

        top = landmarks[13]
        bottom = landmarks[14]

        left = landmarks[78]
        right = landmarks[308]

        vertical = self.distance(
            top,
            bottom
        )

        horizontal = self.distance(
            left,
            right
        )

        if horizontal == 0:
            return 0

        return vertical / horizontal

    def extract(self, landmarks):

        left_ear = self.calc_ear(
            landmarks,
            33, 160, 158,
            133, 153, 144
        )

        right_ear = self.calc_ear(
            landmarks,
            362, 385, 387,
            263, 373, 380
        )

        mar = self.calc_mar(
            landmarks
        )

        return FaceMetrics(
            left_ear,
            right_ear,
            mar
        )