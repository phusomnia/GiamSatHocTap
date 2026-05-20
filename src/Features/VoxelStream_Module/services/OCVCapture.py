import cv2
from .interfaces.FrameSource import FrameSource
import time

class OCVCapture(FrameSource):
    def __init__(
        self,
        camera_id=0,
        width=640,
        height=480
    ):
        self.cap = cv2.VideoCapture(camera_id)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,width)

        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,height)

        self.start_time = time.monotonic()

    def read(self):
        success, frame = self.cap.read()

        if not success:
            return None

        frame = cv2.flip(frame, 1)

        return frame

    def is_opened(self):
        return self.cap.isOpened()

    def timestamp(self):
        return int(
            (time.monotonic() - self.start_time) * 1000
        )

    def release(self):
        self.cap.release()
