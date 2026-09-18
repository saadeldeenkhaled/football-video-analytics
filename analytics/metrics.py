from collections import defaultdict
from math import hypot


class AnalyticsEngine:
    def __init__(self, fps):
        self.fps = max(float(fps), 1.0)
        self.players = {}

    def update_player(self, track_id, frame_idx, pitch_x, pitch_y):
        track_id = int(track_id)
        previous = self.players.get(track_id)
        if previous is None:
            self.players[track_id] = {
                "frame": frame_idx,
                "x": float(pitch_x),
                "y": float(pitch_y),
                "distance": 0.0,
                "speed": 0.0,
            }
            return
        elapsed_frames = max(frame_idx - previous["frame"], 1)
        distance = hypot(float(pitch_x) - previous["x"], float(pitch_y) - previous["y"])
        previous["distance"] += distance
        previous["speed"] = distance / (elapsed_frames / self.fps) * 3.6
        previous.update({"frame": frame_idx, "x": float(pitch_x), "y": float(pitch_y)})

    def get_stats(self, track_id):
        stats = self.players.get(int(track_id), defaultdict(float))
        return stats["speed"], stats["distance"]

    def get_distance_to_ball(self, track_id, ball_position):
        player = self.players.get(int(track_id))
        if player is None or ball_position is None:
            return None
        return hypot(player["x"] - float(ball_position[0]), player["y"] - float(ball_position[1]))
