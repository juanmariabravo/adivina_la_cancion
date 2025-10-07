from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/pista')
def pista():
    return jsonify({
        "audio": "https://ejemplo.com/audio.mp3",
        "imagen": "https://ejemplo.com/imagen.jpg",
        "dato": "Año de lanzamiento: 2005"
    })

if __name__ == '__main__':
    app.run(debug=True)
