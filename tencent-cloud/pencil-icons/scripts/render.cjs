// Smoke-test the native files in the live Excalidraw editor.
const fs = require('node:fs');
const path = require('node:path');
const runtime = path.join(require('node:os').homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
const { chromium } = require(path.join(runtime, 'playwright'));
const root = path.resolve(__dirname, '..');

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const page = await browser.newPage({ viewport: { width: 1100, height: 1000 }, deviceScaleFactor: 1 });
    const scene = JSON.parse(fs.readFileSync(path.join(root, 'output/icon-sheet.excalidraw'), 'utf8'));
    await page.addInitScript((data) => {
      localStorage.setItem('excalidraw', JSON.stringify(data.elements));
      localStorage.setItem('excalidraw-state', JSON.stringify({ viewBackgroundColor: '#ffffff', theme: 'light', zoom: { value: 1.65 }, scrollX: 140, scrollY: 75 }));
    }, scene);
    await page.goto('https://excalidraw.com', { waitUntil: 'networkidle', timeout: 60000 });
    await page.locator('canvas').first().waitFor();
    await page.keyboard.press('Shift+1');
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(root, 'assets/native-sheet.png') });
    const restored = await page.evaluate(() => JSON.parse(localStorage.getItem('excalidraw')));
    if (restored.length !== scene.elements.length) throw new Error('Element count changed during load');
    // Select a visible server stroke to exercise native grouped selection.
    await page.mouse.click(410, 396);
    await page.waitForTimeout(400);
    const text = await page.locator('body').innerText();
    if (!text.includes('Selected shape actions')) throw new Error('Native selection controls unavailable');
    await page.screenshot({ path: path.join(root, 'assets/native-selection.png') });
    await page.keyboard.press('Escape');
    console.log(`Native editor loaded ${restored.length} editable elements; screenshot saved.`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
