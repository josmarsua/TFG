from ultralytics import YOLO
import cv2
import cvzone
import math
 

cap = cv2.VideoCapture("video.mp4")  # For Video
 
model = YOLO("best.pt")
 
classNames = ['Ball', 'Hoop', 'Period', 'Player', 'Ref', 'Shot Clock', 'Team Name', 'Team Points', 'Time Remaining', 'player']

# Definir colores para cada clase
colors = {
    'Ball': (0, 255, 0),         # Verde
    'Hoop': (255, 0, 0),         # Azul
    'Period': (0, 255, 255),     # Amarillo
    'Player': (255, 165, 0),     # Naranja
    'Ref': (255, 0, 255),        # Fucsia
    'Shot Clock': (0, 128, 255), # Naranja claro
    'Team Name': (0, 0, 255),    # Rojo
    'Team Points': (128, 0, 128),# Púrpura
    'Time Remaining': (0, 255, 128) # Verde claro
}

# Tamaño de la pantalla
screen_width = 1366  
screen_height = 768

while True:
    ret, frame = cap.read()
    
    if not ret:
        break  # Salir si el video termina

    # Redimensionar el frame al tamaño de la pantalla
    frame_resized = cv2.resize(frame, (screen_width, screen_height))

    # Realizar detección en el frame redimensionado
    results = model(frame_resized)

    # Obtener las cajas de detección para cada frame
    for result in results:
        for box in result.boxes:
            # Extraer coordenadas y datos de la caja
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordenadas de la caja
            conf = box.conf.item()                  # Confianza de la detección
            class_id = int(box.cls.item())          # ID de la clase detectada
            class_name = classNames[class_id]       # Nombre de la clase detectada

            # Obtener el color según la clase
            color = colors.get(class_name, (255, 255, 255))  

            # Dibujar el rectángulo con el color correspondiente
            cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)

            # Colocar el nombre de la clase y la confianza sobre el rectángulo
            cvzone.putTextRect(frame_resized, f'{class_name} {conf:.2f}', (x1, y1 - 10), scale=1, thickness=2, colorR=color, offset=5)

    # Mostrar el video redimensionado
    cv2.imshow("Basketball Detection", frame_resized)

    # Salir del bucle si se presiona 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()