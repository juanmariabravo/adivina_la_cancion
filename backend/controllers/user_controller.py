from flask import Blueprint, request, jsonify
from services.user_service import UserService

# Crear Blueprint para rutas de usuarios
user_bp = Blueprint('user', __name__, url_prefix='/api/v1/auth')

# Instanciar servicio
user_service = UserService()


@user_bp.route('/register', methods=['POST'])
def register():
    """Registro de nuevo usuario"""
    payload, status = user_service.register(request.get_json())
    return jsonify(payload), status


@user_bp.route('/login', methods=['POST'])
def login():
    """Login de usuario"""
    payload, status = user_service.login(request.get_json())
    return jsonify(payload), status


@user_bp.route('/me', methods=['GET'])
def get_current_user():
    """Obtener información del usuario actual"""
    payload, status = user_service.get_current_user(request.headers.get('Authorization'))
    return jsonify(payload), status


@user_bp.route('/update-profile', methods=['PUT'])
def update_profile():
    """Actualizar perfil de usuario"""
    payload, status = user_service.update_profile(
        request.headers.get('Authorization'), 
        request.get_json()
    )
    return jsonify(payload), status
