from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .database import db
from .users import User
from werkzeug.utils import secure_filename
import os
import sys

auth_bp = Blueprint('auth',__name__)
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))

# ===================
# REGISTRO DE USUARIO
# ===================

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "El usuario ya existe"}),400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya existe"}),400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, 
                    email = email,
                    password_hash = hashed_password,
                    profile_picture="../uploads/default_profile.webp")
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message":"Usuario registrado satisfactoriamente"}), 201

# ===================
# LOGIN DE USUARIO
# ===================

@auth_bp.route('/login',methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity=username)
        return jsonify({"token": access_token}), 200

    return jsonify({"error": "Credenciales incorrectas"}), 401

# ===========================
# OBTENER PERFIL DEL USUARIO
# ===========================
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email,
        "profile_picture": user.profile_picture
        
    }), 200


# ===========================
# ACTUALIZAR PERFIL DEL USUARIO
# ===========================
@auth_bp.route('/update-profile', methods=['POST'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()

    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    new_username = request.form.get('username', user.username)
    new_email = request.form.get('email', user.email)

    # Verificar si el nuevo username ya existe y pertenece a otro usuario
    existing_user = User.query.filter(User.username == new_username, User.username != current_user).first()
    if existing_user:
        return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

    # Verificar si el nuevo email ya existe en otro usuario
    existing_email = User.query.filter(User.email == new_email, User.username != current_user).first()
    if existing_email:
        return jsonify({"error": "El correo electrónico ya está en uso"}), 400

    # Actualizar datos solo si no están en uso
    user.username = new_username
    user.email = new_email

    if 'password' in request.form and request.form['password']:
        user.password_hash = generate_password_hash(request.form['password'])

   # Manejo de la imagen de perfil
    if 'profile_picture' in request.files:
        profile_picture = request.files['profile_picture']
        if profile_picture.filename != '':
            # Extraer extensión del archivo original
            extension = os.path.splitext(profile_picture.filename)[1].lower()
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

            # Verificar si la extensión es válida
            if extension not in allowed_extensions:
                return jsonify({"error": "Formato de imagen no permitido"}), 400

            # Crear nombre seguro con la extensión original
            filename = secure_filename(f"{user.username}_profile{extension}")
            profile_picture_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_picture.save(profile_picture_path)
            user.profile_picture = filename  # Guardar solo el nombre del archivo en la BD
    
    db.session.commit()
    return jsonify({
        "message": "Perfil actualizado correctamente",
        "profile_picture": user.profile_picture 
    }), 200
