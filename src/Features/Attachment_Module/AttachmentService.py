import shutil
from typing import Sequence, List
from fastapi import HTTPException, UploadFile, status
from langchain_community.utilities.pebblo import dir_loader
from src.Domain.base_entities import Attachments
from src.Features.Attachment_Module.AttachmentRepository import AttachmentRepository
from src.SharedKernel.base.Container import Service
from src.SharedKernel.base.Logger import Logger
import uuid
import os
from datetime import datetime
from src.infrastructure.Config import Config
import mimetypes

config = Config()
config.load_env_yaml()

@Service
class AttachmentService:
    def __init__(self, attachment_repo: AttachmentRepository, logger: Logger) -> None:
        self.attachment_repo = attachment_repo
        self.logger = logger
        self.upload_dir_path = "src/static/uploads"

    async def list_attachments(self):
        """Get all attachments."""
        self.logger.info("Fetching all attachments")
        attachments = await self.attachment_repo.search_attachment()
        return attachments

    def _get_file_path(self, file_id: str):
        dir_path = os.path.join("src/static/uploads/", file_id)

        if not os.path.exists(dir_path):
            raise HTTPException(
                detail="File directory not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Get first file in directory
        files = os.listdir(dir_path)
        if files:
            return os.path.join(dir_path, files[0])
        
        raise HTTPException(
            detail="No file found in directory",
            status_code=status.HTTP_404_NOT_FOUND
        )

    async def get_attchment_by_id(self, id: str):
        file = await self.attachment_repo.find_by_id(id)
        if not file:
            raise HTTPException(
                detail="File not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        file_path = self._get_file_path(id)
        mime_type = mimetypes.guess_type(file_path)[0]

        return {
            "file_path": file_path,
            "mime_type": mime_type
        }

    async def upload_attachment(self, files: List[UploadFile]) -> None:
        """Upload/save an attachment."""
        attachment_urls = []
        for file in files:
            content = await file.read()
            file_size = len(content)

            new_uuid = uuid.uuid4()
            
            upload_dir = self.upload_dir_path + str(new_uuid)
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, file.filename)

            with open(file_path, "wb") as f:
                f.write(content)

            attachment_entity = Attachments()
            attachment_entity.id = new_uuid
            attachment_entity.filename = file.filename
            attachment_entity.original_name = file.filename
            attachment_entity.file_path = file_path
            attachment_entity.file_size = file_size
            attachment_entity.mime_type = file.content_type or "application/octet-stream"
            attachment_entity.url = "http://{}:{}/{}/{}".format(
                config.app.host,
                config.app.port,
                "api/v1/attchments",
                new_uuid
            )
            attachment_entity.uploaded_at = datetime.now()
            await self.attachment_repo.save(attachment_entity)
            attachment_urls.append(attachment_entity.url)
        return {
            "urls": attachment_urls
        }

    async def delete_attachment(self, id: str) -> None:
        """Delete an attachment by id."""
        self.logger.info(f"Deleting attachment with id: {id}")
        attachment = await self.attachment_repo.find_by_id(id)
        if not attachment:
            raise HTTPException(
                detail="File not found",
                status_code=status.HTTP_404_NOT_FOUND
            )

        upload_dir = self.upload_dir_path + id
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
            self.logger.info("Remove ok")
        
        await self.attachment_repo.delete(attachment)
        
    async def update_attachment(self, id: str, attachment: Attachments) -> dict:
        """Update an attachment by id."""
        self.logger.info(f"Updating attachment with id: {id}")
        existing = await self.attachment_repo.find_by_id(id)
        if not existing:
            return None

        updated = await self.attachment_repo.update(attachment)
        return updated.model_dump()
