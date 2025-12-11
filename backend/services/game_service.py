from difflib import SequenceMatcher
from database.database import db
from dotenv import load_dotenv
import os
import json
import random
import re

from helpers.spotify_helper import SpotifyHelper

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

class GameService:
    def __init__(self):
        self.set_daily_song()

    def set_daily_song(self):
        # Cargar lista de canciones para el desafío diario desde JSON está en backend/songs_local_data&spotify_ids/possible_daily_songs.json
        json_path = os.path.join(os.path.dirname(__file__), '..', 'songs_local_data&spotify_ids', 'possible_daily_songs.json')
        try:
            with open(json_path, 'r') as f:
                self.daily_songs = json.load(f)
        except Exception as e:
            print(f"Error cargando canciones diarias: {e}")
            # Fallback a una lista mínima si falla la carga
            self.daily_songs = ["4blQLWBwNYjL3Z0x8ctMBq"]
            
        self.daily_song_id = random.choice(self.daily_songs)
        print(f"Canción del día seleccionada: {self.daily_song_id}")
        db.delete_daily_songs()
        db.init_daily_song_level(self.daily_song_id)

    def validate_answer(self, level_id: str, user_answer: str) -> bool:
        """Validar respuesta del usuario"""
        if level_id.endswith('_local'):
            level_str = level_id[:-6]  # quitar sufijo '_local'
            try:
                level_num = int(level_str)
            except ValueError:
                return False
            song = db.get_local_song_by_level(level_num)
            song_name = song.title if song else None
            if not song_name:
                return False
        else:
            song_name = db.get_spotify_song_by_level(int(level_id))
            song_name = song_name.title if song_name else None
            if not song_name:
                return False
            
        # Normalizar ambas cadenas para comparación
        normalized_answer = self._clean_title(user_answer)
        normalized_title = self._clean_title(song_name)
        
        # Comparación exacta
        if normalized_answer == normalized_title:
            return True
        
        # Comparación con 85% de similitud usando SequenceMatcher: si la respuesta es muy parecida al título se considera correcta
        similarity = SequenceMatcher(None, normalized_answer, normalized_title).ratio()
        return similarity >= 0.85

    def _clean_title(self, title: str) -> str:
        # Convertir a minúsculas
        title = title.lower()
        # Eliminar contenido entre paréntesis o corchetes (ej: (Remix), [Live])
        title = re.sub(r'[\(\[].*?[\)\]]', '', title)
        # Cuando haya un guion, quitar el guion y todo lo que sigue
        title = re.sub(r'-.*', '', title)
        # Eliminar "feat." y todo lo que sigue
        title = re.sub(r'\b(feat|ft|featuring)\b.*', '', title)
        # Reemplazar guiones bajos por espacios
        title = re.sub(r'_', ' ', title)
        # Eliminar espacios extra
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def mark_level_played(self, auth_header, level_id):
        try:
            if not auth_header or not auth_header.lower().startswith('bearer '):
                return {"error": "Token requerido"}, 401

            token = auth_header.split(' ')[1]
            user = db.verify_token(token)
            if not user:
                return {"error": "Token inválido"}, 401

            if not level_id:
                return {"error": "Nivel requerido"}, 400

            user.mark_level_played(level_id)
            db.save_user(user)
            return {"message": "Nivel marcado como jugado"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def update_score(self, auth_header, data):
        try:
            if not auth_header or not auth_header.lower().startswith('bearer '):
                return {"error": "Token requerido"}, 401

            token = auth_header.split(' ')[1]
            user = db.verify_token(token)
            if not user:
                return {"error": "Token inválido"}, 401

            if not data or 'score' not in data:
                return {"error": "Puntuación requerida"}, 400

            score = data['score']
            level_id = data.get('level_id', '')

            if user.is_level_played(level_id):
                return {"error": "Nivel ya jugado"}, 400
            user.complete_level(level_id)
            user.add_score(score) # Update score in memory

            if level_id == "0":
                user.complete_daily()
            
            if db.save_user(user):
                return {"message": "Puntuación actualizada", "total_score": user.total_score}, 200
            else:
                return {"error": "Error guardando usuario"}, 500
        except Exception as e:
            return {"error": str(e)}, 500

    def get_ranking(self, limit: int = 10):
        try:
            ranking = db.get_ranking(limit)
            for user in ranking:
                str_levels_completed = user.get('levels_completed', '')
                user['levels_completed'] = len(str_levels_completed.split(',')) if str_levels_completed else 0
            return {"ranking": ranking}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def complete_daily(self, auth_header):
        try:
            if not auth_header or not auth_header.lower().startswith('bearer '):
                return {"error": "Token requerido"}, 401

            token = auth_header.split(' ')[1]
            user = db.verify_token(token)
            if not user:
                return {"error": "Token inválido"}, 401

            user.complete_daily()
            db.save_user(user)
            return {"message": "Desafío diario completado"}, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def get_level_song(self, level_id: str, auth_header: str = None) -> tuple[dict, int]:
        """
        Obtener canción de un nivel.
        Si es invitado o no autenticado (tabla local_songs)
        Sino: canciones de Spotify (tabla spotify_songs)
        """
        try:
            # Determinar si es invitado
            is_guest = '_local' in level_id
            if is_guest:
                level_str = level_id[:-6]  # quitar sufijo '_local'
                try:
                    level_num = int(level_str)
                except ValueError:
                    return {"error": "ID de nivel inválido"}, 400

                song = db.get_local_song_by_level(level_num)
                if not song:
                    return {"error": "Nivel no disponible para invitados"}, 404

                return song.to_dict(), 200

            else:
                # Usuario autenticado: verificar token de autenticación
                if not auth_header or not auth_header.lower().startswith('bearer '):
                    return {"error": "Token requerido"}, 401

                token = auth_header.split(' ')[1]
                user = db.verify_token(token)

                if not user:
                    return {"error": "Token inválido"}, 401

                # Buscar canción en tabla spotify_songs
                song = db.get_spotify_song_by_level(int(level_id))
                
                if not song:
                    return {"error": "Nivel no disponible"}, 404
                
                # si ya tiene los datos guardados en la BD, devolverlos directamente
                if song and song.title and song.artists and song.album and song.year and song.genre and song.audio and song.image_url:
                    return song.to_dict(), 200
                else: # si solo tiene spotify_id, obtener datos desde Spotify API
                    # Obtener token de Spotify del usuario
                    username = user.username
                    success, message, spotify_token = db.get_spotify_access_token(username)
                    print(f"Spotify token status: {message}")
                    if not success:
                        return {"error": f"No hay conexión de Spotify disponible: {message}"}, 403
                    
                    spotiHelper = SpotifyHelper()
                    spoti_song = spotiHelper.get_track_info(song.id, spotify_token)
                    
                    if not spoti_song:
                        return {"error": "Nivel no disponible"}, 404

                    # Guardar datos obtenidos en la base de datos para futuras consultas
                    spoti_song.level_id = int(level_id)
                    db.add_spotify_song(spoti_song)

                    return spoti_song.to_dict(), 200

        except Exception as e:
            return {"error": str(e)}, 500
