# Features

Các module tính năng cho GSHT (Giám sát học tập).

## Modules

| Module | Mô tả |
|---|---|
| [VoxelStream_Module](./VoxelStream_Module/VoxelStream_Module.md) | Phân tích tập trung khuôn mặt thời gian thực qua webcam + MediaPipe |
| Attachment_Module | Xử lý tệp đính kèm |
| Auton_Module | Lớp facade AI/tự động hóa |
| Shared_Module | Controller dùng chung |

### VoxelStream_Module

Pipeline theo dõi khuôn mặt và phân tích tập trung thời gian thực:

```
Capture → Detect → Extract → HeadPose → FSM → Analyze → Render → Display
```

- MediaPipe Face Landmarker (lưới 478 điểm)
- Phát hiện buồn ngủ dựa trên EAR/MAR
- Ước tính head pose (pitch/yaw/roll)
- Máy trạng thái hysteresis (7 trạng thái)
- Tính điểm tập trung (% khung hình tập trung)
- Lưu trữ SQLite qua SharedKernel
- REST API (FastAPI, 5 endpoints)

Xem [tài liệu đầy đủ](./VoxelStream_Module/VoxelStream_Module.md) để biết chi tiết thuật toán, tham khảo component và cách sử dụng API.
