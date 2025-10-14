from typing import Optional, Dict

class UserDAO:
    """
    DAO simple en memoria. Sustituir por implementación real (SQLAlchemy, etc.).
    """
    def __init__(self):
        # key=username
        self._users: Dict[str, Dict] = {}

    def create_user(self, username: str, email: str, password: str) -> bool:
        if username in self._users:
            return False
        self._users[username] = {
            "username": username,
            "email": email,
            "password": password  # NO guardar plano en producción
        }
        return True

    def get_user(self, username: str) -> Optional[Dict]:
        return self._users.get(username)

    def exists_username(self, username: str) -> bool:
        return username in self._users
    
    def exists_email(self, email: str) -> bool:
        return any(user["email"] == email for user in self._users.values())

    def validate_credentials(self, username: str, password: str) -> bool:
        user = self.get_user(username)
        return bool(user and user["password"] == password)

    def all_users(self):
        return list(self._users.values())
