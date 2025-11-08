import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../../services/user-service';
import { SpotifyService } from '../../services/spotify.service';

interface Level {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  songsCount: number;
  completed: boolean;
  score: number;
  progress: number;
  genre?: string;
}

@Component({
  selector: 'app-levels',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './levels.html',
  styleUrls: ['./levels.css']
})
export class Levels implements OnInit {
  username: string = '';
  totalScore: number = 0;
  gamesPlayed: number = 0;
  dailyCompleted: boolean = false;
  timeRemaining: string = '00:00:00'; // Tiempo restante para que empiece el próximo nivel diario
  isGuest: boolean = false;
  spotifyRequired: boolean = true;
  showSpotifyWarning: boolean = false;

  // TODO: cargar niveles desde la API
  levels: Level[] = [
    {
      id: 1,
      title: 'Nivel 1 - Principiante',
      description: 'Adivina una canción clásica',
      difficulty: 'Fácil',
      songsCount: 1,
      completed: false,
      score: 0,
      progress: 0
    },
    {
      id: 2,
      title: 'Nivel 2 - Intermedio',
      description: 'Canción moderna popular',
      difficulty: 'Intermedio',
      songsCount: 1,
      completed: false,
      score: 0,
      progress: 0
    },
    {
      id: 3,
      title: 'Nivel 3 - Avanzado',
      description: 'Desafío musical',
      difficulty: 'Difícil',
      songsCount: 1,
      completed: false,
      score: 0,
      progress: 0
    },
    {
      id: 4,
      title: 'Nivel 4 - Experto',
      description: 'Solo para conocedores',
      difficulty: 'Experto',
      songsCount: 1,
      completed: false,
      score: 0,
      progress: 0
    },
    {
      id: 5,
      title: 'Nivel 5 - Rock',
      description: 'Un clásico del rock',
      difficulty: 'Intermedio',
      songsCount: 1,
      completed: false,
      score: 0,
      progress: 0,
      genre: 'Rock'
    },
    {
      id: 6,
      title: 'Nivel 6 - Pop',
      description: 'Éxito reciente del pop',
      difficulty: 'Intermedio',
      songsCount: 1,
      completed: false,
      score: 0,
      progress: 0,
      genre: 'Pop'
    }
  ];

  constructor(
    public userService: UserService,
    private router: Router,
    private spotifyService: SpotifyService
  ) {}

  ngOnInit(): void {
    this.loadUserData();
    this.checkSpotifyConnection();
    this.startCountdown();
  }

  private loadUserData(): void {
    const token = this.userService.getToken();
    
    if (token) {
      // Validar y actualizar datos del usuario
      this.userService.validateToken().subscribe({
        next: (userData) => {
          this.isGuest = false;
          this.username = userData.username;
          this.totalScore = userData.total_score || 0;
          this.gamesPlayed = userData.games_played || 0;
          this.dailyCompleted = userData.daily_completed || false;
          
          // Guardar datos actualizados
          this.userService.saveCurrentUser(userData);
        },
        error: (err) => {
          console.error('Token inválido o expirado:', err);
          this.userService.logout();
          this.setGuestMode();
        }
      });
    } else {
      this.setGuestMode();
    }
  }

  private setGuestMode(): void {
    this.username = 'Invitado';
    this.isGuest = true;
    this.totalScore = 0;
    this.gamesPlayed = 0;
    this.dailyCompleted = false;
  }

  private startCountdown(): void {
    // Tomar la hora actual y restarla a 23:59:59 para obtener la cuenta regresiva
    setInterval(() => {
      const now = new Date();
      const endOfDay = new Date();
      endOfDay.setHours(23, 59, 59, 999);

      let diff = endOfDay.getTime() - now.getTime();
      if (diff < 0) diff = 0; // evitar valores negativos cuando ya pasó el día

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      this.timeRemaining = `${hours.toString().padStart(2, '0')}:${minutes
        .toString()
        .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
  }

  private checkSpotifyConnection(): void {
    if (this.isGuest) {
      // Los invitados NO necesitan Spotify
      this.showSpotifyWarning = false;
      return;
    }

    // Usuarios autenticados SÍ necesitan Spotify
    const isConnected = this.spotifyService.isSpotifyConnected();
    this.showSpotifyWarning = !isConnected;
  }

  startLevel(levelId: number): void {
    // Invitados solo pueden jugar niveles 1-10 (canciones locales)
    if (this.isGuest && levelId > 10) {
      alert('⚠️ Los invitados solo pueden jugar los primeros 10 niveles. Regístrate para acceder a todos los niveles.');
      this.router.navigate(['/register']);
      return;
    }

    // Usuarios autenticados DEBEN tener Spotify conectado
    if (!this.isGuest && !this.spotifyService.isSpotifyConnected()) {
      alert('⚠️ Debes conectar tu cuenta de Spotify para jugar. Usa el mismo email que tu cuenta de Spotify.');
      this.router.navigate(['/profile']);
      return;
    }

    this.router.navigate(['/game'], { 
      queryParams: { level: levelId } 
    });
  }

  startDailyChallenge(): void {
    this.startLevel(0); // Nivel diario tiene ID 0
  }

  goToProfile(): void {
    this.router.navigate(['/profile']);
  }

  goToRanking(): void {
    this.router.navigate(['/ranking']);
  }

  logout(): void {
    this.userService.logout();
    this.router.navigate(['/']);
  }
}