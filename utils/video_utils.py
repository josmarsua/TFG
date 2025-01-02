import cv2
from typing import NamedTuple


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

def get_frame(video_file, frame_num, height=0):
    """
    Obtiene un cuadro específico de un video, con la opción de cambiar su tamaño.
    """
    vc = cv2.VideoCapture(video_file)
    try:
        vc.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = vc.read()
        if not ret:
            raise ValueError(f"No se pudo obtener el cuadro {frame_num}")
        if height > 0:
            h, w, _ = frame.shape
            width = int(w * height / h)
            frame = cv2.resize(frame, (width, height))
    finally:
        vc.release()
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def cut_segment(video_file, out_file, start_frame, end_frame):
    """
    Extrae un segmento de un video entre dos cuadros dados y lo guarda en un nuevo archivo.
    """
    print(f'Extrayendo segmento: {out_file}')
    vc = cv2.VideoCapture(video_file)
    metadata = get_metadata(video_file)
    vo = cv2.VideoWriter(out_file, cv2.VideoWriter_fourcc(*'mp4v'),
                         metadata.fps, (metadata.width, metadata.height))

    vc.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    for _ in range(start_frame, end_frame):
        ret, frame = vc.read()
        if not ret:
            break
        vo.write(frame)

    vc.release()
    vo.release()

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

def select_points(video_path):
    """
    Permite seleccionar puntos en el primer cuadro de un video haciendo clic con el ratón.
    """
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Punto seleccionado: ({x}, {y})")
            points.append((x, y))

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Error al cargar el video.")
        return []

    cv2.imshow("Selecciona Puntos", frame)
    cv2.setMouseCallback("Selecciona Puntos", click_event)

    print("Haz clic en los puntos de referencia en el video.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cap.release()

    return points

