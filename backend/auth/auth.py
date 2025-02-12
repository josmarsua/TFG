from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .database import db
from .users import User

auth_bp = Blueprint('auth',__name__)

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
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, 
                    email = email,
                    password_hash = hashed_password)
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
    current_username = get_jwt_identity()  # Obtiene el usuario actual desde el token

    user = User.query.filter_by(username=current_username).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({
        "username": user.username,
        "email": user.email
    }), 200