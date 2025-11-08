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
    
    def to_dict(self, include_answer: bool = False) -> dict:
        """Convertir canción a diccionario"""
        song_dict = {
            'id': self.id,
            'audio': self.audio,
            'image_url': self.image_url,
            'hints': {
                'year': self.year,
                'genre': self.genre,
                'album': self.album,
                'artists': self.artists,
                'title_hint': self.title[:len(self.title)//2]  # Primera mitad del título
            }
        }
        
        if include_answer:
            song_dict['title'] = self.title
            song_dict['artists'] = self.artist
        
        return song_dict
    
    @staticmethod
    def from_dict(data: dict) -> 'Song':
        """Crear instancia desde diccionario"""
        return Song(
            id=data.get('id'),
            title=data.get('title'),
            artists=data.get('artists'),
            album=data.get('album'),
            year=data.get('year'),
            genre=data.get('genre'),
            audio=data.get('audio'),
            image_url=data.get('image_url'),
            level_id=data.get('level_id')
        )
