export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface DocumentItem {
  id: string;
  case_id: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  status: string;
  chunk_count: number;
  created_at: string;
}

export interface Case {
  id: string;
  user_id: string;
  title: string;
  description: string;
  jurisdiction: string;
  legal_domain: string;
  client_name?: string;
  status: string;
  created_at: string;
  updated_at: string;
  documents: DocumentItem[];
}

export interface AgentExecution {
  id: string;
  agent_name: string;
  step_number: number;
  status: string;
  execution_time_ms: number;
  output_payload_json: Record<string, any>;
  created_at: string;
}

export interface Citation {
  id?: string;
  title: string;
  citation_text: string;
  jurisdiction: string;
  quote?: string;
  relevance_score: number;
  source_type: 'statute' | 'precedent' | 'regulation' | 'exhibit' | string;
  evidence_type?: 'SUPPORTED BY SOURCE' | 'MODEL INFERENCE' | 'INSUFFICIENT EVIDENCE' | string;
}

export interface Report {
  id: string;
  case_id: string;
  session_id: string;
  title: string;
  executive_summary: string;
  case_context?: string;
  factual_analysis?: string;
  statutory_matrix: Array<{
    provision?: string;
    title?: string;
    law?: string;
    section?: string;
    relevance?: string;
    finding?: string;
    [key: string]: any;
  }>;
  precedent_analysis: Array<{
    case?: string;
    case_name?: string;
    citation?: string;
    court?: string;
    principle?: string;
    rule_of_law?: string;
    application?: string;
    factual_distinctions?: string[];
    [key: string]: any;
  }>;
  strategic_recommendations: Array<{
    step?: number;
    action?: string;
    impact?: string;
    objective?: string;
    [key: string]: any;
  }>;
  opposing_arguments: Array<{
    claim?: string;
    claim_challenged?: string;
    refutation?: string;
    basis?: string;
    [key: string]: any;
  }>;
  judicial_evaluation: {
    standard?: string;
    standard_of_review?: string;
    predicted_outcome?: string;
    predicted_disposition?: string;
    evaluations?: Array<any>;
    [key: string]: any;
  };
  critique_summary: {
    citation_integrity?: string | number;
    citation_validity_score?: number;
    reasoning_coherence_score?: number;
    admissibility?: string;
    actionable_feedback?: string;
    [key: string]: any;
  };
  confidence_score: number;
  limitations_disclaimer: string;
  full_report_json?: Record<string, any>;
  citations: Citation[];
  created_at: string;
}

export interface ResearchSession {
  id: string;
  case_id: string;
  user_id: string;
  objective: string;
  current_agent: string;
  status: 'pending' | 'in_progress' | 'retrying' | 'completed' | 'failed' | string;
  iteration_count: number;
  agent_executions: AgentExecution[];
  state_snapshot?: Record<string, any>;
  reports: Report[];
  created_at: string;
  updated_at: string;
}