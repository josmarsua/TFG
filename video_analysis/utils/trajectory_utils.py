import cv2
import numpy as np

def calculate_homography(video_points, court_points):
    """
    Calcula la matriz de homografía a partir de puntos en el video y sus correspondencias en la pista
    """
    video_points = np.array(video_points, dtype=np.float32)
    court_points = np.array(court_points, dtype=np.float32)

    #Calcular matriz homografia
    H, _ = cv2.findHomography(video_points, court_points)
    return H

def apply_homography(player_position, H):
    """
    Aplica la homografia para transformar las coordenadas de un jugador
    """
    player_position = np.array([player_position[0],player_position[1],1],dtype=np.float32).reshape(3,1)
    transformed_position = np.dot(H,player_position)
    transformed_position /= transformed_position[2] #Normalizar
    return int(transformed_position[0]), int(transformed_position[1])

def filter_outliers(points, max_distance=50):
    """
    Filtra puntos que están demasiado lejos del punto previo para evitar outliers.
    """
    if len(points) < 2:
        return points  # Nada que filtrar si hay menos de 2 puntos

    filtered_points = [points[0]]  # Mantener el primer punto
    for i in range(1, len(points)):
        prev_point = filtered_points[-1]
        curr_point = points[i]
        distance = np.sqrt((curr_point[0] - prev_point[0])**2 + (curr_point[1] - prev_point[1])**2)
        if distance <= max_distance:
            filtered_points.append(curr_point)

    return filtered_points

def smooth_trajectory(points, window_size=3):
    """
    Suaviza una trayectoria usando un filtro de media móvil
    """
    if len(points) < window_size:
        return points  # No se puede suavizar con menos puntos que el tamaño de la ventana

    smoothed_points = []
    for i in range(len(points)):
        start = max(0, i - window_size + 1)
        window = points[start:i + 1]
        avg_x = int(np.mean([p[0] for p in window]))
        avg_y = int(np.mean([p[1] for p in window]))
        smoothed_points.append((avg_x, avg_y))

    return smoothed_points

def validate_position(court_x, court_y, court_size):
    """
    Valida que la posición esté dentro de los límites de la cancha.
    """
    court_width, court_height = court_size
    return 0 <= court_x < court_width and 0 <= court_y < court_height

def draw_trajectories(tracks, video_frames, court_image_path, court_size, output_video_path, H):
    """
    Dibuja las trayectorias de los jugadores en un video en tiempo real usando una homografía predefinida
    """
    # Cargar la imagen de la cancha
    court_template = cv2.imread(court_image_path)
    court_template = cv2.resize(court_template, court_size)

    trajectories = {}

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

    # Dibujar las trayectorias cuadro a cuadro
    for frame_num, (frame, player_tracks) in enumerate(zip(video_frames, tracks["players"])):
        # Clonar la cancha para este frame
        court = court_template.copy()

        for track_id, player_data in player_tracks.items():
            track_id = int(track_id)

            if track_id not in trajectories:
                trajectories[track_id] = []

            bbox = player_data["bbox"]
            video_x = (bbox[0] + bbox[2]) / 2  # Centro del jugador en el video
            video_y = (bbox[1] + bbox[3]) / 2
            court_x, court_y = apply_homography((video_x, video_y), H)

            # Validar posición
            if not validate_position(court_x, court_y, court_size):
                continue

            # Agregar posición transformada a la trayectoria
            trajectories[track_id].append((court_x, court_y))

        # Dibujar las trayectorias
        for track_id, points in trajectories.items():
            # Filtrar outliers antes de dibujar la trayectoria
            points = filter_outliers(points)
            points = smooth_trajectory(points)
            color = team_colors.get(player_teams.get(track_id, None), (0, 0, 0))  # Negro si no se conoce el equipo

            for i in range(1, len(points)):
                cv2.line(court, points[i - 1], points[i], color, 2)
            if points:
                cv2.circle(court, points[-1], 5, color, -1)


        # Escribir el frame en el video de salida
        video_writer.write(court)

    video_writer.release()
