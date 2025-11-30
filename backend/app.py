from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from services.user_service import UserService
from services.spoti_service import SpotiService
from services.game_service import GameService

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar CORS de manera más explícita
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:4200", "http://127.0.0.1:4200"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuración desde variables de entorno
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 5000))

# Instanciar servicios (internamente usan db y env)
user_service = UserService()
spoti_service = SpotiService()
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


@app.route('/api/v1/game/submit-score', methods=['POST'])
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
    payload, status = spoti_service.get_authorization_token(code, client_id)
    return jsonify(payload), status


@app.route('/api/v1/songs/<level_id>', methods=['GET'])
def get_level_song(level_id):
    payload, status = game_service.get_level_song(level_id, request.headers.get('Authorization'))
    return jsonify(payload), status


@app.route('/api/v1/game/validate', methods=['POST'])
def validate_answer():
    lev = request.get_json().get('level_id')
    ans = request.get_json().get('answer')
    if game_service.validate_answer(lev, ans):
        return jsonify({"correct": True}), 200
    else:
        return jsonify({"correct": False}), 200

@app.route('/api/v1/game/mark-level-played', methods=['POST'])
def mark_level_played():
    data = request.get_json()
    auth_token = request.headers.get('Authorization')
    payload, status = game_service.mark_level_played(auth_token, data)
    return jsonify(payload), status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG_MODE)