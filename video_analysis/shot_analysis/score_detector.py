import supervision as sv

class ScoreDetector:
    def __init__(self, display_duration=20):
        """
        Inicializa el detector de puntuaciones.
        :param display_duration: Número de frames que se mostrará el cartel de "FIELD GOAL MADE"
        """
        self.display_duration = display_duration
        self.last_score_frame = -999  # Para recordar cuándo fue la última canasta

    def is_inside_net(self, point, bbox):
        """
        Verifica si un punto (x, y) está dentro de un bbox.
        """
        x, y = point
        x1, y1, x2, y2 = bbox
        return x1 <= x <= x2 and y1 <= y <= y2

    def detect_scores(self, ball_tracks, net_tracks):
        """
        Devuelve una lista con 1 si hay canasta (o se está mostrando), 0 en otro caso.
        """
        scores = [0] * len(ball_tracks)
        prev_inside = False

        for frame_idx, (ball_info, net_info) in enumerate(zip(ball_tracks, net_tracks)):
            ball_bbox = ball_info.get(1, {}).get("bbox", None)
            if not ball_bbox or not net_info:
                prev_inside = False
                continue

            # Centro del balón
            cx = (ball_bbox[0] + ball_bbox[2]) / 2
            cy = (ball_bbox[1] + ball_bbox[3]) / 2
            ball_center = (cx, cy)

            # Verificar si entra en alguna de las redes detectadas en este frame
            inside_any_net = any(self.is_inside_net(ball_center, net["bbox"]) for net in net_info.values())

            # Transición: fuera → dentro ⇒ canasta
            if inside_any_net and not prev_inside:
                self.last_score_frame = frame_idx

            # Mostrar cartel si estamos dentro del rango de visualización
            if frame_idx - self.last_score_frame < self.display_duration:
                scores[frame_idx] = 1

            prev_inside = inside_any_net

        return scores
    
    def draw_scores_on_frames(self, video_frames, score_flags):
        """
        Dibuja "FIELD GOAL MADE" con fondo blanco y estilo dinámico usando Supervision
        en la esquina superior izquierda.
        """
        output_frames = []

        for frame_idx, frame in enumerate(video_frames):
            frame = frame.copy()

            if score_flags[frame_idx] == 1:
                text = "FIELD GOAL MADE"

                frame_height, frame_width = frame.shape[:2]

                # Estilo dinámico
                font_scale = sv.calculate_optimal_text_scale((frame_width, frame_height))
                thickness = sv.calculate_optimal_line_thickness((frame_width, frame_height))

                # Posición (esquina superior izquierda)
                anchor = sv.Point(
                    x=int(frame_width * 0.1),   # 20% desde la izquierda
                    y=int(frame_height * 0.05)  # 5% desde arriba
                )

                # Dibujo con fondo blanco y texto verde
                frame = sv.draw_text(
                    scene=frame,
                    text=text,
                    text_anchor=anchor,
                    text_color=sv.Color.from_hex("#00B000"),     # Verde fuerte
                    background_color=sv.Color.WHITE,
                    text_scale=font_scale,
                    text_thickness=thickness
                )

            output_frames.append(frame)

        return output_frames
