const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  if (!fs.existsSync('docs/screenshots')) {
    fs.mkdirSync('docs/screenshots', { recursive: true });
  }

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('http://127.0.0.1:3000/');
  await page.screenshot({ path: 'docs/screenshots/landing_desktop.png' });

  await page.setViewportSize({ width: 375, height: 667 });
  await page.screenshot({ path: 'docs/screenshots/landing_mobile.png' });

  await page.setViewportSize({ width: 1280, height: 720 });
  await page.goto('http://127.0.0.1:3000/physics');
  await page.screenshot({ path: 'docs/screenshots/physics_desktop.png' });

  await page.goto('http://127.0.0.1:3000/limits');
  await page.screenshot({ path: 'docs/screenshots/limits_desktop.png' });

  await page.goto('http://127.0.0.1:3000/viewer/F03');
  await page.screenshot({ path: 'docs/screenshots/viewer_desktop.png' });

  await browser.close();
  console.log("Screenshots saved successfully.");
})();
