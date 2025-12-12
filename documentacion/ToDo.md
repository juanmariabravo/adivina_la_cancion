# ToDo Proyecto "Adivina la Canción"

> **Fecha de entrega:** 14 de diciembre de 2025  
> **Estado:** ✓ COMPLETADO

---

## Requisitos del Proyecto

### ✓ Funcionalidades Principales
- [x] **Sistema de autenticación completo** (registro, login, JWT)
- [x] **Modo invitado** (juego sin registro, niveles locales 1-10)
- [x] **Integración con Spotify API** (OAuth 2.0)
- [x] **Sistema de niveles por dificultad** (Fácil, Medio, Difícil, Experto: 30 niveles)
- [x] **Nivel diario** (canción del día)
- [x] **Sistema de pistas progresivas** (6 intentos: audio + imagen + datos textuales)
- [x] **Sistema de puntuación** (1000 pts base - penalización por intento)
- [x] **Ranking global** (top jugadores por puntuación total)
- [x] **Perfil de usuario** (estadísticas, edición, conexión Spotify)
- [x] **Base de datos SQLite** (usuarios, puntuaciones, niveles jugados)

---

## Tareas Completadas

### ✓ Estructura y Organización
- [x] **Arquitectura por capas en Backend:**
  - [x] `controllers/` - Endpoints API (user, game, spotify)
  - [x] `services/` - Lógica de negocio
  - [x] `models/` - Modelos de datos (User, Song)
  - [x] `database/` - Capa de acceso a datos
  - [x] `helpers/` - Utilidades (Spotify API, web scraping)
- [x] **Blueprints de Flask** para organizar rutas
- [x] **Componentes standalone de Angular 19**

### ✓ Configuración de Entornos
- [x] **Backend:** Archivo `.env` con variables de entorno
  - SECRET_KEY, DEBUG, PORT
  - SPOTIFY_REDIRECT_URI, SPOTIFY_TOKEN_URL
- [x] **Frontend:** `environment.ts` con configuración
  - apiUrl, spotifyAuthUrl, redirectUri, scopes

### ✓ Base de Datos
- [x] **Tabla users** con todos los campos necesarios:
  - Autenticación (username, email, password_hash)
  - Puntuación (total_score, games_played)
  - Progreso (played_levels, last_daily_completed)
  - Spotify (credenciales encriptadas, tokens)
- [x] **Múltiples usuarios de prueba** para ranking:
  - Usuarios con diferentes puntuaciones
  - Variedad de nombres para ranking realista

### Seguridad
- [x] **JWT** para autenticación (expiración 24h)
- [x] **Bcrypt** para hashing de contraseñas
- [x] **CORS** configurado correctamente
- [x] **Tokens Spotify nunca expuestos al frontend**
- [x] **sessionStorage** en lugar de localStorage para mayor seguridad

### ✓ Funcionalidades
- [x] **Sistema de niveles diarios automático:**
  - Cálculo basado en fecha actual
  - Rotación automática de `possible_daily_songs.json`
  - Detección de nivel ya completado hoy
- [x] **Web scraping** para previews de Spotify (cuando no disponibles)
- [x] **Normalización de respuestas** (sin acentos, minúsculas, sin espacios)
- [x] **Validación en tiempo real** de credenciales
- [x] **Manejo de errores robusto** (códigos HTTP apropiados)
- [x] **Diseño responsive** (móvil, tablet, desktop)
- [x] **Sistema de Pistas Progresivas**
- [x] **Integración Completa con Spotify: OAuth 2.0 completo con callback**
- [x] **Perfil de Usuario con estadísticas detalladas**


## Objetivos Secundarios Para Futuras Mejoras
- [ ] **Jugar con playlists personalizadas** del usuario
Que el usuario pueda seleccionar una de sus playlists de Spotify para jugar con canciones de esa lista.

---


*Última actualización: 12 de diciembre de 2025*