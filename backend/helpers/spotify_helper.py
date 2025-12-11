import requests
import os
from helpers.spotify_preview import get_spotify_preview_url
from typing import Optional
from dotenv import load_dotenv

from models.song import Song

load_dotenv()

class SpotifyHelper:
    """Helper para interactuar con la API de Spotify"""

    def __init__(self):
        self.api_url = os.getenv("SPOTIFY_API_URL")

    def get_track_info(
        self, spotify_track_id: str, access_token: str
    ) -> Optional[Song]:
        """
        Obtener información de un track de Spotify por su ID
        """
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                f"{self.api_url}/tracks/{spotify_track_id}", headers=headers
            )

            if response.status_code != 200:
                print(f"Error obteniendo track: {response.status_code}")
                return None

            track = response.json()

            # Extraer información relevante
            title = track["name"]
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            album = track["album"]["name"]
            year = int(track["album"]["release_date"][:4])

            # Género (requiere llamada adicional a artista)
            genre = self.get_track_genre(track["artists"][0]["id"], access_token)

            # Preview URL usando spotify_preview
            audio = get_spotify_preview_url(spotify_track_id)

            # Imagen del álbum
            image_url = (
                track["album"]["images"][0]["url"] if track["album"]["images"] else ""
            )

            # Construir objeto Song
            song = Song(
                id=spotify_track_id,
                title=title,
                artists=artists,
                album=album,
                year=year,
                genre=genre or "Unknown",
                audio=audio,
                image_url=image_url,
                level_id=-999,  # level_id temporal, se asignará en game_service.py > get_level_song
            )
            return song

        except Exception as e:
            print(f"Error obteniendo track de Spotify: {e}")
            return None

    def get_track_genre(self, artist_id: str, access_token: str) -> Optional[str]:
        """Obtener género del artista"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(
                f"{self.api_url}/artists/{artist_id}", headers=headers
            )

            if response.status_code == 200:
                artist_data = response.json()
                genres = artist_data.get("genres", [])
                return genres[0] if genres else None

            return None
        except Exception as e:
            print(f"Error obteniendo género del artista: {e}")
            return None

    ## Para la función futura de jugar con playlists de cada usuario
    """
    def get_random_track_from_playlist(self, playlist_id: str, access_token: str) -> Optional[dict]:
        ""
        Obtener track aleatorio de una playlist de Spotify
        ""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            # Obtener tracks de la playlist
            response = requests.get(
                f'{self.api_url}/playlists/{playlist_id}/tracks',
                headers=headers,
                params={'limit': 50}
            )
            
            if response.status_code != 200:
                print(f"Error obteniendo playlist: {response.status_code}")
                return None
            
            data = response.json()
            tracks = data.get('items', [])
            
            if not tracks:
                return None
            
            # Seleccionar track aleatorio
            import random
            track_item = random.choice(tracks)
            track = track_item.get('track')
            
            if not track:
                return None
            
            # Extraer información del track
            spotify_id = track['id']
            title = track['name']
            
            # Artistas: concatenar nombres
            artists = ', '.join([artist['name'] for artist in track['artists']])
            
            # Álbum
            album = track['album']['name']
            
            # Año
            year = int(track['album']['release_date'][:4])
            
            # Género (requiere llamada adicional a artista)
            genre = self.get_track_genre(track['artists'][0]['id'], access_token)
            
            # Preview URL usando spotify_preview
            audio = get_spotify_preview_url(spotify_id)
            
            # Imagen del álbum
            image_url = track['album']['images'][0]['url'] if track['album']['images'] else ''
            
            return {
                'spotify_id': spotify_id,
                'title': title,
                'artists': artists,
                'album': album,
                'year': year,
                'genre': genre or 'Unknown',
                'audio': audio,
                'image_url': image_url
            }
            
        except Exception as e:
            print(f"Error obteniendo track de Spotify: {e}")
            return None
    """


# Instancia global
spotify_helper = SpotifyHelper()
