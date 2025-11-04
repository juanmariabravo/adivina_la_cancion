from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import game
from db.database import db
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para Angular

# Configuración desde variables de entorno
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "clave-secreta-desarrollo-fallback")
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 5000))

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not data or 'username' not in data or 'email' not in data or 'pwd1' not in data or 'pwd2' not in data:
            return jsonify({"error": "Faltan campos"}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        pwd1 = data['pwd1']
        pwd2 = data['pwd2']
        
        # Validaciones
        if len(username) < 3:
            return jsonify({"error": "El username debe tener al menos 3 caracteres"}), 400
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Email inválido"}), 400
        if pwd1 != pwd2:
            return jsonify({"error": "Las contraseñas no coinciden"}), 400
        if len(pwd1) < 6:
            return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
        
        # Crear usuario con feedback específico
        success, message = db.create_user(username, email, pwd1)
        
        if success:
            user = db.get_user_by_username(username)
            token = db.create_token(user)
            
            return jsonify({
                "message": message,
                "access_token": token,
                "token_type": "bearer",
                "user": user.to_public_dict()
            }), 201 # 201 means created
        else:
            # Retornar el mensaje específico de error
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email y contraseña requeridos"}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validar credenciales
        user = db.validate_credentials(email, password)
        if user:
            token = db.create_token(user)
            
            return jsonify({
                "message": "Login exitoso",
                "access_token": token,
                "token_type": "bearer",
                "user": user.to_public_dict()
            })
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/auth/me', methods=['GET'])
def get_current_user():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return jsonify({"error": "Token requerido"}), 401
        
        token = auth_header.split(' ')[1]
        user = db.verify_token(token)
        
        if user:
            return jsonify(user.to_public_dict())
        else:
            return jsonify({"error": "Token inválido"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/game/score', methods=['POST'])
def update_score():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return jsonify({"error": "Token requerido"}), 401
        
        token = auth_header.split(' ')[1]
        user = db.verify_token(token)
        
        if not user:
            return jsonify({"error": "Token inválido"}), 401
        
        data = request.get_json()
        if not data or 'score' not in data:
            return jsonify({"error": "Puntuación requerida"}), 400
        
        score = data['score']
        if db.update_user_score(user['username'], score):
            updated_user = db.get_user_by_username(user['username'])
            return jsonify({
                "message": "Puntuación actualizada",
                "total_score": updated_user['total_score'],
                "games_played": updated_user['games_played']
            })
        else:
            return jsonify({"error": "Error actualizando puntuación"}), 500
            
    except Exception as e:
        return jsonify({"error": "Error interno del servidor "+{e}}), 500

@app.route('/api/v1/ranking', methods=['GET'])
def get_ranking():
    try:
        limit = request.args.get('limit', 10, type=int)
        ranking = db.get_ranking(limit)
        
        return jsonify({
            "ranking": ranking
        })
    except Exception as e:
        return jsonify({"error": "Error interno del servidor "+{e}}), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Adivina la Canción API"})

@app.route('/api/v1/game/daily/complete', methods=['POST'])
def complete_daily():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return jsonify({"error": "Token requerido"}), 401
        
        token = auth_header.split(' ')[1]
        user = db.verify_token(token)
        
        if not user:
            return jsonify({"error": "Token inválido"}), 401
        
        if db.mark_daily_completed(user.username):
            return jsonify({
                "message": "Desafío diario completado",
                "last_daily_completed": datetime.now().strftime("%d-%m-%Y")
            })
        else:
            return jsonify({"error": "Error marcando daily como completado"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/auth/update-profile', methods=['PUT'])
def update_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return jsonify({"error": "Token requerido"}), 401
        
        token = auth_header.split(' ')[1]
        user = db.verify_token(token)
        
        if not user:
            return jsonify({"error": "Token inválido"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        new_username = data.get('username', '').strip()
        new_password = data.get('password', '').strip()
        
        # Validar username si se proporciona
        if new_username and len(new_username) < 3:
            return jsonify({"error": "El username debe tener al menos 3 caracteres"}), 400
        
        # Validar contraseña si se proporciona
        if new_password and len(new_password) < 6:
            return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400
        
        # Actualizar perfil
        success, message = db.update_user_profile(user.username, new_username, new_password)
        
        if success:
            # Obtener usuario actualizado (puede tener nuevo username)
            updated_user = db.get_user_by_username(new_username if new_username else user.username)
            
            # Si cambió el username, generar nuevo token
            new_token = None
            if new_username:
                new_token = db.create_token(updated_user)
            
            response = {
                "message": message,
                "user": updated_user.to_public_dict()
            }
            
            # Incluir nuevo token si se cambió el username
            if new_token:
                response["access_token"] = new_token
                response["token_type"] = "bearer"
            
            return jsonify(response)
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/levels/<int:level_id>/song', methods=['GET'])
def get_level_song(level_id):
    """Obtener LA canción de un nivel (una sola canción por nivel)"""
    try:
        song = db.get_song_by_level(level_id)
        if not song:
            return jsonify({"error": "No hay canción para este nivel"}), 404
        
        return jsonify({
            "song": song.to_dict(include_answer=False)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/game/validate', methods=['POST'])
def validate_answer():
    """Validar respuesta del usuario"""
    try:
        data = request.get_json()
        
        if not data or 'song_id' not in data or 'answer' not in data:
            return jsonify({"error": "Faltan campos"}), 400
        
        song_id = data['song_id']
        answer = data['answer']
        
        # Obtener canción
        song = db.get_song_by_id(song_id)
        if not song:
            return jsonify({"error": "Canción no encontrada"}), 404
        
        # Validar respuesta
        is_correct = game.validate_answer(song_id, answer)
        
        # Siempre devolver la respuesta si es correcta o si el usuario pide revelarla
        if is_correct or answer.upper() == 'REVEAL_ANSWER':
            return jsonify({
                "correct": is_correct,
                "answer": song.to_dict(include_answer=True)
            })
        else:
            return jsonify({
                "correct": False,
                "answer": None
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/game/song/<int:song_id>/reveal', methods=['GET'])
def reveal_song(song_id):
    """Revelar la respuesta correcta de una canción"""
    try:
        song = db.get_song_by_id(song_id)
        if not song:
            return jsonify({"error": "Canción no encontrada"}), 404
        
        return jsonify(song.to_dict(include_answer=True))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/game/submit-score', methods=['POST'])
def submit_score():
    """Enviar puntuación (requiere autenticación)"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            # Invitado - no guardar puntuación
            return jsonify({"message": "Puntuación no guardada (invitado)"}), 200
        
        token = auth_header.split(' ')[1]
        user = db.verify_token(token)
        
        if not user:
            return jsonify({"error": "Token inválido"}), 401
        
        data = request.get_json()
        if not data or 'score' not in data:
            return jsonify({"error": "Puntuación requerida"}), 400
        
        score = data['score']
        
        if db.update_user_score(user.username, score):
            updated_user = db.get_user_by_username(user.username)
            return jsonify({
                "message": "Puntuación guardada",
                "total_score": updated_user.total_score,
                "games_played": updated_user.games_played
            })
        else:
            return jsonify({"error": "Error guardando puntuación"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando Adivina la Canción API...")
    print("📊 Base de datos: SQLite")
    print(f"🌐 Servidor: http://localhost:{PORT}")
    print(f"🔧 Modo debug: {DEBUG_MODE}")
    app.run(debug=DEBUG_MODE, host='0.0.0.0', port=PORT)