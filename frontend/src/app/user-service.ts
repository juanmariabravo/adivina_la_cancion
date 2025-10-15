import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private registerUrl = 'http://localhost:5000/api/v1/auth/register'
  private loginUrl = 'http://localhost:5000/api/v1/auth/login'

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
    localStorage.setItem('currentUser', JSON.stringify({ email }));
    const payload = { email, password };
    const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
    return this.http.post<any>(this.loginUrl, payload, { headers });
  }

  isLoggedIn() {
    return !!localStorage.getItem('authToken'); // !! devuelve true/false según si existe o no el token
  }

  getCurrentUser() {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
  }

  logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
  }
}