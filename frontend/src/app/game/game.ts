import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserService } from '../../services/user-service';

interface Song {
  id: number;
  audio_url: string;
  image_url: string;
  hints: {
    year: number;
    genre: string;
    album: string;
    artist: string;
    title_hint: string;
  };
  title?: string;
  artist?: string;
}

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './game.html',
  styleUrls: ['./game.css']
})
export class Game implements OnInit, OnDestroy {
  levelId: number = 1;
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
  
  // Audio
  audio: HTMLAudioElement | null = null;
  
  // Mensajes
  message: string = '';
  score: number = 0;
  
  private apiUrl = 'http://localhost:5000/api/v1';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private userService: UserService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.levelId = +params['level'] || 1;
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
    this.http.get<any>(`${this.apiUrl}/levels/${this.levelId}/song`).subscribe({
      next: (response) => {
        if (response.song) {
          this.currentSong = response.song;
          this.playAudio();
        } else {
          this.message = 'No hay canción en este nivel';
        }
      },
      error: (err) => {
        console.error('Error cargando canción:', err);
        this.message = 'Error al cargar el nivel';
      }
    });
  }

  private playAudio(): void {
    if (!this.currentSong) return;
    
    if (this.audio) {
      this.audio.pause();
    }
    
    this.audio = new Audio(this.currentSong.audio_url);
    this.audio.play();
    
    // Parar después de X segundos
    setTimeout(() => {
      if (this.audio) {
        this.audio.pause();
        this.audio.currentTime = 0;
      }
    }, this.audioSeconds * 1000);
  }

  submitAnswer(): void {
    if (!this.userAnswer.trim() || !this.currentSong) {
      this.message = 'Introduce una respuesta';
      return;
    }
    
    this.http.post<any>(`${this.apiUrl}/game/validate`, {
      song_id: this.currentSong.id,
      answer: this.userAnswer
    }).subscribe({
      next: (response) => {
        if (response.correct) {
          this.isCorrect = true;
          this.gameOver = true;
          this.showAnswer = true;
          this.currentSong = { ...this.currentSong!, ...response.answer };
          this.calculateScore();
          this.message = `¡Correcto! La canción es "${this.currentSong?.title}" de ${this.currentSong?.artist}`;
          this.saveScore();
        } else {
          this.message = 'Respuesta incorrecta';
          this.userAnswer = '';
          
          // Incrementar intento y mostrar siguiente pista automáticamente
          if (this.currentAttempt < this.maxAttempts) {
            setTimeout(() => {
              this.nextHint();
            }, 1000);
          } else {
            // Se acabaron los intentos
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
    
    this.playAudio();
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
    
    this.http.post<any>(`${this.apiUrl}/game/submit-score`, 
      { score: this.score },
      { headers: { 'Authorization': token } }
    ).subscribe({
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
    
    this.http.get<any>(`${this.apiUrl}/game/song/${this.currentSong.id}/reveal`).subscribe({
      next: (response) => {
        this.currentSong = { ...this.currentSong!, ...response };
        this.message = `La canción era: "${this.currentSong?.title}" de ${this.currentSong?.artist}`;
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
    
    // Revelar la respuesta
    this.http.get<any>(`${this.apiUrl}/game/song/${this.currentSong.id}/reveal`).subscribe({
      next: (response) => {
        this.currentSong = { ...this.currentSong!, ...response };
        this.message = `Te rendiste. La canción era: "${this.currentSong?.title}" de ${this.currentSong?.artist}`;
      },
      error: (err) => {
        console.error('Error obteniendo respuesta:', err);
        this.message = 'Error al obtener la respuesta correcta';
      }
    });
  }
}