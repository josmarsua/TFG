import cv2
import numpy as np
import random

def map_to_court(bbox, frame_size, court_size):
    """
    Mapea las coordenadas del bbox del jugador a las coordenadas de la pista
    """

    x1,y1,x2,y2 = bbox 
    center_x = (x1+x2) / 2
    center_y = (y1+y2) / 2

    frame_width, frame_height = frame_size
    court_width, court_height = court_size

    # Normalizacion
    normalized_x = center_x / frame_width
    normalized_y = center_y / frame_height

    # Escalar al tamaño de la pista
    court_x = int(normalized_x * court_width)
    court_y = int(normalized_y * court_height)

    return court_x, court_y

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

def draw_trajectories(tracks, video_frames, court_image_path, court_size, output_video_path, H):
    """
    Dibuja las trayectorias de los jugadores en un video en tiempo real usando una homografía predefinida.

    :param tracks: Diccionario con las posiciones de los jugadores.
    :param video_frames: Lista de frames del video.
    :param court_image_path: Ruta a la imagen de la cancha.
    :param court_size: Tamaño del boceto de la cancha (ancho, alto).
    :param output_video_path: Ruta donde se guardará el video resultante.
    :param H: Matriz de homografía para transformar las coordenadas.
    """
    # Cargar la imagen de la cancha
    court_template = cv2.imread(court_image_path)
    court_template = cv2.resize(court_template, court_size)

    trajectories = {}
    player_colors = {}

    # Configurar el VideoWriter para guardar el video
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = 24
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, court_size)

    # Generar colores únicos para cada jugador
    for frame_tracks in tracks["players"]:
        for track_id in frame_tracks.keys():
            track_id = int(track_id)
            if track_id not in player_colors:
                player_colors[track_id] = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )

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

            # Agregar posición transformada a la trayectoria
            trajectories[track_id].append((court_x, court_y))

        # Dibujar las trayectorias
        for track_id, points in trajectories.items():
            color = player_colors[track_id]

            for i in range(1, len(points)):
                cv2.line(court, points[i - 1], points[i], color, 2)

            # Dibujar posición actual
            if points:
                cv2.circle(court, points[-1], 5, color, -1)

        # Escribir el frame en el video de salida
        video_writer.write(court)

    video_writer.release()


