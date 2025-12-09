from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Importar Blueprints de los controladores
from controllers.user_controller import user_bp
from controllers.game_controller import game_bp
from controllers.spotify_controller import spotify_bp

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

# Registrar Blueprints
app.register_blueprint(user_bp)
app.register_blueprint(game_bp)
app.register_blueprint(spotify_bp)


# Ruta de health check
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "Adivina la Canción API"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG_MODE)