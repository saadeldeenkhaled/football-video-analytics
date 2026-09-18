import cv2
import numpy as np
from sklearn.cluster import KMeans


class TeamClassifier:
    def __init__(self, refresh_interval=30, min_samples=20):
        self.team_ids = {}
        self.team_colors = None
        self.refresh_interval = max(1, int(refresh_interval))
        self.min_samples = max(2, int(min_samples))
        self.last_fit_frame = -self.refresh_interval

    def fit_teams(self, frame, player_boxes, player_ids, frame_idx=0, force=False):
        if not force and frame_idx - self.last_fit_frame < self.refresh_interval:
            return False

        samples = []
        for bbox in player_boxes:
            samples.extend(self._jersey_pixels(frame, bbox))
        if len(samples) < self.min_samples:
            return False

        sample_array = np.asarray(samples, dtype=np.float32)
        model = KMeans(n_clusters=2, n_init=10, random_state=0)
        model.fit(sample_array)
        new_colors = model.cluster_centers_
        if self.team_colors is not None:
            direct_distance = np.linalg.norm(self.team_colors - new_colors, axis=1).sum()
            swapped_distance = np.linalg.norm(self.team_colors - new_colors[::-1], axis=1).sum()
            if swapped_distance < direct_distance:
                new_colors = new_colors[::-1]
        self.team_colors = new_colors
        self.last_fit_frame = frame_idx
        self.team_ids.clear()
        return True

    def get_team(self, frame, bbox, track_id):
        track_id = int(track_id)
        if self.team_colors is None:
            return "unknown"
        if track_id in self.team_ids:
            return self.team_ids[track_id]
        jersey_color = self._jersey_color(frame, bbox)
        if jersey_color is None:
            return self.team_ids.get(track_id, "unknown")
        distances = np.linalg.norm(self.team_colors - jersey_color, axis=1)
        team_id = int(np.argmin(distances))
        self.team_ids[track_id] = team_id
        return self.team_ids[track_id]

    @staticmethod
    def _crop(frame, bbox):
        left, top, right, bottom = map(int, bbox)
        height, width = frame.shape[:2]
        left = max(0, min(left, width))
        right = max(left + 1, min(right, width))
        top = max(0, min(top, height))
        bottom = max(top + 1, min(bottom, height))
        jersey_bottom = top + int((bottom - top) * 0.65)
        jersey_top = top + int((bottom - top) * 0.15)
        return frame[jersey_top:max(jersey_top + 1, jersey_bottom), left:right]

    @classmethod
    def _jersey_pixels(cls, frame, bbox):
        crop = cls._crop(frame, bbox)
        if crop.size == 0:
            return []
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        saturation = hsv[:, :, 1]
        hue = hsv[:, :, 0]
        mask = (saturation > 45) & ~((hue >= 35) & (hue <= 95) & (saturation > 35))
        pixels = crop[mask]
        if len(pixels) == 0:
            return []
        pixels = pixels[:, ::-1]
        return pixels[::max(1, len(pixels) // 80)].tolist()

    @classmethod
    def _jersey_color(cls, frame, bbox):
        pixels = cls._jersey_pixels(frame, bbox)
        if not pixels:
            return None
        return np.mean(pixels, axis=0)
