from team_assigner import TeamAssigner

def assign_teams(video_frames, tracks):
    """ Asigna equipos a los jugadores usando KMeans clustering. """
    team_assigner = TeamAssigner()
    for i in range(min(len(video_frames), 50)):  # Analizar los primeros 50 frames
        team_assigner.assign_team_color(video_frames[i], tracks['players'][i])

    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
            
    return tracks