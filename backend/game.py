from difflib import SequenceMatcher
from db.database import db

def validate_answer(song_id: int, user_answer: str) -> bool:
        """Validar respuesta del usuario"""
        song = db.get_song_by_id(song_id)
        if not song:
            return False
        
        # Normalizar ambas cadenas para comparación
        normalized_answer = user_answer.lower().strip()
        normalized_title = song.title.lower().strip()
        
        # Comparación exacta
        if normalized_answer == normalized_title:
            return True
        
        # Comparación con 90% de similitud usando SequenceMatcher: si la respuesta es muy parecida al título se considera correcta
        similarity = SequenceMatcher(None, normalized_answer, normalized_title).ratio()
        return similarity >= 0.90