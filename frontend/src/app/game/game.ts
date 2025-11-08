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
  currentSong: Song | null = null;
  currentAttempt: number = 1;
  maxAttempts: number = 6;
  userAnswer: string = '';
  
  // Estado del juego
  gameOver: boolean = false;
  isCorrect: boolean = false;
  showAnswer: boolean = false;
  
  // Pistas reveladas
  revealedHints: string[] = [];
  audioSeconds: number = 3;
  imageQuarters: number = 1;
  primeras_letras: string = '';
  // Audio
  audio: HTMLAudioElement | null = null;
  
  // Mensajes
  message: string = '';
  score: number = 0;
  audioReady: boolean = false;
  audioError: string = '';
  
  private apiUrl = 'http://127.0.0.1:5000/api/v1';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private userService: UserService,
    private gameService: GameService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.levelId = params['level'] || '1_local';
      this.loadSong();
    });
  }

  ngOnDestroy() {
    if (this.audio) {
      this.audio.pause();
      this.audio = null;
    }
  }

  private loadSong(): void {
    const token = this.userService.getToken();
    
    this.gameService.getSongForLevel(this.levelId, token || undefined).subscribe({
      next: (response) => {
        if (response.song) {
          this.currentSong = response.song;
          this.audioReady = true; // Audio listo, esperar interacción del usuario
          this.primeras_letras = this.currentSong!.title.substring(0, 3) + '...';
          this.currentSong!.title_hint = this.primeras_letras;
        } else {
          this.message = 'No hay canción en este nivel';
        }
      },
      error: (err) => {
        console.error('Error cargando canción:', err);
        
        if (err.status === 403) {
          if (err.error?.spotify_required) {
            this.message = 'Debes conectar Spotify para este nivel';
            setTimeout(() => this.router.navigate(['/profile']), 2000);
          } else if (err.error?.upgrade_required) {
            this.message = 'Regístrate para jugar más niveles';
            setTimeout(() => this.router.navigate(['/register']), 2000);
          }
        } else {
          this.message = 'Error al cargar el nivel';
        }
      }
    });
  }

  startAudioManually(): void {
    if (!this.audioReady) {
      this.message = 'Esperando que cargue la canción...';
      return;
    }
    
    this.playAudio();
    this.audioReady = false; // Ocultar botón de play después del primer clic
  }

  private playAudio(): void {
    if (!this.currentSong) return;
    
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
    }
    
    this.audio = new Audio(this.currentSong.audio);
    
    // Manejar errores de reproducción
    this.audio.addEventListener('error', (e) => {
      console.error('Error reproduciendo audio:', e);
      this.audioError = 'Error al reproducir el audio. Intenta de nuevo.';
    });
    
    // Intentar reproducir
    const playPromise = this.audio.play();
    
    if (playPromise !== undefined) {
      playPromise
        .then(() => {
          console.log('Audio reproduciéndose correctamente');
          this.audioError = '';
          
          // Parar después de X segundos
          setTimeout(() => {
            if (this.audio) {
              this.audio.pause();
              this.audio.currentTime = 0;
            }
          }, this.audioSeconds * 1000);
        })
        .catch((error) => {
          console.error('Error al reproducir audio:', error);
          this.audioError = 'Haz clic en "▶ Reproducir" para escuchar la canción';
          this.audioReady = true; // Mostrar botón de nuevo
        });
    }
  }

  submitAnswer(): void {
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
          this.message = `¡Correcto! La canción es "${this.currentSong!.title}" de ${this.currentSong!.artists}`;
          this.saveScore();
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
    if (!token) {
      console.log('Invitado - puntuación no guardada');
      return;
    }
    
    this.gameService.submitScore(this.score, token).subscribe({
      next: (response) => {
        console.log('Puntuación guardada:', response);
      },
      error: (err) => {
        console.error('Error guardando puntuación:', err);
      }
    });
  }

  private revealAnswer(): void {
    if (!this.currentSong) return;
    
    this.gameService.revealSong(this.currentSong.id).subscribe({
      next: (response) => {
        this.currentSong = { ...this.currentSong!, ...response };
        this.message = `La canción era: "${this.currentSong!.title}" de ${this.currentSong!.artists}`;
      },
      error: (err) => {
        console.error('Error obteniendo respuesta:', err);
      }
    });
  }

  playAgain(): void {
    window.location.reload();
  }

  goToLevels(): void {
    this.router.navigate(['/levels']);
  }

  giveUp(): void {
    if (!this.currentSong) return;
    
    this.gameOver = true;
    this.isCorrect = false;
    this.showAnswer = true;
    this.message = 'Te has rendido';
    this.score = 0; // Sin puntuación por rendirse
    
    this.revealAnswer();
  }
}