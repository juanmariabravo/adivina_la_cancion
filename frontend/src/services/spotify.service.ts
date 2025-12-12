import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class SpotifyService {
  private apiUrl = `${environment.apiUrl}/spoti`;
  private spotifyAuthUrl = environment.spotifyAuthUrl;
  private redirectUri = environment.spotifyRedirectUri;
  private scopes = environment.spotifyScopes;

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

  // 3. Intercambiar código por token (SOLO confirma conexión, no recibe tokens)
  exchangeCodeForTokenWithClientId(code: string, clientId: string, authToken: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/getAuthorizationToken`, {
      params: { code, clientId },
      headers: { 'Authorization': authToken }
    });
  }

  // 4. Marcar que Spotify está conectado (sin guardar tokens en frontend)
  markSpotifyConnected(): void {
    sessionStorage.setItem('spotifyConnected', 'true');
  }

  // 5. Verificar si el usuario está conectado a Spotify
  isSpotifyConnected(): boolean {
    return sessionStorage.getItem('spotifyConnected') === 'true';
  }

  // 6. Desconectar de Spotify
  disconnectSpotify(): void {
    sessionStorage.removeItem('spotifyConnected');
  }
}
