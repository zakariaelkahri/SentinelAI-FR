import os
import time
import uuid
from urllib.parse import urlparse, urlunparse

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user
from app.core.database import AsyncSessionLocal, get_db
from app.core.security import decode_access_token
from app.models.camera import Camera
from app.models.user import User
from app.schemas.prediction import CameraResponse, CameraStreams, ModelInfo


router = APIRouter(prefix="/api/v1", tags=["Predictions"])
MJPEG_FPS = max(1, int(os.getenv("MJPEG_FPS", "10")))
MJPEG_JPEG_QUALITY = max(40, min(95, int(os.getenv("MJPEG_JPEG_QUALITY", "75"))))
MJPEG_MAX_READ_FAILURES = max(1, int(os.getenv("MJPEG_MAX_READ_FAILURES", "40")))
MJPEG_RECONNECT_DELAY_SECONDS = float(os.getenv("MJPEG_RECONNECT_DELAY_SECONDS", "0.25"))


def _normalize_rtsp_url(rtsp_url: str) -> str:
    """
    Replace localhost-like hosts with the configured Docker alias so containers can resolve it.
    """
    parsed = urlparse(rtsp_url)
    if parsed.scheme.lower() != "rtsp":
        return rtsp_url

    if parsed.hostname not in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return rtsp_url

    docker_rtsp_host = os.getenv("RTSP_HOST_ALIAS", "mediamtx")
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
    ffmpeg_capture_opts = os.getenv(
        "OPENCV_FFMPEG_CAPTURE_OPTIONS",
        "rtsp_transport;tcp|max_delay;500000|stimeout;5000000",
    )
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


@router.get("/models", response_model=list[ModelInfo])
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
