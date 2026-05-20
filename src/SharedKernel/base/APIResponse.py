from typing import Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):   
    message: str = "success"
    result: Optional[T] = None
    status_code: int = 200
        
        