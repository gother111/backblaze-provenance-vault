import { describe, expect, it } from "vitest";

import { formatBytes, shortHash } from "./format";

describe("format helpers", () => {
  it("preserves short hashes and contracts long hashes", () => {
    expect(shortHash("abc")).toBe("abc");
    expect(shortHash("a".repeat(64))).toBe(`${"a".repeat(12)}…${"a".repeat(8)}`);
  });

  it("formats byte counts for the provenance inspector", () => {
    expect(formatBytes(900)).toBe("900 B");
    expect(formatBytes(2048)).toBe("2.0 KB");
  });
});
