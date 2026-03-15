import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration } from 'chart.js';
import { AnalyzeResponse } from '../../core/services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, BaseChartDirective, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  result: AnalyzeResponse | null = null;

  // Doughnut chart config for ATS score
  doughnutData: ChartConfiguration<'doughnut'>['data'] = { labels: [], datasets: [] };
  doughnutOptions: ChartConfiguration<'doughnut'>['options'] = {
    responsive: true,
    cutout: '75%',
    plugins: { legend: { display: false } },
  };

  // Bar chart config for score breakdown
  barData: ChartConfiguration<'bar'>['data'] = { labels: [], datasets: [] };
  barOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    scales: {
      y: { beginAtZero: true, max: 100, ticks: { color: 'rgba(255,255,255,0.5)' }, grid: { color: 'rgba(255,255,255,0.05)' } },
      x: { ticks: { color: 'rgba(255,255,255,0.5)' }, grid: { display: false } },
    },
    plugins: { legend: { display: false } },
  };

  constructor(private router: Router) {}

  ngOnInit(): void {
    const nav = this.router.getCurrentNavigation();
    const state = nav?.extras?.state || history.state;

    if (state && state['result']) {
      this.result = state['result'] as AnalyzeResponse;
      this.buildCharts();
    }
  }

  private buildCharts(): void {
    if (!this.result) return;

    const score = this.result.ats_score;
    const remaining = Math.max(0, 100 - score);

    this.doughnutData = {
      labels: ['Score', 'Remaining'],
      datasets: [{
        data: [score, remaining],
        backgroundColor: [this.getScoreColor(score), 'rgba(255,255,255,0.05)'],
        borderWidth: 0,
      }],
    };

    this.barData = {
      labels: ['Keyword', 'Skill Coverage', 'Experience'],
      datasets: [{
        data: [
          this.result.keyword_score,
          this.result.skill_coverage_score,
          this.result.experience_score,
        ],
        backgroundColor: ['#6c63ff', '#2ed573', '#ffa502'],
        borderRadius: 8,
        borderSkipped: false,
      }],
    };
  }

  getScoreColor(score: number): string {
    if (score >= 75) return '#2ed573';
    if (score >= 50) return '#ffa502';
    return '#ff6b81';
  }

  getScoreLabel(score: number): string {
    if (score >= 75) return 'Excellent';
    if (score >= 50) return 'Good';
    if (score >= 25) return 'Needs Work';
    return 'Poor';
  }
}
