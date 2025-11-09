import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Login } from './login/login';
import { Register } from './register/register';
import { Levels } from './levels/levels';
import { Profile } from './profile/profile';
import { Game } from './game/game';
import { Callback } from './callback/callback';
import { Ranking } from './ranking/ranking';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'levels', component: Levels },
  { path: 'profile', component: Profile },
  { path: 'game', component: Game },
  { path: 'callback', component: Callback },
  { path: 'ranking', component: Ranking }
];