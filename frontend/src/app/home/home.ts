import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { UserService } from '../../services/user-service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.html',
  styleUrls: ['./home.css']
})
export class Home {
  constructor(
    private router: Router,
    private userService: UserService
  ) {}

  playAsGuest(): void {
    // Limpiar toda la sesión antes de jugar como invitado
    this.userService.logout();
    sessionStorage.clear();
    
    // Redirigir a niveles
    this.router.navigate(['/levels']);
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }

  goToRegister(): void {
    this.router.navigate(['/register']);
  }
}
