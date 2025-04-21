import numpy as np
import cv2
from utils import get_center_of_bbox
import supervision as sv

class ShotTracker:
    def __init__(self, court_pic_path):
        self.make_count = 0
        self.attempt_count = 0
        self.make_positions = []
        self.fail_positions = []
        self.prev_inside = False

        self.court_pic_path = court_pic_path
        self.width = 300
        self.height = 161

        self.last_possessor_id = -1  # 🆕 Recordar último jugador con posesión válida

    def get_accuracy(self):
        if self.attempt_count == 0:
            return 0.0
        return (self.make_count / self.attempt_count) * 100

    def is_inside_net(self, point, bbox):
        x, y = point
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2

    def update(self, ball_info, net_info, player_positions):
        if not ball_info or not net_info:
            self.prev_inside = False
            return

        ball_bbox = ball_info.get("bbox")
        if not ball_bbox:
            self.prev_inside = False
            return

        ball_center = get_center_of_bbox(ball_bbox)
        inside_any_net = any(self.is_inside_net(ball_center, net["bbox"]) for net in net_info.values())

        if inside_any_net and not self.prev_inside:
            self.make_count += 1
            self.attempt_count += 1

            if player_positions and self.last_possessor_id in player_positions:
                shooter_pos = player_positions[self.last_possessor_id]["position"]
                self.make_positions.append(shooter_pos)

        if not inside_any_net and self.prev_inside:
            self.attempt_count += 1
            if player_positions and self.last_possessor_id in player_positions:
                shooter_pos = player_positions[self.last_possessor_id]["position"]
                self.fail_positions.append(shooter_pos)

        self.prev_inside = inside_any_net

    def draw_overlay(self, frame):
        height, width = frame.shape[:2]
        scale_y = height / 720

        font_scale = sv.calculate_optimal_text_scale((width, height))
        thickness = int(sv.calculate_optimal_line_thickness((width, height)))

        anchor = sv.Point(
            x=int(width * 0.50),
            y=int(height * 0.05)
        )

        lines = [
            f"Makes: {self.make_count}, Attempts: {self.attempt_count}, Accuracy: {self.get_accuracy():.2f}%"
        ]

        for i, line in enumerate(lines):
            y_pos = anchor.y + int(i * 50 * scale_y)
            anchor_line = sv.Point(x=anchor.x, y=y_pos)
            frame = sv.draw_text(
                scene=frame,
                text=line,
                text_anchor=anchor_line,
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
        for frame_idx, frame in enumerate(video_frames):
            ball_info = tracks["ball"][frame_idx].get(1, {})
            net_info = tracks["net"][frame_idx]
            player_pos = court_player_positions[frame_idx]
            possessor_id = ball_possession[frame_idx] if frame_idx < len(ball_possession) else -1

            # 🆕 Recordar último jugador con posesión válida
            if possessor_id != -1:
                self.last_possessor_id = possessor_id

            self.update(ball_info, net_info, player_pos)

            frame = self.draw_overlay(frame)

            frame_height, frame_width = frame.shape[:2]
            gap = 20
            total_width = width * 2 + gap
            start_x = (frame_width - total_width) // 2

            minimap_x = start_x + width + gap
            minimap_y = frame_height - 40 - height

            frame = self.draw_on_minimap(frame, minimap_x, minimap_y)

            output_video_frames.append(frame)

        return output_video_frames
