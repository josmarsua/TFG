import sys
sys.path.append('../')
from utils.bbox_utils import measure_distance, get_center_of_bbox, get_key_points
import cv2 
import numpy as np
import supervision as sv

class BallPossession:
    def __init__(self):
        self.possession_threshold = 50
        self.min_frames = 4
        self.containment_threshold = 0.8
        self.possession_retention = 3

    def get_ball_containment_ratio(self, player_bbox, ball_bbox):
        px1, py1, px2, py2 = player_bbox
        bx1, by1, bx2, by2 = ball_bbox
        ix1 = max(px1, bx1)
        iy1 = max(py1, by1)
        ix2 = min(px2, bx2)
        iy2 = min(py2, by2)
        if ix2 < ix1 or iy2 < iy1:
            return 0.0
        intersection_area = (ix2 - ix1) * (iy2 - iy1)
        ball_area = (bx2 - bx1) * (by2 - by1)
        return intersection_area / ball_area

    def find_min_distance_to_ball(self, ball_center, player_bbox):
        key_points = get_key_points(player_bbox)
        return min(measure_distance(ball_center, point) for point in key_points)

    def find_best_candidate(self, ball_center, player_tracks_frame, ball_bbox):
        high_containment_players = []
        regular_distance_players = []

        for player_id, player_info in player_tracks_frame.items():
            player_bbox = player_info.get('bbox', [])
            if not player_bbox:
                continue
            containment = self.get_ball_containment_ratio(player_bbox, ball_bbox)
            min_distance = self.find_min_distance_to_ball(ball_center, player_bbox)
            if containment > self.containment_threshold:
                high_containment_players.append((player_id, min_distance))
            else:
                regular_distance_players.append((player_id, min_distance))

        if high_containment_players:
            return min(high_containment_players, key=lambda x: x[1])
        if regular_distance_players:
            best_candidate = min(regular_distance_players, key=lambda x: x[1])
            if best_candidate[1] < self.possession_threshold:
                return best_candidate

        return -1, float('inf')

    def detect_ball_possession(self, player_tracks, ball_tracks):
        total_frames = len(ball_tracks)
        possession_list = [-1] * total_frames
        consecutive_possession_count = {}
        last_possessor = -1
        retention_counter = 0

        for frame_num in range(total_frames):
            ball_info = ball_tracks[frame_num].get(1, {})
            if not ball_info:
                continue
            ball_bbox = ball_info.get('bbox', [])
            if not ball_bbox:
                continue
            ball_center = get_center_of_bbox(ball_bbox)

            best_player_id, min_distance = self.find_best_candidate(
                ball_center,
                player_tracks[frame_num],
                ball_bbox
            )

            if best_player_id != -1 and min_distance < self.possession_threshold:
                count = consecutive_possession_count.get(best_player_id, 0) + 1
                consecutive_possession_count = {best_player_id: count}
                if count >= self.min_frames:
                    possession_list[frame_num] = best_player_id
                    last_possessor = best_player_id
                    retention_counter = self.possession_retention
            else:
                if retention_counter > 0:
                    possession_list[frame_num] = last_possessor
                    retention_counter -= 1
                else:
                    last_possessor = -1
                    consecutive_possession_count.clear()

        return possession_list

    def get_team_ball_control(self, player_assignment, ball_possession):
        team_control = []
        for assign_frame, owner in zip(player_assignment, ball_possession):
            if owner == -1:
                team_control.append(-1)
            else:
                team = assign_frame.get(owner, -1)
                team_control.append(team if team in (1, 2) else -1)
        return np.array(team_control)

    def draw_possession(self, video_frames, player_assignment, ball_possession):
        team_ball_control = self.get_team_ball_control(player_assignment, ball_possession)
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            frame_drawn = self.draw_frame(frame, frame_num, team_ball_control)
            output_video_frames.append(frame_drawn)
        return output_video_frames

    def draw_frame(self, frame, frame_num, team_ball_control):
        frame_height, frame_width = frame.shape[:2]

        team_control_till_frame = team_ball_control[:frame_num + 1]
        controlled = team_control_till_frame[team_control_till_frame > 0]
        total_controlled = len(controlled)

        team1_percent = (controlled == 1).sum() / total_controlled if total_controlled > 0 else 0
        team2_percent = (controlled == 2).sum() / total_controlled if total_controlled > 0 else 0

        lines = [
            "Ball Possession",
            f"Team 1: {team1_percent * 100:.2f}%",
            f"Team 2: {team2_percent * 100:.2f}%"
        ]

        font_scale = sv.calculate_optimal_text_scale((frame_width, frame_height))
        thickness = sv.calculate_optimal_line_thickness((frame_width, frame_height))
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_heights = [cv2.getTextSize(line, font, font_scale, thickness)[0][1] + 12 for line in lines]

        base_x, base_y = frame_width - 250, 40
        current_y = base_y
        for i, line in enumerate(lines):
            anchor = sv.Point(x=base_x, y=current_y)
            frame = sv.draw_text(
                scene=frame,
                text=line,
                text_anchor=anchor,
                text_color=sv.Color.BLACK,
                background_color=sv.Color.WHITE,
                text_scale=font_scale,
                text_thickness=thickness
            )
            current_y += line_heights[i]

        return frame