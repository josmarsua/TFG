from ultralytics import YOLO
import supervision as sv
import sys 
import pickle
import os
import cv2
import numpy as np
sys.path.append('../')


class CourtKeypointDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
    
    def get_court_keypoints(self, frames,read_from_stub=False, stub_path=None):

        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                court_keypoints = pickle.load(f)
            return court_keypoints
        
        batch_size=20
        court_keypoints = []
        for i in range(0,len(frames),batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size],conf=0.5)
            for detection in detections_batch:
                court_keypoints.append(detection.keypoints)
 
        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(court_keypoints,f)
        
        return court_keypoints
    
    def draw_court_keypoints(self, frames, court_keypoints):
        """
        Dibuja los keypoints en los frames y anota su class_id encima de cada punto.
        """
        vertex_annotator = sv.VertexAnnotator(
            color=sv.Color.from_hex('#d313a2'),
            radius=5
        )

        output_frames = []
        for index, frame in enumerate(frames):
            annotated_frame = frame.copy()

            keypoints = court_keypoints[index]

            if keypoints is not None and keypoints.xy is not None:
                keypoints_array = keypoints.xy[0].cpu().numpy()  # Extraer coordenadas
                class_ids = np.arange(len(keypoints_array))  # Asignar class_id (0, 1, 2, ...)

                # Dibujar puntos
                annotated_frame = vertex_annotator.annotate(
                    scene=annotated_frame,
                    key_points=keypoints
                )

                # Dibujar class_id sobre cada keypoint
                for i, (x, y) in enumerate(keypoints_array):
                    if x > 0 and y > 0:  # Filtrar keypoints no detectados
                        cv2.putText(
                            annotated_frame, 
                            str(class_ids[i]),  # Texto con el class_id
                            (int(x), int(y) - 10),  # Posición encima del punto
                            cv2.FONT_HERSHEY_SIMPLEX, 
                            0.5,  # Tamaño del texto
                            (0, 0, 0),  # Color (blanco)
                            2, 
                            cv2.LINE_AA
                        )

            output_frames.append(annotated_frame)

        return output_frames
    
    def match_keypoints(self, source_kp, court_reference_points):
        """
        Asocia los keypoints detectados con los puntos de referencia de la cancha.
        """
        if len(source_kp) == 0:
            return np.full_like(court_reference_points, -1) # Rellenar con -1 si no hay kp detectados
        
        matched_kp = np.zeros_like(court_reference_points)
        assigned = set()

        for i, ref_point in enumerate(court_reference_points):
            if len(source_kp) == 0:
                matched_kp[i] = [-1, -1]
                continue

            distances = np.linalg.norm(source_kp - ref_point, axis=1)

            if distances.size == 0:
                matched_kp[i] = [-1, -1]
                continue

            closest_idx = np.argmin(distances)

            if closest_idx not in assigned:
                matched_kp[i] = source_kp[closest_idx]
                assigned.add(closest_idx)
            else:
                matched_kp[i] = [-1, -1]  # Marcar como no asignado
        
        return matched_kp