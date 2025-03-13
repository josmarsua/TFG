import cv2
import numpy as np
from view_transformer import ViewTransformer

def save_court_video(tracks, video_frames, court_image_path, court_size, output_video_path):
    """
    Dibuja las posiciones de los jugadores en un video en tiempo real usando una homografía predefinida
    y guarda el video resultante en un archivo.
    """
     # Cargar la imagen de la cancha
    court_template = cv2.imread(court_image_path)
    court_template = cv2.resize(court_template, court_size)

    # Colores por equipo
    team_colors = {
        1: (255, 128, 0),  # Naranja
        2: (0, 128, 255),  # Azul
    }

    # Asociar cada jugador a su equipo de forma fija
    player_teams = {}  # track_id -> team
    for frame_tracks in tracks["players"]:
        for track_id, player_data in frame_tracks.items():
            track_id = int(track_id)
            if track_id not in player_teams:
                player_teams[track_id] = player_data.get("team", None)

    # Configurar el VideoWriter para guardar el video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = 24
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, court_size)

    # Dibujar las posiciones en cada frame
    for frame_num, (frame, player_tracks) in enumerate(zip(video_frames, tracks["players"])):
        # Clonar la cancha para este frame
        court = court_template.copy()

        for track_id, player_data in player_tracks.items():
            track_id = int(track_id)
            
            # Obtener la posición en la cancha
            court_position = player_data.get("court_position", None)
            if court_position is None or len(court_position) != 2:
                continue  # Saltar si la posición no es válida

            court_x, court_y = court_position

            # Escalar las coordenadas para que se ajusten al tamaño de la cancha del minimapa
            court_x = int((court_x / 2000) * court_size[0])
            court_y = int((court_y / 1163) * court_size[1])

            # Color basado en el equipo del jugador
            color = team_colors.get(player_teams.get(track_id, None), (0, 0, 0))  # Negro si no se conoce el equipo

            # Dibujar círculo relleno en la posición del jugador
            cv2.circle(img=court, 
                       center=(court_x, court_y), 
                       radius=20, 
                       color=color, 
                       thickness=-1)
            
            cv2.circle(img=court, 
                       center=(court_x, court_y), 
                       radius=20, 
                       color=(0, 0, 0), 
                       thickness=1)
        # Escribir el frame en el video de salida
        video_writer.write(court)

    video_writer.release()

def generate_court_overlay(tracks, video_frames, court_image_path, court_size):
    """ Genera los frames con el mapeo de posiciones de los jugadores en la cancha. """
    court_template = cv2.imread(court_image_path)
    court_template = cv2.resize(court_template, court_size)

    team_colors = {1: (255, 128, 0), 2: (0, 128, 255)}
    player_teams = {}

    for frame_tracks in tracks["players"]:
        for track_id, player_data in frame_tracks.items():
            track_id = int(track_id)
            if track_id not in player_teams:
                player_teams[track_id] = player_data.get("team", None)

    court_frames = []
    for frame_num, player_tracks in enumerate(tracks["players"]):
        court = court_template.copy()
        for track_id, player_data in player_tracks.items():
            track_id = int(track_id)
            court_position = player_data.get("court_position", None)
            if court_position is None or len(court_position) != 2:
                continue

            court_x, court_y = court_position
            court_x = int((court_x / 2000) * court_size[0])
            court_y = int((court_y / 1163) * court_size[1])

            color = team_colors.get(player_teams.get(track_id, None), (0, 0, 0))
            cv2.circle(court, (court_x, court_y), 20, color, -1)
            cv2.circle(court, (court_x, court_y), 20, (0, 0, 0), 1)

        court_frames.append(court)

    return court_frames

def calculate_transformers_per_frame(court_keypoint_detector_perframe, court_keypoint_detector, court_reference_points):
    """ Obtiene las homografías para cada frame utilizando keypoints detectados. """
    transformers_per_frame = [] # Lista de transformadores por cada frame
    for frame_num, keypoints_obj in enumerate(court_keypoint_detector_perframe):
        source_kp = keypoints_obj.xy.cpu().numpy()[0]  # Extraer coordenadas xy del frame

        # Aplicar filtro de keypoints válidos
        mask = (source_kp[:, 0] > 1) & (source_kp[:, 1] > 1)
        filtered_kp = source_kp[mask]  # Filtra los puntos válidos

        # Asociar keypoints detectados con puntos de referencia de la cancha
        matched_kp = court_keypoint_detector.match_keypoints(filtered_kp, court_reference_points)

        # Filtrar kp 
        valid_mask = matched_kp[:, 0] != -1
        filtered_kp = matched_kp[valid_mask]
        filtered_target = court_reference_points[valid_mask]

        # Verificar si hay al menos 4 puntos válidos
        if len(filtered_kp) < 4 or len(filtered_target) < 4:
            #print(f"[WARNING] Frame {frame_num}: No hay suficientes keypoints válidos ({len(filtered_kp)} detectados).")
            transformers_per_frame.append(None)  # Evita errores, pero permite continuar con otros frames
            continue

        # Crear homografía solo si hay suficientes puntos válidos
        try:
            transformer = ViewTransformer(source=filtered_kp.astype(np.float32), target=filtered_target.astype(np.float32))
            transformers_per_frame.append(transformer)
        except Exception as e:
            #print(f"[ERROR] Frame {frame_num}: Fallo al calcular homografía -> {e}")
            transformers_per_frame.append(None)
    return transformers_per_frame