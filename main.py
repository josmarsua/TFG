from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
import cv2
from utils import draw_trajectories, calculate_homography, select_points


def main():
    # Read video
    video_frames = read_video('nbashort.mp4')
    
    # Datos
    court_image_path = "boceto_pista.webp"
    court_size = (800,428) #Segun imagen de la pista
    trajectory_video_path = "trayectorias.mp4" #Ruta video salida trayectorias
    video_points = select_points('nbashort.mp4')
    court_points = select_points(court_image_path)  # Coordenadas en el boceto
    H = calculate_homography(video_points, court_points)

    # Initialize Tracker
    tracker = Tracker('models/aisport.pt')
    
    # Run tracker
    tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path='stubs/track_stubs.pkl')
    
    # Test crop visualization (optional, for debugging purposes)
    for track_id, player in tracks['players'][0].items():
        bbox = player['bbox']
        frame = video_frames[0]
        cropped_image = frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]
        cv2.imwrite(f'cropped_img_debug.jpg', cropped_image)
        break

    # Interpolate Ball Positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])
    
    # Assign Player Teams using multiple frames for better robustness
    team_assigner = TeamAssigner()
    initial_frames = min(len(video_frames), 30)  # Use up to 30 frames for initial color assignment
    for i in range(initial_frames):
        team_assigner.assign_team_color(video_frames[i], tracks['players'][i])

    # Assign teams to players in all frames
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]

    # Draw output
    # Draw object tracks
    output_video_frames = tracker.draw_annotations(video_frames, tracks)

    # Save video
    save_video(output_video_frames, 'output.avi')

    # Generate trajectories
    draw_trajectories(tracks, video_frames, court_image_path, court_size, trajectory_video_path,H)

if __name__ == "__main__":
    main()
