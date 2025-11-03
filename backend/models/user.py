from datetime import datetime
from typing import Optional

class User:
    """Modelo de usuario para la aplicación"""
    
    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
        total_score: int = 0,
        games_played: int = 0,
        last_daily_completed: Optional[str] = None
    ):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
        self.total_score = total_score
        self.games_played = games_played
        self.last_daily_completed = last_daily_completed  # formato: "dd-mm-yyyy"
    
    def to_public_dict(self) -> dict:
        """Convertir a diccionario público (sin datos sensibles)"""
        return {
            'username': self.username,
            'email': self.email,
            'total_score': self.total_score,
            'games_played': self.games_played,
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
        self.games_played += 1
    
    def reset_daily_status(self) -> None:
        """Resetear el estado del desafío diario"""
        self.last_daily_completed = False
    
    def complete_daily(self) -> None:
        """Marcar el desafío diario como completado hoy"""
        self.last_daily_completed = datetime.now().strftime("%d-%m-%Y")
    
    @staticmethod
    def from_dict(data: dict) -> 'User':
        """Crear instancia de User desde un diccionario"""
        return User(
            username=data.get('username'),
            email=data.get('email'),
            hashed_password=data.get('hashed_password'),
            created_at=data.get('created_at'),
            is_active=data.get('is_active', True),
            total_score=data.get('total_score', 0),
            games_played=data.get('games_played', 0),
            last_daily_completed=data.get('last_daily_completed')
        )
    
    def __repr__(self) -> str:
        return f"User(username='{self.username}', email='{self.email}', score={self.total_score})"
    
    def __str__(self) -> str:
        return f"{self.username} ({self.email}) - Score: {self.total_score}"
