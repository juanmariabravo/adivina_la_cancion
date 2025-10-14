import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../user-service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterModule],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class Register {
  username = '';
  email = '';
  pwd1 = '';
  pwd2 = '';
  loading = false;
  formError = '';
  successMessage = '';

  private apiUrl = 'http://127.0.0.1:5000/api/v1/register';

  constructor(private service: UserService, private router: Router) {}

  registroExitoso = false;
  onRegister() {
    this.formError = '';
    this.successMessage = '';

    if (!this.username || !this.email || !this.pwd1 || !this.pwd2) {
      this.formError = 'Completa todos los campos.';
      return;
    }
    if (this.pwd1.length < 6) {
      this.formError = 'La contraseña debe tener al menos 6 caracteres.';
      return;
    }
    if (this.pwd1 !== this.pwd2) {
      this.formError = 'Las contraseñas no coinciden.';
      return;
    }
    if (!this.email.includes('@')) {
      this.formError = 'Email inválido.';
      return;
    }

    this.service.register(this.username, this.email, this.pwd1, this.pwd2).subscribe({
      next: ok => {
        this.successMessage = '¡Cuenta creada exitosamente!';
        this.loading = false;
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 2000);
      },
      error: err => {
        this.formError = err.error?.message || 'Error de servidor.';
        this.loading = false;
      }
    });
  }
}