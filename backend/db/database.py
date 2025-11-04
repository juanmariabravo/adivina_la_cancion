import sqlite3
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from models.user import User
from models.song import Song

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-desarrollo")
DATABASE_PATH = os.getenv("DATABASE_PATH", "adivina_la_cancion.db")

class Database:
    def __init__(self):
        self.init_database()
        self.init_songs_data()  # Datos de canciones en memoria
    
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
                    games_played INTEGER DEFAULT 0,
                    last_daily_completed TEXT
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
    
    def create_user(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """
        Crear nuevo usuario.
        Retorna (éxito, mensaje) para feedback específico.
        """
        conn = self.get_connection()
        try:
            # Verificar si el username ya existe
            if self.get_user_by_username(username):
                return False, "El nombre de usuario ya existe"
            
            # Verificar si el email ya existe
            if self.get_user_by_email(email):
                return False, "El email ya está registrado"
            
            # Hashear contraseña
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insertar usuario
            conn.execute('''
                INSERT INTO users (username, email, hashed_password)
                VALUES (?, ?, ?)
            ''', (username, email, hashed_password))
            
            conn.commit()
            return True, "Usuario creado exitosamente"
        except Exception as e:
            print(f"Error creando usuario: {e}")
            return False, f"Error al crear el usuario: {str(e)}"
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, email, hashed_password, created_at, is_active, total_score, games_played, last_daily_completed
                FROM users WHERE username = ?
            ''', (username,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
        except Exception as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, email, hashed_password, created_at, is_active, total_score, games_played, last_daily_completed
                FROM users WHERE email = ?
            ''', (email,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None
        finally:
            conn.close()
    
    def validate_credentials(self, email: str, password: str) -> Optional[User]:
        """Validar credenciales de usuario"""
        user = self.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
            return user
        return None
    
    def create_token(self, user: User) -> str:
        """Crear JWT token"""
        payload = {
            'sub': user.username,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[User]:
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
    
    def mark_daily_completed(self, username: str) -> bool:
        """Marcar desafío diario como completado hoy"""
        conn = self.get_connection()
        try:
            today = datetime.now().strftime("%d-%m-%Y")
            conn.execute('''
                UPDATE users 
                SET last_daily_completed = ?
                WHERE username = ?
            ''', (today, username))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error marcando daily completado: {e}")
            return False
        finally:
            conn.close()
    
    def update_user_profile(self, username: str, new_username: str = None, new_password: str = None) -> tuple[bool, str]:
        """
        Actualizar username y/o contraseña del usuario.
        Retorna (éxito, mensaje) para feedback.
        """
        conn = self.get_connection()
        try:
            # Verificar si el nuevo username ya existe (si se proporciona)
            if new_username:
                existing_user = self.get_user_by_username(new_username)
                if existing_user and existing_user.username != username:
                    return False, "El nombre de usuario ya está en uso"
            
            # Preparar actualización
            if new_username and new_password:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                conn.execute('''
                    UPDATE users 
                    SET username = ?, hashed_password = ?
                    WHERE username = ?
                ''', (new_username, hashed_password, username))
                message = "Nombre de usuario y contraseña actualizados"
            elif new_username:
                conn.execute('''
                    UPDATE users 
                    SET username = ?
                    WHERE username = ?
                ''', (new_username, username))
                message = "Nombre de usuario actualizado"
            elif new_password:
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                conn.execute('''
                    UPDATE users 
                    SET hashed_password = ?
                    WHERE username = ?
                ''', (hashed_password, username))
                message = "Contraseña actualizada"
            else:
                return False, "No se proporcionaron datos para actualizar"
            
            conn.commit()
            return True, message
        except Exception as e:
            print(f"Error actualizando perfil: {e}")
            return False, f"Error al actualizar el perfil: {str(e)}"
        finally:
            conn.close()
    
    def init_songs_data(self):
        """Inicializar datos de canciones (simulación en memoria)"""
        # Cada nivel tiene UNA canción asociada
        self.songs = [
            Song(1, "Bohemian Rhapsody", "Queen", "A Night at the Opera", 1975, "Rock", 
                 "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", 
                 "https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/Bohemian_Rhapsody.png/220px-Bohemian_Rhapsody.png", 1),
            
            Song(2, "Blinding Lights", "The Weeknd", "After Hours", 2020, "Pop", 
                 "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3", 
                 "https://cdn-images.dzcdn.net/images/cover/cf22674710be326f668dfb27d5af9576/1900x1900-000000-81-0-0.jpg", 2),
            
            Song(3, "Bad Guy", "Billie Eilish", "When We All Fall Asleep, Where Do We Go?", 2019, "Pop", 
                 "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3", 
                 "https://cdn-images.dzcdn.net/images/cover/6630083f454d48eadb6a9b53f035d734/500x500.jpg", 3),
            
            Song(4, "Stairway to Heaven", "Led Zeppelin", "Led Zeppelin IV", 1971, "Rock", 
                 "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3", 
                 "https://upload.wikimedia.org/wikipedia/en/2/26/Led_Zeppelin_-_Led_Zeppelin_IV.jpg", 4),
            
            Song(5, "Smells Like Teen Spirit", "Nirvana", "Nevermind", 1991, "Rock", 
                 "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3", 
                 "https://upload.wikimedia.org/wikipedia/en/b/b7/NirvanaNevermindalbumcover.jpg", 5),
            
            Song(6, "Shape of You", "Ed Sheeran", "÷ (Divide)", 2017, "Pop", 
                 "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3", 
                 "https://upload.wikimedia.org/wikipedia/en/b/b4/Shape_Of_You_%28Official_Single_Cover%29_by_Ed_Sheeran.png", 6),
        ]
    
    def get_song_by_id(self, song_id: int) -> Optional[Song]:
        """Obtener canción por ID"""
        for song in self.songs:
            if song.id == song_id:
                return song
        return None
    
    def get_song_by_level(self, level_id: int) -> Optional[Song]:
        """Obtener LA canción de un nivel (una sola canción por nivel)"""
        for song in self.songs:
            if song.level_id == level_id:
                return song
        return None

# Instancia global de la base de datos
db = Database()