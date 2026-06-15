from fastapi import FastAPI, APIRouter, status
from src.SharedKernel.base.Decorators import Controller
from src.SharedKernel.base.Container import Container
from src.Features.VoxelStream_Module.handlers.VoxelStreamProc import VoxelStreamProc
from src.SharedKernel.base.APIResponse import APIResponse

@Controller
class VoxelStreamController:
    def __init__(self, container: Container) -> None:
        self.tags = ["VoxelStream"]
        self.container = container
        self.voxel_stream_proc: VoxelStreamProc = self.container.resolve(VoxelStreamProc)
        self.router = APIRouter(prefix="/api/v1/voxels_stream", tags=self.tags)

    def init_routes(self) -> None:
        @self.router.post("/run", description="Start voxel stream processing")
        def run_voxel_stream():
            self.voxel_stream_proc.run_tracker()
            return APIResponse(
                status_code=status.HTTP_200_OK,
                message="Voxel stream processing completed"
            )

    def register(self, app: FastAPI) -> None:
        self.init_routes()
        app.include_router(self.router)