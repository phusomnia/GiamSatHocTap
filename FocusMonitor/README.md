# GiamSatHocTap - FocusMonitor

FocusMonitor là ứng dụng Python OOP dùng webcam để theo dõi mức độ tập trung khi học tập hoặc làm việc. Ứng dụng dùng OpenCV để phát hiện khuôn mặt, ước lượng mắt, hướng nhìn và trạng thái buồn ngủ, sau đó lưu phiên học vào SQLite và hiển thị thống kê bằng matplotlib.

## Cấu trúc chính

- `main.py`: điểm khởi chạy chương trình.
- `camera/camera_manager.py`: mở, đọc và đóng webcam an toàn.
- `detectors/face_detector.py`: phát hiện khuôn mặt và hiển thị FPS.
- `detectors/eye_detector.py`: tính EAR và phát hiện buồn ngủ.
- `detectors/gaze_detector.py`: phân loại hướng nhìn.
- `detectors/focus_detector.py`: hợp nhất trạng thái tập trung.
- `services/focus_service.py`: tính thời gian tập trung, mất tập trung và điểm số.
- `services/statistics_service.py`: tạo dữ liệu thống kê cho lịch sử.
- `models/session.py`: model phiên học và các kết quả detector.
- `database/sqlite_manager.py`: lưu và đọc dữ liệu từ SQLite.
- `ui/dashboard.py`: giao diện chính PyQt5.
- `ui/history_window.py`: cửa sổ lịch sử và biểu đồ.
- `utils/constants.py`: hằng số, enum và theme màu.
- `reports/`: nơi lưu database SQLite và các báo cáo xuất ra.

## Cài đặt

1. Tạo môi trường ảo nếu cần.
2. Cài thư viện:

```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

```bash
python main.py
```

## Cách hoạt động

- Bấm `Start` để mở webcam và bắt đầu theo dõi.
- Bấm `Stop` để kết thúc phiên và lưu dữ liệu vào SQLite.
- Bấm `View History` để xem tổng số phiên học, điểm trung bình và biểu đồ theo ngày.

## Quy tắc tính điểm

- Nhìn vào màn hình: cộng thời gian tập trung.
- Mất khuôn mặt hoặc nhìn lệch quá lâu: tăng thời gian mất tập trung.
- Mắt nhắm liên tục sẽ được xem là trạng thái buồn ngủ và làm giảm điểm số.

## Yêu cầu hệ thống

- Python 3.10 trở lên.
- Webcam hoạt động bình thường.
- Quyền truy cập camera cho ứng dụng.

## Lưu ý

- Ứng dụng không dùng TensorFlow hay mô hình AI nặng.
- Khi không phát hiện khuôn mặt quá lâu hoặc trạng thái buồn ngủ kéo dài, ứng dụng sẽ phát âm thanh cảnh báo bằng `QApplication.beep()` và hiển thị popup.
