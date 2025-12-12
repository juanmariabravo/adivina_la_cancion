# Flujo del Proyecto "Adivina la Canción" - Documentación

> Proyecto completo de una aplicación web de adivinanza musical con integración Spotify
> Autor: Juan María Bravo López
> Curso: Multimedia 2025/26

---

## TABLA DE CONTENIDOS

1. [Arquitectura General](#arquitectura-general)
2. [Flujo de Autenticación](#flujo-de-autenticación)
3. [Flujo de Integración con Spotify](#flujo-de-integración-con-spotify)
4. [Flujo de Juego](#flujo-de-juego)
5. [Sistema de Puntuación y Ranking](#sistema-de-puntuación-y-ranking)
6. [Endpoints de la API](#endpoints-de-la-api)
7. [Flujo Completo Ejemplo](#flujo-completo-ejemplo)
8. [Notas Finales](#notas-finales)

---

## ARQUITECTURA GENERAL

### Stack Tecnológico
- **Frontend:** Angular 19 + TypeScript
- **Backend:** Flask (Python) con arquitectura por capas
- **Base de datos:** SQLite
- **Autenticación:** JWT (JSON Web Tokens)
- **API Externa:** Spotify Web API
- **CORS:** Flask-CORS

### Arquitectura del Backend

```
backend/
├── app.py                    # Punto de entrada, registro de blueprints
├── controllers/              # Capa de presentación (endpoints)
│   ├── user_controller.py    # /api/v1/auth/*
│   ├── game_controller.py    # /api/v1/game/*, /api/v1/songs/*, /api/v1/ranking
│   └── spotify_controller.py # /api/v1/spoti/*
├── services/                 # Lógica de negocio
│   ├── user_service.py
│   ├── game_service.py
│   └── spoti_service.py
├── models/                   # Modelos de datos
│   ├── user.py
│   └── song.py
├── database/                 # Capa de acceso a datos
│   └── database.py
└── helpers/                  # Utilidades
    ├── spotify_helper.py     # Llamadas a Spotify API
    └── spotify_preview.py    # Web scraping para previews
```

### Arquitectura del Frontend

```
frontend/src/app/
├── app.ts                    # Componente raíz
├── app.routes.ts             # Configuración de rutas
├── home/                     # Página principal
├── login/                    # Inicio de sesión
├── register/                 # Registro
├── levels/                   # Selección de niveles
├── game/                     # Pantalla de juego
├── profile/                  # Perfil de usuario
├── ranking/                  # Clasificación
├── callback/                 # OAuth Spotify callback
└── services/                 # Servicios compartidos
    ├── user-service.ts       # Autenticación y gestión de usuarios
    ├── game.service.ts       # Lógica de juego
    └── spotify.service.ts    # Comunicación con Spotify
```

---

## FLUJO DE AUTENTICACIÓN

### 1a. Registro de Usuario (`POST /api/v1/auth/register`)

**Frontend:**
1. Usuario completa formulario (username, email, password, confirmPassword)
2. Se valida que las contraseñas coincidan
3. Se envía petición POST al backend
4. Si es exitoso:
   - Se guarda el token JWT en `sessionStorage`
   - Se guardan datos del usuario en el servicio
   - Redirección a `/levels`

**Backend:**
1. Recibe datos del formulario
2. Validaciones:
   - Campos obligatorios presentes
   - Email con formato válido
   - Contraseñas coinciden
   - Username/email únicos
3. Hash de contraseña con bcrypt
4. Inserta usuario en base de datos
5. Genera token JWT con expiración de 24h
6. Respuesta (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6I...",
  "message": "Usuario creado exitosamente",
  "token_type": "bearer",
  "user": {
    "daily_completed": false,
    "email": "example@gmail.com",
    "levels_completed": "",
    "played_levels": "",
    "total_score": 0,
    "username": "exampleuser"
  }
}
```

---

### 1b. Inicio de Sesión (`POST /api/v1/auth/login`)

**Frontend:**
1. Verifica si ya existe token en `sessionStorage`
   - Si existe y es válido → redirección automática a `/levels`
2. Usuario ingresa credenciales (username/email + password)
3. Envía petición POST al backend
4. Si exitoso:
   - Guarda token en `sessionStorage`
   - Actualiza estado del usuario
   - Redirección a `/levels`

**Backend:**
1. Recibe credenciales
2. Busca usuario por username o email
3. Verifica contraseña con bcrypt
4. Calcula `daily_completed` comparando `last_daily_completed` con fecha actual
5. Genera nuevo token JWT
6. Respuesta (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5c...",
  "message": "Login exitoso",
  "token_type": "bearer",
  "user": {
    "daily_completed": false,
    "email": "example@gmail.com",
    "levels_completed": "",
    "played_levels": "",
    "total_score": 0,
    "username": "exampleuser"
  }
}
```

---

### 1c. Modo Invitado

**Flujo:**
1. Usuario accede sin registrarse
2. No se genera ni almacena token
3. Acceso limitado a:
   - Niveles locales (1-10)
   - No se guarda puntuación
   - No acceso a niveles de Spotify
   - No participa en el ranking, pero sí puede verlo
4. Redirección directa a `/levels`

**Limitaciones:**
- Solo 10 niveles disponibles (`1_local`, `2_local`, `3_local`, ..., `10_local`)
- Progreso no persistente
- Sin estadísticas
- Sin perfil personalizado


---

## FLUJO DE INTEGRACIÓN CON SPOTIFY

### Configuración Inicial

**Requisitos:**
- Usuario registrado en la aplicación
- Cuenta de Spotify (Free o Premium)
- Client ID y Client Secret de Spotify Developer Dashboard

### Proceso de Conexión

#### Fase 1: Registro con Credenciales Spotify

**Durante el Registro (`POST /api/v1/auth/register`):**

Frontend envía credenciales Spotify junto con datos de registro:
```typescript
const registerData = {
  username: 'usuario123',
  email: 'user@example.com',
  pwd1: 'password',
  pwd2: 'password',
  spotify_client_id: 'tu_client_id',
  spotify_client_secret: 'tu_client_secret'
};
```

Backend (`user_service.py`):
1. Valida que Client ID y Client Secret sean obligatorios
2. Guarda en base de datos:
```sql
UPDATE users 
SET spotify_client_id = ?, 
    spotify_client_secret = ? 
WHERE username = ?
```

---

#### Fase 2: Autorización OAuth de Spotify

**1. Inicio de Autorización (desde Perfil)**

Usuario hace clic en "Conectar Spotify" en `/profile` o en `/levels`:

```typescript
connectSpotify(): void {
  this.spotifyService.getClientId(this.email).subscribe({
    next: (response) => {
      this.spotifyService.redirectToSpotifyAuth(response.clientId);
    }
  });
}
```

**2. Solicitud de Client ID (`GET /api/v1/spoti/getClientId?email={email}`)**

Backend devuelve el Client ID:
```python
def get_spotify_client_id(self, email):
    user = db.get_user_by_email(email.lower())
    if user and user.spotify_client_id:
        return {"clientId": user.spotify_client_id}, 200
    return {"error": "No tienes credenciales de Spotify configuradas"}, 400
```

**3. Redirección a Spotify OAuth**

Frontend redirige al usuario a:
```
https://accounts.spotify.com/authorize?
  client_id={CLIENT_ID}&
  response_type=code&
  redirect_uri={REDIRECT_URI}&
  scope=user-read-private user-read-email&
  show_dialog=true
```

**4. Usuario Autoriza en Spotify**

Spotify muestra pantalla de autorización → Usuario acepta

**5. Callback con Código de Autorización**

Spotify redirige a: `http://localhost:4200/callback?code={AUTH_CODE}`

---

#### Fase 3: Intercambio de Código por Token

**Componente Callback (`/callback`):**

```typescript
private exchangeCodeForToken(code: string): void {
  const email = sessionStorage.getItem('email');
  
  // Primera petición: obtener clientId
  this.spotifyService.getClientId(email).subscribe({
    next: (clientIdResponse) => {
      const clientId = clientIdResponse.clientId;
      const token = sessionStorage.getItem('authToken');
      
      // Segunda petición: intercambiar código por token
      this.spotifyService.exchangeCodeForTokenWithClientId(
        code, 
        clientId, 
        token!
      ).subscribe({
        next: (response) => {
          if (response.connected) {
            this.spotifyService.markSpotifyConnected();
            this.router.navigate(['/levels']);
          }
        }
      });
    }
  });
}
```

**Backend (`GET /api/v1/spoti/getAuthorizationToken`)**

```python
def get_authorization_token(self, code: str, client_id: str) -> tuple[dict, int]:
    # 1. Buscar usuario por client_id
    user = db.get_user_by_client_id(client_id)
    
    # 2. Desencriptar client_secret
    client_secret = user.get_client_secret()
    
    # 3. Preparar petición a Spotify
    form_data = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    
    auth_header = self._basic_auth(client_id, client_secret)
    
    # 4. Intercambiar código por token
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data=form_data,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )
    
    token_data = response.json()
    
    # 5. Guardar tokens en BD
    db.save_spotify_tokens(
        user.username,
        token_data.get("access_token"),
        token_data.get("refresh_token"),
        token_data.get("expires_in")
    )
    
    # 6. Solo confirmar éxito (NO enviar tokens al frontend)
    return {"message": "Spotify conectado exitosamente", "connected": True}, 200
```

---

#### Fase 4: Uso de Tokens en Peticiones

**Cuando se solicita una canción de Spotify:**

Frontend:
```typescript
// Solo envía JWT del usuario
this.gameService.getSongForLevel(levelId, token).subscribe();
```

Backend (`game_service.py`):
1. Valida JWT del usuario
2. Obtiene username del token
3. Busca usuario en BD
4. Usa token para llamar a Spotify API:
```python
headers = {
    "Authorization": f"Bearer {spotify_access_token}"
}
response = requests.get(
    f"https://api.spotify.com/v1/tracks/{track_id}",
    headers=headers
)
```

**Manejo de Expiración:**

Si Spotify retorna 401:
```python
# Marcar token como expirado
UPDATE users 
SET spotify_token_expired = 1 
WHERE username = ?
```

Frontend muestra mensaje:
```
"Tu conexión con Spotify ha expirado. Por favor, vuelve a conectarte desde tu perfil"
```

---

### Verificación de Conexión

**Frontend mantiene estado local:**
```typescript
// sessionStorage (temporal, se pierde al cerrar navegador)
sessionStorage.setItem('spotifyConnected', 'true');

// Verificar
isSpotifyConnected(): boolean {
  return sessionStorage.getItem('spotifyConnected') === 'true';
}
```

**Backend valida en cada petición:**
```python
def get_level_song(self, level_id, auth_header):
    # Para niveles Spotify (no locales)
    if not level_id.endswith('_local'):
        user = self.get_user_from_token(auth_header)
        
        if not user.has_spotify_credentials():
            return {"error": "Spotify no conectado"}, 403
            
        if user.spotify_token_expired:
            return {"error": "Tu token de Spotify ha expirado"}, 403
```

---

### Diagrama de Flujo OAuth

```
┌─────────┐      ┌──────────┐       ┌─────────┐      ┌─────────┐
│ Usuario │      │ Frontend │       │ Backend │      │ Spotify │
└────┬────┘      └────┬─────┘       └────┬────┘      └────┬────┘
     │                │                  │                │
     │ Clic "Conectar"│                  │                │
     ├───────────────>│                  │                │
     │                │ GET clientId     │                │
     │                ├─────────────────>│                │
     │                │<─────────────────┤                │
     │                │ Redirige a OAuth │                │
     │                ├──────────────────────────────────>│
     │                │                  │ Autorización   │
     │                │<──────────────────────────────────┤
     │ Callback+code  │                  │                │
     │<───────────────┤                  │                │
     │                │ Exchange code    │                │
     │                ├─────────────────>│ POST token     │
     │                │                  ├───────────────>│
     │                │                  │ access_token   │
     │                │                  │<───────────────┤
     │                │ Confirma conexión│                │
     │                │<─────────────────┤                │
     │ Redirect /levels                  │                │
     │<───────────────┤                  │                │
```

---

## FLUJO DE JUEGO

### Estructura de Niveles

**Niveles Locales (Invitados):**
- `1_local`, `2_local`, `3_local`
- Datos de `local_songs.json`
- Sin necesidad de autenticación

**Niveles Spotify (Usuarios Registrados):**
- Niveles 1-30
- Datos de `spotify_songs.json`
- Requiere Spotify conectado

**Nivel Diario:**
- `level_id = 0`
- Una canción diferente cada día
- Solo jugable una vez al día

---

### Inicialización del Juego

**1. Navegación a Nivel**

Usuario selecciona nivel → Router navega a `/game?level={level_id}`

**2. Carga de Canción (`GET /api/v1/songs/{level_id}`)**

Frontend solicita datos del nivel:
```typescript
this.gameService.getSongForLevel(levelId, token).subscribe({
  next: (song) => {
    this.currentSong = song;
    this.audioReady = true;
  },
  error: (err) => {
    // Manejo de errores según código HTTP
  }
});
```

Backend (`game_service.py`):
1. Determina tipo de nivel (local/spotify/daily)
2. **Para niveles locales:**
   - Lee `local_songs.json`
   - Retorna datos directamente
3. **Para niveles Spotify:**
   - Valida token JWT
   - Verifica Spotify conectado
   - Obtiene Spotify access_token
   - Llama a `spotify_helper.py`
   - Si canción no tiene preview:
     - Llama a `spotify_preview.py` (web scraping)
   - Retorna datos procesados
4. **Para nivel diario:**
   - Selecciona aleatoriamente de `possible_daily_songs.json`
   - Aplica mismo proceso que nivel Spotify

Respuesta (200 OK):
```json
{
  "album": "VIDA",
  "artists": "Luis Fonsi, Daddy Yankee",
  "audio": "https://p.scdn.co/mp3-preview/2ea246524bf5a1a6432d4cf1b911a98bd84e3e8e",
  "genre": "latin",
  "id": "6habFhsOp2NvshLv26DqMb",
  "image_url": "https://i.scdn.co/image/ab67616d0000b273ef0d4234e1a645740f77d59c",
  "level_id": 1,
  "title": "Despacito",
  "year": 2019
}
```

Códigos de error:
- **401:** Token inválido/expirado
- **403:** 
  - Spotify no conectado
  - Token Spotify expirado
  - Límite de niveles para invitados
- **404:** Nivel no existe

---

### Progresión del Juego

**Sistema de 6 Intentos**

Cada intento revela más pistas:

| Intento | Audio Total | Imagen              | Pistas Textuales             |
| ------- | ----------- | ------------------- | ---------------------------- |
| 1       | 1s          | 1/4 (superior izq.) | -                            |
| 2       | 3s          | 2/4                 | Año de lanzamiento           |
| 3       | 5s          | 3/4                 | Género musical               |
| 4       | 7s          | 4/4 (completa)      | Álbum                        |
| 5       | 9s          | 4/4                 | Artista                      |
| 6       | 11s         | 4/4                 | Primeras 3 letras del título |

**Interacción Frontend:**

```typescript
playAudio() {
  this.audio = new Audio(this.currentSong!.audio);
  this.audio.currentTime = 0;
  
  // Reproducir los segundos según intento
  setTimeout(() => {
    this.audio!.pause();
  }, this.audioSeconds * 1000);
  
  this.audio.play();
}

submitAnswer() {
  const normalized = this.normalizeString(this.userAnswer);
  const correctTitle = this.normalizeString(this.currentSong!.title);
  
  if (normalized === correctTitle) {
    this.isCorrect = true;
    this.calculateScore();
    if (!this.isGuest) {
      this.submitScore();
    }
  } else {
    this.currentAttempt++;
    this.updateHints();
  }
}

private normalizeString(str: string): string {
  return str
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, '');
}
```

---

### Sistema de Pistas

**Audio:**
- Intento 1: 0-1s
- Intento 2: 0-3s
- Intento 3: 0-5s
- Intento 4: 0-7s
- Intento 5: 0-9s
- Intento 6: 0-11s

**Imagen (cuadrícula 2x2):**
```css
.image-container {
  width: 400px;
  height: 400px;
  overflow: hidden;
}

.quarter-1 { clip-path: inset(0 50% 50% 0); }      /* Superior izq */
.quarter-2 { clip-path: inset(0 0 50% 50%); }      /* Superior der */
.quarter-3 { clip-path: inset(50% 50% 0 0); }      /* Inferior izq */
.quarter-4 { clip-path: none; }                    /* Imagen completa */
```

**Pistas Textuales:**
1. **Año:** `this.currentSong.year` (ej: "1975")
2. **Género:** `this.currentSong.genre` (ej: "Rock")
3. **Álbum:** `this.currentSong.album` (ej: "A Night at the Opera")
4. **Artista:** `this.currentSong.artists` (ej: "Queen")
5. **Título parcial:** `this.currentSong.title_hint` (ej: "Boh...")

---

### Finalización del Nivel

**Victoria (respuesta correcta):**
```typescript
this.isCorrect = true;
this.gameOver = true;
this.showAnswer = true;
this.calculateScore();

if (!this.isGuest) {
  this.submitScore();
  this.markLevelAsPlayed();
}
```

**Derrota (6 intentos fallidos):**
```typescript
if (this.currentAttempt > this.maxAttempts) {
  this.gameOver = true;
  this.showAnswer = true;
  this.score = 0;
  
  if (!this.isGuest) {
    this.submitScore(); // Puntuación 0
    this.markLevelAsPlayed();
  }
}
```

**Opciones post-juego:**
- Reintentar nivel
- Volver a niveles
- Siguiente nivel (si disponible)

---

## SISTEMA DE PUNTUACIÓN Y RANKING

### Cálculo de Puntuación

**Fórmula Base:**
```typescript
calculateScore() {
  const baseScore = 1000;
  const penalty = (this.currentAttempt - 1) * 150;
  this.score = Math.max(0, baseScore - penalty);
  
  // Bonus nivel diario
  if (this.levelId === 'daily') {
    this.score = Math.floor(this.score * 1.5);
  }
}
```

**Tabla de Puntos:**
| Intento | Puntuación Base |
| ------- | --------------- |
| 1       | 1000            |
| 2       | 850             |
| 3       | 700             |
| 4       | 550             |
| 5       | 400             |
| 6       | 250             |
| Fallo   | 0               |
---

### Envío de Puntuación (`POST /api/v1/game/submit-score`)

Frontend:
```typescript
submitScore() {
  const payload = {
    score: this.score,
    level_id: this.levelId
  };
  
  this.gameService.submitScore(payload, this.userService.getToken()!)
    .subscribe({
      next: (response) => {
        console.log('Puntuación actualizada:', response.total_score);
      }
    });
}
```

Backend (`game_service.py`):
1. Valida token JWT
2. Extrae username del token
3. Actualiza base de datos:
```python
UPDATE users 
SET total_score = total_score + ?, 
    games_played = games_played + 1 
WHERE username = ?
```
4. Si es nivel diario:
```python
UPDATE users 
SET last_daily_completed = ? 
WHERE username = ?
```
5. Respuesta (200 OK):
```json
{
  "message": "Puntuación actualizada",
  "total_score": 15420,
  "games_played": 48
}
```

---

### Ranking Global (`GET /api/v1/ranking`)

Frontend:
```typescript
this.gameService.getRanking(10).subscribe(ranking => {
  this.topPlayers = ranking;
});
```

Backend:
```python
SELECT username, total_score, games_played 
FROM users 
WHERE total_score > 0 
ORDER BY total_score DESC 
LIMIT ?
```

Respuesta (200 OK):
```json
[
  {
    "username": "player1",
    "total_score": 25000,
    "games_played": 85
  },
  {
    "username": "player2",
    "total_score": 22500,
    "games_played": 72
  }
]
```

---

### Marcar Nivel como Jugado (`POST /api/v1/game/mark-level-played`)

Frontend:
```typescript
markLevelAsPlayed() {
  this.gameService.markLevelPlayed(this.levelId, this.userService.getToken()!)
    .subscribe();
}
```

Backend:
1. Valida token
2. Obtiene `played_levels` del usuario
3. Añade `level_id` si no existe
4. Actualiza:
```sql
UPDATE users 
SET played_levels = ? 
WHERE username = ?
```

Formato `played_levels`: `"1,2,5,0,15,20"`

---

## ENDPOINTS DE LA API

### Autenticación (`/api/v1/auth`)

| Método | Endpoint    | Descripción              | Auth |
| ------ | ----------- | ------------------------ | ---- |
| POST   | `/register` | Registro de usuario      | No   |
| POST   | `/login`    | Inicio de sesión         | No   |
| POST   | `/logout`   | Cierre de sesión         | Sí   |
| GET    | `/me`       | Datos del usuario actual | Sí   |
---

### Juego (`/api/v1/game`, `/api/v1/songs`)

| Método | Endpoint                  | Descripción               | Auth     |
| ------ | ------------------------- | ------------------------- | -------- |
| GET    | `/songs/{level_id}`       | Obtener canción del nivel | Opcional |
| POST   | `/game/submit-score`      | Enviar puntuación         | Sí       |
| POST   | `/game/mark-level-played` | Marcar nivel jugado       | Sí       |
| POST   | `/game/daily/complete`    | Completar desafío diario  | Sí       |
| GET    | `/ranking?limit=10`       | Obtener ranking           | No       |

---

### Spotify (`/api/v1/spoti`)

| Método | Endpoint                                           | Descripción               | Auth |
| ------ | -------------------------------------------------- | ------------------------- | ---- |
| GET    | `/getClientId?email={email}`                       | Obtener Client ID         | No   |
| GET    | `/getAuthorizationToken?code={code}&clientId={id}` | Intercambiar código OAuth | No   |

---

## FLUJO COMPLETO EJEMPLO

### Usuario Nuevo → Juego Completo

1. **Registro:**
   - POST `/api/v1/auth/register`
   - Recibe token JWT
   - Guarda en localStorage

2. **Conexión Spotify:**
   - POST `/api/v1/auth/spotify-credentials`
   - Redirección a Spotify OAuth
   - Callback con código
   - GET `/api/v1/spoti/getAuthorizationToken`
   - POST `/api/v1/auth/update-spotify-token`

3. **Selección de Nivel:**
   - Navega a `/levels`
   - Visualiza niveles 1-40 desbloqueados

4. **Juego:**
   - Navega a `/game?level=15`
   - GET `/api/v1/songs/15` (con token)
   - Recibe datos de Spotify
   - Juega 6 intentos
   - Acierta en intento 3 → 700 puntos

5. **Puntuación:**
   - POST `/api/v1/game/submit-score` → +700
   - POST `/api/v1/game/mark-level-played` → nivel 15 marcado

6. **Ranking:**
   - Navega a `/ranking`
   - GET `/api/v1/ranking?limit=10`
   - Visualiza posición global

---

## NOTAS FINALES

### Limitaciones Conocidas
- Spotify Free: Preview de 30s máximo
- Web scraping puede fallar si Spotify cambia HTML
- Token Spotify expira cada hora (requiere reconexión)
- SQLite no recomendado para producción a gran escala

### Mejoras Futuras
- Implementar refresh token de Spotify
- Migrar a PostgreSQL
- Añadir modo multijugador
- Sistema de logros y badges
- Playlists personalizadas

---

**Fin de la Documentación**  
*Proyecto "Adivina la Canción" | Juan María Bravo López | Multimedia | Curso 2025/26*

