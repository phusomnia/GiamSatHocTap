import cv2
import numpy as np
from .FaceState import FaceState

class Renderer:

    def draw_landmarks(self, frame, landmarks):

        h, w, _ = frame.shape

        for landmark in landmarks:

            x = int(landmark.x * w)
            y = int(landmark.y * h)

            cv2.circle(
                frame,
                (x, y),
                1,
                (0, 255, 0),
                -1
            )

    def draw_bbox(self, frame, landmarks):
        h, w, _ = frame.shape
        xs = [int(l.x * w) for l in landmarks]
        ys = [int(l.y * h) for l in landmarks]
        x1, y1 = max(0, min(xs)), max(0, min(ys))
        x2, y2 = min(w, max(xs)), min(h, max(ys))
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

    def draw_state(self, frame, state, metrics):

        cv2.putText(
            frame,
            f"STATE: {state.value}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"EAR: {metrics.ear:.3f}",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"MAR: {metrics.mar:.3f}",
            (30, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        if metrics.pitch is not None:
            cv2.putText(
                frame,
                f"Pitch: {metrics.pitch:.1f}",
                (30, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Yaw: {metrics.yaw:.1f}",
                (30, 220),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Roll: {metrics.roll:.1f}",
                (30, 260),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

    def render_no_face(self, frame, state, *, show_overlay=True):
        if show_overlay:
            cv2.putText(
                frame,
                f"STATE: {state.value}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2
            )

            cv2.putText(
                frame,
                "NO FACE DETECTED",
                (30, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        return frame

    def render(
        self,
        frame,
        landmarks,
        state,
        metrics,
        *,
        show_landmarks=False,
        show_bbox=False,
        show_overlay=False
    ):
        if show_landmarks:
            self.draw_landmarks(frame, landmarks)
        if show_bbox:
            self.draw_bbox(frame, landmarks)
        if show_overlay:
            self.draw_state(frame, state, metrics)

        return frame
        