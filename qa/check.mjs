// Visual QA: opens every built site at phone, tablet and desktop widths and fails on
//  - horizontal overflow (anything wider than the screen)
//  - accessibility violations (axe-core, WCAG 2.1 A/AA)
// Usage: node check.mjs <dir with built sites> [shots dir]
import { chromium } from "playwright-core";
import { readFileSync, mkdirSync, existsSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const axeSource = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const root = process.argv[2] ?? "out";
const shots = process.argv[3];
if (shots) mkdirSync(shots, { recursive: true });
const sites = JSON.parse(readFileSync(`${root}/sites.json`, "utf8"));
const WIDTHS = [320, 768, 1440];
const executablePath = process.env.CHROMIUM_PATH || (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);

const browser = await chromium.launch({ executablePath, args: ["--no-sandbox"] });
const failures = [];
const page = await (await browser.newContext({ reducedMotion: "reduce" })).newPage(); // content fully visible

for (const site of sites) {
  const pages = ["index.html"];
  for (const width of WIDTHS) {
    await page.setViewportSize({ width, height: 900 });
    for (const file of pages) {
      await page.goto(`file://${process.cwd()}/${root}/${site}/${file}`);
      await page.waitForTimeout(150);
      const over = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth, out = [];
        document.querySelectorAll("body *").forEach((el) => {
          const r = el.getBoundingClientRect();
          if (r.width > 0 && (r.right > vw + 1 || r.left < -1) && !el.closest("[hidden],dialog,.nav:not(.open),.skip")) {
            const cs = getComputedStyle(el);
            if (cs.position !== "fixed" && cs.visibility !== "hidden") out.push(`${el.tagName.toLowerCase()}.${String(el.className).split(" ")[0]}`);
          }
        });
        return { scroll: document.documentElement.scrollWidth - vw, offenders: [...new Set(out)].slice(0, 5) };
      });
      if (over.scroll > 1) failures.push(`${site} @${width}: page scrolls sideways by ${over.scroll}px (${over.offenders.join(", ")})`);
      if (width === 1440 || width === 320) {
        await page.evaluate(axeSource);
        const res = await page.evaluate(() => axe.run({ runOnly: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"] }));
        // the hostile copy is deliberately ugly; only accessibility rules that are about structure matter there
        for (const v of res.violations) {
          if (v.impact === "minor") continue;
          if (site.includes("--hostile") && v.id === "color-contrast") continue;
          failures.push(`${site} @${width}: ${v.id} (${v.impact}) ${v.nodes.length}x, e.g. ${v.nodes[0].target.join(" ")}`);
        }
      }
      if (shots) await page.screenshot({ path: `${shots}/${site}-${width}.png`, fullPage: true });
    }
  }
}
await browser.close();
if (failures.length) {
  console.error(`\n${failures.length} problem(s):\n- ` + [...new Set(failures)].join("\n- "));
  process.exit(1);
}
console.log(`OK: ${sites.length} sites x ${WIDTHS.length} widths`);
