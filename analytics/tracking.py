"""Small, dependency-light centroid tracker and metric accumulator."""

from dataclasses import dataclass, field
from math import hypot
from typing import Dict, Iterable, List, Optional, Tuple, Union

Point = Tuple[float, float]
BoundingBox = Tuple[float, float, float, float]
Detection = Union[Tuple[Point, str], Tuple[Point, str, BoundingBox]]


@dataclass
class Track:
    track_id: int
    centroid: Point
    team: str = "unknown"
    bbox: Optional[BoundingBox] = None
    distance_m: float = 0.0
    speed_mps: float = 0.0
    missed_frames: int = 0


@dataclass
class CentroidTracker:
    max_distance: float = 80.0
    max_missed_frames: int = 20
    _next_id: int = 1
    tracks: Dict[int, Track] = field(default_factory=dict)

    def update(self, detections: Iterable[Detection], fps: float, pixels_per_meter: float) -> List[Track]:
        candidates = list(detections)
        unmatched = set(self.tracks)
        updated: Dict[int, Track] = {}
        for detection in candidates:
            centroid, team = detection[:2]
            bbox = detection[2] if len(detection) > 2 else None
            best_id = None
            best_distance = self.max_distance
            for track_id in unmatched:
                distance = hypot(centroid[0] - self.tracks[track_id].centroid[0], centroid[1] - self.tracks[track_id].centroid[1])
                if distance < best_distance:
                    best_id, best_distance = track_id, distance
            if best_id is None:
                best_id = self._next_id
                self._next_id += 1
                track = Track(best_id, centroid, team=team, bbox=bbox)
            else:
                track = self.tracks[best_id]
                track.distance_m += best_distance / pixels_per_meter
                track.speed_mps = (best_distance / pixels_per_meter) * max(fps, 1.0)
                track.centroid = centroid
                track.team = team if team != "unknown" else track.team
                track.bbox = bbox
                track.missed_frames = 0
                unmatched.remove(best_id)
            updated[best_id] = track
        for track_id in unmatched:
            track = self.tracks[track_id]
            track.missed_frames += 1
            if track.missed_frames <= self.max_missed_frames:
                updated[track_id] = track
        self.tracks = updated
        return list(updated.values())
