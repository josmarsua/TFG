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

# Ajustar el directorio raíz para apuntar correctamente a la carpeta principal del proyecto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Ruta al directorio video_analysis
video_analysis_dir = os.path.join(root_dir, 'video_analysis')
sys.path.append(video_analysis_dir)

# Ruta al archivo main.py dentro de video_analysis
main_file_path = os.path.join(video_analysis_dir, 'main.py')

# Cargar el archivo como un módulo
spec = importlib.util.spec_from_file_location("main", main_file_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)

# Uso la función para procesar el video desde main
process_video = main.process_video

# =======================
# SUBIR UN VIDEO
# =======================
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
    court_image_path = os.path.join(video_analysis_dir, 'boceto_pista.webp')  # Nueva ruta de la cancha

    try:
        process_video(input_path, output_video_path, trajectory_video_path, court_image_path)
    except Exception as e:
        app.logger.error(f"Error al procesar el video: {e}")
        return jsonify({'error': f'Error al procesar el video: {str(e)}'}), 500

    # Ajustar nombres de archivos compatibles (para previsualizacion)
    compatible_output_video = output_video_path.replace(".mp4", "_compatible.mp4")
    compatible_trajectory_video = trajectory_video_path.replace(".mp4", "_compatible.mp4")

    return jsonify({
        'processed_file': f"/processed/{os.path.basename(compatible_output_video)}",
        'trajectory_file': f"/processed/{os.path.basename(compatible_trajectory_video)}"
    })

# =======================
# DESCARGAR UN VIDEO
# =======================
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(path, as_attachment=True)

# =======================
# PREVISUALIZAR UN VIDEO
# =======================
@app.route('/processed/<filename>', methods=['GET'])
def serve_processed_video(filename):
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
