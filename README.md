# GiamSatHocTap

GiamSatHocTap là dự án Python OOP dùng webcam để theo dõi mức độ tập trung khi học tập hoặc làm việc. Phần chạy chính nằm trong thư mục [FocusMonitor](FocusMonitor), dùng OpenCV, PyQt5 và SQLite.

## Cài đặt

Từ thư mục gốc dự án:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python FocusMonitor/main.py
```

## Tóm tắt cấu trúc

- [FocusMonitor/main.py](FocusMonitor/main.py): điểm khởi chạy ứng dụng.
- [FocusMonitor/camera/camera_manager.py](FocusMonitor/camera/camera_manager.py): quản lý webcam.
- [FocusMonitor/detectors/face_detector.py](FocusMonitor/detectors/face_detector.py): phát hiện khuôn mặt và FPS.
- [FocusMonitor/detectors/eye_detector.py](FocusMonitor/detectors/eye_detector.py): tính EAR và nhận biết buồn ngủ.
- [FocusMonitor/detectors/gaze_detector.py](FocusMonitor/detectors/gaze_detector.py): phân loại hướng nhìn.
- [FocusMonitor/detectors/focus_detector.py](FocusMonitor/detectors/focus_detector.py): ghép trạng thái tập trung tổng thể.
- [FocusMonitor/services/focus_service.py](FocusMonitor/services/focus_service.py): tính focus time, lost time và focus score.
- [FocusMonitor/services/statistics_service.py](FocusMonitor/services/statistics_service.py): tạo dữ liệu thống kê cho lịch sử.
- [FocusMonitor/database/sqlite_manager.py](FocusMonitor/database/sqlite_manager.py): lưu và đọc phiên học SQLite.
- [FocusMonitor/ui/dashboard.py](FocusMonitor/ui/dashboard.py): giao diện chính PyQt5.
- [FocusMonitor/ui/history_window.py](FocusMonitor/ui/history_window.py): cửa sổ lịch sử và biểu đồ.
- [FocusMonitor/models/session.py](FocusMonitor/models/session.py): dataclass và enum cho trạng thái/phiên học.
- [FocusMonitor/utils/constants.py](FocusMonitor/utils/constants.py): hằng số cấu hình và màu giao diện.

## Ghi chú

- Ứng dụng không dùng TensorFlow hay mô hình AI nặng.
- Dữ liệu phiên học được lưu vào SQLite trong thư mục [FocusMonitor/reports](FocusMonitor/reports).