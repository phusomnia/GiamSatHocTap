# Hệ Thống Giám Sát Tập Trung Học Tập

## Phiên bản 1.0

---

# 1. Giới thiệu

Hệ thống Giám sát Tập trung Học tập (Study Monitoring System) là ứng dụng sử dụng webcam để theo dõi trạng thái khuôn mặt của người học theo thời gian thực.

Mục tiêu của hệ thống:

* Theo dõi mức độ tập trung khi học tập.
* Phát hiện các dấu hiệu mất tập trung.
* Ghi nhận thời gian học thực tế.
* Thống kê hiệu suất học tập.
* Hỗ trợ người học cải thiện khả năng tập trung.

Hệ thống được xây dựng trên nền tảng:

* Python
* OpenCV
* MediaPipe Face Landmarker
* FastAPI
* SQLite

MediaPipe Face Landmarker cung cấp 478 điểm landmark khuôn mặt, các hệ số biểu cảm (blendshapes) và ma trận biến đổi khuôn mặt, phù hợp cho các bài toán theo dõi khuôn mặt thời gian thực.

---

# 2. Kiến trúc hiện tại

```text
Capture
   ↓
Face Detection
   ↓
Feature Extraction
   ↓
Expression FSM
   ↓
Rendering
   ↓
Display
```

---

# 3. Các thành phần đã triển khai

## 3.1. OCVCapture

### Chức năng

* Mở webcam.
* Đọc khung hình liên tục.
* Lật ảnh theo chiều ngang.
* Sinh timestamp phục vụ xử lý video.

### Đầu ra

```python
frame
timestamp_ms
```

---

## 3.2. Detector

### Chức năng

* Nạp mô hình Face Landmarker.
* Phát hiện khuôn mặt.
* Trích xuất 478 landmark.

### Đầu ra

```python
FaceLandmarkerResult
```

MediaPipe Face Landmarker hỗ trợ phát hiện landmark 3D khuôn mặt theo thời gian thực từ luồng video.

---

## 3.3. Extractor

### Chức năng

Tính toán các chỉ số khuôn mặt:

### EAR (Eye Aspect Ratio)

Dùng để xác định:

* Mắt mở
* Mắt nhắm

### MAR (Mouth Aspect Ratio)

Dùng để xác định:

* Ngáp
* Mở miệng

### Đầu ra

```python
FaceMetrics
```

```python
left_ear
right_ear
mar
```

```python
ear = (left_ear + right_ear) / 2
```

---

## 3.4. ExpressionFSM

Máy trạng thái hữu hạn sử dụng cơ chế hysteresis nhằm giảm hiện tượng nhấp nháy trạng thái.

### Các trạng thái hiện tại

```python
NORMAL
EYES_CLOSED
YAWNING
```

### Ngưỡng

```python
EAR < 0.20
MAR > 0.03
REQUIRED_FRAMES = 4
```

---

## 3.5. Renderer

### Chức năng

Hiển thị:

* 478 landmark khuôn mặt.
* Trạng thái hiện tại.
* Giá trị EAR.
* Giá trị MAR.

---

# 4. Hạn chế của phiên bản hiện tại

Hiện tại hệ thống chỉ có khả năng:

* Phát hiện nhắm mắt.
* Phát hiện ngáp.

Do đó hệ thống mới chỉ đóng vai trò như một hệ thống phát hiện buồn ngủ (Drowsiness Detection).

Hệ thống chưa đánh giá được:

* Người học có nhìn màn hình hay không.
* Người học có quay đầu sang hướng khác hay không.
* Người học có rời khỏi bàn học hay không.
* Mức độ tập trung tổng thể.

---

# 5. Kế hoạch mở rộng

## Giai đoạn 1 - Ước lượng hướng đầu

### Mục tiêu

Theo dõi hướng nhìn của người học.

### Thành phần mới

```text
HeadPoseEstimator
```

### Chức năng

Tính toán:

```python
pitch
yaw
roll
```

MediaPipe có thể xuất facial transformation matrix phục vụ việc ước lượng tư thế đầu (head pose) và hướng khuôn mặt.

---

## Trạng thái mới

```python
NORMAL
LOOKING_LEFT
LOOKING_RIGHT
LOOKING_DOWN
EYES_CLOSED
YAWNING
ABSENT
```

### LOOKING_LEFT

```text
yaw < -25°
```

### LOOKING_RIGHT

```text
yaw > 25°
```

### LOOKING_DOWN

```text
pitch < -20°
```

### ABSENT

```text
Không phát hiện khuôn mặt
trong hơn 3 giây
```

---

# 6. Focus Analyzer

## Thành phần mới

```text
FocusAnalyzer
```

### Chức năng

* Theo dõi hành vi người học.
* Tính điểm tập trung.
* Đếm số lần mất tập trung.

---

## Công thức điểm tập trung

Điểm ban đầu:

```python
100
```

Trừ điểm:

```text
Nhắm mắt        -20
Ngáp            -10
Nhìn chỗ khác   -15
Rời màn hình    -40
```

Kết quả:

```python
focus_score
```

Giới hạn:

```text
0 - 100
```

---

# 7. Quản lý phiên học

## Đối tượng StudySession

```python
StudySession
```

### Thuộc tính

```python
id
start_time
end_time
duration
focus_score
distraction_count
yawn_count
eye_close_count
```

---

## SessionManager

### Chức năng

* Bắt đầu phiên học.
* Kết thúc phiên học.
* Tính toán thống kê.
* Lưu dữ liệu.

---

# 8. Cơ sở dữ liệu

## Bảng study_sessions

```sql
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY,
    start_time DATETIME,
    end_time DATETIME,
    duration INTEGER,
    focus_score REAL,
    distraction_count INTEGER,
    yawn_count INTEGER,
    eye_close_count INTEGER
);
```

---

# 9. Dashboard thống kê

## Các chỉ số hiển thị

* Tổng thời gian học.
* Điểm tập trung trung bình.
* Số lần mất tập trung.
* Số lần ngáp.
* Số lần nhắm mắt.

---

## Biểu đồ

### Điểm tập trung theo ngày

```text
Ngày
  ↓
Focus Score
```

### Thời gian học theo tuần

```text
Tuần
  ↓
Số giờ học
```

### Thống kê hành vi

```text
Looking Left
Looking Right
Looking Down
Eyes Closed
Yawning
Absent
```

---

# 10. Kiến trúc mục tiêu

```text
Capture
   ↓
Detector
   ↓
Extractor
   ↓
HeadPoseEstimator
   ↓
ExpressionFSM
   ↓
FocusAnalyzer
   ↓
SessionManager
   ↓
SQLite
   ↓
Dashboard
```

---

# 11. Kết quả mong đợi

Sau khi hoàn thành, hệ thống có thể:

* Phát hiện khuôn mặt theo thời gian thực.
* Phát hiện nhắm mắt.
* Phát hiện ngáp.
* Phát hiện hướng nhìn.
* Phát hiện rời khỏi màn hình.
* Tính toán mức độ tập trung.
* Lưu lịch sử học tập.
* Sinh báo cáo thống kê.

---

# 12. Công nghệ sử dụng

* Python
* OpenCV
* MediaPipe Face Landmarker
* FastAPI
* SQLite
* Matplotlib
* Dependency Injection
* Finite State Machine (FSM)
* Object-Oriented Programming (OOP)
