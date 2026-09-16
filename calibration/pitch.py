"""Pixel-to-metre conversion utilities."""

from typing import Optional, Tuple


def estimate_pixels_per_meter(frame_width: int, pitch_width_m: float = 68.0) -> float:
    """Estimate scale for a frame showing the full pitch width."""
    if frame_width <= 0 or pitch_width_m <= 0:
        raise ValueError("frame_width and pitch_width_m must be positive")
    return frame_width / pitch_width_m


def image_to_pitch(point: Tuple[float, float], homography: Optional[object] = None) -> Tuple[float, float]:
    """Map a point with an optional 3x3 homography, without requiring OpenCV."""
    if homography is None:
        return point
    x, y = point
    denominator = homography[2][0] * x + homography[2][1] * y + homography[2][2]
    if denominator == 0:
        raise ValueError("homography maps point to infinity")
    return ((homography[0][0] * x + homography[0][1] * y + homography[0][2]) / denominator,
            (homography[1][0] * x + homography[1][1] * y + homography[1][2]) / denominator)
