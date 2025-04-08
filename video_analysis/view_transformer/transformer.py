import os
import sys
import pathlib
import numpy as np
import cv2 
from copy import deepcopy
from .homography import Homography
from utils import measure_distance

folder_path = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(folder_path, "../"))

class Transformer:
    def __init__(self, court_pic_path):
        self.court_pic_path = court_pic_path
        self.width = 300
        self.height = 161 

        # Dimensiones reales en metros
        real_width = 28 
        real_height = 15 

        self.key_points = [
            # Linea fondo izquierdo
            (0,0),
            (0,int((0.91/real_height)*self.height)),
            (0,int((5.18/real_height)*self.height)),
            (0,int((10/real_height)*self.height)),
            (0,int((14.1/real_height)*self.height)),
            (0,int(self.height)),

            # Linea central
            (int(self.width/2),self.height),
            (int(self.width/2),0),
            
            # Linea TL izquierda
            (int((5.79/real_width)*self.width),int((5.18/real_height)*self.height)),
            (int((5.79/real_width)*self.width),int((10/real_height)*self.height)),

            # Linea fondo derecho
            (self.width,int(self.height)),
            (self.width,int((14.1/real_height)*self.height)),
            (self.width,int((10/real_height)*self.height)),
            (self.width,int((5.18/real_height)*self.height)),
            (self.width,int((0.91/real_height)*self.height)),
            (self.width,0),

            # Linea TL derecha
            (int(((real_width-5.79)/real_width)*self.width),int((5.18/real_height)*self.height)),
            (int(((real_width-5.79)/real_width)*self.width),int((10/real_height)*self.height)),
        ]

    def validate_kp(self, kp):
        """
        Valida los puntos clave detectados comparandolos con los puntos del boceto
        """
        kp = deepcopy(kp)

        for frame_id, frame_kp in enumerate(kp):
            frame_kp = frame_kp.xy.tolist()[0]

            detected_indices = [i for i,kp in enumerate(frame_kp) if kp[0] > 0 and kp[1] > 0]

            # Necesitamos al menos 3 puntos detectados para validar
            if len(detected_indices) < 3:
                continue

            invalid_kp = []
            for i in detected_indices:
                # Si es el (0,0) pasamos
                if frame_kp[i][0] == 0 and frame_kp[i][1] == 0:
                    continue

                # Escogemos otros dos de forma aleatoria
                other_indices = [ii for ii in detected_indices if ii != i and ii not in invalid_kp]
                if len(other_indices) < 2:
                    continue

                j, k = other_indices[0], other_indices[1] #Tomamos los dos primeros por simplicidad

                # Calculamos las distancias entre los detectados
                d_ij = measure_distance(frame_kp[i], frame_kp[j])
                d_ik = measure_distance(frame_kp[i], frame_kp[k])

                # Calculamos las distancias entre los reales
                t_ij = measure_distance(self.key_points[i], self.key_points[j])
                t_ik = measure_distance(self.key_points[i], self.key_points[k])

                # Calculamos las proporciones y comparamos
                if t_ij > 0 and t_ik > 0:
                    prop_detected = d_ij / d_ik if d_ik > 0 else float('inf')
                    prop_tactical = t_ij / t_ik if t_ik > 0 else float('inf')

                    error = (prop_detected - prop_tactical) / prop_tactical
                    error = abs(error)

                    if error >0.8:  # 80% error margin                        
                        kp[frame_id].xy[0][i] *= 0
                        kp[frame_id].xyn[0][i] *= 0
                        invalid_kp.append(i)

        return kp


    def transform_players(self, kp, player_tracks):
        """
        Transforma las coordenadas de los jugadores desde el video a la cancha
        """
        court_player_positions = []

        for frame_id, (frame_kp, frame_tracks) in enumerate(zip(kp,player_tracks)):
            court_positions = {}

            frame_kp = frame_kp.xy.tolist()[0]

            if frame_kp is None or len(frame_kp) == 0:
                court_player_positions.append(court_positions)
                continue

            detected_kp = frame_kp

            valid_indices = [i for i,kp in enumerate(detected_kp) if kp[0] > 0 and kp[1] > 0]

            if len(valid_indices) < 4:
                court_player_positions.append(court_positions)
                continue

            source_points = np.array([detected_kp[i] for i in valid_indices], dtype=np.float32)
            target_points = np.array([self.key_points[i] for i in valid_indices], dtype=np.float32)

            try:
                homography = Homography(source_points, target_points)

                for player_id, player_data in frame_tracks.items():
                    bbox = player_data["bbox"]
                    player_position = np.array([[bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[3]]])

                    court_position = homography.transform_points(player_position)

                    if court_position[0][0] < 0 or court_position[0][0] > self.width or court_position[0][1] < 0 or court_position[0][1] > self.height:
                        continue

                    team_color = frame_tracks[player_id].get("team_color", [0,0,0])
                    court_positions[player_id] = {
                        "position": court_position[0].tolist(),
                        "team_color": team_color
                    }

            except (ValueError, cv2.error) as e:
                # Si la homografía falla, continuar con diccionario vacío
                pass

            court_player_positions.append(court_positions)

        return court_player_positions
    
    def draw_court_overlay(self, video_frames, court_image_path, width,height, tactical_court_keypoints, tactical_player_positions=None, player_assignment=None, ball_acquisition=None):
        """
        Dibuja la cancha y las posiciones de los jugadores.
        """
        court_image = cv2.imread(court_image_path)
        court_image = cv2.resize(court_image, (width, height))

        output_video_frames = []
        for frame_idx, frame in enumerate(video_frames):
            frame = frame.copy()

            # Posición en la que dibujamos el overlay
            frame_height, frame_width = frame.shape[:2]
            x1 = int((frame_width - width) / 2)
            x2 = x1 + width
            y2 = frame_height - 40
            y1 = y2 - height
            
            alpha = 0.8  # Transparencia
            overlay = frame[y1:y2, x1:x2].copy()
            cv2.addWeighted(court_image, alpha, overlay, 1 - alpha, 0, frame[y1:y2, x1:x2])
            
            # Dibujar keypoints de la cancha táctica
            #for keypoint_index, keypoint in enumerate(tactical_court_keypoints):
            #    x, y = keypoint
            #    x += self.start_x
            #    y += self.start_y
            #    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
            #    cv2.putText(frame, str(keypoint_index), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Mapear posiciones de los jugadores
            if tactical_player_positions and player_assignment and frame_idx < len(tactical_player_positions):
                frame_positions = tactical_player_positions[frame_idx]
                frame_assignments = player_assignment[frame_idx] if frame_idx < len(player_assignment) else {}
                #player_with_ball = ball_acquisition[frame_idx] if ball_acquisition and frame_idx < len(ball_acquisition) else -1
                
                for player_id, player_data in frame_positions.items():
                    # Establecer el color según el equipo
                    x, y = int(player_data["position"][0]) + x1, int(player_data["position"][1]) + y1
                    color = tuple(map(int, player_data.get("team_color", [0, 0, 0])))

                    # Dibujar círculo en la posición del jugador
                    cv2.circle(frame, 
                               (x, y), 
                               5, 
                               color, 
                               -1)
                    
                    # Mostrar ID del jugador
                    #cv2.putText(frame, str(player_id), (x-4, y+4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                    
                    # Resaltar jugador con balón
                    #if player_id == player_with_ball:
                        #cv2.circle(frame, (x, y), player_radius+2, (0, 0, 255), 2)
            
            output_video_frames.append(frame)

        return output_video_frames
    