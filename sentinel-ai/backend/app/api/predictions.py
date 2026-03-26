import os
import time
import uuid
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user, require_role
from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_db
from app.core.security import decode_access_token
from app.models.camera import Camera, CameraStatus
from app.models.operator import Operator
from app.models.user import User
from app.schemas.prediction import (
    CameraCreateRequest,
    CameraResponse,
    CameraStreams,
    CameraUpdateRequest,
    ModelInfo,
)


router = APIRouter(prefix="/api/v1", tags=["Predictions"])
MJPEG_FPS = max(1, settings.MJPEG_FPS)
MJPEG_JPEG_QUALITY = max(40, min(95, settings.MJPEG_JPEG_QUALITY))
MJPEG_MAX_READ_FAILURES = max(1, settings.MJPEG_MAX_READ_FAILURES)
MJPEG_RECONNECT_DELAY_SECONDS = settings.MJPEG_RECONNECT_DELAY_SECONDS


def _normalize_rtsp_url(rtsp_url: str) -> str:
    """
    Replace localhost-like hosts with the configured Docker alias so containers can resolve it.
    """
    parsed = urlparse(rtsp_url)
    if parsed.scheme.lower() != "rtsp":
        return rtsp_url

    if parsed.hostname not in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return rtsp_url

    docker_rtsp_host = settings.RTSP_HOST_ALIAS
    auth_prefix = ""

    if parsed.username:
        auth_prefix = parsed.username
        if parsed.password:
            auth_prefix += f":{parsed.password}"
        auth_prefix += "@"

    port_suffix = f":{parsed.port}" if parsed.port else ""
    netloc = f"{auth_prefix}{docker_rtsp_host}{port_suffix}"

    return urlunparse(
        (
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def _derive_yolo_rtsp_url(raw_rtsp_url: str) -> str:
    """
    Convert any stream path into the YOLO output path.
    """
    parsed = urlparse(raw_rtsp_url)
    path_parts = [part for part in parsed.path.split("/") if part]

    if path_parts:
        path_parts[-1] = "yolo.stream"
        new_path = "/" + "/".join(path_parts)
    else:
        new_path = "/yolo.stream"

    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            new_path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )


def _open_rtsp_capture(cv2_module, target_rtsp_url: str):
    # Prefer TCP RTSP for stability through Docker networking.
    ffmpeg_capture_opts = settings.OPENCV_FFMPEG_CAPTURE_OPTIONS
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = ffmpeg_capture_opts

    capture = cv2_module.VideoCapture(target_rtsp_url, cv2_module.CAP_FFMPEG)
    if not capture.isOpened():
        capture.release()
        capture = cv2_module.VideoCapture(target_rtsp_url)

    capture.set(cv2_module.CAP_PROP_BUFFERSIZE, 1)
    return capture


def _validate_stream_token(
    stream_token: str | None,
    authorization_header: str | None,
) -> None:
    """
    MJPEG requests from <img> cannot send custom headers in frontend code,
    so we allow either Authorization bearer header or a token query param.
    """
    token = None

    if authorization_header and authorization_header.lower().startswith("bearer "):
        token = authorization_header.split(" ", 1)[1].strip()
    elif stream_token:
        token = stream_token.strip()

    if not token or decode_access_token(token) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing stream token",
        )


def _camera_to_response(camera: Camera, request: Request) -> CameraResponse:
    raw_rtsp_url = _normalize_rtsp_url(camera.rtsp_url)
    yolo_rtsp_url = _derive_yolo_rtsp_url(raw_rtsp_url)
    base_url = str(request.base_url).rstrip("/")

    streams = CameraStreams(
        raw_rtsp_url=raw_rtsp_url,
        yolo_rtsp_url=yolo_rtsp_url,
        raw_mjpeg_url=f"{base_url}/api/v1/cameras/{camera.id}/mjpeg?stream=raw",
        yolo_mjpeg_url=f"{base_url}/api/v1/cameras/{camera.id}/mjpeg?stream=yolo",
    )

    return CameraResponse(
        id=camera.id,
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        location=camera.location,
        status=camera.status.value,
        operator_id=camera.operator_id,
        streams=streams,
    )


