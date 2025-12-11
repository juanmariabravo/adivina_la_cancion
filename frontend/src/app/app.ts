/*
  app.ts - Componente raíz de la aplicación Angular "Adivina la Canción"

    Autor: Juan María Bravo
    Correo: juanmaria.bravo@alu.uclm.es
    Proyecto: Adivina la Canción
    Última edición: 2025-12-11
    URL del repositorio: https://github.com/juanmariabravo/adivina_la_cancion

*/
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
// Importamos el cliente HTTP para hacer peticiones
import { HttpClient, HttpClientModule } from '@angular/common/http'; 
import { CommonModule } from '@angular/common'; // Necesario para directivas (ngIf, ngClass, pipes)
import { Home } from './home/home';
import { RouterOutlet } from '@angular/router';

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
  imports: [CommonModule, RouterOutlet, HttpClientModule],
  templateUrl: './app.html'
})
export class AppComponent {
  title = 'Adivina la Canción';

}
