import * as esbuild from "esbuild";
import { readFileSync, writeFileSync, cpSync } from "fs";

const shared: esbuild.BuildOptions = {
  entryPoints: ["./src/index.ts"],
  bundle: true,
  platform: "neutral",
  target: "es2022",
  external: ["zlib"],
};

async function build() {
  console.log("Building ESM...");
  await esbuild.build({
    ...shared,
    format: "esm",
    outfile: "./dist/index.js",
  });

  console.log("Building CJS...");
  await esbuild.build({
    ...shared,
    format: "cjs",
    outfile: "./dist/index.cjs",
  });

  console.log("Generating declarations...");
  const proc = Bun.spawn(["bun", "tsc", "--emitDeclarationOnly"], {
    stdout: "inherit",
    stderr: "inherit",
  });
  await proc.exited;

  // Copy .d.ts to .d.cts for CJS
  cpSync("./dist/index.d.ts", "./dist/index.d.cts");
  cpSync("./dist/types.d.ts", "./dist/types.d.cts");
  cpSync("./dist/unpack.d.ts", "./dist/unpack.d.cts");
  cpSync("./dist/data.d.ts", "./dist/data.d.cts");

  console.log("Done!");
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
