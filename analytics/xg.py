import numpy as np


def calculate_live_xg(player_pos, team_id, team_attacking_goal, frame_width=1280, frame_height=720):
    """Estimate live goal threat from normalized image-space goal distance."""
    target_goal = team_attacking_goal.get(team_id, np.array([frame_width, frame_height / 2.0]))

    player_arr = np.array(player_pos, dtype=np.float32)
    target_arr = np.array(target_goal, dtype=np.float32)
    distance = np.linalg.norm(player_arr - target_arr)

    max_possible_dist = np.linalg.norm([frame_width, frame_height])
    norm_dist = distance / max_possible_dist

    raw_xg = np.exp(-4.0 * norm_dist)
    xg_score = float(np.clip(raw_xg, 0.001, 0.95))
    return xg_score, float(distance)