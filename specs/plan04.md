# Kế hoạch: Tối ưu xác thực khuôn mặt — tầm gần và tầm xa

## Vấn đề

Hệ thống hiện tại dùng single embedding cố định được đăng ký ở một khoảng cách nhất định. Khi user di chuyển lại gần hoặc ra xa camera trong quá trình track, embedding khác biệt so với lúc đăng ký → cosine distance tăng → `verify_face` trả về `False` → `auth_fail_count` tăng → `handle_auth_violation` bị gọi sai.

Các tình huống cụ thể:
1. **Mặt quá xa** (<150px): Thiếu chi tiết, embedding nhiễu, dễ false negative
2. **Mặt quá gần** (>60% khung hình): Mất context, chỉ thấy một phần mặt
3. **Di chuyển gần/xa liên tục**: Khoảng cách thay đổi làm embedding biến động, threshold 0.68 cứng không thích ứng được

## Root Cause

1. **Single embedding**: Chỉ lưu 1 vector khuôn mặt tại 1 thời điểm — không đại diện được cho nhiều khoảng cách
2. **Không kiểm tra kích thước mặt**: Không biết face bounding box size trước khi xác thực
3. **Threshold cứng 0.68**: Không thích ứng với sự thay đổi khoảng cách
4. **Không preprocessing**: Ảnh gần/xa đều đưa thẳng vào DeepFace mà không chuẩn hóa

## Giải pháp

### 1. Multi-embedding gallery

Lưu nhiều embedding ở các khoảng cách khác nhau trong lúc đăng ký. Khi xác thực, so sánh với toàn bộ gallery — nếu khớp với bất kỳ embedding nào thì coi là hợp lệ.

```python
class FaceAuthenticator:
    def __init__(self, model_name="ArcFace", base_threshold=0.68):
        self.model_name = model_name
        self.base_threshold = base_threshold
        self.embeddings: list[dict] = []
```

Mỗi entry trong gallery:

```python
{
    "embedding": [...],       # vector ArcFace 512-dim
    "face_size": 200,         # kích thước face bounding box lúc đăng ký
}
```

### 2. Quality check trước khi xác thực

```python
# Ngưỡng
MIN_FACE_SIZE = 150    # px — mặt quá xa, bỏ qua xác thực
MAX_FACE_RATIO = 0.6   # % khung hình — mặt quá gần, bỏ qua xác thực

def check_distance(landmarks, img_shape) -> tuple[bool, str, int]:
    h, w = img_shape[:2]
    xs = [lm.x * w for lm in landmarks]
    ys = [lm.y * h for lm in landmarks]
    face_size = max(max(xs) - min(xs), max(ys) - min(ys))

    if face_size < MIN_FACE_SIZE:
        return False, "Mặt quá xa", face_size
    if face_size / min(w, h) > MAX_FACE_RATIO:
        return False, "Mặt quá gần", face_size
    return True, "", face_size
```

### 3. BackgroundVerifier truyền face_size

```python
class BackgroundVerifier:
    def submit_frame(self, frame: np.ndarray, face_size=None):
        ...

    def _run(self):
        ...
        ok = self.face_auth.verify_face(frame, face_size=face_size)
```

### 4. Adaptive threshold dựa trên khoảng cách

```python
def verify_face(self, frame, face_size=None):
    ...
    for stored in self.embeddings:
        distance = cosine(stored["embedding"], current_emb)
        threshold = self.base_threshold
        if face_size is not None and stored["face_size"] is not None:
            ratio = min(face_size, stored["face_size"]) / max(face_size, stored["face_size"])
            if ratio < 0.5:
                threshold += 0.05   # nới lỏng nếu khác xa khoảng cách lúc đăng ký
        if distance < threshold:
            return True
```

### 5. Cập nhật flow dashboard.py

**Registration (Case 1A):** Đăng ký 3 embedding ở các frame 30, 60, 90 với face_size tương ứng

```python
if self.register_attempt_count % 30 == 0:
    brightness = self.quality_checker.estimate_brightness(frame, landmarks, frame.shape)
    face_size = self.quality_checker.estimate_face_size(landmarks, frame.shape)
    processed = self.image_preprocessor.enhance(frame, brightness)
    success = self.face_auth.register_face(processed, brightness, face_size)
    if len(self.face_auth.embeddings) >= 3:
        self.is_registered = True
```

**Verification (Case 1B):** Check quality, pass face_size to verifier

```python
landmarks = result.face_landmarks[0]
quality_pass, reason, face_size = self.quality_checker.check_distance(landmarks, frame.shape)
if not quality_pass:
    # occlusion buffer 30 frame cho phép che/tạm xa
    self.occlusion_count += 1
    if self.occlusion_count < 30:
        self._render_frame(frame)
        return
else:
    self.occlusion_count = 0

if self.auth_frame_count % 90 == 0:
    self.background_verifier.submit_frame(frame, face_size=face_size)
```

### 6. Reset gallery khi violation

```python
def handle_auth_violation(self):
    self.face_auth.reset()
    ...
```

## Tóm tắt thay đổi

| # | Task | Files | Độ phức tạp |
|---|------|-------|------------|
| 1 | Multi-embedding gallery + adaptive threshold | `services/FaceAuth.py` | Trung bình |
| 2 | Face quality checker (khoảng cách) | `services/FaceAuth.py` | Thấp |
| 3 | ImagePreprocessor (CLAHE) | `services/FaceAuth.py` | Thấp |
| 4 | BackgroundVerifier truyền face_size | `services/FaceAuth.py` | Thấp |
| 5 | Cập nhật dashboard flow | `ui/dashboard.py` | Trung bình |
| 6 | Reset gallery trong handle_auth_violation | `ui/dashboard.py` | Thấp |

## Rủi ro

| Rủi ro | Giảm thiểu |
|--------|------------|
| Multi-embedding làm tăng false positive | Threshold base 0.68 vẫn được giữ, chỉ nới +0.05 khi khác xa khoảng cách |
| CLAHE ảnh hưởng embedding | Chỉ apply khi brightness < 0.3 |
| Occlusion buffer 30 frame bỏ sót rời khỏi thật | 30 frame ~1s, không đáng kể so với 9s threshold violation |
