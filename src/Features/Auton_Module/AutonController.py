# from email import message
# from enum import Enum
# import base64
# import io
# import numpy as np
# from fastapi.responses import StreamingResponse
# from src.Features.Auton_Module import AIFacade
# from src.SharedKernel.base.APIResponse import APIResponse
# from src.SharedKernel.base.Decorators import Controller
# from src.SharedKernel.base.Container import Container
# from fastapi import APIRouter, Body, FastAPI, Depends, status, UploadFile, Form, File
# from pydantic import BaseModel, Field
# from typing import List
# from .AIFacade import AIFacade
# from src.SharedKernel.base import Metrics

# class ChatRequest(BaseModel):
#     query: str = Field(default="")

# class FileRequest:
#     def __init__(
#         self,
#         files: List[UploadFile] = File(...)
#     ):
#         self.files = files

# @Controller
# class AutonController:
#     def __init__(self, container: Container) -> None:
#         self.tags = ["Auton"]
#         self.container = container
#         self.ai_facade: AIFacade = self.container.resolve(AIFacade)
#         self.router = APIRouter(prefix="/api/v1/auton", tags=self.tags)
#         self.model = None

#     def _get_model(self):
#         if self.model is None:
#             self.model = YOLO("yolov8n.pt")
#         return self.model

#     def vision_routes(self) -> None:
#         @self.router.get("/vision/camera", description="Mo camera nhe may ku")
#         async def vision_camera():
#             return StreamingResponse(
#                 self.ai_facade.VISION.open_camera(),
#                 media_type="multipart/x-mixed-replace; boundary=frame"
#             )
        
#         @self.router.get("/vision/demo", description="Vision YOLO demo")
#         async def vision_demo():
#             return StreamingResponse(
#                 self.ai_facade.VISION.demo_yolo_pipeline(),
#                 media_type="multipart/x-mixed-replace; boundary=frame"
#             )
    
#     def llm_routes(self) -> None:
#         @self.router.post("/query", description="Query nhe may ku")
#         @Metrics.time_function
#         async def query(req: ChatRequest):
#             result = self.ai_facade.LLM.sprompt(req.query)

#             return StreamingResponse(
#                 result,
#                 media_type="text/event-stream"
#             )
#         ...

#         @self.router.post("/index-rag-docs", description="Load web nhe may ku")
#         def indexing_rag_docs(
#             req: ChatRequest = Depends(),
#             file_req: FileRequest = Depends()
#         ):
#             self.ai_facade.LLM.naive_rag.indexing(file_req.files)
#         ...

#         @self.router.post("/rag-agumenting", description="Retrieve nhe may ki")
#         def rag_agumenting(
#             req: ChatRequest = Body()
#         ):
#             result = self.ai_facade.LLM.naive_rag.augmenting(
#                 "", 
#                 req.query
#             )

#             return StreamingResponse(
#                 result,
#                 media_type="text/event-stream"
#             )
#         ...

#         @self.router.post("/index-graph-docs", description="Load web nhe may ku")
#         def indexing_graph_docs(
#             req: ChatRequest = Depends(),
#             file_req: FileRequest = Depends()
#         ):
#             self.ai_facade.LLM.graph_rag.indexing()
#         ...

#         @self.router.post("/rag-agumenting", description="Retrieve nhe may ku")
#         def graph_rag_agumenting(
#             req: ChatRequest = Body()
#         ):
#             result = self.ai_facade.LLM.graph_rag.retrieve()

#             return StreamingResponse(
#                 result,
#                 media_type="text/event-stream"
#             )

#     def register(self, app: FastAPI) -> None:
#        self.vision_routes()
#        self.llm_routes()
#        app.include_router(self.router)