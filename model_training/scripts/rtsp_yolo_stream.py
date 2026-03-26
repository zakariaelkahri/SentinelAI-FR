import os
import subprocess
import time

import cv2
from ultralytics import YOLO


MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "/workspace/runs/detect/runs/yolo8m_violence_detection/weights/best.pt",
)
INPUT_RTSP_URL = os.getenv("INPUT_RTSP_URL", "rtsp://mediamtx:8554/live.stream")
OUTPUT_RTSP_URL = os.getenv("OUTPUT_RTSP_URL", "rtsp://mediamtx:8554/yolo.stream")
RTSP_TRANSPORT = os.getenv("RTSP_TRANSPORT", "tcp")
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "640"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "640"))
FPS = int(os.getenv("FPS", "12"))
OUTPUT_ENCODER = os.getenv("OUTPUT_ENCODER", "auto")
PROCESS_EVERY_NTH_FRAME = max(1, int(os.getenv("PROCESS_EVERY_NTH_FRAME", "2")))
MAX_READ_FAILURES = max(1, int(os.getenv("MAX_READ_FAILURES", "30")))
RECONNECT_DELAY_SECONDS = max(1, int(os.getenv("RECONNECT_DELAY_SECONDS", "2")))


def get_available_encoders() -> set[str]:
    try:
        result = subprocess.run(
            ["ffmpeg", "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return set()

    encoders = set()
    encoder_text = "\n".join([result.stdout, result.stderr])
    for line in encoder_text.splitlines():
        line = line.strip()
        if not line or line.startswith("-") or line.startswith("Encoders:"):
            continue

        parts = line.split()
        if len(parts) >= 2:
            encoders.add(parts[1])

    return encoders


def resolve_encoder() -> str:
    if OUTPUT_ENCODER != "auto":
        return OUTPUT_ENCODER

    available_encoders = get_available_encoders()
    for candidate in ("libx264", "mpeg4"):
        if candidate in available_encoders:
            return candidate

    return "mpeg4"


def start_ffmpeg_process(encoder: str) -> subprocess.Popen:
    ffmpeg_cmd = [
        "ffmpeg",
        "-loglevel",
        "warning",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "bgr24",
        "-s",
        f"{FRAME_WIDTH}x{FRAME_HEIGHT}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-an",
    ]

    if encoder == "libx264":
        ffmpeg_cmd.extend(
            [
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-tune",
                "zerolatency",
                "-g",
                str(max(2, FPS * 2)),
            ]
        )
    elif encoder == "mpeg4":
        ffmpeg_cmd.extend(
            [
                "-c:v",
                "mpeg4",
                "-q:v",
                "5",
                "-g",
                str(max(2, FPS * 2)),
            ]
        )
    else:
        ffmpeg_cmd.extend(["-c:v", encoder])

    ffmpeg_cmd.extend(
        [
            "-f",
            "rtsp",
            "-rtsp_transport",
            RTSP_TRANSPORT,
            "-muxdelay",
            "0.05",
            "-muxpreload",
            "0",
            OUTPUT_RTSP_URL,
        ]
    )

    return subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def open_input_capture() -> cv2.VideoCapture:
    capture = cv2.VideoCapture(INPUT_RTSP_URL, cv2.CAP_FFMPEG)
    if not capture.isOpened():
        capture.release()
        capture = cv2.VideoCapture(INPUT_RTSP_URL)

    # Keep the RTSP buffer small to reduce latency and stale frames.
    capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return capture


def run_pipeline() -> None:
    print(f"Loading YOLO model from: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    encoder = resolve_encoder()
    print(f"Using output encoder: {encoder}")
    print("Model loaded. Starting RTSP pipeline...")

    frame_interval = 1.0 / max(1, FPS)

    while True:
        capture = open_input_capture()
        if not capture.isOpened():
            print(
                f"Could not open input stream: {INPUT_RTSP_URL}. "
                f"Retrying in {RECONNECT_DELAY_SECONDS}s..."
            )
            time.sleep(RECONNECT_DELAY_SECONDS)
            continue

        ffmpeg_proc = start_ffmpeg_process(encoder)
        print(f"Streaming YOLO output to: {OUTPUT_RTSP_URL}")
        read_failures = 0
        frame_index = 0
        last_annotated = None
        next_frame_ts = time.perf_counter()

        try:
            while True:
                if ffmpeg_proc.poll() is not None:
                    print("FFmpeg process exited. Restarting pipeline...")
                    break

                ok, frame = capture.read()
                if not ok:
                    read_failures += 1
                    if read_failures >= MAX_READ_FAILURES:
                        print("Input stream disconnected for too long. Reconnecting...")
                        break
                    time.sleep(0.03)
                    continue

                read_failures = 0
                frame_index += 1
                frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

                should_run_inference = (
                    last_annotated is None
                    or PROCESS_EVERY_NTH_FRAME == 1
                    or frame_index % PROCESS_EVERY_NTH_FRAME == 0
                )

                if should_run_inference:
                    try:
                        results = model(frame, verbose=False)
                        last_annotated = results[0].plot()
                    except Exception as infer_error:
                        print(f"Inference error: {infer_error}")
                        continue

                try:
                    if ffmpeg_proc.stdin is None:
                        print("FFmpeg stdin is not available. Restarting...")
                        break
                    ffmpeg_proc.stdin.write(last_annotated.tobytes())
                except BrokenPipeError:
                    print("FFmpeg pipe broken. Restarting FFmpeg process...")
                    break

                # Pace output to the configured FPS for steadier CPU usage.
                next_frame_ts += frame_interval
                sleep_time = next_frame_ts - time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_frame_ts = time.perf_counter()
        finally:
            capture.release()
            if ffmpeg_proc.stdin:
                ffmpeg_proc.stdin.close()
            try:
                ffmpeg_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                ffmpeg_proc.kill()
            time.sleep(1)


if __name__ == "__main__":
    run_pipeline()
