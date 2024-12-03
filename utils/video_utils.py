import cv2

def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break #Salir si el video termina
        frames.append(frame)
    return frames

def save_video(output_video_frames, output_video_path):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (output_video_frames[0].shape[1],output_video_frames[0].shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()


def select_points(video_path):
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"Selected point: ({x}, {y})")
            points.append((x, y))

    # Cargar el primer frame del video
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Error al cargar el video.")
        return []

    # Mostrar el frame
    cv2.imshow("Select Points", frame)
    cv2.setMouseCallback("Select Points", click_event)

    # Esperar a que selecciones los 4 puntos
    print("Haz clic en los 4 puntos de referencia en el video.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cap.release()

    return points
