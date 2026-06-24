# GSHT

Giám sát học tập là dự án Python dùng webcam để theo dõi mức độ tập trung khi học tập hoặc làm việc

## Cài đặt

## Yêu cầu: 
* Scoop: https://scoop.sh/
```
scoop install miniconda3
scoop install versions/python312
```

## Chạy ứng dụng

* chạy lẹnh ./script.sh bằng git bash
### Pipeline workflow: 
```
init venv -> activate venv -> install requirements -> run application
```

* ### Virtual Env:
    ```
    chạy ./script.sh -> python install requirements
    python frontend/native/lain.py
    ```

* ### Local:  
    ```
    pip -r install requirements
    conda activate ./.venv
    python frontend/native/lain.py
    ```

## Cấu trúc thư mục

```
.
├── frontend/
│   └── native/                        # Native desktop frontend (PyQt5)
│       ├── ui/
│       │   ├── dashboard.py           # Main dashboard (sidebar + monitor)
│       │   ├── history_window.py      # History page with charts
│       │   └── tracking_settings.py   # Settings dialog
│       ├── utils/
│       │   └── config.py              # Loads config.yaml
│       ├── config.yaml                # App / camera / tracking / display config
│       └── lain.py                    # Entry point
├── scripts/                            # Shell scripts
├── specs/                              # Architecture docs
├── src/
│   ├── Domain/                         # Domain entities
│   ├── Features/
│   │   └── VoxelStream_Module/         # Face tracking core
│   │       ├── config/
│   │       │   └── face_landmarker.task
│   │       ├── controllers/
│   │       │   └── VoxelStreamController.py  # FastAPI endpoints
│   │       ├── dto/
│   │       │   └── VoxelStreamDTO.py
│   │       ├── handlers/
│   │       │   └── VoxelStreamProc.py        # Pipeline orchestrator
│   │       ├── models/
│   │       │   └── StudySession.py           # Dataclass model
│   │       ├── services/
│   │       │   ├── Detector.py           # MediaPipe FaceLandmarker
│   │       │   ├── ExpressionFSM.py      # Face state machine
│   │       │   ├── Extractor.py          # EAR, MAR extraction
│   │       │   ├── FaceState.py          # State enum
│   │       │   ├── FocusAnalyzer.py      # Focus percentage logic
│   │       │   ├── HeadPoseEstimator.py  # Pitch/yaw/roll from matrix
│   │       │   ├── Metrics.py            # EAR/MAR dataclass
│   │       │   ├── OCVCapture.py         # OpenCV camera capture
│   │       │   ├── Renderer.py           # Draw landmarks, bbox, text
│   │       │   └── interfaces/
│   │       │       └── FrameSource.py
│   │       └── VoxelStream_Module.md
│   ├── SharedKernel/
│   │   ├── base/                         # Decorators, Container, APIResponse
│   │   └── persistence/
│   │       ├── CrudORM.py                # Generic CRUD base
│   │       ├── StudySessionRepo.py       # StudySession repository
│   │       └── SessionManager.py         # Session lifecycle + FocusAnalyzer
│   ├── Infrastructure/                   # Config loader, app config
│   └── lain.py                           # Server entry point
├── requirements.txt
└── script.sh
```

