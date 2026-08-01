import { useEffect, useRef } from "react";

import { CloseIcon } from "./Icons";

interface ManifestDialogProps {
  manifest: Record<string, unknown> | null;
  onClose: () => void;
}

export function ManifestDialog({ manifest, onClose }: ManifestDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    if (manifest) dialogRef.current?.showModal();
    else dialogRef.current?.close();
  }, [manifest]);
  return (
    <dialog ref={dialogRef} className="manifest-dialog" onClose={onClose}>
      <div className="dialog-heading">
        <div><h2>Canonical manifest</h2><p>Generated and verified by Genblaze.</p></div>
        <button type="button" onClick={onClose} aria-label="Close manifest"><CloseIcon /></button>
      </div>
      <pre>{manifest ? JSON.stringify(manifest, null, 2) : ""}</pre>
    </dialog>
  );
}
