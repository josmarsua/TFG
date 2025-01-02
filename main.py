from utils import read_video, save_video, draw_trajectories, calculate_homography
from trackers import Tracker
from team_assigner import TeamAssigner
import os

def process_video(input_video, output_video, trajectory_video_path, court_image_path):
    # Verifica si los archivos existen
    if not os.path.exists(input_video):
        raise FileNotFoundError(f"El archivo de entrada {input_video} no existe.")
    if not os.path.exists(court_image_path):
        raise FileNotFoundError(f"El archivo de imagen de la cancha {court_image_path} no existe.")

    # Leer vídeo
    video_frames = read_video(input_video)
    
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

    # Guardar vídeos y trayectorias
    save_video(output_video_frames, output_video)
    draw_trajectories(tracks, video_frames, court_image_path, court_size, trajectory_video_path, H)
