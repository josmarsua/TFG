from utils import frame_to_time

class PassDetector:
    def __init__(self, fps):
        self.fps = fps
        self.events = []

    def detect_passes(self, ball_possession, player_assignment):
        """
        Detecta pases entre jugadores del mismo equipo y guarda los eventos.
        """
        prev_holder = -1
        prev_frame = -1

        for frame_idx in range(1, len(ball_possession)):
            if ball_possession[frame_idx - 1] != -1:
                prev_holder = ball_possession[frame_idx - 1]
                prev_frame = frame_idx - 1

            current_holder = ball_possession[frame_idx]

            if prev_holder != -1 and current_holder != -1 and prev_holder != current_holder:
                prev_team = player_assignment[prev_frame].get(prev_holder, -1)
                current_team = player_assignment[frame_idx].get(current_holder, -1)

                if prev_team == current_team and prev_team != -1:
                    event = {
                        "type": "Pase",
                        "from_player_id": prev_holder,
                        "to_player_id": current_holder,
                        "time": frame_to_time(frame_idx, self.fps),
                        "frame": frame_idx
                    }
                    self.events.append(event)

    def get_events(self):
        return self.events
