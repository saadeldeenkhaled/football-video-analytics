"""Simple jersey-colour team assignment."""

from typing import Sequence


def assign_team(mean_color: Sequence[float]) -> str:
    """Return a coarse team label from an RGB mean jersey colour."""
    if len(mean_color) < 3:
        return "unknown"
    red, green, blue = mean_color[:3]
    brightness = (red + green + blue) / 3
    if brightness < 35:
        return "dark"
    if red > blue * 1.25 and red > green * 1.15:
        return "red"
    if blue > red * 1.25 and blue > green * 1.1:
        return "blue"
    return "light" if brightness > 150 else "unknown"
