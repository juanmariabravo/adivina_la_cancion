import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GameService {
  private apiUrl = 'http://127.0.0.1:5000/api/v1';

  constructor(private http: HttpClient) {}

  // Obtener canción de un nivel
  getSongForLevel(levelId: string, authToken?: string): Observable<any> {
    const headers: any = {
      'Content-Type': 'application/json'
    };
    
    if (authToken) {
      headers['Authorization'] = authToken;
    }

    return this.http.get<any>(`${this.apiUrl}/songs/${levelId}`, { headers });
  }

  // Validar respuesta del usuario
  validateAnswer(levelId: string, answer: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/game/validate`, {
      level_id: levelId,
      answer: answer
    });
  }

  // Revelar respuesta correcta
  revealSong(songId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/game/song/${songId}/reveal`);
  }

  // Enviar puntuación (solo usuarios autenticados)
  submitScore(score: number, authToken: string): Observable<any> {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': authToken
    };

    return this.http.post<any>(`${this.apiUrl}/game/submit-score`, 
      { score }, 
      { headers }
    );
  }

  // Marcar desafío diario como completado
  completeDailyChallenge(authToken: string): Observable<any> {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': authToken
    };

    return this.http.post<any>(`${this.apiUrl}/game/daily/complete`, {}, { headers });
  }

  // Obtener ranking
  getRanking(limit: number = 10): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/ranking`, {
      params: { limit: limit.toString() }
    });
  }
}
