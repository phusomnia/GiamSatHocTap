from fastapi import FastAPI, APIRouter, status, Query
from src.SharedKernel.base.Decorators import Controller
from src.SharedKernel.base.Container import Container
from src.SharedKernel.base.APIResponse import APIResponse
from src.Features.VoxelStream_Module.handlers.VoxelStreamProc import VoxelStreamProc
from src.SharedKernel.persistence.StudySessionRepo import StudySessionRepo
from src.Features.VoxelStream_Module.dto.VoxelStreamDTO import (
    SessionResponse,
    StatsSummary,
    DailyScore,
    SessionStats,
)

@Controller
class VoxelStreamController:
    def __init__(self, container: Container) -> None:
        self.tags = ["VoxelStream"]
        self.container = container
        self.voxel_stream_proc: VoxelStreamProc = (
            self.container.resolve(VoxelStreamProc)
        )
        self.db = StudySessionRepo()
        self.router = APIRouter(
            prefix="/api/v1/voxels_stream", tags=self.tags
        )

    def init_routes(self) -> None:
        @self.router.post("/run", description="Start voxel stream processing")
        def run_voxel_stream():
            self.voxel_stream_proc.run_tracker()
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="Voxel stream processing completed",
            )

        @self.router.get(
            "/sessions",
            response_model=APIResponse[list[SessionResponse]],
            description="Get all study sessions",
        )
        def get_sessions():
            sessions = self.db.get_all()
            return APIResponse(
                status_code=status.HTTP_200_OK,
                result=[SessionResponse(**s.__dict__) for s in sessions],
            )

        @self.router.get(
            "/sessions/stats",
            response_model=APIResponse[StatsSummary],
            description="Get summary statistics",
        )
        def get_stats():
            stats = self.db.get_stats_summary()
            return APIResponse(
                status_code=status.HTTP_200_OK,
                result=StatsSummary(**stats),
            )

        @self.router.get(
            "/sessions/daily",
            response_model=APIResponse[list[DailyScore]],
            description="Get daily focus scores for charts",
        )
        def get_daily_scores(days: int = Query(default=7, ge=1, le=90)):
            scores = self.db.get_daily_scores(days)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                result=[DailyScore(**s) for s in scores],
            )

        @self.router.get(
            "/sessions/recent",
            response_model=APIResponse[list[SessionResponse]],
            description="Get recent study sessions",
        )
        def get_recent_sessions(days: int = Query(default=7, ge=1, le=90)):
            sessions = self.db.get_recent(days)
            return APIResponse(
                status_code=status.HTTP_200_OK,
                result=[SessionResponse(**s.__dict__) for s in sessions],
            )

    def register(self, app: FastAPI) -> None:
        self.init_routes()
        app.include_router(self.router)