
export interface LiveEvent {
  id: string;
  timestamp: string;
  source: string;
  title: string;
  content: string;
  impactScore: number;
  company: string;
}

export interface IntelligenceReport {
  query: string;
  liveSignals: { timestamp: string; source: string; content: string }[];
  beforeAfter: { before: string; after: string } | null;
  impactReasoning: {
    business: string;
    tech: string;
    supplyChain: string;
  };
  competitorImpact: string;
  strategicOutlook: string[];
  confidence: 'Confirmed' | 'Developing' | 'Uncertain';
  signalStrength: number;
  ceoSummary: string;
  highImpactAlert?: string;
}

export enum ConfidenceLevel {
  HIGH = '✅ Confirmed',
  MEDIUM = '🟡 Developing',
  LOW = '🔴 Uncertain'
}

export interface RadarStatus {
  company: string;
  status: 'High' | 'Moderate' | 'Low';
  trend: 'up' | 'down' | 'neutral';
}
