from difflib import SequenceMatcher
from database import db
from dotenv import load_dotenv

from spotify_helper import SpotifyHelper

load_dotenv()


def _get_username(user):
    if user is None:
        return None
    return getattr(user, 'username', None) or (user.get('username') if isinstance(user, dict) else None)


class GameService:
    def validate_answer(self, level_id: str, user_answer: str) -> bool:
        """Validar respuesta del usuario"""
        if level_id.endswith('_local'):
            level_str = level_id[:-6]  # quitar sufijo '_local'
            try:
                level_num = int(level_str)
            except ValueError:
                return False
            song_name = db.get_local_song_by_level(level_num).get('title')
            if not song_name:
                return False
            
        else:
            song_name = db.get_song_title_by_level(int(level_id))
            if not song_name:
                return False
            
        # Normalizar ambas cadenas para comparación
        normalized_answer = user_answer.lower().strip()
        normalized_title = song_name.lower().strip()
        
        # Comparación exacta
        if normalized_answer == normalized_title:
            return True
        
        # Comparación con 90% de similitud usando SequenceMatcher: si la respuesta es muy parecida al título se considera correcta
        similarity = SequenceMatcher(None, normalized_answer, normalized_title).ratio()
        return similarity >= 0.90

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
            if db.update_user_score(_get_username(user), score):
                updated_user = db.get_user_by_username(_get_username(user))
                # assume updated_user returns dict-like
                return {
                    "message": "Puntuación actualizada",
                    "total_score": updated_user.get('total_score') if isinstance(updated_user, dict) else getattr(updated_user, 'total_score', None),
                    "games_played": updated_user.get('games_played') if isinstance(updated_user, dict) else getattr(updated_user, 'games_played', None)
                }, 200
            else:
                return {"error": "Error actualizando puntuación"}, 500
        except Exception as e:
            return {"error": str(e)}, 500

    def get_ranking(self, limit: int = 10):
        try:
            ranking = db.get_ranking(limit)
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

            if db.mark_daily_completed(_get_username(user)):
                return {"message": "Desafío diario completado"}, 200
            else:
                return {"error": "Error marcando daily como completado"}, 500
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

                return {
                    "song": {
                        "id": song['id'],
                        "title": song['title'],
                        "artists": song['artists'],
                        "album": song['album'],
                        "year": song['year'],
                        "genre": song['genre'],
                        "audio": song['audio_codificado'],
                        "image_url": song['image_url']
                    },
                    "source": "local"
                }, 200

            else:
                # Usuario autenticado: verificar token de autenticación
                if not auth_header or not auth_header.lower().startswith('bearer '):
                    return {"error": "Token requerido"}, 401

                token = auth_header.split(' ')[1]
                user = db.verify_token(token)

                if not user:
                    return {"error": "Token inválido"}, 401


                # Buscar canción en tabla spotify_songs
                song = db.get_spotify_song_by_level(level_id)
                
                if not song:
                    return {"error": "Nivel no disponible"}, 404
                
                spotify_track_id = song.get('spotify_id')
                
                if song.get('title'): # si título existe, significa que la canción está completa
                    return {
                        "song": {
                            "id": spotify_track_id,
                            "title": song['title'],
                            "artists": song['artists'],
                            "album": song['album'],
                            "year": song['year'],
                            "genre": song['genre'],
                            "audio": song['audio'],
                            "image_url": song['image_url']
                        },
                        "source": "spotify"
                    }, 200
                else: # si solo tiene spotify_id, obtener datos desde Spotify API
                    # Obtener token de Spotify del usuario
                    username = _get_username(user)
                    spotify_token = db.get_spotify_access_token(username)
                    
                    if not spotify_token:
                        return {"error": "No hay conexión de Spotify disponible"}, 403
                    
                    spotiHelper = SpotifyHelper()
                    spotify_data = spotiHelper.get_track_info(spotify_track_id, spotify_token)
                    
                    if not spotify_data:
                        return {"error": "Nivel no disponible"}, 404

                    # Guardar datos obtenidos en la base de datos para futuras consultas
                    db.update_spotify_song(
                        spotify_track_id,
                        spotify_data['title'],
                        spotify_data['artists'],
                        spotify_data['album'],
                        spotify_data['year'],
                        spotify_data['genre'],
                        spotify_data['audio'],
                        spotify_data['image_url']
                    )

                    return {
                        "song": {
                            "id": spotify_data['spotify_id'],
                            "title": spotify_data['title'],
                            "artists": spotify_data['artists'],
                            "album": spotify_data['album'],
                            "year": spotify_data['year'],
                            "genre": spotify_data['genre'],
                            "audio": spotify_data['audio'],
                            "image_url": spotify_data['image_url']
                        },
                        "source": "spotify"
                    }, 200
        except Exception as e:
            return {"error": str(e)}, 500
