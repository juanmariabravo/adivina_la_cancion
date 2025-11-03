import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private registerUrl = 'http://localhost:5000/api/v1/auth/register'
  private loginUrl = 'http://localhost:5000/api/v1/auth/login'
  private meUrl = 'http://localhost:5000/api/v1/auth/me'

  constructor(private http: HttpClient) {}

  register(username: string, email: string, pwd1: string, pwd2: string) {
    let info = {
      username : username,
      email : email,
      pwd1 : pwd1, 
      pwd2 : pwd2
    };
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    return this.http.post<any>(this.registerUrl, info, { headers });
  }

  login(email: string, password: string) {
    const payload = { email, password };
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    return this.http.post<any>(this.loginUrl, payload, { headers });
  }

  saveToken(type: string, access_token: string) {
    const token = `${type} ${access_token}`;
    localStorage.setItem('authToken', token);
  }

  saveCurrentUser(user: string) {
    localStorage.setItem('currentUser', JSON.stringify(user));
  }

  getCurrentUser() {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
  }

  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
  }

  getToken(): string | null {
    return localStorage.getItem('authToken');
  }

  validateToken(token: string) {
    const headers = { 
      'Content-Type': 'application/json',
      'Authorization': token
    };

    return this.http.get<any>(this.meUrl, { headers });
  }

  refreshUserData() {
    const token = this.getToken();
    if (token) {
      // Validar token con el backend
      this.validateToken(token).subscribe({
        next: (userData) => {
          
          // Actualizar datos en localStorage
          this.saveCurrentUser(userData);
        },
        error: (err) => {
          console.error('Token inválido o expirado:', err);
          this.logout();
        }
      });
    }
  }
}