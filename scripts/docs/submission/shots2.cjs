const { chromium } = require('playwright');
const OUT = process.argv[2];
const MID = '9972daab-2c86-459f-9d78-3fe1be4e3280';
const FULL = '2e31fe2f-aee2-4a87-8a2c-675e0e977fab', PART = '608feb20-9304-447c-9b10-9bc677c159be', BATCH='55e60e0c-0197-4475-a752-8d4a09ba5d74';
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1280, height: 800 } }); const p = await c.newPage();
  await p.goto('http://localhost:5173/dashboard/login');
  await p.getByLabel('Merchant ID').fill(MID);
  await p.getByLabel('Email').fill('owner@alpharetail.example');
  await p.getByLabel('Password').fill('FilsPaySeed!2026');
  await p.getByRole('button', { name: 'Continue' }).click();
  const code = await p.locator('code').first().textContent({ timeout: 10000 });
  await p.getByLabel('One-time code').fill(code.trim());
  await p.getByRole('button', { name: 'Verify' }).click();
  await p.waitForURL(/dashboard\/transactions/);
  for (const [n, u] of [['fixed-partial', '/dashboard/transactions/' + PART], ['fixed-full', '/dashboard/transactions/' + FULL],
      ['settlement-list', '/dashboard/settlement'], ['settlement-batch', '/dashboard/settlement/' + BATCH], ['reconciliation', '/dashboard/reconciliation']]) {
    await p.goto('http://localhost:5173' + u); await p.waitForTimeout(2500);
    await p.screenshot({ path: `${OUT}/${n}.png`, fullPage: true });
  }
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
