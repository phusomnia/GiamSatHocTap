# from fastapi import APIRouter, HTTPException, UploadFile, status
# from fastapi.responses import FileResponse
# from src.SharedKernel.base.APIResponse import APIResponse
# from src.SharedKernel.base.Decorators import Controller
# from src.SharedKernel.base.Container import Container
# from src.Features.Attachment_Module.AttachmentService import AttachmentService
# from src.Domain.base_entities import Attachments
# import uuid
# from datetime import datetime
# import os
# from typing import List

# @Controller
# class AttachmentController:
#     def __init__(self, container: Container, attachment_service: AttachmentService) -> None:
#         self.tags = ["Attachment"]
#         self.prefix = "/api/v1/attachments"
#         self.router = APIRouter(tags=self.tags, prefix=self.prefix)
#         self.attachment_service = attachment_service

#     def register(self, app) -> None:
#         @self.router.get("/", description="List all attachments")
#         async def list_attachments():
#             return await self.attachment_service.list_attachments()

#         @self.router.get("/{id}", description="Get attachment by id")
#         async def get_attachment_by_id(id: str):
#             result = await self.attachment_service.get_attchment_by_id(id)

#             return FileResponse(
#                 path=result["file_path"],
#                 media_type=result["mime_type"]
#             )

#         @self.router.post("/", description="Upload attachment")
#         async def upload_attachment(
#             files: List[UploadFile]
#         ):
#             result = await self.attachment_service.upload_attachment(files)

#             return APIResponse(
#                 status_code=status.HTTP_200_OK,
#                 message="Upload attachment sucessfully",
#                 result=result
#             )

#         @self.router.put("/{id}", description="Update attachment")
#         async def update_attachment(id: str, attachment: Attachments):
#             await self.attachment_service.update_attachment(id, attachment)

#             return APIResponse(
#                 status_code=status.HTTP_200_OK,
#                 message="Update attachment sucessfully"
#             )

#         @self.router.delete("/{id}", description="Delete attachment")
#         async def delete_attachment(id: str):
#             await self.attachment_service.delete_attachment(id)

#             return APIResponse(
#                 status_code=status.HTTP_200_OK,
#                 message="Delete attachment sucessfully"
#             )
#         app.include_router(self.router)