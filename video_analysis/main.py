from utils import read_video, save_video, get_metadata, assign_teams
from trackers import Tracker
import os
import numpy as np
from court_keypoint_detector import CourtKeypointDetector
from ball_possession import BallPossession
from view_transformer import Transformer
import json
from shot_detector import ScoreDetector
import cv2 

def process_video(input_video, output_video, court_image_path, status_path):
    """
    Procesar un video de un partido de baloncesto para realizar la lógica de detecciones,
    análisis y mapeo de posiciones.
    """
    def set_status(msg, progress=None):
        status = {"step": msg}
        if progress is not None:
            status["progress"] = progress
        with open(status_path, "w") as f:
            json.dump(status, f)

    # =======================
    # 1️⃣ CONFIGURACIÓN INICIAL
    # =======================
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(input_video) or not os.path.exists(court_image_path):
        raise FileNotFoundError("❌ Archivo de entrada o imagen de cancha no encontrado.")

    video_metadata = get_metadata(input_video)
    print(f"📹 Procesando video: {input_video} - {video_metadata.num_frames} frames")
    set_status(f"📹 Procesando video: {input_video} - {video_metadata.num_frames} frames", 5)
    # =======================
    # 2️⃣ LECTURA DE VIDEO
    # =======================
    video_frames = read_video(input_video)

    if len(video_frames) != video_metadata.num_frames:
        print(f"⚠️ Advertencia: {len(video_frames)} frames obtenidos, se esperaban {video_metadata.num_frames}.")

    # =======================
    # 3️⃣ DETECCIÓN DE PUNTOS CLAVE DE LA CANCHA
    # =======================
    print("🏀 Detectando puntos clave de la cancha...")
    set_status("🏀 Detectando puntos clave de la cancha...", 10)
    keypoint_model_path = os.path.join(base_dir, 'models', 'keypoint.pt')
    stub_path_kp = os.path.join(base_dir, 'stubs', 'track_stubskpnuevo5.pkl')

    court_keypoint_detector = CourtKeypointDetector(keypoint_model_path)
    court_keypoint_detector_perframe = court_keypoint_detector.get_court_keypoints(video_frames, 
                                                                                   read_from_stub=True,
                                                                                   stub_path=stub_path_kp)
   
    
    # =======================
    # 4️⃣ DETECCIÓN Y SEGUIMIENTO DE OBJETOS
    # =======================    
    tracker_model_path = os.path.join(base_dir, 'models', 'aisports.pt')
    stub_path = os.path.join(base_dir, 'stubs', 'track_stubsshortnuevo5.pkl')
    print("🏃‍♂️ Detectando y trackeando objetos...")
    set_status("🏃‍♂️ Detectando y trackeando objetos...", 20)
    tracker = Tracker(tracker_model_path)
    tracks = tracker.get_object_tracks(video_frames, 
                                       read_from_stub=True, 
                                       stub_path=stub_path)

    # =======================
    # 5️⃣ INTERPOLACIÓN DEL BALÓN
    # =======================
    print("🏀 Interpolando posiciones del balon...")
    set_status("🏀 Interpolando posiciones del balon...", 35)
    tracks["ball"] = tracker.interpolate_ball_tracks(tracks["ball"])

    # =======================
    # 6️⃣ ASIGNACIÓN DE EQUIPOS
    # =======================
    print("⛹️ Asignando equipos...")
    set_status("⛹️ Asignando equipos...", 40)
    tracks = assign_teams(video_frames, 
                          tracks)

    # =======================
    # 7️⃣ MAPEO DE POSICIONES
    # =======================
    print("📍 Realizando calculos para homografia...")
    set_status("📍 Realizando cálculos para homografia...", 55)
    transformer = Transformer(court_image_path)
    court_keypoint_detector_perframe = transformer.validate_kp(court_keypoint_detector_perframe)
    court_player_positions = transformer.transform_players(court_keypoint_detector_perframe, tracks["players"])
    
    # =======================
    # 8️⃣ CALCULAR POSESIÓN
    # =======================
    print("🎯 Calculando posesion de balon...")
    set_status("🎯 Calculando posesion de balon...", 60)
    ball_possession_detector = BallPossession()
    ball_possession = ball_possession_detector.detect_ball_possession(tracks['players'],tracks["ball"])

    # Construir player_assignment a partir de tracks:
    player_assignment = []
    for frame_players in tracks['players']:
        # Para cada frame, creamos un diccionario {player_id: team}
        assignment = {player_id: info.get('team', -1) 
                    for player_id, info in frame_players.items()}
        player_assignment.append(assignment)


    # =======================
    # 9️⃣ DIBUJAR ANOTACIONES
    # =======================

    print("🏀 Detectando canastas...")
    set_status("🏀 Detectando canastas...", 65)

    score_detector = ScoreDetector()
    score_frames = score_detector.detect_scores(tracks["ball"], tracks["net"])
   

    # =======================
    # 🎨 DIBUJAR ANOTACIONES
    # =======================
    print("🎨 Dibujando anotaciones...")
    set_status("🎨 Dibujando anotaciones...", 70)

    output_video_frames = tracker.draw_annotations(video_frames, tracks)
    set_status("🎨 Dibujando anotaciones...", 75)
    output_video_frames = court_keypoint_detector.draw_court_keypoints(output_video_frames, court_keypoint_detector_perframe)
    set_status("🎨 Dibujando anotaciones...", 80)
    output_video_frames = transformer.draw_court_overlay(output_video_frames, 
                                          transformer.court_pic_path, 
                                          transformer.width, 
                                          transformer.height, 
                                          transformer.key_points,
                                          court_player_positions,
                                          player_assignment,
                                          ball_possession)      
    
    output_video_frames = ball_possession_detector.draw_possession(output_video_frames,
                                                                   player_assignment,
                                                                   ball_possession)
    
    output_video_frames = score_detector.draw_scores_on_frames(output_video_frames, score_frames)

    # =======================
    # 💾 GUARDAR VIDEOS
    # =======================
    print("💾 Guardando video...")
    set_status("💾 Guardando video...", 85)
    
    # Guardar el video 
    save_video(output_video_frames, output_video, fps=video_metadata.fps)
    set_status("✅ Video procesado", 100)
