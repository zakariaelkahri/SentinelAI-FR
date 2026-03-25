from typing import Optional
import uuid
from pydantic import BaseModel


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
