import { Component, ViewChild } from '@angular/core';
import { FormsModule, NgForm, NgModel } from '@angular/forms';
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
  // Modelos
  username = '';
  email = '';
  pwd1 = '';
  pwd2 = '';
  
  // Estados
  loading = false;
  showPassword = false;
  
  // Errores específicos
  formError = '';
  usernameError = '';
  emailError = '';
  confirmPasswordError = '';
  
  // Mensajes de éxito
  successMessage = '';
  
  // Referencias a los inputs
  @ViewChild('registerForm') registerForm!: NgForm;
  @ViewChild('usernameInput') usernameInput!: NgModel;
  @ViewChild('emailInput') emailInput!: NgModel;
  @ViewChild('passwordInput') passwordInput!: NgModel;
  @ViewChild('confirmPasswordInput') confirmPasswordInput!: NgModel;

  constructor(private service: UserService, private router: Router) {}

  // Getters para validación visual
  get usernameInvalid(): boolean {
    return (this.usernameInput?.invalid && this.usernameInput?.touched) || !!this.usernameError;
  }

  get emailInvalid(): boolean {
    return (this.emailInput?.invalid && this.emailInput?.touched) || !!this.emailError;
  }

  get passwordInvalid(): boolean {
    return (this.passwordInput?.invalid && this.passwordInput?.touched) ?? false;
  }

  get confirmPasswordInvalid(): boolean {
    return (this.confirmPasswordInput?.invalid && this.confirmPasswordInput?.touched) || !!this.confirmPasswordError;
  }

  // Validación de fuerza de contraseña
  get passwordStrengthClass(): string {
    if (this.pwd1.length === 0) return '';
    if (this.pwd1.length < 6) return 'weak';
    if (this.pwd1.length < 8) return 'medium';
    
    const hasUpperCase = /[A-Z]/.test(this.pwd1);
    const hasLowerCase = /[a-z]/.test(this.pwd1);
    const hasNumbers = /\d/.test(this.pwd1);
    const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(this.pwd1);
    
    const strength = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChars].filter(Boolean).length;
    
    if (strength <= 1) return 'weak';
    if (strength <= 2) return 'medium';
    return 'strong';
  }

  get passwordStrengthText(): string {
    const strength = this.passwordStrengthClass;
    switch (strength) {
      case 'weak': return 'Contraseña débil';
      case 'medium': return 'Contraseña media';
      case 'strong': return 'Contraseña fuerte';
      default: return 'Seguridad de la contraseña';
    }
  }

  // Métodos de validación
  validateUsername(): void {
    this.usernameError = '';
    
    if (!this.username) return;
    
    if (this.username.length < 3) {
      this.usernameError = 'Mínimo 3 caracteres';
    } else if (this.username.length > 20) {
      this.usernameError = 'Máximo 20 caracteres';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(this.username)) {
      this.usernameError = 'Solo letras, números, _ y -';
    }
  }

  validateEmail(): void {
    this.emailError = '';
    
    if (!this.email) return;
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(this.email)) {
      this.emailError = 'Formato de email inválido';
    }
  }

  validatePassword(): void {
    // La validación básica se maneja con las directivas de Angular
  }

  validateConfirmPassword(): void {
    this.confirmPasswordError = '';
    
    if (this.pwd2 && this.pwd1 !== this.pwd2) {
      this.confirmPasswordError = 'Las contraseñas no coinciden';
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  isFormValid(): boolean {
    return !this.usernameInvalid && 
           !this.emailInvalid && 
           !this.passwordInvalid && 
           !this.confirmPasswordInvalid &&
           this.username.length > 0 &&
           this.email.length > 0 &&
           this.pwd1.length > 0 &&
           this.pwd2.length > 0 &&
           this.pwd1 === this.pwd2;
  }

  onRegister(): void {
    // Limpiar mensajes anteriores
    this.formError = '';
    this.successMessage = '';
    
    // Marcar todos los campos como touched para mostrar errores
    if (this.usernameInput) this.usernameInput.control.markAsTouched();
    if (this.emailInput) this.emailInput.control.markAsTouched();
    if (this.passwordInput) this.passwordInput.control.markAsTouched();
    if (this.confirmPasswordInput) this.confirmPasswordInput.control.markAsTouched();
    
    // Ejecutar validaciones
    this.validateUsername();
    this.validateEmail();
    this.validateConfirmPassword();
    
    // Verificar si el formulario es válido
    if (!this.isFormValid()) {
      this.formError = 'Por favor, corrige los errores del formulario.';
      return;
    }

    this.loading = true;

    this.service.register(this.username, this.email, this.pwd1, this.pwd2).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = '¡Cuenta creada exitosamente! Redirigiendo...';
        
        // Limpiar formulario
        this.username = '';
        this.email = '';
        this.pwd1 = '';
        this.pwd2 = '';

        // Guardar datos de la respuesta
        this.service.saveCurrentUser(response.user);
        this.service.saveToken(response.token_type, response.access_token);
        
        // Redirigir después de 2 segundos
        setTimeout(() => {
          this.router.navigate(['/levels']);
        }, 2000);
      },
      error: (err) => {
        this.loading = false;
        
        if (err.status === 400) {
          if (err.error?.error?.includes('username')) {
            this.usernameError = 'Este nombre de usuario ya está en uso';
          } else if (err.error?.error?.includes('email')) {
            this.emailError = 'Este email ya está registrado';
          } else {
            this.formError = err.error?.error || 'Error en el registro';
          }
        } else if (err.status === 0) {
          this.formError = 'Error de conexión. Verifica tu internet.\nRevisa que el servidor esté en funcionamiento.';
        } else {
          this.formError = err.error?.error || 'Error del servidor. Intenta más tarde.';
        }
      }
    });
  }
}