import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  register(username: string, email: string, pwd1: string, pwd2: string, spotifyClientId?: string, spotifyClientSecret?: string) {
    let info = {
      username: username,
      email: email,
      pwd1: pwd1,
      pwd2: pwd2,
      spotify_client_id: spotifyClientId,
      spotify_client_secret: spotifyClientSecret
    };
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    return this.http.post<any>(`${this.apiUrl}/auth/register`, info, { headers });
  }

  login(email: string, password: string) {
    const payload = { email, password };
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    return this.http.post<any>(`${this.apiUrl}/auth/login`, payload, { headers });
  }

  saveToken(type: string, access_token: string) {
    const token = `${type} ${access_token}`;
    sessionStorage.setItem('authToken', token);
  }

  logout() {
    sessionStorage.clear();
  }

  getToken(): string {
    const token = sessionStorage.getItem('authToken');
    if (!token) {
      return '';
    }
    return token;
  }

  validateToken() {
    const token = this.getToken();
    if (!token) {
      throw new Error('No token found');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': token
    };

    return this.http.get<any>(`${this.apiUrl}/auth/me`, { headers });
  }

  updateProfile(username?: string, password?: string) {
    const token = this.getToken();
    if (!token) {
      throw new Error('No token found');
    }

    const payload: any = {};
    if (username) payload.username = username;
    if (password) payload.password = password;

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': token
    };

    return this.http.put<any>(`${this.apiUrl}/auth/update-profile`, payload, { headers });
  }
}