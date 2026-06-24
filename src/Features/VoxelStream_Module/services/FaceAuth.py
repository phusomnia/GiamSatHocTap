import cv2
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
                enforce_detection=True,
                detector_backend='mtcnn' 
            )
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