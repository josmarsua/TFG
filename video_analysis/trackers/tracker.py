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
    
    def get_object_tracks(self, frames, transformer_per_frame, read_from_stub=False, stub_path=None):
        
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                tracks = pickle.load(f)
            return tracks
        
        detections = self.detect_frames(frames)
                
        tracks = {
            "players":[], #{0:{"bbox:[x1,y1,x2,y2]"},...}
            "referees":[],
            "ball":[],
            "net":[]
        }

        for frame_num, detection in enumerate(detections):
            transformer = transformer_per_frame[frame_num] # Transformacion del frame actual
           
            class_names = detection.names #{0: player, 1: referee...}
            class_names_inverse = {value:key for key,value in class_names.items()}

            # Convertir al formato de supervision
            detection_sv = sv.Detections.from_ultralytics(detection)

            # Track (añade un objeto para trackear las detecciones)
            detection_with_tracks = self.tracker.update_with_detections(detection_sv)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})
            tracks["net"].append({})

            for frame_detection in detection_with_tracks:
                bounding_box = frame_detection[0].tolist()
                class_id = frame_detection[3]
                track_id = frame_detection[4]
                
                x_center, y_center = get_center_of_bbox(bounding_box)

                 # Verificar si el transformer es None antes de aplicar la homografía
                if transformer is None:
                    court_x, court_y = x_center, y_center  # Usar las coordenadas originales sin transformación
                else:
                    court_x, court_y = transformer.transform_points(np.array([[x_center, y_center]]))[0]

                if class_id == class_names_inverse['player']:
                    tracks["players"][frame_num][track_id] = {
                        "bbox": bounding_box,
                        "court_position": (court_x, court_y)
                    }

                if class_id == class_names_inverse['referee']:
                    tracks["referees"][frame_num][track_id] = {"bbox":bounding_box}
                
                if class_id == class_names_inverse['net']:
                    tracks["net"][frame_num][track_id] = {"bbox":bounding_box}
            
            for frame_detection in detection_sv:
                bounding_box = frame_detection[0].tolist()
                class_id = frame_detection[3]
                
                if class_id == class_names_inverse['basketball']:
                    tracks["ball"][frame_num][1] = {"bbox":bounding_box} #Solo hay un balon, almacenamos en el track 1

        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(tracks,f)

        return tracks
    
    def draw_ellipse(self, frame, bbox, color, track_id=None, label=None):
        y2 = int(bbox[3])
        x_center, _ = get_center_of_bbox(bbox)
        width = get_width_of_bbox(bbox)

        # Dibujar la elipse
        cv2.ellipse(
            frame,
            center=(x_center, y2),
            axes=(int(width), int(0.35 * width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4,
        )

        # Determinar el texto que se mostrará
        if label:
            text = label
        elif track_id is not None:
            text = f"Player\nID: {track_id}"
        else:
            return frame

        # Configurar el texto
        font_scale = 0.5
        font_thickness = 2
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

        # Determinar las dimensiones del rectángulo para el texto
        text_lines = text.split("\n")
        line_height = text_size[1] + 5
        rect_width = max([cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0][0] for line in text_lines]) + 10
        rect_height = line_height * len(text_lines) + 5

        # Coordenadas del rectángulo
        x1_rect = x_center - rect_width // 2
        x2_rect = x_center + rect_width // 2
        y1_rect = y2 - rect_height - 5
        y2_rect = y2 - 5

        # Dibujar el rectángulo de fondo
        cv2.rectangle(
            frame,
            (int(x1_rect), int(y1_rect)),
            (int(x2_rect), int(y2_rect)),
            color,
            cv2.FILLED,
        )

        # Dibujar cada línea de texto, centrada en el rectángulo
        y_text = y1_rect + line_height
        for line in text_lines:
            text_size, _ = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            x_text = x_center - text_size[0] // 2
            cv2.putText(
                frame,
                line,
                (int(x_text), int(y_text)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (0, 0, 0),
                font_thickness,
            )
            y_text += line_height

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
    
    def draw_rectangle(self, frame, bbox, color, track_id=None):
        """
        Dibuja un rectángulo alrededor de la red basado en su bbox.
        """
        # Extraer coordenadas del bounding box
        x1, y1, x2, y2 = map(int, bbox)

        # Dibujar el rectángulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness=2)

        # Añadir etiqueta opcional
        if track_id is not None:
            label = f"Net"
            font_scale = 0.5
            font_thickness = 2
            text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            text_x = x1
            text_y = y1 - 5  # Justo encima del rectángulo

            # Fondo del texto
            cv2.rectangle(frame,
                        (text_x, text_y - text_size[1]),
                        (text_x + text_size[0], text_y + 5),
                        color,
                        cv2.FILLED)

            # Texto
            cv2.putText(frame,
                        label,
                        (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale,
                        (0, 0, 0),  # Texto en negro
                        font_thickness)

        return frame

    def draw_annotations(self,video_frames,tracks):
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            ball_dict = tracks["ball"][frame_num]
            referee_dict = tracks["referees"][frame_num]
            net_dict = tracks["net"][frame_num]


            # Draw Players
            for track_id, player in player_dict.items():
                color = player.get("team_color",(0,0,255))
                frame = self.draw_ellipse(frame, player["bbox"],color, track_id)

            # Draw Referee
            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"],(255, 0, 255), label="Referee")

            # Draw Ball
            for _, ball in ball_dict.items():
                frame = self.draw_triangle(frame,ball["bbox"],(0,255,0)) 
                frame = self.draw_circle(frame,ball["bbox"],(0,255,0))

            # Draw Net
            for track_id, net in net_dict.items():
                color = (0, 128, 255)
                frame = self.draw_rectangle(frame,net["bbox"],color,track_id)

            output_video_frames.append(frame)

        return output_video_frames
                
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

