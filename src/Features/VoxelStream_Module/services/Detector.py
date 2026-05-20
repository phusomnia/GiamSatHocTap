import os
import mediapipe as mp
from mediapipe import Image, ImageFormat
import cv2

class Detector:
    def __init__(
        self,
        model_path=None,
        num_faces=1
    ):
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "config",
                "face_landmarker.task"
            )
            model_path = os.path.abspath(model_path)

        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = (
            mp.tasks.vision.FaceLandmarkerOptions
        )

        VisionRunningMode = (
            mp.tasks.vision.RunningMode
        )

        self.FaceLandmarker = FaceLandmarker

        self.options = FaceLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=VisionRunningMode.VIDEO,
            num_faces=num_faces
        )

    def __enter__(self):
        self.landmarker = (
            self.FaceLandmarker
            .create_from_options(self.options)
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.landmarker.close()

    def detect(
        self,
        frame,
        timestamp_ms
    ):
        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        rgb_frame = Image(
            image_format=ImageFormat.SRGB,
            data=rgb
        )

        return self.landmarker.detect_for_video(
            rgb_frame,
            timestamp_ms
        )