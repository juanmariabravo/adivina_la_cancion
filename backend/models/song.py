class Song:
    """Modelo de canción para el juego"""
    
    def __init__(
        self,
        id: str,
        title: str,
        artists: str,
        album: str,
        year: int,
        genre: str,
        audio: str,
        image_url: str,
        level_id: int
    ):
        self.id = id
        self.title = title
        self.artists = artists
        self.album = album
        self.year = year
        self.genre = genre
        self.audio = audio
        self.image_url = image_url
        self.level_id = level_id
    
    def to_dict(self) -> dict:
        """Convertir objeto Song a diccionario"""
        return {
            'id': self.id,
            'title': self.title,
            'artists': self.artists,
            'album': self.album,
            'year': self.year,
            'genre': self.genre,
            'audio': self.audio,
            'image_url': self.image_url,
            'level_id': self.level_id
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Song':
        """Crear instancia desde diccionario compatible con local_songs o spotify_songs."""
        # id puede venir como 'spotify_id' o como 'id' (local)
        song_id = data.get('spotify_id') or data.get('id') or ''
        song_id = str(song_id)

        # el audio puede llamarse 'audio' (spotify) o 'audio_codificado' (local)
        audio = data.get('audio') or data.get('audio_codificado') or ''

        # level_id no existe en la tabla local_songs; usar el mismo valor del id
        level_raw = data.get('level_id')
        try:
            level_id = int(level_raw) if level_raw is not None else int(song_id)
        except (ValueError, TypeError):
            level_id = 0

        # convertir year a int seguro
        try:
            year = int(data.get('year')) if data.get('year') is not None else 0
        except (ValueError, TypeError):
            year = 0

        return Song(
            id=song_id,
            title=data.get('title', '') or '',
            artists=data.get('artists', '') or '',
            album=data.get('album', '') or '',
            year=year,
            genre=data.get('genre', '') or '',
            audio=audio,
            image_url=data.get('image_url', '') or '',
            level_id=level_id
        )
