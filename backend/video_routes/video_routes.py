import os
import re
import importlib.util
import sys
from flask import Blueprint, request, jsonify, send_file, Response
from werkzeug.utils import secure_filename

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
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_video_path = os.path.join(PROCESSED_FOLDER, f"processed_{filename}")
    trajectory_video_path = os.path.join(PROCESSED_FOLDER, f"trajectory_{filename}")
    court_image_path = os.path.join(video_analysis_dir, 'boceto_pista.webp')

    try:
        process_video(input_path, output_video_path, trajectory_video_path, court_image_path)
    except Exception as e:
        return jsonify({'error': f'Error al procesar el video: {str(e)}'}), 500

    return jsonify({
        'processed_file': f"/video/processed/{os.path.basename(output_video_path)}",
        'trajectory_file': f"/video/processed/{os.path.basename(trajectory_video_path)}"
    })

# =======================
# DESCARGAR UN VIDEO
# =======================
@video_bp.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(path, as_attachment=True)

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
