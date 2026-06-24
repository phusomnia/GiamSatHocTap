import cv2
from src.SharedKernel.base.Container import Component
from ..services.OCVCapture import OCVCapture as Capture
from ..services.Detector import Detector
from ..services.Extractor import Extractor
from ..services.Renderer import Renderer
from ..services.ExpressionFSM import ExpressionFSM
from ..services.HeadPoseEstimator import HeadPoseEstimator
from ....SharedKernel.persistence.SessionManager import SessionManager

@Component
class VoxelStreamProc:
    def __init__(self):
        self.capture = Capture()
        self.extractor = Extractor()
        self.renderer = Renderer()
        self.fsm = ExpressionFSM()
        self.head_pose_estimator = HeadPoseEstimator()

    def run_tracker(self, session_manager: SessionManager = None):
        with Detector() as detector:
            while self.capture.is_opened():
                if self._stop_requested:
                    break

                frame = self.capture.read()

                if frame is None:
                    break

                result = detector.detect(
                    frame,
                    self.capture.timestamp()
                )

                if result.face_landmarks:
                    # Chỉ track 1 khuôn mặt đầu tiên
                    landmarks = result.face_landmarks[0]
                    metrics = self.extractor.extract(landmarks)

                    if result.facial_transformation_matrixes:
                        tf_matrix = result.facial_transformation_matrixes[0]
                        pitch, yaw, roll = self.head_pose_estimator.estimate(tf_matrix)
                        metrics.pitch = pitch
                        metrics.yaw = yaw
                        metrics.roll = roll

                    state = self.fsm.update(metrics)
                    frame = self.renderer.render(frame, landmarks, state, metrics)

                    if session_manager:
                        session_manager.update(state)

                else:
                    state = self.fsm.update(None)
                    frame = self.renderer.render_no_face(frame, state)
                    if session_manager:
                        session_manager.update(state)

                cv2.imshow(
                    "Focus Analysis",
                    frame
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        self.capture.release()
        if session_manager:
            session_manager.stop()