import cv2
import torch
from ultralytics import YOLO

# Cargar el modelo YOLO
model_path = "models/aisport.pt"  # Reemplaza con la ruta de tu modelo .pt
model = YOLO(model_path)

# Clases del modelo
class_names = ['basketball', 'net', 'player', 'referee']

# Configurar la fuente de video (cámara o archivo)
video_source = "emilio.mp4"  # Reemplaza con la ruta de un archivo de video si no usas cámara
cap = cv2.VideoCapture(video_source)

# Función para dibujar las cajas y nombres
def draw_predictions(frame, results):
    for result in results:
        boxes = result.boxes.xyxy.cpu().numpy()  # Coordenadas de las cajas (x1, y1, x2, y2)
        confidences = result.boxes.conf.cpu().numpy()  # Confianza de cada detección
        class_ids = result.boxes.cls.cpu().numpy().astype(int)  # IDs de las clases

        for box, conf, class_id in zip(boxes, confidences, class_ids):
            x1, y1, x2, y2 = map(int, box)
            label = f"{class_names[class_id]}: {conf:.2f}"
            color = (0, 255, 0)  # Color de la caja (verde)

            # Dibujar la caja y el texto
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# Loop de captura y detección
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Realizar la detección
    results = model(frame)  # Inferencia directa sobre el frame

    # Dibujar resultados
    draw_predictions(frame, results)

    # Mostrar el frame procesado
    cv2.imshow('YOLO Detections', frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()

 