import { gzipSync } from "zlib";

const API_URL = "https://models.dev/api.json";
const OUTPUT_PATH = "./src/data.ts";

async function main() {
  console.log("Fetching data from models.dev...");
  const response = await fetch(API_URL);
  if (!response.ok) {
    throw new Error(`Failed to fetch: ${response.status}`);
  }

  const json = await response.text();
  console.log(`Fetched ${(json.length / 1024).toFixed(1)} KB`);

  console.log("Compressing...");
  const compressed = gzipSync(json);
  const base64 = compressed.toString("base64");
  console.log(`Compressed to ${(base64.length / 1024).toFixed(1)} KB`);

  const content = `// Auto-generated from https://models.dev/api.json
// Do not edit manually

export const DATA = "${base64}";
`;

  await Bun.write(OUTPUT_PATH, content);
  console.log(`Written to ${OUTPUT_PATH}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
