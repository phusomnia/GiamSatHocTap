import cv2
from src.SharedKernel.base.Container import Component
from ..services.OCVCapture import OCVCapture as Capture
from ..services.Detector import Detector
from ..services.Extractor import Extractor
from ..services.Renderer import Renderer
from ..services.ExpressionFSM import ExpressionFSM
from ..services.HeadPoseEstimator import HeadPoseEstimator
from ....SharedKernel.persistence.SessionManager import SessionManager

from ..services.FaceAuth import FaceAuthenticator

@Component
class VoxelStreamProc:
    def __init__(self):
        self.capture = Capture()
        self.extractor = Extractor()
        self.renderer = Renderer()
        self.fsm = ExpressionFSM()
        self.head_pose_estimator = HeadPoseEstimator()
        self.face_auth = FaceAuthenticator()
        self._stop_requested = False

    def stop(self):
        self._stop_requested = True

    def run_tracker(self, session_manager: SessionManager = None):
        self._stop_requested = False
        is_registered = False
        frame_count = 0
        auth_warning = False

        with Detector() as detector:
            while self.capture.is_opened():
                if self._stop_requested:
                    break

                frame = self.capture.read()

                if frame is None:
                    break

                #GIAI ĐOẠN ĐĂNG KÝ KHUÔN MẶT
                if not is_registered:
                    cv2.putText(frame, "Nhin thang camera, nhan 'S' de Dang ky", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    cv2.imshow("Focus Analysis", frame)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("s") or key == ord("S"):
                        print("Đang xử lý đăng ký khuôn mặt...")
                        success = self.face_auth.register_face(frame)
                        if success:
                            print("✅ Đăng ký thành công! Bắt đầu giám sát.")
                            is_registered = True
                        else:
                            print("❌ Không tìm thấy khuôn mặt hợp lệ, vui lòng thử lại!")
                    elif key == ord("q") or key == ord("Q"):
                        break
                        
                    continue


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


                #GIAI ĐOẠN KIỂM TRA ĐỊNH KỲ & CẢNH BÁO
                frame_count += 1
                if frame_count % 90 == 0:
                    is_verified = self.face_auth.verify_face(frame)
                    if not is_verified:
                        auth_warning = True
                        print("⚠️ CẢNH BÁO: Phát hiện người lạ hoặc người dùng rời khỏi vị trí!")
                    else:
                        auth_warning = False

                if auth_warning:
                    cv2.putText(frame, "WARNING: UNAUTHORIZED USER!", (50, 80), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                cv2.imshow("Focus Analysis", frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        self.capture.release()
        if session_manager:
            session_manager.stop()