@router.get(
    "/models",
    response_model=list[ModelInfo],
    dependencies=[Depends(require_role("admin"))],
)
async def list_models(current_user: User = Depends(get_current_active_user)):
    """
    Simple model list used by dashboard.
    """
    _ = current_user
    return [
        ModelInfo(name="yolov8-violence-detector", latest_version="v1"),
    ]


@router.get("/cameras", response_model=list[CameraResponse])
async def list_cameras(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user
    result = await db.execute(select(Camera).order_by(Camera.name.asc()))
    cameras = result.scalars().all()
    return [_camera_to_response(camera, request) for camera in cameras]


@router.post(
    "/cameras",
    response_model=CameraResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
async def create_camera(
    camera_data: CameraCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user

    if camera_data.operator_id:
        operator_result = await db.execute(
            select(Operator).where(Operator.id == camera_data.operator_id)
        )
        operator = operator_result.scalar_one_or_none()
        if operator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator not found",
            )

    camera = Camera(
        name=camera_data.name,
        rtsp_url=camera_data.rtsp_url,
        location=camera_data.location,
        status=CameraStatus(camera_data.status),
        operator_id=camera_data.operator_id,
    )
    db.add(camera)
    await db.flush()
    await db.refresh(camera)

    return _camera_to_response(camera, request)


@router.patch(
    "/cameras/{camera_id}",
    response_model=CameraResponse,
    dependencies=[Depends(require_role("admin"))],
)
async def update_camera(
    camera_id: uuid.UUID,
    camera_data: CameraUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user

    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    updates = camera_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    if "operator_id" in updates and updates["operator_id"] is not None:
        operator_result = await db.execute(
            select(Operator).where(Operator.id == updates["operator_id"])
        )
        operator = operator_result.scalar_one_or_none()
        if operator is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator not found",
            )

    if "name" in updates:
        camera.name = updates["name"]
    if "rtsp_url" in updates:
        camera.rtsp_url = updates["rtsp_url"]
    if "location" in updates:
        camera.location = updates["location"]
    if "status" in updates and updates["status"] is not None:
        camera.status = CameraStatus(updates["status"])
    if "operator_id" in updates:
        camera.operator_id = updates["operator_id"]

    await db.flush()
    await db.refresh(camera)

    return _camera_to_response(camera, request)


@router.delete(
    "/cameras/{camera_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role("admin"))],
)
async def delete_camera(
    camera_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    _ = current_user

    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    await db.delete(camera)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/cameras/{camera_id}/mjpeg")
async def stream_camera_mjpeg(
    camera_id: uuid.UUID,
    stream: str = Query("raw", pattern="^(raw|yolo)$"),
    token: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
):
    try:
        import cv2  # Imported lazily so API boots even if OpenCV is missing.
    except ImportError as import_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="opencv-python-headless is not installed in backend container",
        ) from import_error

    _validate_stream_token(token, authorization)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Camera).where(Camera.id == camera_id))
        camera = result.scalar_one_or_none()

    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    raw_rtsp_url = _normalize_rtsp_url(camera.rtsp_url)
    target_rtsp_url = raw_rtsp_url if stream == "raw" else _derive_yolo_rtsp_url(raw_rtsp_url)

    def frame_generator():
        capture = None
        read_failures = 0
        frame_interval = 1.0 / MJPEG_FPS
        next_frame_ts = time.perf_counter()

        try:
            while True:
                if capture is None or not capture.isOpened():
                    capture = _open_rtsp_capture(cv2, target_rtsp_url)
                    if not capture.isOpened():
                        if capture is not None:
                            capture.release()
                        capture = None
                        time.sleep(max(0.05, MJPEG_RECONNECT_DELAY_SECONDS))
                        continue

                is_ok, frame = capture.read()
                if not is_ok:
                    read_failures += 1
                    if read_failures >= MJPEG_MAX_READ_FAILURES:
                        capture.release()
                        capture = None
                        read_failures = 0
                    time.sleep(max(0.02, MJPEG_RECONNECT_DELAY_SECONDS))
                    continue 

                read_failures = 0
                encoded_ok, buffer = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), MJPEG_JPEG_QUALITY],
                )
                if not encoded_ok:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
                )

                next_frame_ts += frame_interval
                sleep_time = next_frame_ts - time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_frame_ts = time.perf_counter()
        finally:
            if capture is not None:
                capture.release()

    return StreamingResponse(
        frame_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Connection": "keep-alive",
        },
    )
