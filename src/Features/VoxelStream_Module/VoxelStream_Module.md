# VoxelStream Module

Real-time face focus analysis pipeline using a webcam and MediaPipe Face Landmarker.

## Pipeline

```
Capture → Detect → Extract → HeadPoseEstimator → FSM → FocusAnalyzer → Render → Display
                                                                          ↓
                                                                    SessionManager
                                                                          ↓
                                                                      SQLite
                                                                          ↓
                                                                   Dashboard
```

## Directory Structure

```
VoxelStream_Module/
├── config/
│   └── face_landmarker.task       # MediaPipe pre-trained face landmark model
├── controllers/
│   └── VoxelStreamController.py   # FastAPI controller
├── handlers/
│   └── VoxelStreamProc.py         # Main processing orchestration
├── services/
│   ├── interfaces/
│   │   └── FrameSource.py         # Abstract frame source
│   ├── Detector.py                # MediaPipe FaceLandmarker wrapper
│   ├── ExpressionFSM.py           # Hysteresis-based state machine
│   ├── Extractor.py               # EAR/MAR computation
│   ├── FaceState.py               # Face state enum
│   ├── FocusAnalyzer.py           # Focus score & behavior tracking
│   ├── HeadPoseEstimator.py       # Pitch/Yaw/Roll from transform matrix
│   ├── Metrics.py                 # FaceMetrics data class
│   ├── OCVCapture.py              # OpenCV camera capture
│   ├── Renderer.py                # Frame annotation & display
│   └── SessionManager.py          # Study session lifecycle
├── models/
│   ├── __init__.py
│   └── StudySession.py            # Session data model
├── database/
│   ├── __init__.py
│   └── SQLiteManager.py           # SQLite CRUD operations
├── dto/
│   ├── __init__.py
│   └── VoxelStreamDTO.py          # Pydantic API response models
├── __init__.py
└── VoxelStream_Module.md
```

## Components

### VoxelStreamController (`controllers/VoxelStreamController.py`)

FastAPI controller registered via the `@Controller` decorator.

| Route | Method | Description |
|---|---|---|
| `/api/v1/voxels_stream/run` | POST | Start video processing |
| `/api/v1/voxels_stream/sessions` | GET | List all study sessions |
| `/api/v1/voxels_stream/sessions/stats` | GET | Aggregate statistics |
| `/api/v1/voxels_stream/sessions/daily` | GET | Daily focus scores (chart data) |
| `/api/v1/voxels_stream/sessions/recent` | GET | Recent N-day sessions |

### VoxelStreamProc (`handlers/VoxelStreamProc.py`)

Main processing loop. Accepts optional `SessionManager` for real-time tracking.

```python
while capture.is_opened():
    frame = capture.read()
    result = detector.detect(frame, timestamp)
    if result.face_landmarks:
        for idx, landmarks in enumerate(result.face_landmarks):
            metrics = extractor.extract(landmarks)
            if result.facial_transformation_matrixes:
                pitch, yaw, roll = head_pose_estimator.estimate(tf_matrix)
                metrics.pitch, metrics.yaw, metrics.roll = pitch, yaw, roll
            state = fsm.update(metrics)
            if session_manager: session_manager.update(state)
            frame = renderer.render(frame, landmarks, state, metrics)
    else:
        state = fsm.update(None)  # ABSENT tracking
    cv2.imshow("Focus Analysis", frame)
```

Press `q` to quit.

### OCVCapture (`services/OCVCapture.py`)

Implements `FrameSource`. Opens webcam via `cv2.VideoCapture(0)` at 1280x720, flips frames horizontally, and provides monotonic timestamps in milliseconds.

### Detector (`services/Detector.py`)

Context manager wrapping MediaPipe's `FaceLandmarker` in VIDEO mode. Loads the model from `config/face_landmarker.task`. The `detect()` method converts BGR→RGB and calls `detect_for_video()`.

### Extractor (`services/Extractor.py`)

Extracts face metrics from MediaPipe landmarks (478-point mesh):

- **EAR** (Eye Aspect Ratio) — computed independently for left eye (indices `33,160,158,133,153,144`) and right eye (`362,385,387,263,373,380`). Uses the standard EAR formula: `(||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)`.
- **MAR** (Mouth Aspect Ratio) — vertical distance between landmarks `13` and `14` divided by horizontal distance between `78` and `308`.

