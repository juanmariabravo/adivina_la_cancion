import base64
import os
from typing import Optional
import requests
from requests.exceptions import RequestException

from services.user_service import UserService
from database.database import db

REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_TOKEN_URL = os.getenv("SPOTIFY_TOKEN_URL")

class SpotiService:
    def __init__(self):
        self.user_service = UserService()

    def get_authorization_token(self, code: str, client_id: str) -> dict:
        """Get authorization token from Spotify API."""
        user = db.get_user_by_client_id(client_id)
        client_secret = user.get_client_secret()

        # Prepare form data
        form_data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }

        # Create authorization header
        auth_header = self._basic_auth(client_id, client_secret)

        # Make request to Spotify API
        try:
            response = requests.post(
                SPOTIFY_TOKEN_URL,
                data=form_data,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()
            db.save_spotify_tokens(
                user.username,
                response.json().get("access_token"),
                response.json().get("refresh_token"),
                response.json().get("expires_in")
            )
            return response.json(), 200
        except RequestException as e:
            return {"error": f"Error getting authorization token: {str(e)}"}, 400

    def _basic_auth(self, client_id: str, client_secret: str) -> str:
        """Create Basic Authentication header."""
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"

    def refresh_spotify_token(self, username: str) -> Optional[str]:
        """
        Renovar el access token de Spotify usando el refresh token.
        Retorna el nuevo access token o None si falla.
        """
        user = db.get_user_by_username(username)
        if not user or not user.spotify_refresh_token:
            print(f"No hay refresh token para el usuario {username}")
            return None
        
        try:
            client_id = user.spotify_client_id
            client_secret = user.spotify_client_secret
            if not client_id or not client_secret:
                print(f"No hay credenciales de cliente de Spotify para el usuario {username}")
                return None
            
            credentials = f"{client_id}:{client_secret}"
            credentials_b64 = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {credentials_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': user.spotify_refresh_token
            }

            response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                new_access_token = token_data.get('access_token')
                expires_in = token_data.get('expires_in', 3600)
                
                # El refresh_token puede o no cambiar
                new_refresh_token = token_data.get('refresh_token', user.spotify_refresh_token)
                
                # Guardar nuevos tokens
                db.save_spotify_tokens(username, new_access_token, new_refresh_token, expires_in)
                
                return new_access_token
            else:
                print(f"Error renovando token de Spotify: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error renovando token de Spotify: {e}")
            return None