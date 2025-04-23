import numpy as np
import cv2
from collections import deque
from utils import get_center_of_bbox
import supervision as sv
from utils import frame_to_time

class ShotTracker:
    def __init__(self, court_pic_path, fps):

        self.fps = fps
        
        self.make_count = 0
        self.attempt_count = 0
        self.make_positions = []
        self.fail_positions = []

        self.team_stats = {
            1: {"makes": 0, "attempts": 0},
            2: {"makes": 0, "attempts": 0}
        }

        self.court_pic_path = court_pic_path
        self.width = 300
        self.height = 161

        self.last_possessor_id = -1
        self.ball_path = deque(maxlen=10)
        self.in_net_history = []
        self.shot_in_progress = False
        self.min_descending_frames = 1

        self.make_flags = []  # Frame flags para FIELD GOAL MADE

        self.events = [] # Para mostrar secuencia de eventos en el frontend

    def get_accuracy(self):
        if self.attempt_count == 0:
            return 0.0
        return (self.make_count / self.attempt_count) * 100
    
    def get_events(self):
        return self.events


    def is_inside_net(self, point, bbox):
        x, y = point
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2

    def is_descending(self):
        if len(self.ball_path) < self.min_descending_frames:
            return False
        y_coords = [y for _, y in self.ball_path]
        return all(earlier < later for earlier, later in zip(y_coords, y_coords[1:]))

    def reset_shot_tracking(self):
        self.shot_in_progress = False
        self.ball_path.clear()
        self.in_net_history.clear()

    def update(self, ball_info, net_info, player_positions, frame_idx):
        if not ball_info or not net_info:
            self.reset_shot_tracking()
            return

        ball_bbox = ball_info.get("bbox")
        if not ball_bbox:
            self.reset_shot_tracking()
            return

        ball_center = get_center_of_bbox(ball_bbox)
        self.ball_path.append(ball_center)

        inside_any_net = any(self.is_inside_net(ball_center, net["bbox"]) for net in net_info.values())

        self.in_net_history.append(inside_any_net)
        if len(self.in_net_history) > 5:
            self.in_net_history.pop(0)

        if inside_any_net:
            self.shot_in_progress = True

        if self.shot_in_progress and not inside_any_net and any(self.in_net_history):
            is_make = self.is_descending()
            self.attempt_count += 1

            if player_positions and self.last_possessor_id in player_positions:
                shooter_pos = player_positions[self.last_possessor_id]["position"]
                event_type = "Tiro convertido" if is_make else "Tiro fallado"

                team = player_positions[self.last_possessor_id].get("team", -1)
                if team in (1, 2):
                    self.team_stats[team]["attempts"] += 1
                    if is_make:
                        self.team_stats[team]["makes"] += 1

                if is_make:
                    self.make_count += 1
                    self.make_positions.append(shooter_pos)
                else:
                    self.fail_positions.append(shooter_pos)

                # Guardar el evento:            
                event = {
                    "type": event_type,
                    "player_id": self.last_possessor_id,
                    "position": shooter_pos,
                    "time": frame_to_time(frame_idx, self.fps),
                    "team": team
                }
                self.events.append(event)

            self.reset_shot_tracking()


    def draw_overlay(self, frame):
        height, width = frame.shape[:2]
        scale_y = height / 720

        font_scale = sv.calculate_optimal_text_scale((width, height))
        thickness = int(sv.calculate_optimal_line_thickness((width, height)))

        anchor_team1 = sv.Point(x=int(width * 0.50), y=int(height * 0.05))
        anchor_team2 = sv.Point(x=int(width * 0.50), y=int(height * 0.11))

        for team, anchor in zip([1, 2], [anchor_team1, anchor_team2]):
            makes = self.team_stats[team]["makes"]
            attempts = self.team_stats[team]["attempts"]
            accuracy = (makes / attempts) * 100 if attempts > 0 else 0

            line = f"Team {team} -> Makes: {makes}, Attempts: {attempts}, Accuracy: {accuracy:.2f}%"

            frame = sv.draw_text(
                scene=frame,
                text=line,
                text_anchor=anchor,
                text_color=sv.Color.BLACK,
                background_color=sv.Color.WHITE,
                text_scale=font_scale,
                text_thickness=thickness
            )

        return frame


    def draw_on_minimap(self, frame, x1, y1):
        court_image = cv2.imread(self.court_pic_path)
        court_image = cv2.resize(court_image, (self.width, self.height))

        if court_image is not None:
            overlay = frame[y1:y1 + self.height, x1:x1 + self.width].copy()
            blended = cv2.addWeighted(court_image, 0.8, overlay, 0.2, 0)
            frame[y1:y1 + self.height, x1:x1 + self.width] = blended

        for pos in self.make_positions:
            x = int(round(pos[0]))
            y = int(round(pos[1]))
            cv2.circle(frame, (x + x1, y + y1), 6, (0, 255, 0), -1)

        for pos in self.fail_positions:
            x = int(round(pos[0]))
            y = int(round(pos[1]))
            offset = 6
            p1 = sv.Point(x=x + x1 - offset, y=y + y1 - offset)
            p2 = sv.Point(x=x + x1 + offset, y=y + y1 + offset)
            p3 = sv.Point(x=x + x1 - offset, y=y + y1 + offset)
            p4 = sv.Point(x=x + x1 + offset, y=y + y1 - offset)

            frame = sv.draw_line(frame, p1, p2, color=sv.Color.RED, thickness=2)
            frame = sv.draw_line(frame, p3, p4, color=sv.Color.RED, thickness=2)

        return frame

    def draw_minimap_overlay(self, video_frames, court_player_positions, tracks, ball_possession, width, height):
        output_video_frames = []
        field_goal_display_frames = 30 

        for frame_idx, frame in enumerate(video_frames):
            ball_info = tracks["ball"][frame_idx].get(1, {})
            net_info = tracks["net"][frame_idx]
            player_pos = court_player_positions[frame_idx]
            possessor_id = ball_possession[frame_idx] if frame_idx < len(ball_possession) else -1

            if possessor_id != -1:
                self.last_possessor_id = possessor_id

            prev_makes = self.make_count
            self.update(ball_info, net_info, player_pos, frame_idx)
            new_makes = self.make_count > prev_makes

            if new_makes:
                # Añadir 60 frames con flag de make
                self.make_flags.extend([1] * field_goal_display_frames)
            else:
                self.make_flags.append(0)

            frame = self.draw_overlay(frame)

            frame_height, frame_width = frame.shape[:2]
            gap = 20
            total_width = width * 2 + gap
            start_x = (frame_width - total_width) // 2

            minimap_x = start_x + width + gap
            minimap_y = frame_height - 40 - height

            frame = self.draw_on_minimap(frame, minimap_x, minimap_y)
            output_video_frames.append(frame)

        # Si hay más flags que frames, cortamos
        if len(self.make_flags) > len(output_video_frames):
            self.make_flags = self.make_flags[:len(output_video_frames)]

        return output_video_frames


    def get_make_flags(self):
        return self.make_flags

    def draw_scores_on_frames(self, video_frames, make_flags):
        output_frames = []

        for frame_idx, frame in enumerate(video_frames):
            frame = frame.copy()

            if make_flags[frame_idx] == 1:
                text = "FIELD GOAL MADE"

                frame_height, frame_width = frame.shape[:2]
                font_scale = sv.calculate_optimal_text_scale((frame_width, frame_height))
                thickness = sv.calculate_optimal_line_thickness((frame_width, frame_height))

                anchor = sv.Point(
                    x=int(frame_width * 0.1),
                    y=int(frame_height * 0.05)
                )

                frame = sv.draw_text(
                    scene=frame,
                    text=text,
                    text_anchor=anchor,
                    text_color=sv.Color.from_hex("#00B000"),
                    background_color=sv.Color.WHITE,
                    text_scale=font_scale,
                    text_thickness=thickness
                )

            output_frames.append(frame)

        return output_frames
