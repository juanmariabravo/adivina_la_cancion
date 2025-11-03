import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../user-service';

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
  editEmail: string = '';
  editPassword: string = '';
  editPasswordConfirm: string = '';
  
  // Mensajes
  successMessage: string = '';
  errorMessage: string = '';
  
  // Estadísticas adicionales
  averageScore: number = 0;
  rank: number = 0;
  
  constructor(
    private userService: UserService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadUserProfile();
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
        this.gamesPlayed = userData.games_played || 0;
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
      this.editEmail = this.email;
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
    if (this.editEmail && !this.editEmail.includes('@')) {
      this.errorMessage = 'Email inválido';
      return;
    }

    if (this.editPassword && this.editPassword.length < 6) {
      this.errorMessage = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }

    if (this.editPassword !== this.editPasswordConfirm) {
      this.errorMessage = 'Las contraseñas no coinciden';
      return;
    }

    // TODO: Implementar endpoint de actualización en el backend
    // Por ahora solo simular éxito
    this.successMessage = 'Perfil actualizado correctamente';
    this.isEditing = false;
    
    if (this.editEmail) {
      this.email = this.editEmail;
    }
  }

  cancelEdit(): void {
    this.isEditing = false;
    this.editEmail = '';
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
}
