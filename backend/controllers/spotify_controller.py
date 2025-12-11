from flask import Blueprint, request, jsonify
from services.user_service import UserService
from services.spoti_service import SpotiService

# Crear Blueprint para rutas de Spotify
spotify_bp = Blueprint('spotify', __name__, url_prefix='/api/v1/spoti')

# Instanciar servicios
user_service = UserService()
spoti_service = SpotiService()


@spotify_bp.route('/getClientId', methods=['GET'])
def get_spotify_client_id():
    """Obtener Client ID de Spotify del usuario"""
    payload, status = user_service.get_spotify_client_id(request.args.get('email'))
    return jsonify(payload), status


@spotify_bp.route('/getAuthorizationToken', methods=['GET'])
def get_spotify_authorization_token():
    """Obtener token de autorización de Spotify"""
    code = request.args.get('code')
    client_id = request.args.get('clientId')
    
    if not code or not client_id:
        return jsonify({"error": "Faltan parámetros requeridos"}), 400
    
    payload, status = spoti_service.get_authorization_token(code, client_id)
    return jsonify(payload), status
