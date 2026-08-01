import type { RunRecord, VerificationResult } from "../types";
import { shortHash } from "../lib/format";
import { SealIcon } from "./Icons";

interface ProvenanceInspectorProps {
  run: RunRecord | null;
  verification: VerificationResult | null;
  verifying: boolean;
  onManifest: () => void;
  onVerify: () => void;
}

export function ProvenanceInspector({
  run,
  verification,
  verifying,
  onManifest,
  onVerify,
}: ProvenanceInspectorProps) {
  if (!run) return null;
  const verified = verification
    ? verification.manifest_verified && verification.bytes_verified
    : run.manifest_verified && run.bytes_verified;
  return (
    <section className="provenance-inspector" id="verify" aria-labelledby="provenance-title">
      <div className="integrity-heading">
        <SealIcon />
        <div>
          <p id="provenance-title">{verified ? "Integrity verified" : "Verification incomplete"}</p>
          <span>{run.storage_mode === "b2" ? "Backblaze B2 object" : "Local rehearsal object"}</span>
        </div>
      </div>

      <div className="lineage">
        {run.provenance_steps.map((step) => (
          <div className="lineage-step" key={`${step.index}-${step.model}`}>
            <span className="lineage-index">{String(step.index).padStart(2, "0")}</span>
            <div><strong>{step.provider}</strong><span>{step.model}</span></div>
            <em>{step.status}</em>
          </div>
        ))}
        <div className="lineage-step">
          <span className="lineage-index">{String(run.provenance_steps.length + 1).padStart(2, "0")}</span>
          <div><strong>Integrity seal</strong><span>SHA-256 + canonical manifest</span></div>
          <em>{verified ? "verified" : "check"}</em>
        </div>
      </div>

      <dl className="proof-fields">
        <div><dt>Provider</dt><dd>{run.provider}</dd></div>
        <div><dt>Model</dt><dd>{run.model}</dd></div>
        <div><dt>Asset hash</dt><dd title={run.asset_sha256}>{shortHash(run.asset_sha256)}</dd></div>
        <div><dt>Manifest hash</dt><dd title={run.manifest_hash}>{shortHash(run.manifest_hash)}</dd></div>
        <div className="proof-wide"><dt>Storage key</dt><dd title={run.storage_key}>{run.storage_key}</dd></div>
      </dl>

      <div className="proof-actions">
        <button type="button" onClick={onManifest}>Open manifest</button>
        <button type="button" onClick={onVerify} disabled={verifying}>
          {verifying ? "Verifying…" : "Verify bytes"}
        </button>
      </div>
    </section>
  );
}
