import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  email: string;
  full_name: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = '/api';
  private loggedIn$ = new BehaviorSubject<boolean>(this.hasToken());

  constructor(private http: HttpClient, private router: Router) {}

  get isLoggedIn$(): Observable<boolean> {
    return this.loggedIn$.asObservable();
  }

  get isLoggedIn(): boolean {
    return this.hasToken();
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  register(data: RegisterRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API}/auth/register`, data).pipe(
      tap(res => this.storeToken(res.access_token))
    );
  }

  login(data: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.API}/auth/login`, data).pipe(
      tap(res => this.storeToken(res.access_token))
    );
  }

  getMe(): Observable<UserResponse> {
    return this.http.get<UserResponse>(`${this.API}/auth/me`);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    this.loggedIn$.next(false);
    this.router.navigate(['/login']);
  }

  private storeToken(token: string): void {
    localStorage.setItem('access_token', token);
    this.loggedIn$.next(true);
  }

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }
}
