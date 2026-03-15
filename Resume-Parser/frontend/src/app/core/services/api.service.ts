import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface SuggestionItem {
  category: string;
  message: string;
}

export interface AnalyzeResponse {
  name: string | null;
  email: string | null;
  skills: string[];
  ats_score: number;
  keyword_score: number;
  skill_coverage_score: number;
  experience_score: number;
  matched_skills: string[];
  missing_skills: string[];
  suggestions: SuggestionItem[];
}

export interface AnalysisHistoryItem {
  id: string;
  resume_id: string;
  ats_score: number;
  matched_skills: string[];
  missing_skills: string[];
  suggestions: any[];
  created_at: string;
}

export interface ResumeHistoryItem {
  id: string;
  filename: string;
  upload_date: string;
  parsed_data: any;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly API = '/api';

  constructor(private http: HttpClient) {}

  analyzeResume(file: File, jobDescription?: string): Observable<AnalyzeResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (jobDescription && jobDescription.trim()) {
      formData.append('job_description', jobDescription);
    }
    return this.http.post<AnalyzeResponse>(`${this.API}/analyze-resume`, formData);
  }

  getAnalysisHistory(): Observable<AnalysisHistoryItem[]> {
    return this.http.get<AnalysisHistoryItem[]>(`${this.API}/analysis/history`);
  }

  getResumes(): Observable<ResumeHistoryItem[]> {
    return this.http.get<ResumeHistoryItem[]>(`${this.API}/resumes`);
  }

  getResumeById(id: string): Observable<ResumeHistoryItem> {
    return this.http.get<ResumeHistoryItem>(`${this.API}/resumes/${id}`);
  }
}
