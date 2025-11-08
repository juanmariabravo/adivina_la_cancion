import os
import base64
import requests
from dotenv import load_dotenv
from db.database import db
from datetime import datetime

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/api/token'


def _get_username(user):
	if user is None:
		return None
	return getattr(user, 'username', None) or (user.get('username') if isinstance(user, dict) else None)


def _get_email(user):
	if user is None:
		return None
	return getattr(user, 'email', None) or (user.get('email') if isinstance(user, dict) else None)


class UserService:
	def register(self, data):
		try:
			if not data or 'username' not in data or 'email' not in data or 'pwd1' not in data or 'pwd2' not in data:
				return {"error": "Faltan campos"}, 400

			username = data['username'].strip()
			email = data['email'].strip().lower()
			pwd1 = data['pwd1']
			pwd2 = data['pwd2']

			if len(username) < 3:
				return {"error": "El username debe tener al menos 3 caracteres"}, 400
			if '@' not in email or '.' not in email:
				return {"error": "Email inválido"}, 400
			if pwd1 != pwd2:
				return {"error": "Las contraseñas no coinciden"}, 400
			if len(pwd1) < 6:
				return {"error": "La contraseña debe tener al menos 6 caracteres"}, 400

			success, message = db.create_user(username, email, pwd1)

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

			if not SPOTIFY_CLIENT_ID:
				return {"error": "SPOTIFY_CLIENT_ID no configurado"}, 500

			return {"clientId": SPOTIFY_CLIENT_ID}, 200
		except Exception as e:
			return {"error": str(e)}, 500

	def exchange_spotify_authorization(self, code, client_id, auth_header):
		try:
			if not auth_header or not auth_header.lower().startswith('bearer '):
				return {"error": "Token de usuario requerido"}, 401

			token = auth_header.split(' ')[1]
			user = db.verify_token(token)
			if not user:
				return {"error": "Token inválido"}, 401

			if not code or not client_id:
				return {"error": "Código y clientId requeridos"}, 400

			if client_id != SPOTIFY_CLIENT_ID:
				return {"error": "Client ID inválido"}, 401

			credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
			credentials_b64 = base64.b64encode(credentials.encode()).decode()

			headers = {
				'Authorization': f'Basic {credentials_b64}',
				'Content-Type': 'application/x-www-form-urlencoded'
			}

			data = {
				'grant_type': 'authorization_code',
				'code': code,
				'redirect_uri': SPOTIFY_REDIRECT_URI
			}

			response = requests.post(SPOTIFY_AUTH_URL, headers=headers, data=data)

			if response.status_code == 200:
				token_data = response.json()

				spotify_access_token = token_data.get('access_token')
				user_info_response = requests.get(
					'https://api.spotify.com/v1/me',
					headers={'Authorization': f'Bearer {spotify_access_token}'}
				)

				if user_info_response.status_code == 200:
					spotify_user = user_info_response.json()
					spotify_email = spotify_user.get('email', '').lower()
					if _get_email(user) and _get_email(user).lower() != spotify_email:
						return {
							"error": "El email de Spotify no coincide con tu cuenta",
							"spotify_email": spotify_email,
							"registered_email": _get_email(user)
						}, 403

				spoti_token = {
					'access_token': token_data.get('access_token'),
					'token_type': token_data.get('token_type'),
					'expires_in': token_data.get('expires_in'),
					'refresh_token': token_data.get('refresh_token'),
					'scope': token_data.get('scope')
				}

				return spoti_token, 200
			else:
				try:
					error_data = response.json()
				except Exception:
					error_data = {"status_code": response.status_code}
				return {"error": "Error obteniendo token de Spotify", "details": error_data}, response.status_code

		except Exception as e:
			return {"error": str(e)}, 500

