import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const outDir = join(__dirname, "../public/media");
mkdirSync(outDir, { recursive: true });

const url = process.env.FLA_URL ?? "http://localhost:5173/flywheel-layers.html";
// Build to Flywheel+Triple (~7s), then hold on that final scene
const buildMs = Number(process.env.FLA_BUILD_MS ?? 7500);
const holdMs = Number(process.env.FLA_HOLD_MS ?? 4500);

const browser = await chromium.launch({
  channel: "chrome",
  headless: true,
});

const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  deviceScaleFactor: 2,
  recordVideo: {
    dir: outDir,
    size: { width: 1280, height: 800 },
  },
});

const page = await context.newPage();
await page.goto(url, { waitUntil: "networkidle" });

// One-shot sequence that freezes on Flywheel + Triple Zero (no loop back to Harness)
await page.addStyleTag({
  content: `
    .meta { display: none !important; }
    body { padding: 0 !important; }
    .seq-h { animation: recInH 7.5s ease-in-out 1 forwards !important; }
    .seq-l { animation: recInL 7.5s ease-in-out 1 forwards !important; }
    .seq-g { animation: recInG 7.5s ease-in-out 1 forwards !important; }
    .seq-fly { animation: recInFly 7.5s ease-in-out 1 forwards !important; }
    .seq-tri { animation: recInTri 7.5s ease-in-out 1 forwards !important; }
    .seq-lab { animation: recSoftLab 7.5s ease-in-out 1 forwards !important; }
    .seq-lh { animation: recOnH 7.5s ease-in-out 1 forwards !important; }
    .seq-ll { animation: recOnL 7.5s ease-in-out 1 forwards !important; }
    .seq-lg { animation: recOnG 7.5s ease-in-out 1 forwards !important; }
    .seq-lf { animation: recOnF 7.5s ease-in-out 1 forwards !important; }
    @keyframes recInH {
      0%, 5% { opacity: 0; }
      12%, 100% { opacity: 1; }
    }
    @keyframes recInL {
      0%, 20% { opacity: 0; }
      28%, 100% { opacity: 1; }
    }
    @keyframes recInG {
      0%, 38% { opacity: 0; }
      46%, 100% { opacity: 1; }
    }
    @keyframes recInFly {
      0%, 55% { opacity: 0; }
      65%, 100% { opacity: 1; }
    }
    @keyframes recInTri {
      0%, 68% { opacity: 0; }
      76%, 100% { opacity: 1; }
    }
    @keyframes recSoftLab {
      0%, 60% { opacity: 1; }
      68%, 100% { opacity: 0.28; }
    }
    @keyframes recOnH {
      0%, 8% { opacity: 0.35; }
      12%, 100% { opacity: 1; }
    }
    @keyframes recOnL {
      0%, 24% { opacity: 0.35; }
      28%, 100% { opacity: 1; }
    }
    @keyframes recOnG {
      0%, 42% { opacity: 0.35; }
      46%, 100% { opacity: 1; }
    }
    @keyframes recOnF {
      0%, 62% { opacity: 0.35; }
      70%, 100% { opacity: 1; }
    }
  `,
});

// Restart animations from t=0 after style inject
await page.evaluate(() => {
  const svg = document.querySelector("svg");
  if (!svg) return;
  // Neutralize embedded looping keyframes so page-level rec* animations win
  for (const style of svg.querySelectorAll("style")) {
    style.textContent = "";
  }
  const clone = svg.cloneNode(true);
  svg.replaceWith(clone);
});

await page.waitForTimeout(buildMs + holdMs);

const video = page.video();
await page.close();
const rawPath = video ? await video.path() : null;
await context.close();
await browser.close();

if (!rawPath) {
  console.error("No video recorded");
  process.exit(1);
}
console.log(rawPath);
