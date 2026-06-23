import cv2
from deepface import DeepFace
from scipy.spatial.distance import cosine

class FaceAuthenticator:
    def __init__(self, model_name="ArcFace", threshold=0.68):
        self.model_name = model_name
        self.threshold = threshold
        self.registered_embedding = None

    def register_face(self, frame):
        """
        Nhận vào 1 frame từ webcam. 
        Nếu tìm thấy mặt, trích xuất vector embedding và lưu lại.
        Trả về True nếu đăng ký thành công, False nếu không thấy mặt.
        """
        try:
            # Trích xuất đặc trưng khuôn mặt, enforce_detection=True để bắt buộc có mặt
            embedding_objs = DeepFace.represent(img_path=frame, model_name=self.model_name, enforce_detection=True)
            self.registered_embedding = embedding_objs[0]["embedding"]
            return True
        except ValueError:
            return False

    def verify_face(self, frame):
        """
        Kiểm tra xem khuôn mặt trong frame hiện tại có khớp với khuôn mặt đã đăng ký không.
        """
        if self.registered_embedding is None:
            return False # Chưa đăng ký thì không thể xác thực

        try:
            # Lấy vector của frame hiện tại (không ép buộc phát hiện để tránh crash app)
            current_embedding_objs = DeepFace.represent(img_path=frame, model_name=self.model_name, enforce_detection=False)
            current_embedding = current_embedding_objs[0]["embedding"]
            
            # Tính khoảng cách
            distance = cosine(self.registered_embedding, current_embedding)
            
            # Nếu khoảng cách nhỏ hơn ngưỡng cho phép => Cùng 1 người
            if distance < self.threshold:
                return True
            return False
        except Exception as e:
            return False