from typing import Optional
from pydantic import BaseModel
from src.SharedKernel.persistence.CrudRepository import CrudRepository
from src.SharedKernel.base.Container import Repository

class BlogDTO(BaseModel):
    id: str
    name: str

@Repository
class BlogRepository(CrudRepository[BlogDTO, str]):
    def __init__(self):
        super().__init__()
        self.model = BlogDTO