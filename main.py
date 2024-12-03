from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
import cv2

def main():
    # Read video
    video_frames = read_video('nbashort.mp4')

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

if __name__ == "__main__":
    main()
