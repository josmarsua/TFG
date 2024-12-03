from ultralytics import YOLO
import supervision as sv
import pickle
import os
import numpy as np
import pandas as pd
import cv2
import sys
sys.path.append('../')
from utils import get_width_of_bbox, get_center_of_bbox
from scipy.interpolate import CubicSpline

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()

    def detect_frames(self, frames):
        batch_size = 20
        detections = []
        for i in range(0,len(frames),batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size], conf=0.1)
            detections += detections_batch 
        return detections
    
    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                tracks = pickle.load(f)
            return tracks
        
        detections = self.detect_frames(frames)

        tracks = {
            "players":[], #{0:{"bbox:[x1,y1,x2,y2]"},...}
            "referees":[],
            "ball":[]
        }

        for frame_num, detection in enumerate(detections):
            class_names = detection.names #{0: player, 1: referee...}
            class_names_inverse = {value:key for key,value in class_names.items()}

            # Convertir al formato de supervision
            detection_sv = sv.Detections.from_ultralytics(detection)

            # Track (añade un objeto para trackear las detecciones)
            detection_with_tracks = self.tracker.update_with_detections(detection_sv)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detection_with_tracks:
                bounding_box = frame_detection[0].tolist()
                class_id = frame_detection[3]
                track_id = frame_detection[4]

                if class_id == class_names_inverse['player']:
                    tracks["players"][frame_num][track_id] = {"bbox":bounding_box}

                if class_id == class_names_inverse['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox":bounding_box}
            
            for frame_detection in detection_sv:
                bounding_box = frame_detection[0].tolist()
                class_id = frame_detection[3]
                
                if class_id == class_names_inverse['basketball']:
                    tracks["ball"][frame_num][1] = {"bbox":bounding_box} #Solo hay un balon

        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(tracks,f)

        return tracks
    
    def draw_ellipse(self,frame,bbox,color,track_id=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_width_of_bbox(bbox)

        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width),int(0.35*width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color= color,
            thickness=2,
            lineType=cv2.LINE_4
        )

        rectangle_width = 40
        rectangle_height = 20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2 - rectangle_height//2) + 15
        y2_rect = (y2 + rectangle_height//2) + 15

        if track_id is not None:
            cv2.rectangle(
                frame,
                (int(x1_rect),int(y1_rect)),
                (int(x2_rect),int(y2_rect)),
                color,
                cv2.FILLED
            )
            x1_text = x1_rect + 12
            if track_id > 99:
                x1_text -= 10
            
            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text),int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )

        return frame

    def draw_triangle(self,frame,bbox,color):
        y = int(bbox[1]) #y1
        x,_ = get_center_of_bbox(bbox) #xcenter

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])

        cv2.drawContours(frame,
                         [triangle_points],
                         0,
                         color,
                         cv2.FILLED)
        
        cv2.drawContours(frame,
                         [triangle_points],
                         0,
                         (0,0,0),
                         2)
        
        return frame
    
    def draw_circle(self, frame, bbox, color):
        """
        Dibuja un círculo alrededor del balón basado en su bbox.
        """
        # Calcular el centro del bounding box
        x1, y1, x2, y2 = map(int, bbox)
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        # Calcular el radio como la mitad de la mayor dimensión del bounding box
        radius = max((x2 - x1) // 2, (y2 - y1) // 2)

        # Dibujar el círculo
        cv2.circle(frame, (center_x, center_y), radius, color, thickness=2)

        return frame

    def draw_annotations(self,video_frames,tracks):
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]

            # Draw Players
            for track_id, player in player_dict.items():
                color = player.get("team_color",(0,0,255))
                frame = self.draw_ellipse(frame, player["bbox"],color, track_id)

            # Draw Referee
            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"],(255, 0, 255))

            # Draw Ball
            for _, ball in ball_dict.items():
                frame = self.draw_triangle(frame,ball["bbox"],(0,255,0)) 
                frame = self.draw_circle(frame,ball["bbox"],(0,255,0))

            output_video_frames.append(frame)

        return output_video_frames
                
    #Seguimiento de la posicion de la pelota (evitar frames en las que no se detecta)

    def interpolate_ball_positions(self, ball_positions):
        # Extraer las posiciones del balón (x1, y1, x2, y2)
        ball_positions = [x.get(1, {}).get('bbox', []) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions, columns=['x1', 'y1', 'x2', 'y2'])

        # Índices donde las posiciones del balón están disponibles
        valid_indices = df_ball_positions.dropna().index.to_numpy()
        missing_indices = df_ball_positions[df_ball_positions.isna().any(axis=1)].index.to_numpy()

        if len(valid_indices) < 2:  # No hay suficiente información para interpolar
            return [{1: {"bbox": [0, 0, 0, 0]}} for _ in ball_positions]

        # Interpolación cúbica para cada columna (x1, y1, x2, y2)
        interpolated_positions = df_ball_positions.copy()
        for col in df_ball_positions.columns:
            valid_values = df_ball_positions[col].dropna().to_numpy()
            if len(valid_values) >= 2:  # Necesita al menos dos puntos válidos
                spline = CubicSpline(valid_indices, valid_values, bc_type='natural')
                interpolated_positions.loc[missing_indices, col] = spline(missing_indices)

        # Rellenar valores faltantes al principio o al final (si es necesario)
        interpolated_positions = interpolated_positions.bfill().ffill()

        # Reconstruir el formato original
        ball_positions = [{1: {"bbox": x}} for x in interpolated_positions.to_numpy().tolist()]
        return ball_positions
