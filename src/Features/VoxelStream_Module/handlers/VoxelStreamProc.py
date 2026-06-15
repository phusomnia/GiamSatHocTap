import cv2
from src.SharedKernel.base.Container import Component
from ..services.OCVCapture import OCVCapture as Capture
from ..services.Detector import Detector
from ..services.Extractor import Extractor
from ..services.Renderer import Renderer
from ..services.ExpressionFSM import ExpressionFSM

@Component
class VoxelStreamProc:
    def __init__(self):
        self.capture    = Capture()
        self.extractor  = Extractor()
        self.renderer   = Renderer()
        self.fsm        = ExpressionFSM()

    def run_tracker(self):
        with Detector() as detector:
            while self.capture.is_opened():

                frame = self.capture.read()

                if frame is None:
                    break

                result = detector.detect(
                    frame,
                    self.capture.timestamp()
                )

                if result.face_landmarks:

                    for landmarks in result.face_landmarks:

                        metrics = (
                            self.extractor
                            .extract(landmarks)
                        )

                        state = self.fsm.update(
                            metrics
                        )

                        frame = self.renderer.render(
                            frame,
                            landmarks,
                            state,
                            metrics
                        )

                cv2.imshow(
                    "Focus Analysis",
                    frame
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        self.capture.release()