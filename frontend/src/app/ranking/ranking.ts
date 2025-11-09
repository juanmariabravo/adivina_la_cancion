import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { GameService } from '../../services/game.service';

@Component({
  selector: 'app-ranking',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './ranking.html',
  styleUrls: ['./ranking.css']
})
export class Ranking implements OnInit {
  ranking: any[] = [];
  loading: boolean = true;

  constructor(private gameService: GameService) {}

  ngOnInit(): void {
    this.loadRanking();
  }

  loadRanking(): void {
    this.gameService.getRanking(10).subscribe({
      next: (response) => {
        this.ranking = response.ranking;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error cargando ranking:', err);
        this.loading = false;
      }
    });
  }
}
