#!/usr/bin/env node
const fs = require("node:fs/promises");
const path = require("node:path");
let sharp;
try { sharp = require("sharp"); }
catch { sharp = require(process.env.SHARP_MODULE_PATH || path.join(require("node:os").homedir(), ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp")); }

const root = path.resolve(__dirname, "..");
const sourceRoot = path.join(root, "data", "official-svg");
const outputRoot = path.join(root, "data", "rendered");
const reportPath = path.join(root, "data", "render-report.json");
const size = 512;

async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...(await walk(fullPath)));
    } else if (entry.isFile() && entry.name.toLowerCase().endsWith(".svg")) {
      files.push(fullPath);
    }
  }

  return files;
}

function toPosix(value) {
  return value.split(path.sep).join("/");
}

async function renderSvg(sourcePath) {
  const relativeSvg = path.relative(sourceRoot, sourcePath);
  const parsed = path.parse(relativeSvg);
  const outputPath = path.join(outputRoot, parsed.dir, `${parsed.name}.png`);
  await fs.mkdir(path.dirname(outputPath), { recursive: true });

  const base = sharp(sourcePath, { density: 256, unlimited: true }).resize(size, size, {
    fit: "contain",
    background: { r: 0, g: 0, b: 0, alpha: 0 },
  });

  const pngBuffer = await base.clone().png().toBuffer();
  await fs.writeFile(outputPath, pngBuffer);

  const { data, info } = await sharp(pngBuffer).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  let nonTransparent = 0;
  for (let offset = 3; offset < data.length; offset += info.channels) {
    if (data[offset] > 0) {
      nonTransparent += 1;
    }
  }

  const alphaCoverage = nonTransparent / (info.width * info.height);
  return {
    source: toPosix(path.join("data", "official-svg", relativeSvg)),
    output: toPosix(path.relative(root, outputPath)),
    width: info.width,
    height: info.height,
    alphaCoverage: Number(alphaCoverage.toFixed(6)),
    empty: nonTransparent === 0,
  };
}

async function main() {
  await fs.rm(outputRoot, { recursive: true, force: true });
  await fs.mkdir(outputRoot, { recursive: true });

  const sources = (await walk(sourceRoot)).sort((a, b) => a.localeCompare(b));
  const results = [];
  const failures = [];

  for (const sourcePath of sources) {
    try {
      results.push(await renderSvg(sourcePath));
    } catch (error) {
      failures.push({
        source: toPosix(path.join("data", "official-svg", path.relative(sourceRoot, sourcePath))),
        error: error instanceof Error ? error.message : String(error),
      });
    }
  }

  const empty = results.filter((item) => item.empty);
  const report = {
    generatedAt: new Date().toISOString(),
    sourceRoot: "data/official-svg",
    outputRoot: "data/rendered",
    requestedSize: { width: size, height: size },
    total: sources.length,
    succeeded: results.length,
    failed: failures.length,
    empty: empty.length,
    minAlphaCoverage: results.length ? Math.min(...results.map((item) => item.alphaCoverage)) : 0,
    maxAlphaCoverage: results.length ? Math.max(...results.map((item) => item.alphaCoverage)) : 0,
    results,
    failures,
  };

  await fs.writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
  console.log(
    `Rendered ${report.succeeded}/${report.total} SVGs to ${path.relative(process.cwd(), outputRoot)}; failures=${report.failed}; empty=${report.empty}`,
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
