# Flujo desde el registro hasta el juego (backend y frontend):

---

### 1. Registro de usuario (`/api/v1/auth/register`)

- **Frontend:**  
  El usuario completa el formulario de registro (username, email, pwd1, pwd2) y envía los datos.
- **Backend:**  
  - Recibe los datos.
  - Valida que los campos sean correctos y que las contraseñas coincidan.
  - Si todo es válido, crea el usuario en la base de datos.
  - Genera un **token** (por ejemplo, JWT o similar) para ese usuario.
  - Devuelve al frontend:
    - `access_token` (el token generado)
    - `token_type` (usualmente "bearer")
    - Datos del usuario (username, email, total_score, games_played)
    - Mensaje de éxito

---

### 2. Almacenamiento del token

- **Frontend:**  
  - Recibe el token y los datos del usuario.
  - Guarda el token en el almacenamiento local (localStorage, sessionStorage o en memoria).
  - Opcional: guarda también los datos del usuario para mostrar en la UI. Hasta ahora se guarda games_played y total_score.

---

### 3. Acceso al juego

- **Frontend:**
  - Cuando el usuario navega a la sección de juego, el frontend verifica que el token esté presente.
  - Si no hay token, se procede a jugar como invitado (sin guardar puntuación).
  - Si hay token, lo incluye en las peticiones protegidas (por ejemplo, para obtener datos del usuario o actualizar puntuación).

---

### FLUJO DE UN NIVEL CUALQUIERA
1. El usuario inicia un nivel en el frontend.
2. El frontend solicita al backend los datos del nivel (canción, pistas, etc.).
3. El frontend muestra la pista inicial: 3 segundos de la canción + 1/4 de imagen (artista/álbum/portada)
4. El usuario introduce su respuesta o da a "pasar" (respuesta vacía).
5. El frontend valida la respuesta:
   - Si es correcta, muestra mensaje de acierto, calcula puntuación y si está logueado, envía la puntuación al backend.
   - Si es incorrecta, muestra mensaje de error y se ofrece la siguiente pista.
6. Repite el paso 4 hasta que el usuario acierte o se queden sin pistas.
son 6 oportunidades por nivel, así que las 4 siguientes pistas son:
   - 2ª pista: +2 segundos de canción, +1/4 de imagen, pista textual 1 (año)
   - 3ª pista: +2 segundos de canción, +1/4 de imagen, pista textual 2 (género)
   - 4ª pista: +2 segundos de canción, +1/4 de imagen, pista textual 3 (álbum)
   - 5ª pista: +2 segundos de canción, pista textual 4 (artista)
   - 6ª pista: +2 segundos de canción, pista textual 5 (primeras 1/2 letras del título)
7. Al finalizar el nivel, si el usuario está logueado, el frontend envía la puntuación obtenida al backend para actualizar el total_score y games_played.

#### Explicación del Flujo Completo

##### 1. **Navegación a /levels**
- El usuario accede a la página de niveles (`/levels`)
- Se muestra una lista de niveles disponibles

##### 2. **Selección de Nivel**
- El usuario hace clic en un nivel específico
- Angular Router navega a `/game/:id` (donde `:id` es el ID del nivel)

##### 3. **Inicialización del Componente Game**
- Se ejecuta `ngOnInit()` en `Game`
- Se obtiene el `levelId` de los parámetros de la ruta
- Se llama a `loadGameData()`

##### 4. **Carga de Datos del Nivel**
- Se realiza una petición HTTP GET al backend: `/api/levels/${levelId}`
- El backend responde con:
  - Información de la canción (título, artista, álbum, género, año)
  - URLs del audio y la imagen
  - Pistas textuales predefinidas

##### 5. **Configuración Inicial del Juego**
- Se inicializa el estado del juego con:
  - Intento actual: 1
  - Duración de audio: 3 segundos
  - Imagen revelada: 1/4
  - Sin pistas textuales reveladas

##### 6. **Primera Pista**
- Se reproduce automáticamente 3 segundos del audio
- Se muestra 1/4 de la imagen (cuadrante superior izquierdo)
- El usuario puede:
  - Introducir una respuesta
  - Dar a "Next Hint" para pasar

##### 7. **Validación de Respuesta**
- Cuando el usuario envía una respuesta:
  - Se normaliza y compara con el título correcto
  - Si es correcta:
    - Se calcula la puntuación (máxima en primer intento)
    - Se envía al backend si el usuario está logueado
    - Se muestra pantalla de éxito
  - Si es incorrecta:
    - Se incrementa el número de intento
    - Se actualizan las pistas disponibles

##### 8. **Progresión de Pistas**
Por cada intento fallido:
- **Intento 2**: +2s audio (5s total), +1/4 imagen, pista año
- **Intento 3**: +2s audio (7s total), +1/4 imagen, pista género  
- **Intento 4**: +2s audio (9s total), +1/4 imagen, pista álbum
- **Intento 5**: +2s audio (11s total), pista artista
- **Intento 6**: +2s audio (13s total), pista primeras letras del título

##### 9. **Finalización del Juego**
- **Victoria**: Usuario acierta la canción
- **Derrota**: Usuario usa todos los intentos sin acertar
- En ambos casos se muestra la solución y opciones para reiniciar o volver a niveles

##### 10. **Persistencia de Puntuación**
- Si el usuario está autenticado, se envía la puntuación al backend
- Se actualizan `total_score` y `games_played` del usuario

---

### 4. Autenticación en endpoints protegidos

- **Frontend:**  
  - Para acceder a endpoints como `/api/v1/auth/me` o `/api/v1/game/score`, el frontend envía el token en la cabecera HTTP:
    ```
    Authorization: Bearer <access_token>
    ```
- **Backend:**  
  - Extrae el token de la cabecera.
  - Lo valida (verifica firma, expiración, etc.).
  - Si es válido, obtiene los datos del usuario y permite la operación.
  - Si no es válido, responde con error 401.

---

### 5. Actualización de puntuación y ranking

- **Frontend:**  
  - Cuando el usuario termina una partida, envía la puntuación al endpoint `/api/v1/game/score` con el token.
- **Backend:**  
  - Valida el token.
  - Actualiza la puntuación y partidas jugadas del usuario.
  - Devuelve los nuevos datos al frontend.

---

### 6. Consulta de ranking

- **Frontend:**  
  - Puede consultar `/api/v1/ranking` para mostrar la tabla de posiciones.
- **Backend:**  
  - Devuelve el ranking solicitado.

