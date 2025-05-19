import cv2
from typing import NamedTuple
from moviepy import ImageSequenceClip
import numpy as np
import json

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
    Guarda un video en formato H.264 optimizado usando MoviePy para compatibilidad con navegadores.
    Usa multi-threading y ajustes eficientes para reducir el tiempo de procesamiento.
    """
    if not output_video_frames:
        raise ValueError("No hay cuadros para guardar.")

    height, width = output_video_frames[0].shape[:2]
    print(f"Guardando video en formato H.264: {width}x{height} a {fps} FPS.")

    try:
        # Convertir frames de BGR (OpenCV) a RGB en un solo paso con NumPy
        video_frames_rgb = [cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) for frame in output_video_frames]

        # Crear clip de video con MoviePy
        clip = ImageSequenceClip(video_frames_rgb, fps=fps)

        # Guardar en formato H.264 optimizado
        clip.write_videofile(
            output_video_path,
            codec="libx264",
            audio_codec="aac",
            preset="medium",  # Cambiado de "slow" a "medium" para más velocidad
            threads=4,  # Usa 4 hilos para acelerar la codificación
            ffmpeg_params=["-crf", "23", "-b:v", "1M"]  # Control de calidad y bitrate
        )

        print(f"✅ Video guardado con éxito en formato compatible: {output_video_path}")
    except Exception as e:
        raise RuntimeError(f"❌ Error al guardar el video con MoviePy: {e}")

def save_events(events, output_path):
    # Convertir correctamente los tipos
    def convert(obj):
        if isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        return obj

    with open(output_path, "w") as f:
        json.dump(events, f, default=convert)

def frame_to_time(frame_idx, fps):
    """
    Convierte el índice del frame y el fps en un string formato 'minuto:segundos'.
    """
    total_seconds = frame_idx / fps
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)

    return f"{minutes}:{seconds:02d}"

import cv2

def save_video2(output_video_frames, output_video_path, fps=24):
    """
    Guarda un video usando OpenCV (cv2.VideoWriter), escribiendo frame por frame sin cargar todo en memoria.
    Ideal para reducir consumo de RAM.
    """
    if not output_video_frames:
        raise ValueError("No hay cuadros para guardar.")

    height, width = output_video_frames[0].shape[:2]
    print(f"💾 Guardando video: {width}x{height} a {fps} FPS (OpenCV)...")

    # Define el códec y crea el objeto VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # usa 'XVID' o 'avc1' si 'mp4v' da problemas
    writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame in output_video_frames:
        writer.write(frame)  # BGR, no hace falta convertir

    writer.release()
    print(f"✅ Video guardado con éxito: {output_video_path}")
