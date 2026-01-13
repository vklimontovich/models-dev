import { describe, test, expect } from "bun:test";
import { providers, getProviderInfo, getModel } from "../src";

describe("models-dev", () => {
  test("providers() returns array of providers", async () => {
    const all = await providers();
    expect(all.length).toBeGreaterThan(50);
    expect(all[0]).toHaveProperty("id");
    expect(all[0]).toHaveProperty("name");
    expect(all[0]).toHaveProperty("models");
  });

  test("getProviderInfo() returns provider by id", async () => {
    const openai = await getProviderInfo("openai");
    expect(openai.id).toBe("openai");
    expect(openai.name).toBe("OpenAI");
    expect(openai.env).toContain("OPENAI_API_KEY");
  });

  test("getProviderInfo() throws for unknown provider", async () => {
    await expect(getProviderInfo("nonexistent")).rejects.toThrow("Provider not found");
  });

  test("getModel() returns model by id", async () => {
    const gpt4o = await getModel("openai", "gpt-4o");
    expect(gpt4o.id).toBe("gpt-4o");
    expect(gpt4o.modalities.input).toContain("text");
    expect(gpt4o.limit.context).toBeGreaterThan(0);
  });

  test("getModel() throws for unknown model", async () => {
    await expect(getModel("openai", "nonexistent")).rejects.toThrow("Model not found");
  });

  test("known providers exist", async () => {
    const knownProviders = ["openai", "anthropic", "google"];
    for (const id of knownProviders) {
      const provider = await getProviderInfo(id);
      expect(provider.id).toBe(id);
    }
  });

  test("model has required fields", async () => {
    const claude = await getModel("anthropic", "claude-sonnet-4-20250514");
    expect(typeof claude.id).toBe("string");
    expect(typeof claude.name).toBe("string");
    expect(typeof claude.attachment).toBe("boolean");
    expect(typeof claude.reasoning).toBe("boolean");
    expect(typeof claude.tool_call).toBe("boolean");
    expect(typeof claude.release_date).toBe("string");
    expect(Array.isArray(claude.modalities.input)).toBe(true);
    expect(Array.isArray(claude.modalities.output)).toBe(true);
  });
});
