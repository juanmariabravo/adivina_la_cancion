import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SpotifyService {
  private apiUrl = 'http://127.0.0.1:5000/api/v1/spoti';
  private spotifyAuthUrl = 'https://accounts.spotify.com/authorize';
  private redirectUri = 'http://127.0.0.1:4200/callback';
  private scopes = 'user-read-private playlist-read-private user-read-email';

  constructor(private http: HttpClient) {}

  // 1. Obtener Client ID desde el backend
  getClientId(email: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/getClientId`, {
      params: { email }
    });
  }

  // 2. Redirigir a Spotify para autorización
  redirectToSpotifyAuth(clientId: string): void {
    const params = new URLSearchParams({
      client_id: clientId,
      response_type: 'code',
      redirect_uri: this.redirectUri,
      scope: this.scopes,
      show_dialog: 'true'
    });

    window.location.href = `${this.spotifyAuthUrl}?${params.toString()}`;
  }

  // 3. Intercambiar código por token (con clientId ya obtenido)
  exchangeCodeForTokenWithClientId(code: string, clientId: string, authToken: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/getAuthorizationToken`, {
      params: { code, clientId },
      headers: { 'Authorization': authToken }
    });
  }

  // 4. Guardar tokens en sessionStorage
  saveSpotifyTokens(accessToken: string, refreshToken: string, expiresIn: number): void {
    const expirationTime = Date.now() + (expiresIn * 1000);
    sessionStorage.setItem('spotifyAccessToken', accessToken);
    sessionStorage.setItem('spotifyRefreshToken', refreshToken);
    sessionStorage.setItem('spotifyTokenExpiration', expirationTime.toString());
  }

  // 5. Obtener access token guardado
  getSpotifyAccessToken(): string | null {
    return sessionStorage.getItem('spotifyAccessToken');
  }

  // 6. Verificar si el usuario está conectado a Spotify
  isSpotifyConnected(): boolean {
    const token = this.getSpotifyAccessToken();
    const expiration = sessionStorage.getItem('spotifyTokenExpiration');
    
    if (!token || !expiration) {
      return false;
    }

    // Verificar si el token ha expirado
    return Date.now() < parseInt(expiration);
  }

  // 7. Refrescar token
  refreshToken(): Observable<any> {
    const refreshToken = sessionStorage.getItem('spotifyRefreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    return this.http.post<any>(`${this.apiUrl}/refreshToken`, {
      refresh_token: refreshToken
    });
  }

  // 8. Desconectar de Spotify
  disconnectSpotify(): void {
    sessionStorage.removeItem('spotifyAccessToken');
    sessionStorage.removeItem('spotifyRefreshToken');
    sessionStorage.removeItem('spotifyTokenExpiration');
  }
}
