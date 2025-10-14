import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
// Importamos el cliente HTTP para hacer peticiones
import { HttpClient, HttpClientModule } from '@angular/common/http'; 
import { CommonModule } from '@angular/common'; // Necesario para directivas (ngIf, ngClass, pipes)
import { Home } from './home/home';

// Definición de la estructura de la respuesta JSON que esperamos de Flask
interface SaludoResponse {
  mensaje: string;
  timestamp: string;
  servidor: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  // Es crucial importar HttpClientModule y CommonModule (para pipes y directivas)
  imports: [HttpClientModule, CommonModule, Home], // Agrega HomeComponent aquí
  templateUrl: './app.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  // Inyección de HttpClient usando la función inject (patrón moderno de Angular)
  private http = inject(HttpClient); 
  
  // URL donde corre el backend de Flask, coincidiendo con la configuración en app.py
  private apiUrl = 'http://127.0.0.1:5000/api/saludo';

  // Señales (signals) para manejar el estado de la aplicación de manera reactiva
  respuesta = signal<SaludoResponse | null>(null);
  error = signal<string | null>(null);
  loading = signal<boolean>(false);

  /**
   * Realiza la petición GET al backend de Flask.
   */
  obtenerSaludo() {
    this.loading.set(true);
    this.respuesta.set(null);
    this.error.set(null);

    // Petición HTTP. Usamos subscribe para iniciar la petición.
    this.http.get<SaludoResponse>(this.apiUrl).subscribe({
      next: (data) => {
        // Petición exitosa: actualiza la respuesta
        this.respuesta.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        // Manejo de errores de red o del servidor
        console.error('Error al conectar con Flask:', err);
        this.error.set('No se pudo establecer conexión con el servidor Flask. Revisa la consola para más detalles.');
        this.loading.set(false);
      },
      complete: () => {
        // Limpieza final
        this.loading.set(false);
      }
    });
  }
}
