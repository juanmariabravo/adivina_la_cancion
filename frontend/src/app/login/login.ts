import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { UserService } from '../user-service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login implements OnInit {
  // Formulario reactivo
  loginForm: FormGroup;
  
  // Estados
  loading = false;
  showPassword = false;
  
  // Mensajes de error
  formError = '';
  emailError = '';
  passwordError = '';
  
  // Mensaje de éxito
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private service: UserService,
    private router: Router
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {
    // Si ya está autenticado, redirigir a la página de niveles
    const token = this.service.getToken();
    if (token) {
      this.service.validateToken().subscribe({
        next: () => {
          this.router.navigate(['/levels']);
        },
        error: () => {
          // Token inválido, continuar en login
        }
      });
    }

    // Validación en tiempo real
    this.setupFormValidation();
  }

  private setupFormValidation(): void {
    // Validación en tiempo real para email
    this.loginForm.get('email')?.valueChanges.subscribe(() => {
      if (this.emailControl?.touched) {
        this.validateEmail();
      }
    });

    // Validación en tiempo real para password
    this.loginForm.get('password')?.valueChanges.subscribe(() => {
      if (this.passwordControl?.touched) {
        this.validatePassword();
      }
    });
  }

  // Getters para los controles del formulario
  get emailControl() {
    return this.loginForm.get('email');
  }

  get passwordControl() {
    return this.loginForm.get('password');
  }

  // Getters para validación visual
  get emailInvalid(): boolean {
    return (this.emailControl?.invalid && this.emailControl?.touched) || !!this.emailError;
  }

  get passwordInvalid(): boolean {
    return (this.passwordControl?.invalid && this.passwordControl?.touched) || !!this.passwordError;
  }

  // Métodos de validación
  validateEmail(): void {
    this.emailError = '';
    
    if (!this.emailControl?.value) return;
    
    if (this.emailControl?.errors?.['email']) {
      this.emailError = 'Formato de email inválido';
    }
  }

  validatePassword(): void {
    this.passwordError = '';
    
    if (!this.passwordControl?.value) return;
    
    if (this.passwordControl?.errors?.['minlength']) {
      this.passwordError = 'Mínimo 6 caracteres';
    }
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  isFormValid(): boolean {
    return !this.emailInvalid && 
           !this.passwordInvalid &&
           this.emailControl?.value?.length > 0 &&
           this.passwordControl?.value?.length > 0;
  }

  onSubmit(): void {
    // Limpiar mensajes anteriores
    this.formError = '';
    this.successMessage = '';
    this.emailError = '';
    this.passwordError = '';
    
    // Marcar todos los campos como touched para mostrar errores
    this.emailControl?.markAsTouched();
    this.passwordControl?.markAsTouched();
    
    // Ejecutar validaciones
    this.validateEmail();
    this.validatePassword();
    
    // Verificar si el formulario es válido
    if (!this.isFormValid()) {
      this.formError = 'Por favor, corrige los errores del formulario.';
      return;
    }

    if (this.loginForm.valid) {
      this.attemptLogin();
    }
  }

  private attemptLogin(): void {
    this.loading = true;
    this.formError = '';

    const email = this.loginForm.value.email;
    const password = this.loginForm.value.password;

    this.service.login(email, password).subscribe({
      next: (response: any) => {
        this.loading = false;
        this.successMessage = '¡Sesión iniciada correctamente! Redirigiendo...';
        
        // Limpiar formulario
        this.loginForm.reset();

        // Guardar datos de la respuesta
        this.service.saveCurrentUser(response.user);
        this.service.saveToken(response.token_type, response.access_token);
        
        // Redirigir después de 1.5 segundos
        setTimeout(() => {
          this.router.navigate(['/levels']);
        }, 1500);
      },
      error: (error) => {
        this.loading = false;
        
        if (error.status === 401) {
          this.formError = 'Email o contraseña incorrectos.';
        } else if (error.status === 400) {
          this.formError = error.error?.error || 'Credenciales inválidas.';
        } else if (error.status === 0) {
          this.formError = 'Error de conexión. Revisa que el servidor esté activo.';
        } else {
          this.formError = error.error?.error || 'Error del servidor. Intenta más tarde.';
        }
        
        // Limpiar contraseña en caso de error
        this.loginForm.patchValue({ password: '' });
        this.passwordControl?.markAsUntouched();
      }
    });
  }

  loginAsGuest(): void {
    this.router.navigate(['/game']);
  }
}