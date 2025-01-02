from flask import Flask, request, jsonify, send_file
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

    return jsonify({
        'processed_file': f"/download/processed_{filename}",
        'trajectory_file': f"/download/trajectory_{filename}"
    })

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if not os.path.exists(path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
