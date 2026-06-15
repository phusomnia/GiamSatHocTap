# FastAPI Template Starter

A full-stack template with FastAPI backend and Streamlit frontend, with integrated computer vision capabilities.

## Project Structure

```
Fastapi-Template-Starter/
├── src/                          # Backend (FastAPI)
│   ├── lain.py                   # Main FastAPI application entry
│   ├── __init__.py
│   ├── config/
│   │   ├── Config.py             # Configuration loader
│   │   ├── app-config.yaml       # Main application config
│   │   ├── index.yaml            # Index configuration
│   │   └── prompts/
│   │       └── generation-prompts.yaml
│   ├── database/
│   │   ├── init.sql              # Database initialization script
│   │   ├── template-db-pg.dbml
│   │   └── template-db-pg.dbml.sql
│   ├── Domain/
│   │   ├── base_entities.py      # Base domain entities
│   │   └── enum/                 # Domain enums
│   ├── Features/                 # Feature modules
│   │   ├── Attachment_Module/    # File attachment handling
│   │   │   ├── AttachmentController.py
│   │   │   ├── AttachmentService.py
│   │   │   ├── AttachmentRepository.py
│   │   │   └── AttachmentDTO.py
│   │   ├── Auton_Module/         # AI/Autonomous module
│   │   │   ├── AIFacade.py
│   │   │   ├── AutonController.py
│   │   │   ├── config/
│   │   │   │   └── LLMConfig.py
│   │   │   ├── persistence/
│   │   │   │   ├── Neo4jService.py
│   │   │   │   ├── RedisService.py
│   │   │   │   └── VectorStoreConfig.py
│   │   │   └── services/
│   │   │       ├── AgentService.py
│   │   │       ├── DectectionService.py
│   │   │       ├── LLMService.py
│   │   │       ├── LoaderService.py
│   │   │       ├── ProcessService.py
│   │   │       ├── Retriever.py
│   │   │       ├── Tools.py
│   │   │       └── Vision.py
│   │   ├── Shared_Module/        # Shared features
│   │   │   ├── SharedController.py
│   │   │   ├── BlogRepository.py
│   │   │   └── BlogDTO.py
│   │   └── VoxelStream_Module/   # Computer vision / face detection
│   │       ├── VoxelStreamController.py
│   │       ├── VoxelStreamProc.py
│   │       ├── config/
│   │       │   └── face_landmarker.task
│   │       └── services/
│   │           ├── Capture.py
│   │           ├── Dectector.py
│   │           ├── Extractor.py
│   │           ├── ExpressionFSM.py
│   │           ├── Metrics.py
│   │           ├── Renderer.py
│   │           └── interfaces/
│   │               └── FrameSource.py
│   ├── SharedKernel/             # Shared utilities
│   │   ├── base/
│   │   │   ├── APIResponse.py    # Standard API response
│   │   │   ├── Container.py      # Dependency injection
│   │   │   ├── Decorators.py     # Controller registration
│   │   │   ├── Logger.py         # Logging
│   │   │   └── Metrics.py        # Metrics collection
│   │   └── persistence/
│   │       ├── CrudRepository.py # Generic CRUD operations
│   │       ├── Database.py       # SQL database
│   │       ├── Neo4jManager.py   # Graph database
│   │       ├── Neo4jVectorManager.py  # Vector store
│   │       └── RedisManager.py   # Redis cache
│   ├── VortexRAG/
│   │   └── FaceState.py          # Face state management
│   └── static/
│       ├── data/                 # Static data files
│       ├── img/
│       │   └── store1.jpg
│       ├── templates/            # HTML templates
│       └── uploads/              # Uploaded files
├── frontend/                     # Frontend (Streamlit)
│   ├── app.py                    # Main Streamlit app entry
│   ├── .streamlit/
│   │   └── config.toml
│   ├── pages/
│   │   ├── index.py              # Home page
│   │   ├── Math/
│   │   │   ├── index.py
│   │   │   └── components/
│   │   │       ├── Calculus.py
│   │   │       ├── DataStructures.py
│   │   │       ├── LinearAlgebraComponents.py
│   │   │       ├── MathFundamentals.py
│   │   │       ├── MatrixOperations.py
│   │   │       └── Probability.py
│   │   ├── UseState/
│   │   │   └── index.py
│   │   ├── Video/
│   │   │   ├── index.py
│   │   │   └── components/
│   │   │       └── Processor.py
│   │   └── VisualizationD/
│   │       ├── index.py
│   │       ├── DataManager.py
│   │       ├── IO.py
│   │       ├── components/
│   │       └── data/
│   │           ├── books.csv
│   │           ├── books.json
│   │           ├── data.txt
│   │           └── output.txt
│   ├── SharedKernel/
│   │   ├── components/
│   │   │   ├── Button.py
│   │   │   ├── Form.py
│   │   │   └── Input.py
│   │   ├── core/
│   │   ├── hooks/
│   │   │   └── hooks.py
│   │   └── math/
│   │       ├── LinearAlgebra.py
│   │       └── Probability.py
│   └── tests/
│       └── test_math.py
├── scripts/                      # Shell scripts (see [scripts/README.md](scripts/README.md))
│   ├── core.sh                   # Shared utilities (colors, logging, spinner)
│   ├── menu.sh                   # FZF interactive menu
│   ├── server.sh                 # Server lifecycle (Granian, Streamlit, kill)
│   ├── packages.sh               # Python package management
│   ├── env.sh                    # Environment setup (venv, uv, yq)
│   └── convert.sh                # DBML/SQL conversion, cleanup utilities
├── specs/                        # Specifications
├── data_sample/                  # Sample data
├── requirements/
│   └── learning-curve.md
├── .agents/
│   ├── Plans/
│   │   └── video_page.md
│   └── Skills/
│       ├── Roll-Dice/
│       │   └── SKILL.html
│       ├── Validate/
│       ├── Write-Plans/
│       │   └── SKILL.md
│       └── Write-Tests/
│           └── SKILL.md
├── .streamlit/
│   └── config.toml
├── requirements.txt              # Python dependencies
├── package.json                  # Node dependencies
├── bun.lock
├── script.sh
└── .gitignore
```

