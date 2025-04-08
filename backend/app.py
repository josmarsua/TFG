import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

# Importar blueprints
from auth import auth_bp, db
from video_routes import video_bp

app = Flask(__name__)
CORS(app)  # Habilitar comunicación frontend-backend

# =======================
# CONFIGURACIÓN GENERAL
# =======================
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))
app.config['PROCESSED_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'processed'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Inicializar base de datos y JWT
jwt = JWTManager(app)
db.init_app(app)

# Registrar Blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(video_bp, url_prefix="/video")

# Servir imagenes estaticas
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

# Crear base de datos
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
