import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { UserService } from '../../services/user-service';
import { GameService } from '../../services/game.service';

interface Song {
  id: string;
  title: string;
  artists: string;
  album: string;
  year: number;
  genre: string;
  audio: string;
  image_url: string;
  title_hint: string;
}

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './game.html',
  styleUrls: ['./game.css']
})
export class Game implements OnInit, OnDestroy {
  levelId: string = '1_local';
  isGuest: boolean = false;
  level_number: number = 1;
  currentSong: Song | null = null;
  currentAttempt: number = 1;
  maxAttempts: number = 6;
  userAnswer: string = '';

  // Estado del juego
  gameOver: boolean = false;
  isCorrect: boolean = false;
  showAnswer: boolean = false;
  loadingError: boolean = false;

  // Pistas reveladas
  revealedHints: string[] = [];
  audioSeconds: number = 1;
  imageQuarters: number = 1;
  primeras_letras: string = '';
  // Audio
  audio: HTMLAudioElement | null = null;

  // Mensajes
  message: string = '';
  score: number = 0;
  audioReady: boolean = false;
  audioError: string = '';
  gameStarted: boolean = false; // controlar si el juego ha comenzado
  canReplayAudio: boolean = false; // permitir repetir audio

  private apiUrl = 'http://127.0.0.1:5000/api/v1';
  alreadyPlayed: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private userService: UserService,
    private gameService: GameService
  ) { }

  ngOnInit(): void {

    this.route.queryParams.subscribe(params => {
      this.levelId = params['level'];
      this.loadUserData();
      if (this.isGuest) {
        this.level_number = parseInt(this.levelId.split('_')[0], 10);
      } else {
        this.level_number = parseInt(this.levelId, 10);
      }
      this.loadSong();
    });
  }

  ngOnDestroy() {
    if (this.audio) {
      this.audio.pause();
      this.audio = null;
    }
  }

  private loadUserData(): void {
    const token = this.userService.getToken();

    if (token) {
      // Validar y actualizar datos del usuario
      this.userService.validateToken().subscribe({
        next: (userData) => {
          this.isGuest = false; // si hay token, no es invitado

          // Procesar niveles jugados
          const playedLevelsStr = userData.played_levels || '';
          const playedLevels = playedLevelsStr ? playedLevelsStr.split(',') : [];
        },
        error: (err) => {
          console.error('Token inválido o expirado:', err);
          this.userService.logout();
        }
      });
    } else {
      this.isGuest = true;
    }
  }

  private loadSong(): void {
    const token = this.userService.getToken();
    this.message = 'Cargando nivel...';
    this.loadingError = false;

    this.gameService.getSongForLevel(this.levelId, token || undefined).subscribe({
      next: (response) => {
        this.message = '';
        if (response.song) {
          this.currentSong = response.song;
          this.audioReady = true; // Audio listo, esperar interacción del usuario
          this.primeras_letras = this.currentSong!.title.substring(0, 3) + '...';
          this.currentSong!.title_hint = this.primeras_letras;
        } else {
          this.loadingError = true;
          this.message = 'No hay canción disponible en este nivel';
        }
      },
      error: (err) => {
        console.error('Error cargando canción:', err);
        this.loadingError = true;
        this.audioReady = false;
        this.gameStarted = false;

        if (err.status === 403) {
          if (err.error?.spotify_required) {
            this.message = 'Debes conectar Spotify para acceder a este nivel';
          } else if (err.error?.upgrade_required) {
            this.message = 'Regístrate para jugar más niveles';
            } else if (err.error?.error && err.error.error.includes("ha expirado")) {
              this.message = `Tu conexión con Spotify ha expirado. Por favor, vuelve a conectarte desde tu perfil`;
          }
        } else if (err.status === 404) {
          this.message = 'Este nivel no existe o no está disponible';
        } else if (err.status === 401) {
          this.message = 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo';
        } else if (err.status === 0) {
          this.message = 'Error de conexión. Verifica que el servidor esté funcionando';
        } else {
          this.message = 'Error al cargar el nivel. Inténtalo de nuevo más tarde';
        }
      }
    });
  }

  startAudioManually(): void {
    if (!this.audioReady) {
      this.message = 'Esperando que cargue la canción...';
      return;
    }

    this.gameStarted = true; // Habilitar botones
    this.audioReady = false; // Ocultar botón de comenzar
    this.playAudio();
  }

  replayAudio(): void {
    if (!this.gameStarted || this.gameOver) {
      return;
    }
    this.playAudio();
  }

  // Timeout para detener el audio
  private audioTimeout: any;

  private playAudio(): void {
    if (!this.currentSong) return;

    // Limpiar timeout anterior si existe
    if (this.audioTimeout) {
      clearTimeout(this.audioTimeout);
      this.audioTimeout = null;
    }

    this.canReplayAudio = false; // Deshabilitar durante reproducción

    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0; // Empezar de cero en siguientes intentos
    }

    // Si es audio codificado en Base64, comprobar formato
    const audioSource = this.currentSong.audio;
    if (audioSource.startsWith('data:audio/')) {
      const parts = audioSource.split(',');
      if (parts.length !== 2) {
        console.error('Data URI inválida: debe tener formato data:audio/mp3;base64,{data}');
        this.audioError = 'Formato de audio inválido';
        return;
      }
    }

    this.audio = new Audio(audioSource);
    this.audio.play();

    // Parar después de audioSeconds segundos
    this.audioTimeout = setTimeout(() => {
      if (this.audio) {
        this.audio.pause();
        this.audio.currentTime = 0;
      }
      this.canReplayAudio = true; // Habilitar botón de repetir
      this.audioTimeout = null;
    }, this.audioSeconds * 1000);
  }

  submitAnswer(): void {
    if (!this.gameStarted) {
      this.message = 'Primero debes comenzar el juego';
      return;
    }

    if (!this.userAnswer.trim() || !this.currentSong) {
      this.message = 'Introduce una respuesta';
      return;
    }
    this.gameService.validateAnswer(this.levelId, this.userAnswer).subscribe({
      next: (response) => {
        if (response.correct) {
          this.isCorrect = true;
          this.gameOver = true;
          this.showAnswer = true;
          this.currentSong = { ...this.currentSong!, ...response.answer };
          this.calculateScore();
          this.message = `La canción es "${this.currentSong!.title}" de ${this.currentSong!.artists}`;
          this.playCompleteAudio();
          this.saveScore();
          this.markAsPlayed();
        } else {
          this.message = 'Respuesta incorrecta';
          this.userAnswer = '';

          if (this.currentAttempt < this.maxAttempts) {
            setTimeout(() => {
              this.nextHint();
            }, 1000);
          } else {
            this.gameOver = true;
            this.showAnswer = true;
            this.message = 'Se acabaron los intentos';
            this.revealAnswer();
          }
        }
      },
      error: (err) => {
        console.error('Error validando respuesta:', err);
        this.message = 'Error al validar respuesta';
      }
      
    });
  }

  nextHint(): void {
    if (!this.gameStarted) {
      this.message = 'Haz clic en "Comenzar" para iniciar el juego';
      return;
    }

    if (this.currentAttempt >= this.maxAttempts || this.gameOver) {
      return;
    }

    this.currentAttempt++;
    this.audioSeconds += 2;

    // Revelar pistas según intento
    switch (this.currentAttempt) {
      case 2:
        this.imageQuarters = 2;
        this.revealedHints.push('year');
        this.message = `Pista ${this.currentAttempt}/${this.maxAttempts}: Se reveló el año`;
        break;
      case 3:
        this.imageQuarters = 3;
        this.revealedHints.push('genre');
        this.message = `Pista ${this.currentAttempt}/${this.maxAttempts}: Se reveló el género`;
        break;
      case 4:
        this.imageQuarters = 4;
        this.revealedHints.push('album');
        this.message = `Pista ${this.currentAttempt}/${this.maxAttempts}: Se reveló el álbum`;
        break;
      case 5:
        this.revealedHints.push('artist');
        this.message = `Pista ${this.currentAttempt}/${this.maxAttempts}: Se reveló el artista`;
        break;
      case 6:
        this.revealedHints.push('title_hint');
        this.message = `Pista ${this.currentAttempt}/${this.maxAttempts}: Última pista!`;
        break;
    }

    this.playAudio(); // Reproducir automáticamente en siguientes intentos (ya tiene permiso)
  }

  private calculateScore(): void {
    // Puntuación: 1000 puntos base - (intentos * 100)
    this.score = Math.max(100, 1000 - ((this.currentAttempt - 1) * 150));
  }

  private saveScore(): void {
    const token = this.userService.getToken();
    if (this.isGuest) { // si es invitado no enviamos la puntuación,
      // pero sí añadimos el nivel completado al session storage, siempre que no esté ya jugado
      if (sessionStorage.getItem('played_levels')?.split(',').includes(this.level_number.toString())) {
        this.alreadyPlayed = true;
        return;
      }
      let local_completed_levels = sessionStorage.getItem('completed_levels');
      let completedLevels: string[] = [];
      if (local_completed_levels) {
        completedLevels = local_completed_levels.split(',');
      }
      if (!completedLevels.includes(this.level_number.toString())) {
        completedLevels.push(this.level_number.toString());
        sessionStorage.setItem('completed_levels', completedLevels.join(','));
      }
      return;
    } else if (!token) { // si es usuario registrado pero no hay token, redirigimos al login
      console.error('No hay token de autenticación disponible. Inicia sesión para guardar la puntuación.');
      this.router.navigate(['/login']);
      return;
    }
    // Si es usuario registrado, enviamos la puntuación al backend
    this.gameService.submitScore(this.score, this.levelId, token).subscribe({
      next: (response) => {
        console.log('Puntuación enviada:', response);
      },
      error: (err) => {
        if (err.status === 400 && err.error && err.error.error === 'Nivel ya jugado') {
          this.alreadyPlayed = true;
          console.warn('Nivel ya jugado por este usuario. Puntuación no actualizada.');
          return;
        }
        console.error('Error enviando puntuación:', err);
      }
    });

  }

  private markAsPlayed(): void {
    if (this.isGuest) {
      // marcar nivel como jugado en sessionStorage
      let local_played_levels = sessionStorage.getItem('played_levels');
      let playedLevels: string[] = [];
      if (local_played_levels) {
        playedLevels = local_played_levels.split(',');
      }
      if (!playedLevels.includes(this.level_number.toString())) {
        playedLevels.push(this.level_number.toString());
        sessionStorage.setItem('played_levels', playedLevels.join(','));
      }
      return;
    } else {
      const token = this.userService.getToken();
      if (!token) {
        console.error('No hay token de autenticación disponible. Inicia sesión para marcar el nivel como jugado.');
        this.router.navigate(['/login']);
        return;
      }
      this.gameService.markAsPlayed(this.levelId, token).subscribe({
      next: () => console.log('Nivel marcado como jugado'),
      error: (err) => console.error('Error marcando nivel como jugado', err)
    });
    }
  }
  
  private revealAnswer(): void {
    if (!this.currentSong) return;

    this.message = `La canción era: "${this.currentSong!.title}" de ${this.currentSong!.artists}`;
    this.playCompleteAudio();
    this.markAsPlayed();
  }

  playAgain(): void {
    this.stopAudio();
    window.location.reload();
  }

  giveUp(): void {
    if (!this.currentSong) return;

    this.stopAudio();

    this.gameOver = true;
    this.isCorrect = false;
    this.showAnswer = true;
    this.message = 'Te has rendido';
    this.score = 0; // Sin puntuación por rendirse

    this.revealAnswer();
  }

  private playCompleteAudio(): void {
    if (!this.currentSong) return;

    // Detener audio anterior y limpiar timeout
    if (this.audioTimeout) {
      clearTimeout(this.audioTimeout);
      this.audioTimeout = null;
    }
    this.stopAudio();

    const audioSource = this.currentSong.audio;
    this.audio = new Audio(audioSource);
    this.audio.play();
  }

  private stopAudio(): void {
    if (this.audioTimeout) {
      clearTimeout(this.audioTimeout);
      this.audioTimeout = null;
    }
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
      this.audio = null;
    }
  }

  goToLevels(): void {
    //this.router.navigate(['/levels']); No cancela la reproducción de audio, así que se usa window.location.reload()
    window.location.href = '/levels';
  }

  goToProfile(): void {
    window.location.href = '/profile';
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }

  retryLoadSong(): void {
    this.loadingError = false;
    this.message = 'Cargando nivel...';
    // wait half second to show the message
    setTimeout(() => {
      this.loadSong();
    }, 500);
  }

  nextLevel(): void {
    const nextLevelNum = this.level_number + 1;
    let nextLevelId = nextLevelNum.toString();

    if (this.isGuest) {
      nextLevelId += '_local';
    }

    // Navegar al siguiente nivel
    // Usamos window.location.href para forzar una recarga completa y asegurar que se reinicia todo el estado
    window.location.href = `/game?level=${nextLevelId}`;
  }
}