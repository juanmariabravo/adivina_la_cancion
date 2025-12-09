import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SpotifyService } from '../../services/spotify.service';

@Component({
  selector: 'app-callback',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="callback-container">
      <div class="loading">
        <h2>Conectando con Spotify...</h2>
        <div class="spinner"></div>
        <p *ngIf="errorMessage" class="error">{{ errorMessage }}</p>
      </div>
    </div>
  `,
  styles: [`
    .callback-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
    }
    .loading {
      text-align: center;
      color: white;
    }
    .spinner {
      border: 4px solid rgba(255, 255, 255, 0.1);
      border-top: 4px solid #1DB954;
      border-radius: 50%;
      width: 50px;
      height: 50px;
      animation: spin 1s linear infinite;
      margin: 20px auto;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .error {
      color: #f44336;
      margin-top: 1rem;
    }
  `]
})
export class Callback implements OnInit {
  errorMessage: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private spotifyService: SpotifyService
  ) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      const code = params['code'];
      const error = params['error'];

      if (error) {
        this.errorMessage = 'Error al conectar con Spotify: ' + error;
        setTimeout(() => this.router.navigate(['/levels']), 3000);
        return;
      }

      if (code) {
        this.exchangeCodeForToken(code);
      } else {
        this.errorMessage = 'No se recibió código de autorización';
        setTimeout(() => this.router.navigate(['/levels']), 3000);
      }
    });
  }

  private exchangeCodeForToken(code: string): void {
    const email = sessionStorage.getItem('email');

    if (!email) {
      this.errorMessage = 'Email de usuario no encontrado';
      setTimeout(() => this.router.navigate(['/levels']), 3000);
      return;
    }

    // 1️Primera petición: obtener clientId
    this.spotifyService.getClientId(email).subscribe({
      next: (clientIdResponse) => {
        const clientId = clientIdResponse.clientId;
        const token = sessionStorage.getItem('authToken');

        // 2️Segunda petición: intercambiar código por token
        this.spotifyService.exchangeCodeForTokenWithClientId(code, clientId, token || '').subscribe({
          next: (tokenResponse) => {
            // Guardar tokens
            this.spotifyService.saveSpotifyTokens(
              tokenResponse.access_token,
              tokenResponse.refresh_token,
              tokenResponse.expires_in
            );

            // Redirigir a niveles
            setTimeout(() => this.router.navigate(['/levels']), 1000);
          },
          error: (err) => {
            this.errorMessage = 'Error al conectar con Spotify. ' + err.error.error;
            setTimeout(() => this.router.navigate(['/levels']), 3000);
          }
        });
      },
      error: (err) => {
        console.error('Error obteniendo clientId:', err);
        this.errorMessage = 'Error al obtener configuración';
        setTimeout(() => this.router.navigate(['/levels']), 3000);
      }
    });
  }
}
