import type {
  AppConfig,
  CreateRunPayload,
  RunRecord,
  VerificationResult,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  config: () => request<AppConfig>("/api/config"),
  runs: () => request<RunRecord[]>("/api/runs"),
  createRun: (payload: CreateRunPayload) =>
    request<RunRecord>("/api/runs", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  manifest: (runId: string) => request<Record<string, unknown>>(`/api/runs/${runId}/manifest`),
  verify: (runId: string) =>
    request<VerificationResult>(`/api/runs/${runId}/verify`, { method: "POST" }),
};
