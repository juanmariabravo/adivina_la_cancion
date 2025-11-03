from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from db.database import db
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Habilitar CORS para Angular

# Configuración
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "clave-secreta-desarrollo")

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
        
        # Crear usuario
        if db.create_user(username, email, pwd1):
            user = db.get_user_by_username(username)
            token = db.create_token(user)
            
            return jsonify({
                "message": "Usuario creado exitosamente",
                "access_token": token,
                "token_type": "bearer",
                "user": user.to_public_dict()
            }), 201 # 201 means created
        else:
            return jsonify({"error": "El username o email ya existen"}), 400
            
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
        if not auth_header or not auth_header.startswith('bearer '):
            return jsonify({"error": "Token requerido"}), 401
        
        token = auth_header.split(' ')[1]
        user = db.verify_token(token)
        
        if user:
            return jsonify(user.to_public_dict())
        else:
            return jsonify({"error": "Token inválido"}), 401
            
    except Exception as e:
        return jsonify({"error": {e}}), 500

@app.route('/api/v1/game/score', methods=['POST'])
def update_score():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
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
        if not auth_header or not auth_header.startswith('Bearer '):
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

if __name__ == '__main__':
    print("🚀 Iniciando Adivina la Canción API...")
    print("📊 Base de datos: SQLite")
    print("🌐 Servidor: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)