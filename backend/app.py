import re
from flask import Flask, request, jsonify, send_file, Response
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
import importlib.util
import sys

app = Flask(__name__)
CORS(app)  # Habilitar comunicación frontend-backend

# Configuración de carpetas
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
app.config['PROCESSED_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'processed'))

# Crear las carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Agregar el directorio raíz al sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

# Ruta al archivo main.py
main_file_path = os.path.join(root_dir, 'main.py')

# Cargar el archivo como un módulo
spec = importlib.util.spec_from_file_location("main", main_file_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

# Ahora puedes usar las funciones de main.py, como process_video
process_video = main.process_video

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error("No se envió ningún archivo en la solicitud.")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("El archivo enviado no tiene nombre.")
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(input_path)

    # Rutas de salida
    output_video_path = os.path.join(app.config['PROCESSED_FOLDER'], f"processed_{filename}")
    trajectory_video_path = os.path.join(app.config['PROCESSED_FOLDER'], f"trajectory_{filename}")
    court_image_path = os.path.join(root_dir, 'boceto_pista.webp')  # Ruta de la imagen de la cancha

    try:
        # Llamar a process_video con todos los argumentos necesarios
        process_video(input_path, output_video_path, trajectory_video_path, court_image_path)
    except Exception as e:
        app.logger.error(f"Error al procesar el video: {e}")
        return jsonify({'error': f'Error al procesar el video: {str(e)}'}), 500

    # Ajustar nombres de archivos compatibles
    compatible_output_video = output_video_path.replace(".mp4", "_compatible.mp4")
    compatible_trajectory_video = trajectory_video_path.replace(".mp4", "_compatible.mp4")

    return jsonify({
        'processed_file': f"/processed/{os.path.basename(compatible_output_video)}",
        'trajectory_file': f"/processed/{os.path.basename(compatible_trajectory_video)}"
    })

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(path, as_attachment=True)

@app.route('/processed/<filename>', methods=['GET'])
def serve_processed_video(filename):
    """
    Ruta para servir videos directamente desde la carpeta 'processed'.
    Maneja solicitudes de rango de bytes para reproducción de video.
    """
    path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404

    range_header = request.headers.get('Range', None)
    size = os.path.getsize(path)
    byte1, byte2 = 0, size - 1

    if range_header:
        # Parsear el rango solicitado
        match = re.search(r'(\d+)-(\d*)', range_header)
        if match:
            byte1 = int(match.group(1))
            if match.group(2):
                byte2 = int(match.group(2))

    length = byte2 - byte1 + 1
    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    response = Response(data, 206)
    response.headers.add('Content-Type', 'video/mp4')
    response.headers.add('Content-Range', f'bytes {byte1}-{byte2}/{size}')
    response.headers.add('Accept-Ranges', 'bytes')

    return response

if __name__ == '__main__':
    app.run(debug=True)
