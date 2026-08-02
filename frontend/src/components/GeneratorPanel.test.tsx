import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import type { AppConfig, CreateRunPayload } from "../types";
import { GeneratorPanel } from "./GeneratorPanel";

const form: CreateRunPayload = {
  title: "Launch poster",
  brief: "Create a launch poster with a clean provenance trail.",
  output_format: "square",
  palette: "clay",
  provider: "local",
};

const localConfig: AppConfig = {
  default_provider: "local",
  storage_mode: "local",
  providers: {
    local: true,
    gmicloud: false,
    openai: false,
    nvidia: false,
  },
  b2: {
    configured: false,
    bucket: null,
    region: null,
  },
};

function render(config: AppConfig, value: CreateRunPayload = form) {
  return renderToStaticMarkup(
    <GeneratorPanel
      value={value}
      config={config}
      busy={false}
      error={null}
      onChange={vi.fn()}
      onSubmit={vi.fn()}
    />,
  );
}

describe("GeneratorPanel provider controls", () => {
  it("shows NVIDIA as unavailable when its key is not configured", () => {
    const markup = render(localConfig);

    expect(markup).toContain('value="nvidia" disabled="">NVIDIA NIM — not configured</option>');
    expect(markup).toContain(
      "Local demo exercises Genblaze and verification without claiming a cloud upload.",
    );
  });

  it("enables and selects NVIDIA only when configuration reports it ready", () => {
    const config: AppConfig = {
      ...localConfig,
      storage_mode: "b2",
      providers: { ...localConfig.providers, nvidia: true },
      b2: { configured: true, bucket: "competition-demo", region: "us-west-004" },
    };
    const markup = render(config, { ...form, provider: "nvidia" });

    expect(markup).toContain('value="nvidia" selected="">NVIDIA NIM</option>');
    expect(markup).toContain("Outputs are hashed and written to the configured B2 bucket.");
  });
});
