export type ProviderName = "local" | "gmicloud" | "openai";
export type OutputFormat = "square" | "portrait" | "landscape";
export type Palette = "clay" | "moss" | "night";

export interface ProvenanceStep {
  index: number;
  provider: string;
  model: string;
  status: string;
}

export interface RunRecord {
  id: string;
  title: string;
  brief: string;
  output_format: OutputFormat;
  palette: Palette;
  provider: string;
  model: string;
  created_at: string;
  storage_mode: "local" | "b2";
  storage_key: string;
  manifest_uri: string;
  asset_url: string;
  asset_sha256: string;
  manifest_hash: string;
  manifest_verified: boolean;
  bytes_verified: boolean;
  media_type: string;
  size_bytes: number;
  provenance_steps: ProvenanceStep[];
  is_demo: boolean;
}

export interface AppConfig {
  default_provider: string;
  storage_mode: "local" | "b2";
  providers: Record<ProviderName, boolean>;
  b2: {
    configured: boolean;
    bucket: string | null;
    region: string | null;
  };
}

export interface CreateRunPayload {
  title: string;
  brief: string;
  output_format: OutputFormat;
  palette: Palette;
  provider: ProviderName;
}

export interface VerificationResult {
  run_id: string;
  manifest_verified: boolean;
  bytes_verified: boolean;
  expected_sha256: string;
  actual_sha256: string | null;
  checked_at: string;
}
