from utils import read_video, save_video, get_metadata, calculate_transformers_per_frame, assign_teams, generate_court_overlay, combine_frames
from trackers import Tracker
import os
import numpy as np
from court_keypoint_detector import CourtKeypointDetector
from ball_possession import BallPossession

def process_video(input_video, output_video, court_image_path):
    """
    Procesar un video de un partido de baloncesto para realizar la lógica de detecciones,
    análisis y mapeo de posiciones.
    """
    # =======================
    # 1️⃣ CONFIGURACIÓN INICIAL
    # =======================
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if not os.path.exists(input_video) or not os.path.exists(court_image_path):
        raise FileNotFoundError("❌ Archivo de entrada o imagen de cancha no encontrado.")

    video_metadata = get_metadata(input_video)
    print(f"📹 Procesando video: {input_video} - {video_metadata.num_frames} frames")

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
    keypoint_model_path = os.path.join(base_dir, 'models', 'keypoint.pt')
    stub_path_kp = os.path.join(base_dir, 'stubs', 'track_stubskpnuevo2.pkl')

    court_keypoint_detector = CourtKeypointDetector(keypoint_model_path)
    court_keypoint_detector_perframe = court_keypoint_detector.get_court_keypoints(video_frames, 
                                                                                   read_from_stub=True,
                                                                                   stub_path=stub_path_kp)
   
    court_size = (2000, 1163)  # Dimensiones del boceto de la cancha [px]

    # Puntos referencia en el boceto de la cancha
    court_reference_points = np.array([[145,127],[145,181],[145,436],[145,727],[145,981],[145,1036],[491,436],[491,727],
                                       [1000,127],[1000,1036],
                                       [1855,127],[1855,181],[1855,436],[1855,727],[1855,981],[1855,1036],[1855,436],[1855,727]], dtype=np.float32)  # Coordenadas ideales de la cancha en la imagen de referencia
    
    #court_reference_points = np.array([[144,126],[144,182],[144,435],[144,728],[144,983],[144,1039],
    #                                   [404,182],[404,983],
    #                                   [491,435],[491,728],[599,582],
    #                                   [654,126],[672,582],[654,1039],
    #                                   [1000,126],[1000,1039],
    #                                   [1346,126],[1346,582],[1346,1039],
    #                                   [1508,435],[1383,582],[1508,728],
    #                                   [1596,182],[1596,983],
    #                                   [1855,126],[1855,182],[1855,435],[1855,728],[1855,983],[1855,1039]], dtype=np.float32)  # Coordenadas ideales de la cancha en la imagen de referencia 

    # Realizar transformaciones
    print("🏀 Realizando calculos para homografia...")
    transformers_per_frame = calculate_transformers_per_frame(court_keypoint_detector_perframe, court_keypoint_detector, court_reference_points)

    # =======================
    # 4️⃣ DETECCIÓN Y SEGUIMIENTO DE OBJETOS
    # =======================    
    tracker_model_path = os.path.join(base_dir, 'models', 'aisports.pt')
    stub_path = os.path.join(base_dir, 'stubs', 'track_stubsshortnuevo2.pkl')
    print("🏀 Detectando y trackeando objetos...")

    tracker = Tracker(tracker_model_path)
    tracks = tracker.get_object_tracks(video_frames, 
                                       transformers_per_frame, 
                                       read_from_stub=True, 
                                       stub_path=stub_path)

    # =======================
    # 5️⃣ INTERPOLACIÓN DEL BALÓN
    # =======================
    print("🏀 Interpolando posiciones del balon...")

    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

    # =======================
    # 6️⃣ ASIGNACIÓN DE EQUIPOS
    # =======================
    print("🏀 Asignando equipos...")

    tracks = assign_teams(video_frames, 
                          tracks)

    # =======================
    # 7️⃣ CALCULAR POSESIÓN
    # =======================
    print("🏀 Calculando posesion de balon...")

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
    # 8️⃣ DIBUJAR ANOTACIONES
    # =======================
    print("🏀 Dibujando anotaciones...")

    output_video_frames = tracker.draw_annotations(video_frames, tracks)
    output_video_frames = court_keypoint_detector.draw_court_keypoints(output_video_frames, court_keypoint_detector_perframe)
    

    # =======================
    # 9️⃣ GUARDAR VIDEOS
    # =======================
    print("🏀 Guardando video...")
    # Generar los frames del mapeo de la cancha y dibujar posesion
    court_frames = generate_court_overlay(tracks, video_frames, court_image_path, court_size)
    combined_frames = combine_frames(output_video_frames, court_frames)       
    combined_frames = ball_possession_detector.draw_possession(combined_frames,player_assignment,ball_possession)
    # Guardar el video 
    save_video(combined_frames, output_video, fps=video_metadata.fps)


