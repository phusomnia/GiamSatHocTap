# VoxelStream Module

Real-time face focus analysis pipeline using a webcam and MediaPipe Face Landmarker.

## Pipeline

```
Capture → Detect → Extract → FSM → Render → Display
```

## Directory Structure

```
VoxelStream_Module/
├── config/
│   └── face_landmarker.task    # MediaPipe pre-trained face landmark model
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
│   ├── Metrics.py                 # FaceMetrics data class
│   ├── OCVCapture.py              # OpenCV camera capture
│   └── Renderer.py                # Frame annotation & display
└── VoxelStream_Module.md
```

## Components

### VoxelStreamController (`controllers/VoxelStreamController.py`)

FastAPI controller registered via the `@Controller` decorator.

- **Route:** `POST /api/v1/voxels_stream/run`
- Resolves `VoxelStreamProc` from the DI container and calls `run_tracker()`.

### VoxelStreamProc (`handlers/VoxelStreamProc.py`)

Main processing loop. Uses `Detector` as a context manager.

```python
while capture.is_opened():
    frame = capture.read()
    result = detector.detect(frame, timestamp)
    for landmarks in result.face_landmarks:
        metrics = extractor.extract(landmarks)
        state = fsm.update(metrics)
        frame = renderer.render(frame, landmarks, state, metrics)
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

### FaceMetrics (`services/Metrics.py`)

Data class with fields `left_ear`, `right_ear`, `mar`. Provides a computed `ear` property that averages left and right EAR.

### FaceState (`services/FaceState.py`)

```python
class FaceState(Enum):
    NORMAL = "NORMAL"
    EYES_CLOSED = "EYES CLOSED"
    YAWNING = "YAWNING"
```

### ExpressionFSM (`services/ExpressionFSM.py`)

Hysteresis-based finite state machine to reduce flicker:

- **EYE_CLOSE_THRESHOLD:** EAR < 0.20
- **MOUTH_OPEN_THRESHOLD:** MAR > 0.03
- **REQUIRED_FRAMES:** 4 (dwell count before state transition)

The state only changes after `REQUIRED_FRAMES` consecutive frames show a different state. Returning to the same state resets the counter immediately.

### Renderer (`services/Renderer.py`)

Annotates frames with:

- Green dots on all 478 face landmarks
- Current state text (red, top-left)
- EAR and MAR values (white, below state)

## Running

```bash
# Start the FastAPI server (auto-restarts on .py changes)
python_run_server
# or via the API
curl -X POST http://localhost:8000/api/v1/voxels_stream/run
```

## Dependencies

- `mediapipe` — Face Landmarker model & inference
- `opencv-python` — Camera capture, image processing, display
- `fastapi` — HTTP API
- `granian` — ASGI server
