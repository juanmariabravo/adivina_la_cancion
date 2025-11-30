import os
from dotenv import load_dotenv
from database.database import db

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_TOKEN_URL = os.getenv('SPOTIFY_TOKEN_URL')


def _get_username(user):
	if user is None:
		return None
	return getattr(user, 'username', None) or (user.get('username') if isinstance(user, dict) else None)


class UserService:
	def register(self, data):
		try:
			if not data or 'username' not in data or 'email' not in data or 'pwd1' not in data or 'pwd2' not in data:
				return {"error": "Faltan campos"}, 400

			username = data['username'].strip()
			email = data['email'].strip().lower()
			pwd1 = data['pwd1']
			pwd2 = data['pwd2']
			spotify_client_id = data.get('spotify_client_id', '').strip()
			spotify_client_secret = data.get('spotify_client_secret', '').strip()

			# Validar que las credenciales de Spotify sean obligatorias
			if not spotify_client_id:
				return {"error": "El Client ID de Spotify es requerido"}, 400
			if not spotify_client_secret:
				return {"error": "El Client Secret de Spotify es requerido"}, 400

			if len(username) < 3:
				return {"error": "El username debe tener al menos 3 caracteres"}, 400
			if '@' not in email or '.' not in email:
				return {"error": "Email inválido"}, 400
			if pwd1 != pwd2:
				return {"error": "Las contraseñas no coinciden"}, 400
			if len(pwd1) < 6:
				return {"error": "La contraseña debe tener al menos 6 caracteres"}, 400

			success, message = db.create_user(username, email, pwd1, spotify_client_id, spotify_client_secret)

			if success:
				user = db.get_user_by_username(username)
				token = db.create_token(user)
				return {
					"message": message,
					"access_token": token,
					"token_type": "bearer",
					"user": user.to_public_dict()
				}, 201
			else:
				return {"error": message}, 400
		except Exception as e:
			return {"error": str(e)}, 500

	def login(self, data):
		try:
			if not data or 'email' not in data or 'password' not in data:
				return {"error": "Email y contraseña requeridos"}, 400

			email = data['email'].strip().lower()
			password = data['password']

			user = db.validate_credentials(email, password)
			if user:
				token = db.create_token(user)
				return {
					"message": "Login exitoso",
					"access_token": token,
					"token_type": "bearer",
					"user": user.to_public_dict()
				}, 200
			else:
				return {"error": "Credenciales inválidas"}, 401
		except Exception as e:
			return {"error": str(e)}, 500

	def get_current_user(self, auth_header):
		try:
			if not auth_header or not auth_header.lower().startswith('bearer '):
				return {"error": "Token requerido"}, 401

			token = auth_header.split(' ')[1]
			user = db.verify_token(token)

			if user:
				return user.to_public_dict(), 200
			else:
				return {"error": "Token inválido"}, 401
		except Exception as e:
			return {"error": str(e)}, 500

	def update_profile(self, auth_header, data):
		try:
			if not auth_header or not auth_header.lower().startswith('bearer '):
				return {"error": "Token requerido"}, 401

			token = auth_header.split(' ')[1]
			user = db.verify_token(token)
			if not user:
				return {"error": "Token inválido"}, 401

			if not data:
				return {"error": "No se enviaron datos"}, 400

			new_username = data.get('username', '').strip()
			new_password = data.get('password', '').strip()

			if new_username and len(new_username) < 3:
				return {"error": "El username debe tener al menos 3 caracteres"}, 400
			if new_password and len(new_password) < 6:
				return {"error": "La contraseña debe tener al menos 6 caracteres"}, 400

			success, message = db.update_user_profile(_get_username(user), new_username, new_password)

			if success:
				updated_user = db.get_user_by_username(new_username if new_username else _get_username(user))
				new_token = None
				if new_username:
					new_token = db.create_token(updated_user)

				response = {
					"message": message,
					"user": updated_user.to_public_dict()
				}

				if new_token:
					response["access_token"] = new_token
					response["token_type"] = "bearer"

				return response, 200
			else:
				return {"error": message}, 400
		except Exception as e:
			return {"error": str(e)}, 500

	def get_spotify_client_id(self, email):
		try:
			if not email:
				return {"error": "Email requerido"}, 400

			# Buscar credenciales del usuario
			user = db.get_user_by_email(email.lower())
			if user and user.spotify_client_id:
				return {"clientId": user.spotify_client_id}, 200
			
			return {"error": "No tienes credenciales de Spotify configuradas en tu cuenta"}, 400
		except Exception as e:
			return {"error": str(e)}, 500
