import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService, AnalyzeResponse } from '../../core/services/api.service';

@Component({
  selector: 'app-upload',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './upload.component.html',
  styleUrl: './upload.component.css',
})
export class UploadComponent {
  selectedFile: File | null = null;
  fileName = '';
  jobDescription = '';
  loading = false;
  error = '';

  constructor(private api: ApiService, private router: Router) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
      this.fileName = this.selectedFile.name;
    }
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.selectedFile = event.dataTransfer.files[0];
      this.fileName = this.selectedFile.name;
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  removeFile(): void {
    this.selectedFile = null;
    this.fileName = '';
  }

  onSubmit(): void {
    if (!this.selectedFile) return;

    this.error = '';
    this.loading = true;

    this.api.analyzeResume(this.selectedFile, this.jobDescription).subscribe({
      next: (result) => {
        this.loading = false;
        // Navigate to dashboard with the result data
        this.router.navigate(['/dashboard'], { state: { result } });
      },
      error: (err) => {
        this.loading = false;
        this.error = err.error?.detail || 'Analysis failed. Please try again.';
      },
    });
  }
}
