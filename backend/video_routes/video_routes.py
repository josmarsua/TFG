import os
import re
import importlib.util
import sys
from flask import Blueprint, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request


video_bp = Blueprint('video', __name__)

# Ajustar el directorio raíz y cargar `main.py` desde `video_analysis`
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
video_analysis_dir = os.path.join(root_dir, 'video_analysis')
sys.path.append(video_analysis_dir)

main_file_path = os.path.join(video_analysis_dir, 'main.py')
spec = importlib.util.spec_from_file_location("main", main_file_path)
main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main)
process_video = main.process_video

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))
PROCESSED_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../processed'))

# =======================
# SUBIR UN VIDEO
# =======================
@video_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        video_bp.logger.error("No se envió ningún archivo en la solicitud.")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        video_bp.logger.error("El archivo enviado no tiene nombre.")
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    # Rutas de salida
    output_video_path = os.path.join(PROCESSED_FOLDER, f"processed_{filename}")
    trajectory_video_path = os.path.join(PROCESSED_FOLDER, f"trajectory_{filename}")
    court_image_path = os.path.join(video_analysis_dir, 'boceto_pista.webp')  # Nueva ruta de la cancha

    try:
        process_video(input_path, output_video_path, trajectory_video_path, court_image_path)
    except Exception as e:
        video_bp.logger.error(f"Error al procesar el video: {e}")
        return jsonify({'error': f'Error al procesar el video: {str(e)}'}), 500

    # Ajustar nombres de archivos compatibles (para previsualizacion)
    compatible_output_video = output_video_path.replace(".mp4", "_compatible.mp4")
    compatible_trajectory_video = trajectory_video_path.replace(".mp4", "_compatible.mp4")

    return jsonify({
        'processed_file': f"/video/download/{os.path.basename(compatible_output_video)}",
        'trajectory_file': f"/video/download/{os.path.basename(compatible_trajectory_video)}"
    })

@video_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'Archivo no encontrado'}), 404

    return send_file(
        path,
        as_attachment=True,  
        mimetype="application/octet-stream" 
    )

# =======================
# PREVISUALIZAR UN VIDEO
# =======================
@video_bp.route('/processed/<filename>', methods=['GET'])
def serve_processed_video(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
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
