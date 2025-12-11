"""
Obtener la URL de previsualización (preview) de una pista de Spotify usando la página embebida como workaround.

Descripción:
    Esta función solicita la página embebida de Spotify para una pista concreta
    y extrae, mediante una búsqueda en el HTML, la URL del audio de previsualización.
    Es un método de tipo "workaround" que depende de la estructura interna de la página
    de Spotify y puede dejar de funcionar si Spotify cambia dicho HTML o el formato JSON
    incrustado.

Referencia / Atribución:
    Basado en el workaround publicado en GitHub:
    Rexdotsh. (s. f.). GitHub - rexdotsh/spotify-preview-url-workaround. GitHub.
    https://github.com/rexdotsh/spotify-preview-url-workaround
"""
import re
from typing import Optional

import requests


def get_spotify_preview_url(spotify_track_id: str) -> Optional[str]:
    """
    Get the preview URL for a Spotify track using the embed page workaround.

    Args:
        spotify_track_id (str): The Spotify track ID

    Returns:
        Optional[str]: The preview URL if found, else None
    """
    try:
        embed_url = f"https://open.spotify.com/embed/track/{spotify_track_id}"
        response = requests.get(embed_url)
        response.raise_for_status()

        html = response.text
        match = re.search(r'"audioPreview":\s*{\s*"url":\s*"([^"]+)"', html)
        return match.group(1) if match else None

    except Exception as e:
        print(f"Failed to fetch Spotify preview URL: {e}")
        return None


# example usage:
# preview_url = get_spotify_preview_url('1301WleyT98MSxVHPZCA6M')