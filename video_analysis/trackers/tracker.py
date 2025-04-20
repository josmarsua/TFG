from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.smoother = sv.DetectionsSmoother(length=5)

    def detect_frames(self, frames):
        batch_size = 20
        detections = []
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i:i + batch_size], conf=0.5)
            detections += detections_batch
        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):

        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                return pickle.load(f)

        detections = self.detect_frames(frames)

        tracks = {
            "players": [],
            "referees": [],
            "ball": [],
            "net": []
        }

        for frame_idx, detection in enumerate(detections):
            class_names = detection.names
            class_id_map = {v: k for k, v in class_names.items()}

            sv_detections = sv.Detections.from_ultralytics(detection)
            tracked = self.tracker.update_with_detections(sv_detections)
            smoothed = self.smoother.update_with_detections(tracked)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})
            tracks["net"].append({})

            # Para jugadores, árbitros y red (trackeados)
            for i in range(len(smoothed.xyxy)):
                class_id = int(smoothed.class_id[i])
                track_id = int(smoothed.tracker_id[i])
                bbox = smoothed.xyxy[i].tolist()

                if class_id == class_id_map["player"]:
                    tracks["players"][frame_idx][track_id] = {"bbox": bbox}
                elif class_id == class_id_map["referee"]:
                    tracks["referees"][frame_idx][track_id] = {"bbox": bbox}
                elif class_id == class_id_map["net"]:
                    tracks["net"][frame_idx][track_id] = {"bbox": bbox}

            # Para el balón (no trackeado)
            ball_found = False
            for i in range(len(sv_detections.xyxy)):
                class_id = int(sv_detections.class_id[i])
                if class_id == class_id_map["basketball"]:
                    bbox = sv_detections.xyxy[i].tolist()
                    tracks["ball"][frame_idx][1] = {"bbox": bbox}  # Solo un balón con ID 1
                    ball_found = True

            if not ball_found:
                tracks["ball"][frame_idx][1] = {}  # Marcado como no encontrado

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(tracks, f)

        return tracks

    def draw_annotations(self, frames, tracks):
        triangle_annotator = sv.TriangleAnnotator(base=14, height=18, color=sv.Color(r=128, g=255, b=0))
        circle_annotator = sv.CircleAnnotator(thickness=2, color=sv.Color(r=128, g=255, b=0))
        ellipse_annotator = sv.EllipseAnnotator()
        bbox_annotator = sv.RoundBoxAnnotator()
        label_annotator = sv.LabelAnnotator(text_position=sv.Position.TOP_CENTER)

        
        output_frames = []
        for frame_idx, frame in enumerate(frames):
            frame = frame.copy()

            # Jugadores
            players = tracks["players"][frame_idx]
            for track_id, player in players.items():
                player_color = player.get("team_color",(0,0,255))
                player_ellipse_annotator = sv.EllipseAnnotator(color=sv.Color(r=player_color[2], g=player_color[1], b=player_color[0]),thickness=3)
                player_label_annotator = sv.LabelAnnotator(text_position=sv.Position.BOTTOM_CENTER, color=sv.Color(r=player_color[2], g=player_color[1], b=player_color[0]))
                det = sv.Detections(
                    xyxy=np.array([player["bbox"]]),
                    class_id=np.array([0]),
                    tracker_id=np.array([int(track_id)])
                )
                frame = player_ellipse_annotator.annotate(scene=frame, detections=det)
                frame = player_label_annotator.annotate(scene=frame, detections=det, labels=[f"Player #{track_id}"])

            # Árbitros
            referees = tracks["referees"][frame_idx]
            for rid, rdata in referees.items():
                det = sv.Detections(
                    xyxy=np.array([rdata["bbox"]]),
                    class_id=np.array([1]),
                    tracker_id=np.array([int(rid)])
                )
                frame = ellipse_annotator.annotate(scene=frame, detections=det)
                frame = label_annotator.annotate(scene=frame, detections=det, labels=["Referee"])

            # Balón
            ball_data = tracks["ball"][frame_idx].get(1)
            if ball_data and "bbox" in ball_data:
                bbox = ball_data["bbox"]
                det = sv.Detections(
                    xyxy=np.array([bbox]),
                    class_id=np.array([2]),
                    tracker_id=np.array([1])
                )
                frame = circle_annotator.annotate(scene=frame, detections=det)
                frame = triangle_annotator.annotate(scene=frame, detections=det)

            # Red
            nets = tracks["net"][frame_idx]
            for nid, net_data in nets.items():
                det = sv.Detections(
                    xyxy=np.array([net_data["bbox"]]),
                    class_id=np.array([3]),
                    tracker_id=np.array([int(nid)])
                )
                frame = bbox_annotator.annotate(scene=frame, detections=det)
                frame = label_annotator.annotate(scene=frame, detections=det, labels=["Net"])

            output_frames.append(frame)

        return output_frames
