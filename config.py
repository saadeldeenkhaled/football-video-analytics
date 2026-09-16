"""Runtime configuration for the football analytics pipeline."""

import os

CONFIDENCE_THRESHOLD = float(os.getenv("FOOTBALL_CONFIDENCE", "0.35"))
MODEL_PATH = os.getenv("FOOTBALL_MODEL", "yolo11n.pt")
DEFAULT_FPS = 25.0
PIXELS_PER_METER = float(os.getenv("FOOTBALL_PIXELS_PER_METER", "40"))
MAX_TRACK_DISTANCE = float(os.getenv("FOOTBALL_MAX_TRACK_DISTANCE", "80"))
