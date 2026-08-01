import type { RunRecord } from "../types";
import { formatDate, shortHash } from "../lib/format";

interface RunLibraryProps {
  runs: RunRecord[];
  selectedId?: string;
  onSelect: (run: RunRecord) => void;
}

export function RunLibrary({ runs, selectedId, onSelect }: RunLibraryProps) {
  return (
    <section className="run-library" id="library" aria-labelledby="library-heading">
      <div className="section-heading">
        <h2 id="library-heading">Immutable runs</h2>
        <p>Every generation keeps its own manifest and content hash.</p>
      </div>
      <div className="run-list">
        {runs.map((run) => (
          <button
            type="button"
            key={run.id}
            className={run.id === selectedId ? "selected" : ""}
            onClick={() => onSelect(run)}
          >
            <span className="run-preview"><img src={run.asset_url} alt="" /></span>
            <span className="run-title"><strong>{run.title}</strong><small>{formatDate(run.created_at)}</small></span>
            <span className="run-provider">{run.provider}<small>{run.model}</small></span>
            <span className="run-hash">{shortHash(run.asset_sha256, 8, 6)}</span>
            <span className="run-state">{run.bytes_verified ? "Verified" : "Check"}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
