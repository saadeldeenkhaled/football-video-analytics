"""OpenCV overlay rendering kept behind a lazy dependency boundary."""

from visualization.renderer import GraphicsRenderer


def draw_tracks(frame, tracks):
    for track in tracks:
        bbox = track.bbox
        if bbox is None:
            x, y = track.centroid
            bbox = (x - 10, y - 20, x + 10, y)
        GraphicsRenderer.draw_player_annotation(
            frame,
            bbox,
            track.track_id,
            track.team,
            track.speed_mps * 3.6,
            track.distance_m,
        )
    return frame
