"""End-to-end video processing orchestration."""

from pathlib import Path
from typing import Callable, Optional

import config
from analytics.tracking import CentroidTracker
from team.assignment import assign_team
from visualization.overlay import draw_tracks


def process_video(video_file: str, output_path: str, progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
    """Detect, track, annotate, and write a football video."""
    try:
        import cv2
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError("Video processing requires opencv-python and ultralytics. Install requirements.txt first.") from exc
    source = Path(video_file)
    if not source.is_file():
        raise FileNotFoundError(f"Input video does not exist: {source}")
    capture = cv2.VideoCapture(str(source))
    if not capture.isOpened():
        raise ValueError(f"OpenCV could not open video: {source}")
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS) or config.DEFAULT_FPS
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        capture.release()
        raise ValueError(f"Could not create output video: {output_path}")
    model = YOLO(config.MODEL_PATH)
    tracker = CentroidTracker(max_distance=config.MAX_TRACK_DISTANCE)
    frame_number = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            detections = []
            result = model(frame, conf=config.CONFIDENCE_THRESHOLD, classes=[0], verbose=False)[0]
            for box in result.boxes.xyxy.cpu().tolist():
                left, top, right, bottom = map(int, box)
                center = ((left + right) / 2, bottom)
                crop = frame[max(top, 0):max(bottom, top + 1), max(left, 0):max(right, left + 1)]
                mean_color = crop.mean(axis=(0, 1))[::-1] if crop.size else ()
                detections.append((center, assign_team(mean_color)))
            tracks = tracker.update(detections, fps, config.PIXELS_PER_METER)
            writer.write(draw_tracks(frame, tracks))
            frame_number += 1
            if progress_callback:
                progress_callback(frame_number, total)
    finally:
        capture.release()
        writer.release()
    return output_path
