const { chromium } = require('playwright');
const OUT = process.argv[2];
const MID = '9972daab-2c86-459f-9d78-3fe1be4e3280';
const FULL = '2e31fe2f-aee2-4a87-8a2c-675e0e977fab', PART = '608feb20-9304-447c-9b10-9bc677c159be';
async function login(page, base, shot) {
  await page.goto(base + '/dashboard/login');
  await page.getByLabel('Merchant ID').fill(MID);
  await page.getByLabel('Email').fill('owner@alpharetail.example');
  await page.getByLabel('Password').fill('FilsPaySeed!2026');
  await page.getByRole('button', { name: 'Continue' }).click();
  const code = await page.locator('code').first().textContent({ timeout: 10000 });
  if (shot) await page.screenshot({ path: `${OUT}/${shot}.png` });
  await page.getByLabel('One-time code').fill(code.trim());
  await page.getByRole('button', { name: 'Verify' }).click();
  await page.waitForURL(/dashboard\/(transactions|overview)/, { timeout: 15000 });
}
(async () => {
  const b = await chromium.launch();
  const mk = async () => { const c = await b.newContext({ viewport: { width: 1280, height: 800 } }); const p = await c.newPage(); p.on('dialog', d => d.accept()); return p; };
  // BEFORE (old build on 5175)
  let p = await mk();
  await p.goto('http://localhost:5175/'); await p.waitForTimeout(1500); await p.screenshot({ path: `${OUT}/before-root.png` });
  await p.goto('http://localhost:5175/dashbord'); await p.waitForTimeout(1500); await p.screenshot({ path: `${OUT}/before-404.png` });
  await login(p, 'http://localhost:5175');
  await p.goto('http://localhost:5175/dashboard/transactions/' + PART); await p.waitForTimeout(2500);
  await p.screenshot({ path: `${OUT}/before-txn.png`, fullPage: true });
  await p.context().close();
  // AFTER (current build on 5173)
  p = await mk();
  await p.goto('http://localhost:5173/'); await p.waitForTimeout(1500); await p.screenshot({ path: `${OUT}/after-root.png` });
  await p.goto('http://localhost:5173/dashbord'); await p.waitForTimeout(1500); await p.screenshot({ path: `${OUT}/after-404.png` });
  await login(p, 'http://localhost:5173', 'login-otp');
  // partial refund 5.000 BD
  await p.goto('http://localhost:5173/dashboard/transactions/' + PART); await p.waitForTimeout(2000);
  await p.screenshot({ path: `${OUT}/after-txn-before-refund.png`, fullPage: true });
  await p.getByRole('button', { name: 'Refund' }).click();
  await p.getByLabel(/Amount in fils/).fill('5000');
  await p.screenshot({ path: `${OUT}/after-drawer-partial.png`, fullPage: true });
  await p.getByRole('button', { name: 'Refund', exact: true }).click();
  await p.waitForTimeout(2500);
  await p.screenshot({ path: `${OUT}/after-partial-done.png`, fullPage: true });
  // full refund
  await p.goto('http://localhost:5173/dashboard/transactions/' + FULL); await p.waitForTimeout(2000);
  await p.getByRole('button', { name: 'Refund' }).click();
  await p.screenshot({ path: `${OUT}/after-drawer-full.png`, fullPage: true });
  await p.getByRole('button', { name: 'Refund', exact: true }).click();
  await p.waitForTimeout(2500);
  await p.screenshot({ path: `${OUT}/after-full-done.png`, fullPage: true });
  await p.goto('http://localhost:5173/dashboard/transactions'); await p.waitForTimeout(2500);
  await p.screenshot({ path: `${OUT}/after-txn-list.png` });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
