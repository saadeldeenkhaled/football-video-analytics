"""OpenCV overlay rendering kept behind a lazy dependency boundary."""


def draw_tracks(frame, tracks):
    import cv2

    colors = {"red": (40, 40, 220), "blue": (220, 80, 40), "dark": (40, 40, 40), "light": (230, 230, 230), "unknown": (100, 180, 100)}
    for track in tracks:
        x, y = int(track.centroid[0]), int(track.centroid[1])
        color = colors.get(track.team, colors["unknown"])
        cv2.circle(frame, (x, y), 6, color, -1)
        cv2.putText(frame, f"#{track.track_id} {track.speed_mps:.1f}m/s", (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
    return frame
