import cv2
from typing import NamedTuple
from moviepy import ImageSequenceClip
import numpy as np

class VideoMetadata(NamedTuple):
    fps: float
    num_frames: int
    width: int
    height: int

def get_metadata(video_path):
    """
    Obtiene los metadatos de un video, incluyendo FPS, número de cuadros, ancho y alto.
    """
    vc = cv2.VideoCapture(video_path)
    try:
        fps = vc.get(cv2.CAP_PROP_FPS)
        width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
        num_frames = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        return VideoMetadata(fps, num_frames, width, height)
    finally:
        vc.release()

def read_video(video_path):
    """
    Lee un video y devuelve una lista de cuadros.
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def save_video(output_video_frames, output_video_path, fps=24):
    """
    Guarda un video directamente en formato H.264 usando MoviePy para compatibilidad con navegadores.
    Esto evita el doble procesamiento (guardar con OpenCV y luego reprocesar con MoviePy).
    """
    if not output_video_frames:
        raise ValueError("No hay cuadros para guardar.")

    height, width = output_video_frames[0].shape[:2]
    print(f"Guardando video en formato H.264: {width}x{height} a {fps} FPS.")

    try:
        # Convertir frames de BGR (OpenCV) a RGB (MoviePy usa RGB)
        video_frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in output_video_frames]

        # Crear clip de video
        clip = ImageSequenceClip(video_frames_rgb, fps=fps)

        # Guardar en formato compatible
        clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac", preset="slow")

        print(f"✅ Video guardado con éxito en formato compatible: {output_video_path}")
    except Exception as e:
        raise RuntimeError(f"❌ Error al guardar el video con MoviePy: {e}")

def combine_frames(output_video_frames, court_frames):
    """
    Combina los cuadros de un video
    con los cuadros de un boceto de la cancha.
    """
    # Obtener dimensiones del video original y del boceto de la cancha
    video_height, video_width = output_video_frames[0].shape[:2]
    court_height, court_width = court_frames[0].shape[:2]

    # Definir nuevo ancho del boceto 
    court_new_width = video_width // 4  # Reduce el tamaño a 1/4 del ancho del video principal
    scale_factor = court_new_width / court_width  # Factor de escalado
    court_new_height = int(court_height * scale_factor)  # Mantener la proporción

    combined_frames = []
    for frame_num in range(len(output_video_frames)):
        if frame_num >= len(court_frames):
            break  

        main_frame = output_video_frames[frame_num]
        court_frame = court_frames[frame_num]
        # Redimensionar el boceto manteniendo la proporción
        court_frame_resized = cv2.resize(court_frame, (court_new_width, court_new_height))

        # Crear imagen de fondo blanco con las dimensiones del video original
        white_background = np.ones((video_height, court_new_width, 3), dtype=np.uint8) * 255

        # Calcular la posición para centrar la cancha en altura
        start_y = (video_height - court_new_height) // 2

        # Insertar el boceto en el fondo blanco
        white_background[start_y:start_y + court_new_height, :] = court_frame_resized

        # Combinar el video principal con el boceto más pequeño
        combined_frame = np.hstack((main_frame, white_background))

        combined_frames.append(combined_frame)

    return combined_frames