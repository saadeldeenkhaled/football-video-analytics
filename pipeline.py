import cv2
import os
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO
import config
from calibration.homography import PitchCalibrator
from team.classifier import TeamClassifier
from analytics.metrics import AnalyticsEngine
from analytics.xg import calculate_live_xg
from visualization.renderer import GraphicsRenderer

def process_video(input_path, output_path, progress_callback=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"ملف الفيديو غير موجود: {input_path}")

    # تحميل النموذج
    model = YOLO(config.YOLO_MODEL_PATH)
    
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise ValueError("تعذر فتح ملف الفيديو المرفوع.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    calibrator = PitchCalibrator()
    classifier = TeamClassifier(refresh_interval=getattr(config, "TEAM_COLOR_REFRESH_FRAMES", 30))
    analytics = AnalyticsEngine(fps)
    team_attacking_goal = {
        0: np.array([width, height / 2.0], dtype=np.float32),
        1: np.array([0.0, height / 2.0], dtype=np.float32),
    }
    
    frame_idx = 0
    training_done = False

    pbar = tqdm(total=total_frames, desc="Processing Frames", unit="frame")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame is None:
            break
            
        frame_idx += 1
        pbar.update(1)
        
        # تنفيذ التتبع (0: شخص، 32: كرة)
        results = model.track(
            source=frame, 
            persist=True, 
            classes=[0, 32], 
            conf=config.CONFIDENCE_THRESHOLD, 
            tracker=config.TRACKER_TYPE, 
            verbose=False
        )
        
        if len(results) > 0 and results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            class_ids = results[0].boxes.cls.cpu().numpy().astype(int)
            
            player_boxes, player_ids = [], []
            ball_box = None
            
            for bbox, t_id, c_id in zip(boxes, track_ids, class_ids):
                if c_id == 0:
                    player_boxes.append(bbox)
                    player_ids.append(t_id)
                elif c_id == 32:
                    ball_box = bbox
            
            if len(player_boxes) >= 2 and (not training_done or frame_idx % classifier.refresh_interval == 0):
                training_done = classifier.fit_teams(
                    frame,
                    player_boxes,
                    player_ids,
                    frame_idx=frame_idx,
                    force=not training_done,
                ) or training_done
                
            # رسم بيانات اللاعبين
            ball_pitch_position = None
            if ball_box is not None:
                ball_x = float((ball_box[0] + ball_box[2]) / 2)
                ball_y = float(ball_box[3])
                ball_pitch_position = calibrator.pixel_to_meters(ball_x, ball_y)

            for bbox, t_id in zip(player_boxes, player_ids):
                x_center = float((bbox[0] + bbox[2]) / 2)
                y_bottom = float(bbox[3])
                
                pitch_x, pitch_y = calibrator.pixel_to_meters(x_center, y_bottom)
                analytics.update_player(t_id, frame_idx, pitch_x, pitch_y)
                speed, distance = analytics.get_stats(t_id)
                
                team_id = classifier.get_team(frame, bbox, t_id)
                xg_value, _ = calculate_live_xg(
                    (x_center, y_bottom),
                    team_id,
                    team_attacking_goal,
                    frame_width=width,
                    frame_height=height,
                )
                distance_to_ball = analytics.get_distance_to_ball(t_id, ball_pitch_position)
                GraphicsRenderer.draw_player_annotation(frame, bbox, t_id, team_id, speed, distance)
                GraphicsRenderer.draw_player_stats(
                    frame,
                    bbox,
                    distance_to_ball,
                    speed,
                    xg_value,
                    team_id,
                )
                
            # رسم الكرة
            if ball_box is not None:
                GraphicsRenderer.draw_ball(frame, ball_box)
                
        out.write(frame)
        
        if progress_callback and total_frames > 0:
            progress_callback(frame_idx, total_frames)

    pbar.close()
    cap.release()
    out.release()
    return output_path
