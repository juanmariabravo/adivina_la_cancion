from flask import Blueprint, request, jsonify
from services.game_service import GameService

# Crear Blueprint para rutas de juego
game_bp = Blueprint('game', __name__, url_prefix='/api/v1')

# Instanciar servicio
game_service = GameService()


@game_bp.route('/game/submit-score', methods=['POST'])
def update_score():
    """Actualizar puntuación del jugador"""
    payload, status = game_service.update_score(
        request.headers.get('Authorization'), 
        request.get_json()
    )
    return jsonify(payload), status


@game_bp.route('/ranking', methods=['GET'])
def get_ranking():
    """Obtener ranking de jugadores"""
    limit = request.args.get('limit', 10, type=int)
    payload, status = game_service.get_ranking(limit)
    return jsonify(payload), status


@game_bp.route('/game/daily/complete', methods=['POST'])
def complete_daily():
    """Marcar desafío diario como completado"""
    payload, status = game_service.complete_daily(request.headers.get('Authorization'))
    return jsonify(payload), status


@game_bp.route('/songs/<level_id>', methods=['GET'])
def get_level_song(level_id):
    """Obtener canción de un nivel específico"""
    payload, status = game_service.get_level_song(
        level_id, 
        request.headers.get('Authorization')
    )
    return jsonify(payload), status


@game_bp.route('/game/validate', methods=['POST'])
def validate_answer():
    """Validar respuesta del jugador"""
    data = request.get_json()
    lev = data.get('level_id')
    ans = data.get('answer')
    
    if game_service.validate_answer(lev, ans):
        return jsonify({"correct": True}), 200
    else:
        return jsonify({"correct": False}), 200


@game_bp.route('/game/mark-level-played', methods=['POST'])
def mark_level_played():
    """Marcar nivel como jugado"""
    data = request.get_json()
    auth_token = request.headers.get('Authorization')
    payload, status = game_service.mark_level_played(auth_token, data)
    return jsonify(payload), status
