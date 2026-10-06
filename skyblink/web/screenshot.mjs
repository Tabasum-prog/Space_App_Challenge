import { chromium } from 'playwright';
import fs from 'fs';

(async () => {
    fs.mkdirSync('../docs/screenshots', { recursive: true });
    
    const browser = await chromium.launch();
    const page = await browser.newPage();
    
    // Viewer Blink Mode
    await page.goto('http://localhost:3000/viewer/F_COMET?mode=blink');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '../docs/screenshots/viewer_blink.png' });
    
    // Viewer Swipe Mode
    await page.goto('http://localhost:3000/viewer/F_COMET?mode=swipe');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '../docs/screenshots/viewer_swipe.png' });
    
    // Viewer Diff Mode
    await page.goto('http://localhost:3000/viewer/F_COMET?mode=difference');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '../docs/screenshots/viewer_diff.png' });
    
    // Detective Mode with candidate
    await page.goto('http://localhost:3000/viewer/F_COMET?mode=blink&viewMode=detective&candidate=C001');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '../docs/screenshots/detective_mode.png' });
    
    await browser.close();
    console.log("Screenshots captured successfully.");
})();
