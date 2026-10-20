import axios from 'axios';
import { 
  CaseRecord, 
  ComplaintCreate, 
  CaseDecisionRequest, 
  EvaluationMetrics, 
  DashboardStats 
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const apiService = {
  // Submit a complaint
  async submitComplaint(data: ComplaintCreate): Promise<CaseRecord> {
    const response = await client.post<CaseRecord>('/complaints', data);
    return response.data;
  },

  // Get cases with optional filters
  async getCases(params?: { status?: string; category?: string; search?: string }): Promise<CaseRecord[]> {
    const response = await client.get<CaseRecord[]>('/cases', { params });
    return response.data;
  },

  // Get single case by ID
  async getCaseById(caseId: string): Promise<CaseRecord> {
    const response = await client.get<CaseRecord>(`/cases/${caseId}`);
    return response.data;
  },

  // Admin decision
  async makeCaseDecision(caseId: string, decision: CaseDecisionRequest): Promise<CaseRecord> {
    const response = await client.post<CaseRecord>(`/cases/${caseId}/decision`, decision);
    return response.data;
  },

  // Get Dashboard Stats
  async getStats(): Promise<DashboardStats> {
    const response = await client.get<DashboardStats>('/stats');
    return response.data;
  },

  // Get Benchmark & Ablation Metrics
  async getBenchmarkMetrics(): Promise<EvaluationMetrics> {
    const response = await client.get<EvaluationMetrics>('/metrics/benchmark');
    return response.data;
  },

  // Reset Demo State
  async resetDemo(): Promise<{ message: string }> {
    const response = await client.post<{ message: string }>('/reset-demo');
    return response.data;
  }
};
