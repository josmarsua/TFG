import cv2
from typing import NamedTuple
from moviepy import VideoFileClip

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
    Guarda una lista de cuadros como un archivo de video MP4.
    """
    if not output_video_frames:
        raise ValueError("No hay cuadros para guardar.")

    height, width = output_video_frames[0].shape[:2]
    print(f"Guardando video con resolución: {width}x{height} a {fps} FPS.")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame in output_video_frames:
        if frame.shape[:2] != (height, width):
            raise ValueError("Los cuadros tienen dimensiones inconsistentes.")
        out.write(frame)

    out.release()
    print(f"Video guardado en: {output_video_path}")

def reprocesar_video_moviepy(input_path, output_path):
    """
    Reprocesa un video usando MoviePy para garantizar compatibilidad con navegadores.
    """
    try:
        clip = VideoFileClip(input_path)
        clip.write_videofile(
            output_path, codec="libx264", audio_codec="aac",
            temp_audiofile="temp-audio.m4a", remove_temp=True, preset="slow"
        )
        print(f"✅ Video reprocesado con éxito: {output_path}")
    except Exception as e:
        raise RuntimeError(f"❌ Error al reprocesar el video con MoviePy: {e}")