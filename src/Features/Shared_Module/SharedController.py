from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from src.SharedKernel.persistence.Database import DatabaseSessionConfig
from src.SharedKernel.base.Decorators import Controller
from src.SharedKernel.base.Container import Container
from src.config.Config import Config
from pydantic import BaseModel
from sqlalchemy import desc, text
from src.Features.Shared_Module.BlogRepository import BlogRepository, BlogDTO
from src.SharedKernel.persistence.RedisManager import RedisManager

config = Config().load_env_yaml()

class Blog(BaseModel):
    id: str
    name: str

blogs = [
    Blog(id="123", name="a"),
    Blog(id="321", name="b")
]

@Controller
class SharedController:
    def __init__(self, 
        container: Container, 
        db_config: DatabaseSessionConfig, 
        blog_repo: BlogRepository, 
        redis_manager: RedisManager
    ) -> None:
        self.tags = ["Shared"]
        self.prefix = "/api/v1/shared"
        self.router = APIRouter(tags=self.tags, prefix=self.prefix)
        self.session = db_config.session
        self.blog_repo = blog_repo
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

    def mock_crud(self) -> None:
        @self.router.get("/blogs", description="Get all blogs")
        def get_blog():
            return blogs

        @self.router.get("/blog/{id}", description="Get blog by id")
        def get_blog_by_id(id: str):
            for blog in blogs:
                if blog.id == id:
                    return blog
            return {"message": "Blog not found"}

        @self.router.post("/blog", description="Create blog")
        async def create_blog(req: Blog):
            blog_dto = BlogDTO(id=req.id, name=req.name)
            created_blog = await self.blog_repo.save(blog_dto)
            return {
                "message": "Blog created",
                "data": created_blog
            }

        @self.router.put("/blog/{id}", description="Update blog")
        async def update_blog(id: str, req: Blog):
            blog_dto = BlogDTO(id=id, name=req.name)
            updated_blog = await self.blog_repo.update(blog_dto)
            if updated_blog:
                return updated_blog
            return {"message": "Blog not found"}
        
    def register(self, app: FastAPI) -> None:
        self.init_routes()
        self.checking_health_routes()
        self.mock_crud()
        app.include_router(self.router)