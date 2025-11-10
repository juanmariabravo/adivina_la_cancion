# *en desarrollo...*
Aplicación web en desarrollo como proyecto para la asignatura de Multimedia del cuarto curso del grado en Ingeniería Informática, de la Universidad de Castilla La Mancha.
<img src="home_adivina.png" alt="Mockup del juego Adivina la Canción" width="600"/>
<img src="adivina_la_cancion.png" alt="Nivel de Adivina la Canción" width="*"/>
# 🎵 Adivina la Canción - *¿Cuánto sabes de música?*

**Adivina la Canción** es una aplicación web interactiva que desafía a los usuarios a identificar canciones a partir de pistas multimedia. Cada pista ofrece fragmentos de audio, imágenes parciales y datos del artista o del lanzamiento para poner a prueba tu oído y tu memoria musical.

> Este proyecto ha sido desarrollado para la asignatura de Multimedia del cuarto curso del grado en Ingeniería Informática, de la Universidad de Castilla La Mancha. 

---

## 🚀 Tecnologías utilizadas
- **Frontend:** Angular, TypeScript, HTML5, CSS3
- **Backend:** Flask (Python)
- **Base de datos:** SQLite

---

## 🎮 Características principales

- Reproducción de fragmentos de canciones
- Visualización progresiva de imágenes de portada/artista
- Pistas textuales sobre el lanzamiento o el artista
- Sistema de puntuación por rapidez y precisión
- Modo invitado para jugar sin registro
- Inicio de sesión y conexión con Spotify para usar playlists propias
- Ranking global de jugadores
- Perfil de usuario con estadísticas de juego

---

## 📁 Estructura del proyecto

```
adivina_la_cancion/
├── backend
│   ├── adivina_la_cancion.db #-- base de datos SQLite
│   ├── app.py #-- archivo principal de la aplicación Flask
│   ├── database.py #-- configuración y manejo de la base de datos
│   ├── download_songs
│   │   └── local_songs.json #-- lista de canciones descargadas localmente
│   ├── game_service.py
│   ├── models
│   │   ├── song.py
│   │   └── user.py
│   ├── requirements.txt #-- dependencias del backend
│   ├── spotify_helper.py
│   ├── spotify_preview.py #-- manejo de previews de audio de Spotify
│   ├── spoti_service.py #-- servicio de integración con Spotify
│   └── user_service.py
├── frontend
│   ├── src
│   │   ├── app
│   │   │   ├── app.component.css
│   │   │   ├── app.config.ts
│   │   │   ├── app.css
│   │   │   ├── app.html
│   │   │   ├── app.routes.ts
│   │   │   ├── app.spec.ts
│   │   │   ├── app.ts
│   │   │   ├── callback
│   │   │   │   └── callback.ts
│   │   │   ├── game
│   │   │   │   ├── game.css
│   │   │   │   ├── game.html
│   │   │   │   └── game.ts
│   │   │   ├── home #-- página principal
│   │   │   │   ├── home.css
│   │   │   │   ├── home.html
│   │   │   │   └── home.ts
│   │   │   ├── levels
│   │   │   │   ├── levels.css
│   │   │   │   ├── levels.html
│   │   │   │   └── levels.ts
│   │   │   ├── login
│   │   │   │   ├── login.css
│   │   │   │   ├── login.html
│   │   │   │   └── login.ts
│   │   │   ├── profile
│   │   │   │   ├── profile.css
│   │   │   │   ├── profile.html
│   │   │   │   └── profile.ts
│   │   │   ├── ranking
│   │   │   │   ├── ranking.css
│   │   │   │   ├── ranking.html
│   │   │   │   └── ranking.ts
│   │   │   └── register
│   │   │       ├── register.css
│   │   │       ├── register.html
│   │   │       └── register.ts
│   │   ├── index.html
│   │   ├── main.ts
│   │   ├── services
│   │   │   ├── game.service.ts
│   │   │   ├── spotify.service.ts
│   │   │   └── user-service.ts
│   │   └── styles.css
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   └── tsconfig.spec.json
├── LICENSE
└──  OBJETIVOSySEGUIMIENTO.md
```

---

## 🛠️ Instalación y ejecución

### 1. Clonar el repositorio

```shell
git clone https://github.com/juanmariabravo/adivina_la_cancion
cd adivina_la_cancion
```

### 2. Instalar dependencias

#### Frontend
```shell
# Navega al directorio del frontend
cd frontend
# Instala las dependencias
npm install
```

#### Backend
```shell
# Navega al directorio del backend
cd backend
# Crea un entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
# Instala las dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en `backend/` con tus claves de API (Spotify, base de datos, etc.):
```env
# Clave secreta para encriptación de tokens y sesiones (cadena aleatoria de al menos 32 caracteres)
SECRET_KEY=rq8$y!7z@XcVb[...]]df32saasdasdfg34hjkl;
# Puerto del servidor
PORT=5000

# Ruta de la base de datos SQLite
DATABASE_PATH=adivina_la_cancion.db

# Spotify API Credentials
> Necesitas registrar tu aplicación en el [Dashboard de Desarrolladores de Spotify](https://developer.spotify.com/dashboard/applications) para obtener estas credenciales.
> Después, tendrás que configurar la URI de redirección a `http://<tu_dominio_o_localhost>:4200/callback`
> Es impotante que al registrarte en Adivina la Canción uses el mismo correo electrónico que usas en tu cuenta de Spotify, para que la integración funcione correctamente.

SPOTIFY_CLIENT_ID=1g2[...]a2j7
SPOTIFY_CLIENT_SECRET=2h3[...]b3i3
SPOTIFY_REDIRECT_URI=http://127.0.0.1:4200/callback
```


### 4. Ejecutar la aplicación

#### Backend
```shell
# Asegúrate de estar en el entorno virtual si lo creaste
source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
# Navega al directorio del backend
cd backend
# Ejecuta la aplicación Flask
python3 app.py
```

# Frontend
```shell
# Navega al directorio del frontend
cd frontend
# Ejecuta la aplicación Angular
ng serve --open --host <tu_dominio_o_localhost>
```

---

## 📦 Recursos útiles

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Spotify Preview URLs](https://github.com/rexdotsh/spotify-preview-url-workaround)
- [Angular Docs](https://angular.io/docs)

---

## 📜 Licencia

Este proyecto se desarrolla con fines educativos para la asignatura de Multimedia en la Universidad de Castilla-La Mancha.

---

## ✨ Autor

**Juan María Bravo López** – Estudiante de Ingeniería Informática, apasionado por la música y la tecnología multimedia.
