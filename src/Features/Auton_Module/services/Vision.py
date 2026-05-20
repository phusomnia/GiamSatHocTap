from src.SharedKernel.base.Container import Service
from ultralytics import YOLO
import cv2

@Service
class Vision:
    def __init__(self) -> None:
        self.cam = None
    
    def open_camera(self):
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return self._gen_frames()
    
    def _gen_frames(self):
        while True:
            if self.cam is None:
                break
            suc, fr = self.cam.read()
        
            if not suc:
                break
            
            ret, bf = cv2.imencode(".jpg", fr)

            if ret:
                fr_byte = bf.tobytes()

                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    fr_byte +
                    b'\r\n'
                )

    async def demo_yolo_pipeline(self):
        model = YOLO("yolov8n.pt")
        print(model)

        cap = cv2.VideoCapture(0)

        while True:
            suc, frame = cap.read()
            if not suc:
                break
            
            results = model(frame)
            annotated = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', annotated)
            if ret:
                frame_bytes = buffer.tobytes()
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame_bytes +
                    b'\r\n'
                )


    # def demo_multimodal():
    #     with open("../static/street.jpg", "rb") as f:
    #         image_base64 = base64.b64encode(
    #             f.read()
    #         ).decode("utf-8")