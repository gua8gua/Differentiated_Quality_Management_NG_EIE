export interface DashboardData {
  overview: {
    title: string;
    subtitle: string;
    objects: string[];
    coreWorks: string[];
  };
  dataQuality: {
    dataset: string;
    qualityScore: number;
    missingRate: number;
    anomalyRate: number;
    topFeatures: string[];
  };
  riskPrediction: {
    riskLevel: string;
    phenomenon: string;
    classification?: {
      model: string;
      accuracy: number;
      precision: number;
      recall: number;
      f1: number;
      confusion_matrix: number[][];
      test_size: number;
    } | null;
    trend?: {
      method: string;
      feature: string;
      start: number;
      end: number;
      delta: number;
    } | null;
    dtwSimilarSegments: Array<{
      caseId: string;
      similarity: number;
      label: string;
    }>;
    rul: Array<{
      cycle: number;
      value: number;
    }>;
  };
  graphTrace: {
    phenomenon: string;
    paths: string[][];
    summary: string;
  };
  workflow?: Array<{
    stage: string;
    project: string;
    output: string;
  }>;
  agents: Array<{
    name: string;
    code: string;
    input: string;
    output: string;
    recommendation: string;
  }>;
  agentDecisions?: Array<{
    agent: string;
    judgment: string;
    recommendation: string;
    confidence: number;
  }>;
  disposalReport?: {
    phenomenon: string;
    riskLevel: string;
    evidenceChain: string[];
    rootCausePath: string[];
    recommendation: string;
    responsibleObject: string;
  };
  feedbackEvaluation?: {
    timeliness: number;
    effectiveness: number;
    completeness: number;
    recurrenceRisk: string;
    summary: string;
  };
}

export type DataModality = "tabular" | "timeseries" | "image" | "text" | "audio" | "multimodal";
export type QualityObject = "whole_equipment" | "software" | "component" | "process" | "generic";
export type UseCase =
  | "governance"
  | "quality_evaluation"
  | "anomaly_detection"
  | "risk_prediction"
  | "rag_explanation";
export type QualityStandard = "ISO8000" | "GB_T_34960_5" | "IEC62424" | "project_custom";

export interface DatasetContextForm {
  name: string;
  modality: DataModality;
  quality_object: QualityObject;
  use_case: UseCase;
  standards: QualityStandard[];
  description: string;
  tags: string[];
}

export interface MetadataOptions {
  modalities: string[];
  quality_objects: string[];
  use_cases: string[];
  standards: string[];
  dataset_types: string[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface StreamLogEvent {
  event?: string;
  stage: string;
  project?: string;
  summary: string;
  metrics?: Record<string, unknown>;
  payload?: Record<string, unknown>;
  timestamp?: string;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp?: string;
  stage?: string;
}

export interface RealtimeMetric {
  timestamp: string;
  qualityScore: number;
  anomalyRate: number;
  riskLevelIndex: number;
  sensorValue: number;
  tick: number;
}

export interface UploadResponse {
  upload_id: string;
  filename: string;
  message: string;
}

export interface AnalyzeResponse {
  job_id: string;
  status: string;
}
