from flask import Flask, jsonify
from flask_cors import CORS # Necesario para permitir peticiones desde Angular

# Inicialización de la aplicación Flask
app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde cualquier origen (necesario para Angular)
CORS(app) 

@app.route('/api/saludo', methods=['GET'])
def saludo():
    """
    Endpoint de prueba que devuelve un mensaje JSON.
    """
    print("Petición recibida en /api/saludo")
    
    # Simula una respuesta de la base de datos o lógica de negocio
    data = {
        "mensaje": "¡Hola desde Flask si funciona!",
        "timestamp": "2025-10-07T15:43:00Z",
        "servidor": "Python/Flask"
    }
    
    # Devuelve la respuesta en formato JSON
    return jsonify(data)

if __name__ == '__main__':
    # Ejecuta el servidor en modo debug en el puerto 5000
    # Asegúrate de que Flask esté instalado: pip install Flask flask-cors
    print("Servidor Flask corriendo en http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)