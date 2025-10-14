import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../auth-service';

interface LoginForm {
  email: string;
  password: string;
}

interface ValidationMessages {
  email: string;
  password: string;
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login implements OnInit {
  // Signals para estado reactivo
  isLoading = signal<boolean>(false);
  showPassword = signal<boolean>(false);
  errorMessage = signal<string>('');
  showNotification = signal<boolean>(false);

  loginForm: FormGroup;
  validationMessages: ValidationMessages = {
    email: '',
    password: ''
  };

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {
    // Si ya está autenticado, redirigir al juego
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/game']);
    }

    // Observar cambios en los campos para validación en tiempo real
    this.setupFormValidation();
  }

  private setupFormValidation(): void {
    // Validación en tiempo real para email
    this.loginForm.get('email')?.valueChanges.subscribe(() => {
      this.validateEmail();
    });

    // Validación en tiempo real para password
    this.loginForm.get('password')?.valueChanges.subscribe(() => {
      this.validatePassword();
    });
  }

  private validateEmail(): void {
    const emailControl = this.loginForm.get('email');
    if (!emailControl) return;

    if (emailControl.errors?.['required']) {
      this.validationMessages.email = 'El email es requerido';
    } else if (emailControl.errors?.['email']) {
      this.validationMessages.email = 'Formato de email inválido';
    } else {
      this.validationMessages.email = '';
    }
  }

  private validatePassword(): void {
    const passwordControl = this.loginForm.get('password');
    if (!passwordControl) return;

    if (passwordControl.errors?.['required']) {
      this.validationMessages.password = 'La contraseña es requerida';
    } else if (passwordControl.errors?.['minlength']) {
      this.validationMessages.password = 'Mínimo 6 caracteres';
    } else {
      this.validationMessages.password = '';
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword.update(value => !value);
  }

  onSubmit(): void {
    // Marcar todos los campos como touched para mostrar errores
    this.markFormGroupTouched();

    if (this.loginForm.valid) {
      this.attemptLogin();
    } else {
      this.validateForm();
    }
  }

  private markFormGroupTouched(): void {
    Object.keys(this.loginForm.controls).forEach(key => {
      const control = this.loginForm.get(key);
      control?.markAsTouched();
    });
  }

  private validateForm(): void {
    this.validateEmail();
    this.validatePassword();
  }

  private async attemptLogin(): Promise<void> {
    this.isLoading.set(true);
    this.errorMessage.set('');

    const credentials: LoginForm = this.loginForm.value;

    try {
      const success = await this.authService.login(credentials);
      
      if (success) {
        this.showSuccessNotification();
        // Redirigir después de un breve delay para mostrar la notificación
        setTimeout(() => {
          this.router.navigate(['/game']);
        }, 1500);
      } else {
        this.errorMessage.set('Credenciales inválidas. Por favor, intenta de nuevo.');
      }
    } catch (error) {
      console.error('Error durante el login:', error);
      this.handleLoginError(error);
    } finally {
      this.isLoading.set(false);
    }
  }

  private handleLoginError(error: any): void {
    if (error.status === 401) {
      this.errorMessage.set('Email o contraseña incorrectos.');
    } else if (error.status === 0) {
      this.errorMessage.set('Error de conexión. Verifica tu internet.');
    } else {
      this.errorMessage.set('Error del servidor. Intenta más tarde.');
    }
  }

  private showSuccessNotification(): void {
    this.showNotification.set(true);
    setTimeout(() => {
      this.showNotification.set(false);
    }, 3000);
  }

  loginAsGuest(): void {
    this.router.navigate(['/game']);
  }

  // Getters para facilitar el acceso en el template
  get email() { 
    return this.loginForm.get('email'); 
  }

  get password() { 
    return this.loginForm.get('password'); 
  }

  get isEmailInvalid(): boolean {
    return !!this.email && this.email.invalid && this.email.touched;
  }

  get isPasswordInvalid(): boolean {
    return !!this.password && this.password.invalid && this.password.touched;
  }
}