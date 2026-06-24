import threading
import time
import cv2
import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine


class FaceAuthenticator:
    def __init__(self, model_name="ArcFace", threshold=0.68):
        self.model_name = model_name
        self.threshold = threshold
        self.registered_embedding = None

    def register_face(self, frame):
        """Trích xuất và lưu vector khuôn mặt gốc."""
        try:
            embedding_objs = DeepFace.represent(
                img_path=frame, 
                model_name=self.model_name, 
                enforce_detection=False,
                detector_backend='opencv'
            )
            if not embedding_objs:
                return False
            self.registered_embedding = embedding_objs[0]["embedding"]
            return True
        except Exception as e:
            print(f"❌ Chi tiết lỗi AI: {e}") 
            return False

    def verify_face(self, frame):
        """So sánh khuôn mặt hiện tại với khuôn mặt gốc."""
        if self.registered_embedding is None:
            return True 
        try:
            current_objs = DeepFace.represent(
                img_path=frame, 
                model_name=self.model_name, 
                enforce_detection=False,
                detector_backend='mtcnn'
            )
            if not current_objs:
                return False 
                
            current_embedding = current_objs[0]["embedding"]
            distance = cosine(self.registered_embedding, current_embedding)
            return distance < self.threshold
        except Exception as e:
            return False


class BackgroundVerifier:
    """Chạy DeepFace verify trong thread riêng, không block main thread."""

    def __init__(self, face_auth: FaceAuthenticator, interval_frames=90, fps=30):
        self.face_auth = face_auth
        self.interval = interval_frames / fps
        self._latest_frame: np.ndarray | None = None
        self._result = True
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def submit_frame(self, frame: np.ndarray):
        with self._lock:
            self._latest_frame = frame.copy()

    @property
    def is_verified(self) -> bool:
        with self._lock:
            return self._result

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        while self._running:
            time.sleep(self.interval)
            with self._lock:
                frame = self._latest_frame
            if frame is None:
                continue
            try:
                ok = self.face_auth.verify_face(frame)
            except Exception:
                ok = False
            with self._lock:
                self._result = ok
