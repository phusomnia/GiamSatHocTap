from datetime import datetime
from pydantic import BaseModel


class AttachmentDTO(BaseModel):
    id: str
    filename: str
    file_url: str
    file_size: int
    mime_type: str
    created_at: datetime
    
