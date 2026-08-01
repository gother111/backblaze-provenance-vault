import type { FormEvent } from "react";

import type { AppConfig, CreateRunPayload, OutputFormat, Palette, ProviderName } from "../types";
import { ArrowIcon } from "./Icons";

interface GeneratorPanelProps {
  value: CreateRunPayload;
  config: AppConfig | null;
  busy: boolean;
  error: string | null;
  onChange: (value: CreateRunPayload) => void;
  onSubmit: () => void;
}

const formats: { value: OutputFormat; label: string }[] = [
  { value: "square", label: "Square" },
  { value: "portrait", label: "Portrait" },
  { value: "landscape", label: "Landscape" },
];

const palettes: { value: Palette; label: string }[] = [
  { value: "clay", label: "Clay" },
  { value: "moss", label: "Moss" },
  { value: "night", label: "Night" },
];

const providers: { value: ProviderName; label: string }[] = [
  { value: "local", label: "Local demo" },
  { value: "gmicloud", label: "GMI Cloud" },
  { value: "openai", label: "OpenAI" },
];

export function GeneratorPanel({
  value,
  config,
  busy,
  error,
  onChange,
  onSubmit,
}: GeneratorPanelProps) {
  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit();
  };
  return (
    <section className="generator-panel" id="new-run" aria-labelledby="generator-heading">
      <div className="generator-intro">
        <h1 id="generator-heading">Generate media.<br />Keep the proof.</h1>
        <p>Create a campaign asset and preserve every step from prompt to final file.</p>
      </div>
      <form onSubmit={submit} className="generator-form">
        <label className="field-label" htmlFor="title">Title</label>
        <input
          id="title"
          value={value.title}
          onChange={(event) => onChange({ ...value, title: event.target.value })}
          minLength={1}
          maxLength={80}
          required
        />

        <label className="field-label" htmlFor="brief">Creative brief</label>
        <textarea
          id="brief"
          value={value.brief}
          onChange={(event) => onChange({ ...value, brief: event.target.value })}
          minLength={12}
          maxLength={1200}
          rows={5}
          required
        />

        <fieldset>
          <legend>Format</legend>
          <div className="segment-control">
            {formats.map((format) => (
              <button
                key={format.value}
                type="button"
                aria-pressed={value.output_format === format.value}
                onClick={() => onChange({ ...value, output_format: format.value })}
              >
                {format.label}
              </button>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Palette</legend>
          <div className="palette-control">
            {palettes.map((palette) => (
              <button
                key={palette.value}
                type="button"
                className={`palette-option palette-${palette.value}`}
                aria-pressed={value.palette === palette.value}
                onClick={() => onChange({ ...value, palette: palette.value })}
              >
                <span aria-hidden="true" />
                {palette.label}
              </button>
            ))}
          </div>
        </fieldset>

        <label className="field-label" htmlFor="provider">Provider</label>
        <select
          id="provider"
          value={value.provider}
          onChange={(event) => onChange({ ...value, provider: event.target.value as ProviderName })}
        >
          {providers.map((provider) => {
            const enabled = provider.value === "local" || Boolean(config?.providers[provider.value]);
            return (
              <option key={provider.value} value={provider.value} disabled={!enabled}>
                {provider.label}{enabled ? "" : " — not configured"}
              </option>
            );
          })}
        </select>

        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="primary-action" type="submit" disabled={busy}>
          <span>{busy ? "Generating & sealing…" : "Generate & seal"}</span>
          <ArrowIcon />
        </button>
        <p className="mode-note">
          {config?.storage_mode === "b2"
            ? "Outputs are hashed and written to the configured B2 bucket."
            : "Local demo exercises Genblaze and verification without claiming a cloud upload."}
        </p>
      </form>
    </section>
  );
}
