from typing import Literal, Optional
import uuid
from pydantic import BaseModel, Field


class CameraStreams(BaseModel):
    raw_rtsp_url: str
    yolo_rtsp_url: str
    raw_mjpeg_url: str
    yolo_mjpeg_url: str


class CameraResponse(BaseModel):
    id: uuid.UUID
    name: str
    rtsp_url: str
    location: str
    status: str
    operator_id: Optional[uuid.UUID] = None
    streams: CameraStreams


class ModelInfo(BaseModel):
    name: str
    latest_version: Optional[str] = None


class CameraCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    rtsp_url: str = Field(..., min_length=10, max_length=500)
    location: str = Field(..., min_length=2, max_length=255)
    status: Literal["online", "offline", "maintenance", "error"] = "offline"
    operator_id: Optional[uuid.UUID] = None


class CameraUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    rtsp_url: Optional[str] = Field(default=None, min_length=10, max_length=500)
    location: Optional[str] = Field(default=None, min_length=2, max_length=255)
    status: Optional[Literal["online", "offline", "maintenance", "error"]] = None
    operator_id: Optional[uuid.UUID] = None
