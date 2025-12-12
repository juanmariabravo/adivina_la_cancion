import base64
import os
import requests
from requests.exceptions import RequestException

from services.user_service import UserService
from database.database import db

REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
SPOTIFY_TOKEN_URL = os.getenv("SPOTIFY_TOKEN_URL")

class SpotiService:
    def __init__(self):
        self.user_service = UserService()

    def get_authorization_token(self, code: str, client_id: str) -> tuple[dict, int]:
        """Get authorization token from Spotify API."""
        try:
            user = db.get_user_by_client_id(client_id)
            if not user:
                return {"error": "Usuario no encontrado"}, 404
                
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
            response = requests.post(
                SPOTIFY_TOKEN_URL,
                data=form_data,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()
            
            token_data = response.json()
            db.save_spotify_tokens(
                user.username,
                token_data.get("access_token"),
                token_data.get("refresh_token"),
                token_data.get("expires_in")
            )
            
            # Solo confirmar éxito, NO enviar tokens
            return {"message": "Spotify conectado exitosamente", "connected": True}, 200
        except RequestException as e:
            return {"error": f"Error getting authorization token: {str(e)}"}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    def _basic_auth(self, client_id: str, client_secret: str) -> str:
        """Create Basic Authentication header."""
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"