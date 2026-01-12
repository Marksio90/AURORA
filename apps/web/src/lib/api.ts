/**
 * API client for Decision Calm Engine
 */

import {
  CreateDecisionSessionRequest,
  DecisionSessionResponse,
  ListDecisionSessionsResponse,
  ApiError,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error: ApiError = await response.json();
        throw new Error(error.detail || 'API request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  async createDecisionSession(
    request: CreateDecisionSessionRequest
  ): Promise<DecisionSessionResponse> {
    return this.request<DecisionSessionResponse>('/v1/decision/sessions', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getDecisionSession(sessionId: string): Promise<DecisionSessionResponse> {
    return this.request<DecisionSessionResponse>(
      `/v1/decision/sessions/${sessionId}`
    );
  }

  async listDecisionSessions(
    userId?: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<ListDecisionSessionsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (userId) {
      params.append('user_id', userId);
    }

    return this.request<ListDecisionSessionsResponse>(
      `/v1/decision/sessions?${params.toString()}`
    );
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request<{ status: string }>('/v1/health');
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
