import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './login.component.css',
})
export class RegisterComponent {
  fullName = '';
  email = '';
  password = '';
  error = '';
  loading = false;

  constructor(private auth: AuthService, private router: Router) {}

  onSubmit(): void {
    this.error = '';
    this.loading = true;
    this.auth.register({ email: this.email, password: this.password, full_name: this.fullName }).subscribe({
      next: () => {
        this.loading = false;
        this.router.navigate(['/upload']);
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Registration failed.';
      },
    });
  }
}
