from utils import read_video, save_video, draw_trajectories, calculate_homography, get_metadata
from trackers import Tracker
from team_assigner import TeamAssigner
import os
from moviepy import VideoFileClip

def reprocesar_video_moviepy(input_path, output_path):
    """
    Reprocesa un video usando MoviePy para garantizar compatibilidad con navegadores.
    """
    try:
        # Cargar el video
        clip = VideoFileClip(input_path)
        
        # Guardar en formato H.264
        clip.write_videofile(
            output_path,
            codec="libx264",  # Códec H.264
            audio_codec="aac",  # Códec de audio AAC
            temp_audiofile="temp-audio.m4a",  # Archivo temporal para el audio
            remove_temp=True,  # Elimina el archivo temporal después
            preset="slow"
        )
        print(f"Video reprocesado con éxito: {output_path}")
    except Exception as e:
        raise RuntimeError(f"Error al reprocesar el video con MoviePy: {e}")
def process_video(input_video, output_video, trajectory_video_path, court_image_path):
    # Verifica si los archivos existen
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"El archivo de entrada {input_video} no existe.")
    if not os.path.exists(court_image_path):
        raise FileNotFoundError(f"El archivo de imagen de la cancha {court_image_path} no existe.")

    # Obtener metadatos del video
    video_metadata = get_metadata(input_video)
    print(f"Procesando video: {input_video}")
    print(f"Metadatos: {video_metadata}")

    # Leer video
    video_frames = read_video(input_video)

    # Validar que los cuadros coincidan con los metadatos
    if len(video_frames) != video_metadata.num_frames:
        print(f"Advertencia: Se esperaban {video_metadata.num_frames} cuadros, pero se obtuvieron {len(video_frames)}.")

    # Datos de la cancha
    court_size = (800, 428)  # Dimensiones de la cancha
    video_points = [(567, 359), (1917, 447), (1916, 1074), (5, 894)]
    court_points = [(0, 0), (400, 0), (400, 428), (0, 428)]
    H = calculate_homography(video_points, court_points)

    # Tracker
    tracker = Tracker('models/aisport.pt')
    tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path='stubs/track_stubsshort.pkl')

    # Interpolación balón
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    # Asignar colores por equipo
    team_assigner = TeamAssigner()
    initial_frames = min(len(video_frames), 30) 
    for i in range(initial_frames):
        team_assigner.assign_team_color(video_frames[i], tracks['players'][i])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]

    # Dibujar detecciones
    output_video_frames = tracker.draw_annotations(video_frames, tracks)

    # Guardar videos y trayectorias
    save_video(output_video_frames, output_video, fps=video_metadata.fps)
    draw_trajectories(tracks, video_frames, court_image_path, court_size, trajectory_video_path, H)

    # Reprocesar videos con MoviePy
    compatible_output_video = output_video.replace(".mp4", "_compatible.mp4")
    reprocesar_video_moviepy(output_video, compatible_output_video)

    compatible_trajectory_video = trajectory_video_path.replace(".mp4", "_compatible.mp4")
    reprocesar_video_moviepy(trajectory_video_path, compatible_trajectory_video)
