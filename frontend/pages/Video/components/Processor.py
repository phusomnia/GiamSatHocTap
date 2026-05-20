import av
import cv2

class VideoProcessor:
    def __init__(self):
        self._grayscale = False

    @property
    def grayscale(self):
        return self._grayscale

    @grayscale.setter
    def grayscale(self, value: bool):
        self._grayscale = value

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        if self._grayscale:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        return av.VideoFrame.from_ndarray(img, format="bgr24")