## Architecture Overview

### Backend (FastAPI)

The backend uses **FastAPI** with a modular feature-based architecture:

```
Request → Router → Controller → Service → Repository → Database
```

**Key Components:**
- **Features/**: Self-contained feature modules with controllers, services, repositories, and DTOs
  - `Attachment_Module/`: File upload and attachment handling
  - `Auton_Module/`: AI services (LLM, Vision, Detection, Agents, RAG)
  - `Shared_Module/`: Shared features (Blog, etc.)
  - `VoxelStream_Module/`: Real-time computer vision (face detection, expression analysis)
- **Domain/**: Base domain entities (DDD pattern)
- **SharedKernel/**: Cross-cutting concerns shared across all features
- **Config/**: Centralized configuration management via YAML
- **database/**: SQL schema and DBML definitions

**SharedKernel Base:**
| Module | Purpose |
|--------|---------|
| `APIResponse.py` | Standardized API response format |
| `Decorators.py` | Controller registration decorator |
| `Container.py` | Dependency injection container |
| `Logger.py` | Unified logging |
| `Metrics.py` | Performance monitoring |

**Persistence Layer:**
| Module | Purpose |
|--------|---------|
| `Database.py` | SQL database (PostgreSQL via SQLAlchemy) |
| `RedisManager.py` | Caching and session storage |
| `Neo4jManager.py` | Graph database |
| `Neo4jVectorManager.py` | Vector embeddings storage |
| `CrudRepository.py` | Generic CRUD operations |

### Frontend (Streamlit)

The frontend uses **Streamlit** with a page-based navigation system:

**Page Discovery System (`app.py`):**
```
pages/index.py              → "/" (root page)
pages/Math/index.py         → "Math"
pages/VisualizationD/index.py → "VisualizationD"
pages/Video/index.py        → "Video"
pages/UseState/index.py     → "UseState"
```

Each page directory contains:
- `index.py`: Page entry point with `render()` function
- `components/`: Reusable components for that page

**SharedKernel (Frontend):**
- `components/`: Reusable UI components (Button, Form, Input)
- `hooks/`: State management hooks mimicking React patterns
- `math/`: Mathematical utilities for visualization

### Computer Vision

The project includes real-time computer vision capabilities via `VoxelStream_Module/`:
- Face detection and landmark tracking using MediaPipe
- Expression analysis via finite state machine (`ExpressionFSM.py`)
- Frame capture, extraction, and rendering pipeline

## Flows

### Frontend Flow
1. User visits the Streamlit app
2. `app.py` discovers all pages via `discover_pages()`
3. Pages are registered with Streamlit's navigation system
4. Each page's `render()` function displays content
5. Pages can use SharedKernel components and hooks

### Backend Flow
1. Client sends HTTP request to FastAPI
2. Router matches endpoint to Controller
3. Controller processes request via Services
4. Services interact with Repositories
5. Repositories perform database operations
6. Response flows back through the chain

### Communication
- Frontend communicates with Backend via HTTP/REST APIs
- API documentation available at `/scalar` endpoint
- Standardized response format via `APIResponse.py`

## Running the Application

### Backend
```bash
cd src
python lain.py
# API available at http://localhost:8000/scalar
```

### Frontend
```bash
cd frontend
streamlit run app.py
# App available at http://localhost:8501
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | FastAPI |
| Frontend Framework | Streamlit |
| SQL Database | PostgreSQL (via SQLAlchemy) |
| Cache | Redis |
| Graph Database | Neo4j |
| Vector Store | Neo4j + Vector |
| Computer Vision | MediaPipe (Face Mesh, Expression Analysis) |
| API Docs | Scalar |
| Server | Granian (ASGI) |
