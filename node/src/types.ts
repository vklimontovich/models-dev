export type InputModality = "text" | "image" | "audio" | "video" | "pdf";
export type OutputModality = "text" | "image" | "audio" | "video";
export type Status = "alpha" | "deprecated";

export interface Cost {
  input?: number;
  output?: number;
  cache_read?: number;
  cache_write?: number;
  reasoning?: number;
  input_audio?: number;
  output_audio?: number;
  context_over_200k?: number;
}

export interface Limit {
  context?: number;
  input?: number;
  output?: number;
}

export interface Modalities {
  input: readonly InputModality[];
  output: readonly OutputModality[];
}

export interface Interleaved {
  field?: string;
}

export interface ModelProvider {
  npm: string;
}

export interface Model {
  id: string;
  name: string;
  attachment: boolean;
  reasoning: boolean;
  tool_call: boolean;
  open_weights: boolean;
  release_date: string;
  last_updated: string;
  modalities: Modalities;
  limit: Limit;
  family?: string;
  structured_output?: boolean;
  temperature?: boolean;
  knowledge?: string;
  cost?: Cost;
  status?: Status;
  interleaved?: boolean | Interleaved;
  provider?: ModelProvider;
}

export interface Provider {
  id: string;
  name: string;
  env: readonly string[];
  npm: string;
  doc: string;
  api?: string;
  models: Readonly<Record<string, Model>>;
}

export type ProvidersData = Readonly<Record<string, Provider>>;
