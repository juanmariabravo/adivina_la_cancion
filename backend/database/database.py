import sqlite3
import bcrypt
import jwt
import os
import time
import json
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from models.user import User

# Cargar variables de entorno
load_dotenv()

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH")

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
                    levels_completed TEXT DEFAULT '',
                    played_levels TEXT DEFAULT '',
                    last_daily_completed TEXT,
                    spotify_access_token TEXT,
                    spotify_refresh_token TEXT,
                    spotify_token_expires_at INTEGER,
                    spotify_client_id TEXT,
                    spotify_client_secret TEXT
                )
            ''')
            
            # Tabla de canciones locales (para invitados y usuarios sin Spotify)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS local_songs (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    artists TEXT NOT NULL,
                    album TEXT NOT NULL,
                    year INTEGER,
                    genre TEXT,
                    audio_codificado TEXT NOT NULL,
                    image_url TEXT NOT NULL
                )
            ''')
            
            # Tabla de canciones de Spotify (para usuarios con Spotify conectado)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS spotify_songs (
                    spotify_id TEXT PRIMARY KEY,
                    title TEXT,
                    artists TEXT,
                    album TEXT,
                    year INTEGER,
                    genre TEXT,
                    audio TEXT,
                    image_url TEXT,
                    level_id INTEGER NOT NULL
                )
            ''')

            conn.commit()
            
            # Insertar canciones locales
            self.init_local_songs()
            # Insertar IDs de canciones de Spotify
            self.init_spotify_songs_levels()
            
            print("✅ Base de datos inicializada correctamente en "+ DATABASE_PATH)
        except Exception as e:
            print(f"❌ Error inicializando base de datos: {e}")
        finally:
            conn.close()
    
    def init_local_songs(self):
        """Inicializar canciones locales (niveles 1-10 para invitados)"""
        conn = self.get_connection()
        try:
            # Ruta al archivo JSON
            json_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'songs_local_data&spotify_ids', 'local_songs.json'
            )
            json_path = os.path.normpath(json_path)

            if not os.path.exists(json_path):
                print(f"ERROR: Archivo no encontrado: {json_path}")
                return
            
            # Leer archivo JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                local_songs = data.get('songs', [])
            
            for song in local_songs:
                # cambiar IGNORE por REPLACE para actualizar si ya existe
                try:
                    conn.execute('''
                        INSERT OR IGNORE INTO local_songs 
                        (id, title, artists, album, year, genre, audio_codificado, image_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        song['id'], 
                        song['title'], 
                        song['artists'], 
                        song['album'],
                        song['year'], 
                        song['genre'], 
                        song['audio_codificado'],
                        song['image_url']
                    ))
                except Exception as e:
                    print(f"Error insertando canción {song.get('id', '?')}: {e}")
            
            conn.commit()
            print("✅ Canciones locales inicializadas")
            
        except FileNotFoundError as e:
            print(f"Archivo JSON no encontrado: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decodificando JSON: {e}")
        except Exception as e:
            print(f"Error inicializando canciones locales: {e}")
        finally:
            conn.close()

    def init_spotify_songs_levels(self):
        """Inicializar niveles de canciones de Spotify"""
        conn = self.get_connection()
        try:
            # Ruta al archivo JSON
            json_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'songs_local_data&spotify_ids', 'spotify_songs.json'
            )
            json_path = os.path.normpath(json_path)

            if not os.path.exists(json_path):
                print(f"ERROR: Archivo no encontrado: {json_path}")
                return

            # Leer archivo JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                levels = data.get('levels', [])
            for level in levels:
                # cambiar IGNORE por REPLACE si se desea cambiar la canción de un nivel
                conn.execute('''
                    INSERT OR IGNORE INTO spotify_songs (spotify_id, level_id)
                    VALUES (?, ?)
                ''', (level['spotify_id'], level['level_id']))
            conn.commit()
            print("✅ Niveles de canciones de Spotify inicializados")
        except Exception as e:
            print(f"❌ Error inicializando niveles de canciones de Spotify: {e}")
        finally:
            conn.close()

    def create_user(self, username: str, email: str, password: str, spotify_client_id: str = None, spotify_client_secret: str = None) -> tuple[bool, str]:
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
                INSERT INTO users (username, email, hashed_password, spotify_client_id, spotify_client_secret)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, hashed_password, spotify_client_id, spotify_client_secret))
            
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
                SELECT username, email, hashed_password, created_at, is_active, total_score, levels_completed, played_levels, last_daily_completed,
                       spotify_access_token, spotify_refresh_token, spotify_token_expires_at, spotify_client_id, spotify_client_secret
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
                SELECT username, email, hashed_password, created_at, is_active, total_score, levels_completed, played_levels, last_daily_completed,
                       spotify_access_token, spotify_refresh_token, spotify_token_expires_at, spotify_client_id, spotify_client_secret
                FROM users WHERE email = ?
            ''', (email,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
        except Exception as e:
            print(f"Error obteniendo usuario por email: {e}")
            return None
        finally:
            conn.close()

    def get_user_by_client_id(self, client_id: str) -> Optional[User]:
        """Obtener usuario por client_id de Spotify"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, email, hashed_password, created_at, is_active, total_score, levels_completed, played_levels, last_daily_completed,
                       spotify_access_token, spotify_refresh_token, spotify_token_expires_at, spotify_client_id, spotify_client_secret
                FROM users WHERE spotify_client_id = ?
                LIMIT 1
            ''', (client_id,))
            row = cursor.fetchone()
            return User.from_dict(dict(row)) if row else None
        except Exception as e:
            print(f"Error obteniendo usuario por client_id: {e}")
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
    

    def get_ranking(self, limit: int = 10) -> list:
        """Obtener ranking de usuarios"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT username, total_score, levels_completed
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
    
    def get_local_song_by_level(self, level_id: int) -> Optional[dict]:
        """Obtener canción local por nivel"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT id, title, artists, album, year, genre, audio_codificado, image_url
                FROM local_songs
                WHERE id = ?
            ''', (level_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_spotify_song_by_level(self, level_id: int) -> Optional[dict]:
        """Obtener canción de Spotify por nivel"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT spotify_id, title, artists, album, year, genre, audio, image_url, level_id
                FROM spotify_songs
                WHERE level_id = ?
                LIMIT 1
            ''', (level_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_song_title_by_level(self, level_id: int) -> Optional[str]:
        """Obtener título de la canción por nivel y fuente (local o spotify)"""
        conn = self.get_connection()
        cursor = conn.execute('''
            SELECT title
            FROM spotify_songs
            WHERE level_id = ?
        ''', (level_id,))
            
        row = cursor.fetchone()
        conn.close()
        return row['title'] if row else None


    def add_spotify_song(self, spotify_data: dict) -> bool:
        """Añadir canción de Spotify a la base de datos"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO spotify_songs 
                (spotify_id, title, artists, album, year, genre, audio, image_url, level_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                spotify_data['spotify_id'],
                spotify_data['title'],
                spotify_data['artists'],
                spotify_data['album'],
                spotify_data['year'],
                spotify_data.get('genre', 'Unknown'),
                spotify_data['audio'],
                spotify_data['image_url'],
                spotify_data['level_id']
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error añadiendo canción de Spotify: {e}")
            return False
        finally:
            conn.close()
    
    def update_spotify_song(self, spotify_id: str, title: str, artists: str, album: str, year: int, genre: str, audio: str, image_url: str) -> bool:
        """Actualizar el nivel de una canción de Spotify"""
        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE spotify_songs 
                SET title = ?, artists = ?, album = ?, year = ?, genre = ?, audio = ?, image_url = ?
                WHERE spotify_id = ?
            ''', (title, artists, album, year, genre, audio, image_url, spotify_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando canción de Spotify: {e}")
            return False
        finally:
            conn.close()

    def delete_daily_songs(self) -> bool:
        """Eliminar todas las canciones diarias almacenadas (aquellas con level_id = 0)"""
        conn = self.get_connection()
        try:
            conn.execute('''
                DELETE FROM spotify_songs 
                WHERE level_id = 0
            ''')
            conn.commit()
            return True
        except Exception as e:
            print(f"Error eliminando canciones diarias: {e}")
            return False
        finally:
            conn.close()
    
    def init_daily_song_level(self, spotify_id: str) -> bool:
        """Inicializar canción diaria en la base de datos con level_id = 0"""
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO spotify_songs 
                (spotify_id, level_id)
                VALUES (?, 0)
            ''', (spotify_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error inicializando canción diaria: {e}")
            return False
        finally:
            conn.close()

    def save_spotify_tokens(self, username: str, access_token: str, refresh_token: str, expires_in: int) -> bool:
        """
        Guardar tokens de Spotify para un usuario.
        expires_in: segundos hasta que expire el token
        """
        conn = self.get_connection()
        try:
            # Calcular timestamp de expiración (tiempo actual + expires_in)
            expires_at = int(time.time()) + expires_in
            
            conn.execute('''
                UPDATE users 
                SET spotify_access_token = ?, 
                    spotify_refresh_token = ?, 
                    spotify_token_expires_at = ?
                WHERE username = ?
            ''', (access_token, refresh_token, expires_at, username))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error guardando tokens de Spotify: {e}")
            return False
        finally:
            conn.close()
    
    def save_user(self, user: User) -> bool:
        """Actualizar datos del usuario en la base de datos"""
        conn = self.get_connection()
        try:
            conn.execute('''
                UPDATE users 
                SET email = ?, hashed_password = ?, is_active = ?, total_score = ?, levels_completed = ?, played_levels = ?, last_daily_completed = ?,
                    spotify_access_token = ?, spotify_refresh_token = ?, spotify_token_expires_at = ?, spotify_client_id = ?, spotify_client_secret = ?
                WHERE username = ?
            ''', (
                user.email,
                user.hashed_password,
                user.is_active,
                user.total_score,
                user.levels_completed,
                user.played_levels,
                user.last_daily_completed,
                user.spotify_access_token,
                user.spotify_refresh_token,
                user.spotify_token_expires_at,
                user.spotify_client_id,
                user.spotify_client_secret,
                user.username
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            return False
        finally:
            conn.close()

    def get_spotify_access_token(self, username: str) -> Optional[str]:
        """Obtener access token de Spotify para un usuario"""
        conn = self.get_connection()
        try:
            cursor = conn.execute('''
                SELECT spotify_access_token, spotify_token_expires_at
                FROM users
                WHERE username = ?
            ''', (username,))
            row = cursor.fetchone()
            if row:
                access_token = row['spotify_access_token']
                expires_at = row['spotify_token_expires_at']
                # Verificar si el token ha expirado
                if expires_at and expires_at > int(time.time()):
                    return access_token
            return None
        except Exception as e:
            print(f"Error obteniendo access token de Spotify: {e}")
            return None
        finally:
            conn.close()

# Instancia global de la base de datos
db = Database()