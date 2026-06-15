from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.SharedKernel.persistence.Database import DatabaseSessionConfig
from src.SharedKernel.base.Decorators import Controller
from src.SharedKernel.base.Container import Container
from src.Infrastructure.Config import Config
from pydantic import BaseModel
from src.SharedKernel.persistence.RedisManager import RedisManager

config = Config().load_env_yaml()

@Controller
class SharedController:
    def __init__(self, 
        container: Container, 
        db_config: DatabaseSessionConfig, 
        redis_manager: RedisManager
    ) -> None:
        self.tags = ["Shared"]
        self.prefix = "/api/v1/shared"
        self.router = APIRouter(tags=self.tags, prefix=self.prefix)
        self.session = db_config.session
        self.redis_manager = redis_manager

    def init_routes(self) -> None:
        @self.router.get("/hello")
        def hello_word():
            return {"message": "Hello World"}

    def checking_health_routes(self) -> None:
        @self.router.get("/health/database", description="Check database connection")
        async def check_db_health():
            try:
                result = await self.session.execute(text("SELECT 1"))
                row = result.scalar()

                return {
                    "status": "HEALTHY"
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.get("/health/redis", description="Check Redis connection")
        async def check_redis_health():
            try:
                redis_client = self.redis_manager.get_redis_client()
                redis_client.ping()
                
                return {
                    "status": "HEALTHY",
                    "url": config.redis.url
                }
            except Exception as e:
                return {
                    "status": "UNHEALTHY",
                    "error": str(e),
                    "url": config.redis.url
                }
        
    def register(self, app: FastAPI) -> None:
        self.init_routes()
        self.checking_health_routes()
        app.include_router(self.router)