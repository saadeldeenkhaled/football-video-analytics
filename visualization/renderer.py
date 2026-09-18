import cv2
import config


class GraphicsRenderer:
    @staticmethod
    def draw_player_stats(frame, bbox, dist_to_ball_m, speed_kmh, xg_val, team_color):
        x1, y1, x2, y2 = map(int, bbox)
        center_x = int((x1 + x2) / 2)
        y_offset = max(12, y1 - 50)
        text_x = max(0, center_x - 30)
        text_speed = f"{speed_kmh:.1f} km/h"
        text_dist_ball = "Ball: --" if dist_to_ball_m is None else f"Ball: {dist_to_ball_m:.1f}m"
        text_xg = f"xG: {xg_val * 100:.1f}%"

        cv2.putText(frame, text_speed, (text_x, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, text_dist_ball, (text_x, y_offset + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 255, 200), 1)
        xg_color = (0, 255, 255) if xg_val > 0.25 else (255, 255, 255)
        cv2.putText(frame, text_xg, (text_x, y_offset + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, xg_color, 2)
        return frame

    @staticmethod
    def draw_player_annotation(frame, bbox, track_id, team_id, speed, distance):
        x1, y1, x2, y2 = map(int, bbox)
        center_x = int((x1 + x2) / 2)
        bottom_y = int(y2)

        axis_x = max(10, int((x2 - x1) / 1.5))
        axis_y = max(5, int((x2 - x1) / 4))
        team_colors = {
            0: (40, 40, 220),
            1: (220, 80, 40),
            "red": (40, 40, 220),
            "blue": (220, 80, 40),
            "unknown": (255, 255, 255),
        }
        team_color = team_colors.get(team_id, (255, 255, 255))
        cv2.ellipse(frame, (center_x, bottom_y), (axis_x, axis_y), 0, 0, 360, team_color, 2)
        cv2.arrowedLine(frame, (center_x, y1 - 18), (center_x, y1 - 2), team_color, 2, tipLength=0.35)

        id_text = str(track_id)
        speed_text = f"{speed:.2f} km/h"
        dist_text = f"{distance:.2f} m"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale_id = 0.55
        font_scale_stats = 0.45

        (id_w, id_h), _ = cv2.getTextSize(id_text, font, font_scale_id, 2)
        pad_x, pad_y = 6, 4

        box_x = int(x1 - id_w - 20)
        box_y = int((y1 + y2) / 2)

        if box_x < 0:
            box_x = int(x2 + 10)

        cv2.line(frame, (box_x + id_w + pad_x, box_y), (x1, box_y + 10), (255, 255, 255), 2)
        cv2.rectangle(frame, (box_x, box_y - id_h - pad_y), (box_x + id_w + 2 * pad_x, box_y + pad_y), (0, 0, 0), 1)
        cv2.rectangle(frame, (box_x + 1, box_y - id_h - pad_y + 1), (box_x + id_w + 2 * pad_x - 1, box_y + pad_y - 1), (255, 255, 255), -1)

        cv2.putText(frame, id_text, (box_x + pad_x, box_y), font, font_scale_id, (0, 0, 0), 2)

        stats_x = box_x
        stats_y = box_y + pad_y + 18

        cv2.putText(frame, speed_text, (stats_x, stats_y), font, font_scale_stats, (0, 0, 0), 2)
        cv2.putText(frame, dist_text, (stats_x, stats_y + 18), font, font_scale_stats, (0, 0, 0), 2)

    @staticmethod
    def draw_ball(frame, bbox):
        x1, y1, x2, y2 = map(int, bbox)
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))
        cv2.circle(frame, center, 5, (255, 255, 255), -1)
        cv2.circle(frame, center, 7, (0, 0, 0), 2)
