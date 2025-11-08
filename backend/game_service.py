from difflib import SequenceMatcher
import os
from db.database import db
from dotenv import load_dotenv

load_dotenv()


def _get_username(user):
    if user is None:
        return None
    return getattr(user, 'username', None) or (user.get('username') if isinstance(user, dict) else None)


def validate_answer(song_id: int, user_answer: str) -> bool:
    """Validar respuesta del usuario (alta similitud o exacta)."""
    song = db.get_song_by_id(song_id)
    if not song:
        return False

    normalized_answer = user_answer.lower().strip()
    normalized_title = song.title.lower().strip()

    if normalized_answer == normalized_title:
        return True

    similarity = SequenceMatcher(None, normalized_answer, normalized_title).ratio()
    return similarity >= 0.90


class GameService:
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

    def get_level_song(self, level_id: int, auth_header):
        try:
            is_guest = not auth_header or not auth_header.lower().startswith('bearer ')

            if is_guest:
                if level_id > 10:
                    return {"error": "Los invitados solo pueden jugar niveles 1-10"}, 403

                song = db.get_song_by_level(level_id)
                if not song:
                    return {"error": "No hay canción para este nivel"}, 404

                return {"song": song.to_dict(include_answer=False), "guest_mode": True}, 200

            # usuario autenticado
            token = auth_header.split(' ')[1]
            user = db.verify_token(token)
            if not user:
                return {"error": "Token inválido"}, 401

            if not db.has_valid_spotify_token(_get_username(user)):
                return {"error": "Debes conectar tu cuenta de Spotify para jugar", "spotify_required": True}, 403

            song = db.get_song_by_level(level_id)
            if not song:
                return {"error": "No hay canción para este nivel"}, 404

            return {"song": song.to_dict(include_answer=False), "guest_mode": False}, 200
        except Exception as e:
            return {"error": str(e)}, 500
