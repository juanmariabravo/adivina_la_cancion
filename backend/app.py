from flask import Flask, jsonify, request
from flask_cors import CORS
from dao.user_dao import UserDAO

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde cualquier origen (necesario para Angular)
CORS(app)

user_dao = UserDAO()  # Instancia global (en memoria)

@app.route('/api/v1/register', methods=['POST'])
def register():
    """
    Endpoint para registrar un nuevo usuario.
    Recibe username, email y contraseña en formato JSON.
    """

    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    pwd1 = data.get('pwd1') or ''
    pwd2 = data.get('pwd2') or ''

    if not username or not email or not pwd1 or not pwd2:
        return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400
    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"success": False, "message": "Email inválido"}), 400
    if pwd1 != pwd2:
        return jsonify({"success": False, "message": "Las contraseñas no coinciden"}), 400
    if len(pwd1) < 6:
        return jsonify({"success": False, "message": "Password mínimo 6 caracteres"}), 400
    if user_dao.exists_username(username) or user_dao.exists_email(email):
        return jsonify({"success": False, "message": "Usuario ya existe"}), 409

    created = user_dao.create_user(username, email, hash(pwd1))
    if not created:
        return jsonify({"success": False, "message": "No se pudo crear el usuario"}), 500

    print(f"Nuevo usuario registrado: {username} ({email})")
    return jsonify({"success": True, "message": "Registro exitoso", "user": username}), 201

if __name__ == '__main__':
    # Ejecuta el servidor en modo debug en el puerto 5000
    # Asegúrate de que Flask esté instalado: pip install Flask flask-cors
    print("Servidor Flask corriendo en http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)