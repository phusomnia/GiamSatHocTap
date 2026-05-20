import cv2

class Renderer:

    def draw_landmarks(
        self,
        frame,
        landmarks
    ):

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

    def draw_state(
        self,
        frame,
        state,
        metrics
    ):

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

    def render(
        self,
        frame,
        landmarks,
        state,
        metrics
    ):

        self.draw_landmarks(
            frame,
            landmarks
        )

        self.draw_state(
            frame,
            state,
            metrics
        )

        return frame
        