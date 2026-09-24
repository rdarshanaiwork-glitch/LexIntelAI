import { Case, DocumentItem, ResearchSession, Report, User } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

class ApiService {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('lexintel_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    };
  }

  async getHealth() {
    const res = await fetch(`${BASE_URL}/health`);
    if (!res.ok) throw new Error('Backend health check failed');
    return res.json();
  }

  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error('Invalid email or password');
    const data = await res.json();
    localStorage.setItem('lexintel_token', data.access_token);
    return data;
  }

  async register(email: string, password: string, full_name: string): Promise<{ access_token: string; user: User }> {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, full_name })
    });
    if (!res.ok) throw new Error('Registration failed');
    const data = await res.json();
    localStorage.setItem('lexintel_token', data.access_token);
    return data;
  }

  async getCases(): Promise<Case[]> {
    const res = await fetch(`${BASE_URL}/cases`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Failed to load cases');
    return res.json();
  }

  async getCase(id: string): Promise<Case> {
    const res = await fetch(`${BASE_URL}/cases/${id}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Case not found');
    return res.json();
  }

  async createCase(caseData: { title: string; description: string; jurisdiction?: string; legal_domain?: string; client_name?: string }): Promise<Case> {
    const res = await fetch(`${BASE_URL}/cases`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(caseData)
    });
    if (!res.ok) throw new Error('Failed to create case');
    return res.json();
  }

  async uploadDocument(caseId: string, file: File): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('case_id', caseId);
    formData.append('file', file);

    const token = localStorage.getItem('lexintel_token');
    const res = await fetch(`${BASE_URL}/documents/upload`, {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData
    });
    if (!res.ok) throw new Error('Document upload failed');
    return res.json();
  }

  async startResearch(caseId: string, objective: string, executionStrategy: string = 'full_litigation'): Promise<ResearchSession> {
    const res = await fetch(`${BASE_URL}/research/start`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        case_id: caseId,
        objective,
        execution_strategy: executionStrategy
      })
    });
    if (!res.ok) throw new Error('Failed to initiate research session');
    return res.json();
  }

  async getCaseSessions(caseId: string): Promise<ResearchSession[]> {
    const res = await fetch(`${BASE_URL}/research/case/${caseId}/sessions`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch case sessions');
    return res.json();
  }

  async getResearchSession(id: string): Promise<ResearchSession> {
    const res = await fetch(`${BASE_URL}/research/${id}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Research session not found');
    return res.json();
  }

  async getResearchStatus(id: string): Promise<any> {
    const res = await fetch(`${BASE_URL}/research/${id}/status`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Failed to fetch status');
    return res.json();
  }

  async getReport(id: string): Promise<Report> {
    const res = await fetch(`${BASE_URL}/reports/${id}`, {
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Report not found');
    return res.json();
  }

  async getEvaluationResults(): Promise<any> {
    const res = await fetch(`${BASE_URL}/evaluation/results`);
    if (!res.ok) throw new Error('Failed to fetch evaluation results');
    return res.json();
  }

  async runEvaluation(): Promise<any> {
    const res = await fetch(`${BASE_URL}/evaluation/run`, {
      method: 'POST',
      headers: this.getHeaders()
    });
    if (!res.ok) throw new Error('Failed to run benchmark evaluation');
    return res.json();
  }
}

export const api = new ApiService();