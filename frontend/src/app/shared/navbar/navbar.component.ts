import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <nav class="navbar">
      <a routerLink="/" class="brand">🧠 Resume Intelligence</a>

      <div class="nav-links">
        <ng-container *ngIf="auth.isLoggedIn$ | async; else loggedOut">
          <a routerLink="/upload" routerLinkActive="active">Upload</a>
          <a routerLink="/history" routerLinkActive="active">History</a>
          <button class="logout-btn" (click)="auth.logout()">Logout</button>
        </ng-container>

        <ng-template #loggedOut>
          <a routerLink="/login" routerLinkActive="active">Login</a>
          <a routerLink="/register" routerLinkActive="active">Register</a>
        </ng-template>
      </div>
    </nav>
  `,
  styles: [`
    .navbar {
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 24px; height: 64px;
      background: rgba(255,255,255,0.03);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      backdrop-filter: blur(20px);
    }

    .brand {
      color: #fff; font-size: 18px; font-weight: 700;
      text-decoration: none; letter-spacing: -0.5px;
    }

    .nav-links { display: flex; align-items: center; gap: 8px; }

    .nav-links a {
      color: rgba(255,255,255,0.6); text-decoration: none;
      padding: 8px 16px; border-radius: 8px; font-size: 14px;
      font-weight: 500; transition: all 0.2s;
    }

    .nav-links a:hover { color: #fff; background: rgba(255,255,255,0.08); }
    .nav-links a.active { color: #a29bfe; background: rgba(108,99,255,0.12); }

    .logout-btn {
      background: rgba(255,71,87,0.12); color: #ff6b81;
      border: 1px solid rgba(255,71,87,0.2);
      padding: 8px 16px; border-radius: 8px; font-size: 14px;
      font-weight: 500; cursor: pointer; transition: all 0.2s;
    }

    .logout-btn:hover { background: rgba(255,71,87,0.2); }
  `],
})
export class NavbarComponent {
  constructor(public auth: AuthService) {}
}
