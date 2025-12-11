from datetime import datetime
from typing import Optional

class User:
    """Modelo de usuario"""
    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        created_at: Optional[datetime] = None,
        total_score: int = 0,
        levels_completed: str = '',
        played_levels: str = '',
        last_daily_completed: Optional[str] = None,
        spotify_access_token: Optional[str] = None,
        spotify_refresh_token: Optional[str] = None,
        spotify_token_expires_at: Optional[int] = None,
        spotify_client_id: Optional[str] = None,
        spotify_client_secret: Optional[str] = None
    ):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.created_at = created_at or datetime.utcnow()
        self.total_score = total_score
        self.levels_completed = levels_completed
        self.played_levels = played_levels
        self.last_daily_completed = last_daily_completed  # formato: "dd-mm-yyyy"
        self.spotify_access_token = spotify_access_token
        self.spotify_refresh_token = spotify_refresh_token
        self.spotify_token_expires_at = spotify_token_expires_at
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
    
    def to_public_dict(self) -> dict:
        """Convertir a diccionario público (sin datos sensibles)"""
        return {
            'username': self.username,
            'email': self.email,
            'total_score': self.total_score,
            'levels_completed': self.levels_completed,
            'played_levels': self.played_levels,
            'daily_completed': self.is_daily_completed_today()
        }
    
    def is_daily_completed_today(self) -> bool:
        """Verificar si el desafío diario se completó hoy"""
        if not self.last_daily_completed:
            return False
        today = datetime.now().strftime("%d-%m-%Y")
        return self.last_daily_completed == today
    
    def add_score(self, score: int) -> None:
        """Agregar puntuación al total"""
        self.total_score += score
    
    def is_level_completed(self, level_id: str) -> bool:
        """Verificar si un nivel ya está completado"""
        if not self.levels_completed:
            return False
        completed_levels = self.levels_completed.split(',')
        return level_id in completed_levels

    def is_level_played(self, level_id: str) -> bool:
        """Verificar si un nivel ya ha sido jugado (intentado)"""
        if not self.played_levels:
            return False
        played = self.played_levels.split(',')
        return level_id in played
    
    def complete_level(self, level_id: str) -> None:
        """Marcar un nivel como completado"""
        if not self.is_level_completed(level_id):
            if self.levels_completed:
                self.levels_completed += f',{level_id}'
            else:
                self.levels_completed = level_id

    def mark_level_played(self, level_id: str) -> None:
        """Marcar un nivel como jugado"""
        if not self.is_level_played(level_id):
            if self.played_levels:
                self.played_levels += f',{level_id}'
            else:
                self.played_levels = level_id
    
    def get_completed_levels_count(self) -> int:
        """Obtener número de niveles completados"""
        if not self.levels_completed:
            return 0
        return len(self.levels_completed.split(','))

    def get_played_levels_count(self) -> int:
        """Obtener número de niveles jugados"""
        if not self.played_levels:
            return 0
        return len(self.played_levels.split(','))
    
    def reset_daily_status(self) -> None:
        """Resetear el estado del desafío diario"""
        self.last_daily_completed = False
    
    def complete_daily(self) -> None:
        """Marcar el desafío diario como completado hoy"""
        self.last_daily_completed = datetime.now().strftime("%d-%m-%Y")

    def get_client_secret(self) -> Optional[str]:
        """Obtener el client secret de Spotify"""
        return self.spotify_client_secret
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Crear instancia de User desde un diccionario"""
        return User(
            username=data.get('username'),
            email=data.get('email'),
            hashed_password=data.get('hashed_password'),
            created_at=data.get('created_at'),
            total_score=data.get('total_score', 0),
            levels_completed=data.get('levels_completed', ''),
            played_levels=data.get('played_levels', ''),
            last_daily_completed=data.get('last_daily_completed'),
            spotify_access_token=data.get('spotify_access_token'),
            spotify_refresh_token=data.get('spotify_refresh_token'),
            spotify_token_expires_at=data.get('spotify_token_expires_at'),
            spotify_client_id=data.get('spotify_client_id'),
            spotify_client_secret=data.get('spotify_client_secret')
        )
    
    def __repr__(self) -> str:
        return f"User(username='{self.username}', email='{self.email}', score={self.total_score})"
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email}) - Score: {self.total_score}"
