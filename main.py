from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
import cv2
from utils import draw_trajectories, calculate_homography, select_points
import numpy as np

def main():
    #Rutas
    input_video = "nbashort.mp4"
    output_video = "output_videos/detecciones.mp4"
    #trajectory_video_path = "output_videos/trayectorias.mp4" #Ruta video salida trayectorias
    #court_image_path = "boceto_pista.webp"
    
    # Leer vídeo
    video_frames = read_video(input_video)
    
    # Datos
    #court_size = (800,428) #Segun imagen de la pista
    #video_points = [(567,359),(1917,447),(1916,1074),(5,894)]#select_points(input_video)
    #court_points = [(0,0),(400,0),(400,428),(0,428)] #select_points(court_image_path)  
    #H = calculate_homography(video_points, court_points)

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

    # Guardar vídeo y trayectorias
    save_video(output_video_frames, output_video)
    #draw_trajectories(tracks, video_frames, court_image_path, court_size, trajectory_video_path,H)

if __name__ == "__main__":
    main()
