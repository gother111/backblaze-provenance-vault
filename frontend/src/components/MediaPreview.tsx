import type { RunRecord } from "../types";
import { formatBytes, formatDate } from "../lib/format";

interface MediaPreviewProps {
  run: RunRecord | null;
  loading: boolean;
}

export function MediaPreview({ run, loading }: MediaPreviewProps) {
  return (
    <section className="media-stage" aria-live="polite" aria-busy={loading}>
      {run ? (
        <>
          <div className={`asset-frame format-${run.output_format}`}>
            <img src={`${run.asset_url}?v=${run.asset_sha256.slice(0, 10)}`} alt={`Generated campaign asset: ${run.title}`} />
            {loading && <div className="asset-loading">Sealing provenance…</div>}
          </div>
          <div className="asset-caption">
            <div>
              <h2>{run.title}</h2>
              <p>{run.brief}</p>
            </div>
            <dl>
              <div><dt>Created</dt><dd>{formatDate(run.created_at)}</dd></div>
              <div><dt>File</dt><dd>{formatBytes(run.size_bytes)} · {run.media_type.replace("image/", "")}</dd></div>
            </dl>
          </div>
        </>
      ) : (
        <div className="empty-stage">
          <p>Your sealed campaign asset will appear here.</p>
        </div>
      )}
    </section>
  );
}
