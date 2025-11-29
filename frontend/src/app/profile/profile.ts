import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../../services/user-service';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './profile.html',
  styleUrls: ['./profile.css']
})
export class Profile implements OnInit {
  username: string = '';
  email: string = '';
  totalScore: number = 0;
  gamesPlayed: number = 0;
  dailyCompleted: boolean = false;
  createdAt: string = '';

  // Estado de edición
  isEditing: boolean = false;
  editUsername: string = '';
  editPassword: string = '';
  editPasswordConfirm: string = '';

  // Mensajes
  successMessage: string = '';
  errorMessage: string = '';

  // Estadísticas adicionales
  averageScore: number = 0;
  rank: number = 0;

  isSpotifyConnected: boolean = false;

  constructor(
    private userService: UserService,
    private router: Router,
    private spotifyService: SpotifyService
  ) { }

  ngOnInit(): void {
    this.loadUserProfile();
    this.isSpotifyConnected = this.spotifyService.isSpotifyConnected();
  }

  private loadUserProfile(): void {
    const token = this.userService.getToken();
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }

    this.userService.validateToken().subscribe({
      next: (userData) => {
        this.username = userData.username;
        this.email = userData.email;
        this.totalScore = userData.total_score || 0;

        // Calcular niveles jugados
        const playedLevelsStr = userData.played_levels || '';
        this.gamesPlayed = playedLevelsStr ? playedLevelsStr.split(',').length : 0;

        this.dailyCompleted = userData.daily_completed || false;
        this.createdAt = userData.created_at || '';

        // Calcular promedio
        this.averageScore = this.gamesPlayed > 0
          ? Math.round(this.totalScore / this.gamesPlayed)
          : 0;
      },
      error: (err) => {
        console.error('Error cargando perfil:', err);
        this.errorMessage = 'Error al cargar los datos del perfil';
        this.userService.logout();
        this.router.navigate(['/login']);
      }
    });
  }

  toggleEdit(): void {
    this.isEditing = !this.isEditing;
    if (this.isEditing) {
      this.editUsername = this.username;
      this.editPassword = '';
      this.editPasswordConfirm = '';
    }
    this.successMessage = '';
    this.errorMessage = '';
  }

  saveChanges(): void {
    this.successMessage = '';
    this.errorMessage = '';

    // Validaciones
    if (this.editUsername && this.editUsername.length < 3) {
      this.errorMessage = 'El username debe tener al menos 3 caracteres';
      return;
    }

    if (this.editPassword && this.editPassword.length < 6) {
      this.errorMessage = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }

    if (this.editPassword && this.editPassword !== this.editPasswordConfirm) {
      this.errorMessage = 'Las contraseñas no coinciden';
      return;
    }

    // Verificar si hay cambios
    const hasUsernameChange = this.editUsername && this.editUsername !== this.username;
    const hasPasswordChange = this.editPassword && this.editPassword.length > 0;

    if (!hasUsernameChange && !hasPasswordChange) {
      this.errorMessage = 'No hay cambios para guardar';
      return;
    }

    // Llamar al backend
    this.userService.updateProfile(
      hasUsernameChange ? this.editUsername : undefined,
      hasPasswordChange ? this.editPassword : undefined
    ).subscribe({
      next: (response) => {
        this.successMessage = response.message || 'Perfil actualizado correctamente';
        this.isEditing = false;

        // Si cambió el username, actualizar datos locales
        if (hasUsernameChange) {
          this.username = this.editUsername;

          // Si el backend devuelve un nuevo token, actualizarlo
          if (response.access_token && response.token_type) {
            this.userService.saveToken(response.token_type, response.access_token);
          }
        }

        // Actualizar usuario en localStorage
        this.userService.saveCurrentUser(response.user);
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'Error al actualizar el perfil';
      }
    });
  }

  cancelEdit(): void {
    this.isEditing = false;
    this.editUsername = '';
    this.editPassword = '';
    this.editPasswordConfirm = '';
    this.successMessage = '';
    this.errorMessage = '';
  }

  goToLevels(): void {
    this.router.navigate(['/levels']);
  }

  goToRanking(): void {
    this.router.navigate(['/ranking']);
  }

  logout(): void {
    this.userService.logout();
    this.router.navigate(['/']);
  }

  connectSpotify(): void {
    if (!this.email) {
      this.errorMessage = 'Debes iniciar sesión para conectar con Spotify';
      return;
    }

    this.spotifyService.getClientId(this.email).subscribe({
      next: (response) => {
        // Redirigir directamente sin guardar clientId
        this.spotifyService.redirectToSpotifyAuth(response.clientId);
      },
      error: (err) => {
        this.errorMessage = 'Error al conectar con Spotify';
        console.error(err);
      }
    });
  }

  disconnectSpotify(): void {
    this.spotifyService.disconnectSpotify();
    this.isSpotifyConnected = false;
    this.successMessage = 'Desconectado de Spotify';
  }
}
