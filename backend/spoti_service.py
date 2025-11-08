import base64
import os
import requests
from requests.exceptions import RequestException

REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

class SpotiService:
    def __init__(self, user_dao, user_service):
        self.user_dao = user_dao
        self.user_service = user_service
        self.token_url = "https://accounts.spotify.com/api/token"

    def get_client_id(self, email: str) -> str:
        """Get client ID for a user by email."""
        user = self.user_dao.find_by_id(email)
        if user is None:
            raise ValueError("El email no está registrado")
        return user.client_id

    def get_authorization_token(self, code: str, client_id: str) -> dict:
        """Get authorization token from Spotify API."""
        user = self.user_service.get_user_by_client_id(client_id)
        client_secret = user.client_secret

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
                self.token_url,
                data=form_data,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Error getting authorization token: {str(e)}")

    def _basic_auth(self, client_id: str, client_secret: str) -> str:
        """Create Basic Authentication header."""
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded}"