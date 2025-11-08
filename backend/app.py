from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from user_service import UserService
from game_service import GameService

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilitar CORS para Angular

# Configuración desde variables de entorno
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "clave-secreta-desarrollo-fallback")
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 5000))

# Instanciar servicios (internamente usan db y env)
user_service = UserService()
game_service = GameService()


@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    payload, status = user_service.register(request.get_json())
    return jsonify(payload), status


@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    payload, status = user_service.login(request.get_json())
    return jsonify(payload), status


@app.route('/api/v1/auth/me', methods=['GET'])
def get_current_user():
    payload, status = user_service.get_current_user(request.headers.get('Authorization'))
    return jsonify(payload), status


@app.route('/api/v1/game/score', methods=['POST'])
def update_score():
    payload, status = game_service.update_score(request.headers.get('Authorization'), request.get_json())
    return jsonify(payload), status


@app.route('/api/v1/ranking', methods=['GET'])
def get_ranking():
    limit = request.args.get('limit', 10, type=int)
    payload, status = game_service.get_ranking(limit)
    return jsonify(payload), status


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Adivina la Canción API"}), 200


@app.route('/api/v1/game/daily/complete', methods=['POST'])
def complete_daily():
    payload, status = game_service.complete_daily(request.headers.get('Authorization'))
    return jsonify(payload), status


@app.route('/api/v1/auth/update-profile', methods=['PUT'])
def update_profile():
    payload, status = user_service.update_profile(request.headers.get('Authorization'), request.get_json())
    return jsonify(payload), status


@app.route('/api/v1/spoti/getClientId', methods=['GET'])
def get_spotify_client_id():
    payload, status = user_service.get_spotify_client_id(request.args.get('email'))
    return jsonify(payload), status


@app.route('/api/v1/spoti/getAuthorizationToken', methods=['GET'])
def get_spotify_authorization_token():
    code = request.args.get('code')
    client_id = request.args.get('clientId')
    payload, status = user_service.exchange_spotify_authorization(code, client_id, request.headers.get('Authorization'))
    return jsonify(payload), status


@app.route('/api/v1/levels/<int:level_id>/song', methods=['GET'])
def get_level_song(level_id):
    payload, status = game_service.get_level_song(level_id, request.headers.get('Authorization'))
    return jsonify(payload), status


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG_MODE)