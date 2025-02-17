import sys
sys.path.append('../')
from utils.bbox_utils import measure_distance, get_center_of_bbox, get_key_points
import cv2 
import numpy as np

class BallPossession:
    def __init__(self):
        self.possession_threshold = 50
        self.min_frames = 2
        self.containment_threshold = 0.8
    
    def get_ball_containment_ratio(self, player_bbox, ball_bbox):
        """
        Calcula la fracción de área del balón que se superpone con el bbox del jugador
        Devuelve un valor entre 0 y 1 que indica que fracción de la bola está dentro
        de la bbox del jugador.
        """
        px1, py1, px2, py2 = player_bbox
        bx1, by1, bx2, by2 = ball_bbox
        
        #Calcular la interseccion de ambas bbox
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
        """
        Determina la distancia minima entre el centro del balón y los keypoints del bbox del jugador
        """
        key_points = get_key_points(player_bbox)
        return min(measure_distance(ball_center, point) for point in key_points)
    
    def find_best_candidate(self, ball_center, player_tracks_frame, ball_bbox):
        """
        ball_center: tuple (x, y) calculado a partir de ball_bbox.
        player_tracks_frame: diccionario de jugadores en el frame actual, con formato {player_id: {'bbox': [...]}}
        ball_bbox: bounding box del balón [x1, y1, x2, y2]
        
        Devuelve una tupla: (player_id, distancia) o (-1, inf) si no se encuentra candidato.
        """
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
        
        # Prioridad 1: jugadores con alta contención
        if high_containment_players:
            return min(high_containment_players, key=lambda x: x[1])
            
        # Prioridad 2: jugadores que estén dentro del umbral de distancia
        if regular_distance_players:
            best_candidate = min(regular_distance_players, key=lambda x: x[1])
            if best_candidate[1] < self.possession_threshold:
                return best_candidate
                
        return -1, float('inf')
    
    def detect_ball_possession(self, player_tracks, ball_tracks):
        """
        Detecta que jugador tiene el balón en cada frame dependiendo de la bbox y
        la devuelve como lista de IDs de jugador o -1
        """
        total_frames = len(ball_tracks)
        possession_list = [-1] * total_frames
        consecutive_possession_count = {}
        
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
                consecutive_possession_count[best_player_id] = consecutive_possession_count.get(best_player_id, 0) + 1
                
                if consecutive_possession_count[best_player_id] >= self.min_frames:
                    possession_list[frame_num] = best_player_id
            else:
                consecutive_possession_count.clear()
                
        return possession_list
    
    def get_team_ball_control(self, player_assignment, ball_possession):
        """
        Calcula qué equipo tiene el balón en cada frame.

            player_assignment (list): Lista de diccionarios, uno por frame, con {player_id: team}.
            ball_possession (list): Lista con el id del jugador que posee el balón en cada frame (-1 si nadie).
            
        Devuelve numpy.ndarray: Array indicando qué equipo tiene la posesión en cada frame
                        (1 para Team 1, 2 para Team 2, -1 para sin control).
        """
        team_control = []
        for assign_frame, owner in zip(player_assignment, ball_possession):
            if owner == -1:
                team_control.append(-1)
            else:
                team = assign_frame.get(owner, -1)
                if team == 1:
                    team_control.append(1)
                elif team == 2:
                    team_control.append(2)
                else:
                    team_control.append(-1)
        return np.array(team_control)
    
    def draw_possession(self,video_frames, player_assignment, ball_possession):
        """
        Dibuja estadísticas de posesión de balón sobre cada frame y retorna la lista de frames modificados.
        """
        team_ball_control = self.get_team_ball_control(player_assignment, ball_possession)
        output_video_frames = []
        for frame_num, frame in enumerate(video_frames):
            if frame_num == 0:
                continue
            frame_drawn = self.draw_frame(frame, frame_num, team_ball_control)
            output_video_frames.append(frame_drawn)
        return output_video_frames

    def draw_frame(self, frame, frame_num, team_ball_control):
        """
        Dibuja un overlay semitransparente con las estadísticas de posesión sobre un frame.
        Se ubica en la esquina superior derecha
        """
        overlay = frame.copy()
        frame_height, frame_width = overlay.shape[:2]
        margin = 10  # margen en píxeles desde el borde
        rect_width = int(frame_width * 0.35)
        rect_height = int(frame_height * 0.15)

        # Coordenadas para el rectángulo en la esquina superior derecha
        rect_x2 = frame_width - margin
        rect_x1 = rect_x2 - rect_width
        rect_y1 = margin
        rect_y2 = rect_y1 + rect_height

        # Dibujar el rectángulo de fondo semitransparente
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (255, 255, 255), -1)
        alpha = 0.8
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # Calcular estadísticas de control de balón hasta el frame actual
        team_control_till_frame = team_ball_control[:frame_num+1]
        team1_frames = (team_control_till_frame == 1).sum()
        team2_frames = (team_control_till_frame == 2).sum()
        total = team_control_till_frame.shape[0]
        team1_percent = team1_frames / total if total > 0 else 0
        team2_percent = team2_frames / total if total > 0 else 0

        # Posiciones para el texto dentro del rectángulo
        text_x = rect_x1 + 10
        text_y1 = rect_y1 + int(rect_height * 0.5)
        text_y2 = rect_y1 + int(rect_height * 0.9)

        # Tipografia
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1
        thickness = 1

        cv2.putText(frame, f"Team 1 Ball Possession: {team1_percent*100:.2f}%", (text_x, text_y1),
                    font, font_scale, (0, 0, 0), thickness)
        cv2.putText(frame, f"Team 2 Ball Possession: {team2_percent*100:.2f}%", (text_x, text_y2),
                    font, font_scale, (0, 0, 0), thickness)
        return frame
