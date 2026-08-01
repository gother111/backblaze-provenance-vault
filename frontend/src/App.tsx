import { useEffect, useState } from "react";

import { api } from "./api";
import { GeneratorPanel } from "./components/GeneratorPanel";
import { ManifestDialog } from "./components/ManifestDialog";
import { MediaPreview } from "./components/MediaPreview";
import { ProvenanceInspector } from "./components/ProvenanceInspector";
import { RunLibrary } from "./components/RunLibrary";
import type { AppConfig, CreateRunPayload, ProviderName, RunRecord, VerificationResult } from "./types";

const initialForm: CreateRunPayload = {
  title: "Morning ritual",
  brief: "A quiet morning ritual for a ceramic studio, soft window light, tactile clay textures",
  output_format: "square",
  palette: "clay",
  provider: "local",
};

export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [runs, setRuns] = useState<RunRecord[]>([]);
  const [selected, setSelected] = useState<RunRecord | null>(null);
  const [form, setForm] = useState<CreateRunPayload>(initialForm);
  const [busy, setBusy] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [manifest, setManifest] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    Promise.all([api.config(), api.runs()])
      .then(([nextConfig, nextRuns]) => {
        setConfig(nextConfig);
        setRuns(nextRuns);
        setSelected(nextRuns[0] ?? null);
        const defaultProvider = nextConfig.default_provider as ProviderName;
        if (defaultProvider in nextConfig.providers && nextConfig.providers[defaultProvider]) {
          setForm((current) => ({ ...current, provider: defaultProvider }));
        }
      })
      .catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Could not load the app"));
  }, []);

  const createRun = async () => {
    setBusy(true);
    setError(null);
    setVerification(null);
    try {
      const run = await api.createRun(form);
      setRuns((current) => [run, ...current]);
      setSelected(run);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Generation failed");
    } finally {
      setBusy(false);
    }
  };

  const openManifest = async () => {
    if (!selected) return;
    try {
      setManifest(await api.manifest(selected.id));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Manifest could not be loaded");
    }
  };

  const verify = async () => {
    if (!selected) return;
    setVerifying(true);
    try {
      const result = await api.verify(selected.id);
      setVerification(result);
      setRuns((current) => current.map((run) => run.id === selected.id ? { ...run, bytes_verified: result.bytes_verified, manifest_verified: result.manifest_verified } : run));
      setSelected((run) => run ? { ...run, bytes_verified: result.bytes_verified, manifest_verified: result.manifest_verified } : run);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Verification failed");
    } finally {
      setVerifying(false);
    }
  };

  const navigate = (target: "library" | "new-run" | "verify") => {
    document.getElementById(target)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <button className="wordmark" type="button" onClick={() => navigate("new-run")}>Provenance Vault</button>
        <nav aria-label="Primary navigation">
          <button type="button" onClick={() => navigate("library")}>Library</button>
          <button type="button" onClick={() => navigate("new-run")}>New run</button>
          <button type="button" onClick={() => navigate("verify")}>Verify</button>
        </nav>
        <div className="storage-state"><span aria-hidden="true" />{config?.storage_mode === "b2" ? "B2 connected" : "Local demo"}</div>
      </header>

      <main>
        <div className="workspace">
          <GeneratorPanel value={form} config={config} busy={busy} error={error} onChange={setForm} onSubmit={createRun} />
          <div className="result-column">
            <MediaPreview run={selected} loading={busy} />
            <ProvenanceInspector run={selected} verification={verification} verifying={verifying} onManifest={openManifest} onVerify={verify} />
          </div>
        </div>
        <RunLibrary runs={runs} selectedId={selected?.id} onSelect={(run) => { setSelected(run); setVerification(null); navigate("new-run"); }} />
      </main>
      <footer><span>Provenance Vault</span><p>Genblaze orchestration · content-addressed storage · SHA-256 verification</p></footer>
      <ManifestDialog manifest={manifest} onClose={() => setManifest(null)} />
    </div>
  );
}