### HeadPoseEstimator (`services/HeadPoseEstimator.py`)

Extracts head pose Euler angles from the MediaPipe facial transformation matrix.

- **Input:** 4×4 transformation matrix from `FaceLandmarkerResult.facial_transformation_matrixes`
- **Output:** `(pitch, yaw, roll)` in degrees

Angles are derived from the top-left 3×3 rotation matrix using the standard ZYX Euler angle convention.

### FaceMetrics (`services/Metrics.py`)

Data class with fields `left_ear`, `right_ear`, `mar`. Provides a computed `ear` property that averages left and right EAR. Optional fields `pitch`, `yaw`, `roll` are set by `HeadPoseEstimator`.

### FaceState (`services/FaceState.py`)

```python
class FaceState(Enum):
    NORMAL         = "NORMAL"
    EYES_CLOSED    = "EYES CLOSED"
    YAWNING        = "YAWNING"
    LOOKING_LEFT   = "LOOKING LEFT"
    LOOKING_RIGHT  = "LOOKING RIGHT"
    LOOKING_DOWN   = "LOOKING DOWN"
    ABSENT         = "ABSENT"
```

### ExpressionFSM (`services/ExpressionFSM.py`)

Hysteresis-based finite state machine to reduce flicker:

| State | Condition |
|---|---|
| `YAWNING` | MAR > 0.03 |
| `EYES_CLOSED` | EAR < 0.20 |
| `LOOKING_DOWN` | pitch < -20° |
| `LOOKING_LEFT` | yaw < -25° |
| `LOOKING_RIGHT` | yaw > 25° |
| `ABSENT` | No face for ~90 frames (≈3s) |
| `NORMAL` | Default |

**Hysteresis:** `REQUIRED_FRAMES = 4` — state only changes after 4 consecutive frames show a different state.

### FocusAnalyzer (`services/FocusAnalyzer.py`)

Tracks focus score and behavior events during a study session.

| Event | Penalty |
|---|---|
| Eyes closed | -20 |
| Yawning | -10 |
| Looking away | -15 |
| Absent | -40 |

Score starts at 100 and is clamped to [0, 100]. Each state transition to a negative state counts as one event.

### Renderer (`services/Renderer.py`)

Annotates frames with:

- Green dots on all 478 face landmarks
- Current state text (red, top-left)
- EAR, MAR, Pitch, Yaw, Roll values
- "NO FACE DETECTED" when face is absent

### SessionManager (`services/SessionManager.py`)

Manages the lifecycle of a study session.

- `start()` — reset counters, record `start_time`
- `update(state)` — feed current face state to `FocusAnalyzer`
- `stop()` — finalize stats, persist to SQLite via `SQLiteManager`
- `get_current_stats()` — real-time summary for dashboard

### SQLiteManager (`database/SQLiteManager.py`)

SQLite persistence for `study_sessions` table.

```sql
CREATE TABLE study_sessions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time          TEXT NOT NULL,
    end_time            TEXT NOT NULL,
    duration            INTEGER NOT NULL,
    focus_score         REAL NOT NULL,
    distraction_count   INTEGER DEFAULT 0,
    yawn_count          INTEGER DEFAULT 0,
    eye_close_count     INTEGER DEFAULT 0,
    looking_left_count  INTEGER DEFAULT 0,
    looking_right_count INTEGER DEFAULT 0,
    looking_down_count  INTEGER DEFAULT 0,
    absent_count        INTEGER DEFAULT 0
);
```

### StudySession (`models/StudySession.py`)

Dataclass mirroring the `study_sessions` table schema.

## API Endpoints

```bash
# Start video processing
curl -X POST http://localhost:8000/api/v1/voxels_stream/run

# List all sessions
curl http://localhost:8000/api/v1/voxels_stream/sessions

# Get summary statistics
curl http://localhost:8000/api/v1/voxels_stream/sessions/stats

# Get daily scores (last 7 days)
curl http://localhost:8000/api/v1/voxels_stream/sessions/daily?days=7

# Get recent sessions (last 7 days)
curl http://localhost:8000/api/v1/voxels_stream/sessions/recent?days=7
```

## Dependencies

- `mediapipe` — Face Landmarker model & inference
- `opencv-python` — Camera capture, image processing, display
- `numpy` — Matrix operations for head pose estimation
- `fastapi` — HTTP API
- `granian` — ASGI server
