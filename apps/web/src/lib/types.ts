/**
 * TypeScript types for Decision Calm Engine frontend
 */

export type CalmStepType = 'breathing' | 'break' | 'journaling' | 'movement' | 'grounding';

export interface CalmStep {
  type: CalmStepType;
  title: string;
  description: string;
  duration_minutes: number;
}

export interface DecisionOption {
  title: string;
  description: string;
  consequences: string[];
  emotional_risk: string;
  confidence_level: number;
}

export interface NextCheckIn {
  suggestion: string;
  reasoning: string;
}

export interface DecisionBrief {
  options: DecisionOption[];
  calm_step: CalmStep;
  control_question: string;
  next_check_in: NextCheckIn;
  disclaimer: string;
}

export interface CreateDecisionSessionRequest {
  context: string;
  options: string;
  stress_level: number;
  user_id?: string;
}

export interface DecisionSessionResponse {
  id: string;
  created_at: string;
  user_id: string | null;
  input: CreateDecisionSessionRequest;
  output: DecisionBrief;
  stress_level: number;
  processing_time_seconds: number | null;
}

export interface ListDecisionSessionsResponse {
  sessions: DecisionSessionResponse[];
  total: number;
  page: number;
  page_size: number;
}

export interface ApiError {
  type: string;
  title: string;
  status: number;
  detail: string;
  [key: string]: any;
}
