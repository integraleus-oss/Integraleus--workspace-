import { chromium } from '/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/root-openclaw-workspace/special-tech-astro/node_modules/playwright/index.mjs';

const profile = '/home/stanislav/spectech-chrome-profile';
const context = await chromium.launchPersistentContext(profile, {
  executablePath: '/snap/bin/chromium',
  headless: true,
  args: ['--no-sandbox'],
});
const page = context.pages()[0] || await context.newPage();
await page.goto('https://metrika.yandex.ru/settings?id=110922935', {
  waitUntil: 'domcontentloaded',
  timeout: 60000,
});
await page.waitForTimeout(5000);
console.log(JSON.stringify({
  url: page.url(),
  title: await page.title(),
  body: (await page.locator('body').innerText()).slice(0, 4000),
}, null, 2));
await context.close();
