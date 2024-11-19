from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner

def main():
    #Read video
    video_frames = read_video('acb.mp4')

    #Initialize Tracker
    tracker = Tracker('models/best.pt')
    
    #Run tracker
    tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path='stubs/track_stubs.pkl')

    #Interpolate Ball Positions
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"]
                                                        )
    #Assign Player Teams
    team_assinger = TeamAssigner()
    team_assinger.assign_team_color(video_frames[0],tracks['players'][0])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assinger.get_player_team(video_frames[frame_num],track['bbox'],player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assinger.team_colors[team]

    #Draw output
    ## Draw object tracks
    output_video_frames = tracker.draw_annotations(video_frames,tracks)

    #Save video
    save_video(output_video_frames, 'output.avi')

if __name__ == '__main__':
    main()