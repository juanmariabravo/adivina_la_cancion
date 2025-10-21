import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-desarrollo")
DATABASE_PATH = "adivina_la_cancion.db"

class Database:
    def __init__(self):
        self.init_database()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        return conn
    
    def init_database(self):
        """Inicializar tablas de la base de datos"""
        conn = self.get_connection()
        try:
            # Tabla de usuarios
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    total_score INTEGER DEFAULT 0,
                    games_played TEXT DEFAULT '0',
                    daily_completed BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Tabla de sesiones de juego
            conn.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    clues_used TEXT,
                    time_to_solve INTEGER,
                    score INTEGER,
                    completed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
            
            conn.commit()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
        finally:
            conn.close()
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Crear nuevo usuario"""
        conn = self.get_connection()
        try:
            # Verificar si el usuario ya existe
            if self.get_user_by_username(username) or self.get_user_by_email(email):
                return False
            
            # Hashear contraseña
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insertar usuario
            conn.execute('''
                INSERT INTO users (username, email, hashed_password)
                VALUES (?, ?, ?)
            ''', (username, email, hashed_password))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Obtener usuario por username"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, email, hashed_password, created_at, is_active, total_score, games_played
                FROM users WHERE username = ?
            ''', (username,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Obtener usuario por email"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, email, hashed_password, created_at, is_active, total_score, games_played
                FROM users WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None
        finally:
            conn.close()
    
    def validate_credentials(self, email: str, password: str) -> Optional[Dict]:
        """Validar credenciales de usuario"""
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['hashed_password'].encode('utf-8')):
            return user
        return None
    
    def create_token(self, user: Dict) -> str:
        """Crear JWT token"""
        payload = {
            'sub': user['username'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verificar JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return self.get_user_by_username(payload['sub'])
        except jwt.ExpiredSignatureError:
            print("Token expirado")
            return None
        except jwt.InvalidTokenError:
            print("Token inválido")
            return None
    
    def update_user_score(self, username: str, score: int) -> bool:
        """Actualizar puntuación del usuario"""
        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE users 
                SET total_score = total_score + ?, games_played = games_played + 1
                WHERE username = ?
            ''', (score, username))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando puntuación: {e}")
            return False
        finally:
            conn.close()
    
    def get_ranking(self, limit: int = 10) -> list:
        """Obtener ranking de usuarios"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, total_score, games_played
                FROM users 
                WHERE is_active = TRUE
                ORDER BY total_score DESC
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error obteniendo ranking: {e}")
            return []
        finally:
            conn.close()

# Instancia global de la base de datos
db = Database()