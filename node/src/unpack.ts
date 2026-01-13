import type { ProvidersData } from "./types";

const isNode =
  typeof process !== "undefined" &&
  process.versions != null &&
  process.versions.node != null;

export async function unpack(base64: string): Promise<ProvidersData> {
  if (isNode) {
    const { gunzipSync } = await import("zlib");
    const buffer = Buffer.from(base64, "base64");
    const json = gunzipSync(buffer).toString("utf-8");
    return JSON.parse(json);
  }

  // Browser - use DecompressionStream
  const binary = atob(base64);
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  const stream = new DecompressionStream("gzip");
  const writer = stream.writable.getWriter();
  writer.write(bytes);
  writer.close();
  const decompressed = await new Response(stream.readable).text();
  return JSON.parse(decompressed);
}
