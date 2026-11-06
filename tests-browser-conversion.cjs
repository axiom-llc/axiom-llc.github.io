// Checkout-local browser QA. Test dependencies are isolated to the CI runner.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs/promises');
const assert = require('node:assert/strict');

(async () => {
  const root = process.cwd();
  const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript',
    '.svg':'image/svg+xml', '.png':'image/png', '.woff2':'font/woff2'};
  const server = http.createServer(async (req, res) => {
    try {
      let file = path.resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname));
      if (file !== root && !file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
      if ((await fs.stat(file)).isDirectory()) file = path.join(file, 'index.html');
      res.writeHead(200, {'Content-Type':types[path.extname(file)] || 'application/octet-stream'});
      res.end(await fs.readFile(file));
    } catch { res.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({headless:true});
  const routes = ['/', '/director/', '/systems/', '/research/', '/engineering/',
    '/contact/', '/engagements/', '/engagements/reliability-control-sprint/', '/case-studies/'];
  const observations = [];
  try {
    await fs.mkdir('browser-results', {recursive:true});
    for (const width of [320, 390, 768, 1024, 1440]) {
      for (const colorScheme of ['light', 'dark']) {
        const context = await browser.newContext({viewport:{width,height:1000}, colorScheme});
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', error => errors.push(String(error)));
        for (const route of routes) {
          await page.goto(origin + route);
          await page.evaluate(() => document.fonts.ready);
          const layout = await page.evaluate(() => ({
            width:innerWidth, scroll:document.documentElement.scrollWidth,
            brokenImages:[...document.images].filter(img => img.complete && !img.naturalWidth).map(img => img.getAttribute('src')),
            overflow:[...document.querySelectorAll('main, main section, .package-card')].filter(el => {
              const r = el.getBoundingClientRect(); return r.left < -1 || r.right > innerWidth + 1;
            }).map(el => el.id || el.className)
          }));
          assert.ok(layout.scroll <= width + 1, JSON.stringify({route,width,colorScheme,layout}));
          assert.deepEqual(layout.overflow, [], JSON.stringify({route,width,colorScheme,layout}));
          assert.deepEqual(layout.brokenImages, [], JSON.stringify({route,width,colorScheme,layout}));
          const nav = page.locator('.site-header nav');
          if (width <= 960) {
            const toggle = page.locator('[data-nav-toggle]');
            assert.equal(await nav.isVisible(), false);
            await toggle.click();
            assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
            assert.equal(await nav.isVisible(), true);
            await nav.getByRole('link', {name:'Director',exact:true}).focus();
            await page.keyboard.press('Escape');
            assert.equal(await nav.isVisible(), false);
            assert.equal(await toggle.evaluate(el => el === document.activeElement), true);
            const bounds = await toggle.boundingBox();
            assert.ok(bounds.width >= 44 && bounds.height >= 44);
          } else assert.equal(await nav.isVisible(), true);
          if (route === '/') {
            const links = page.locator('.hero-bottom .actions a');
            assert.deepEqual(await links.allTextContents().then(items => items.map(x => x.replace(/[→↗]/g,'').trim())),
              ['Explore systems','Meet Director','Agent Reliability Packages']);
            assert.ok(await page.locator('.director-cta').isVisible());
          }
          if (route === '/engagements/reliability-control-sprint/') {
            assert.equal(await page.locator('.package-card').count(), 4);
            const buttons = page.locator('.package-card a.button');
            for (let i=0;i<4;i++) {
              const url = new URL(await buttons.nth(i).getAttribute('href'));
              assert.equal(url.pathname, 'axiom.co@proton.me');
              assert.ok(url.searchParams.get('subject'));
            }
            const question = page.getByText('Can we use our existing LLM and infrastructure?', {exact:true});
            await question.click();
            assert.equal(await question.locator('..').getAttribute('open'), '');
            await page.evaluate(() => {
              if (document.activeElement instanceof HTMLElement) document.activeElement.blur();
              window.scrollTo({top:0,left:0,behavior:'instant'});
            });
            await page.screenshot({path:`browser-results/packages-${width}-${colorScheme}.png`,fullPage:true});
          }
          observations.push({route,width,colorScheme,layout:'pass',navigation:'pass'});
        }
        assert.deepEqual(errors, []);
        await context.close();
      }
    }
    // A 1440px display at 200% zoom has a 720 CSS-pixel layout viewport.
    const reflow = await browser.newContext({viewport:{width:720,height:500},deviceScaleFactor:2});
    const reflowPage = await reflow.newPage();
    for (const route of routes) {
      await reflowPage.goto(origin+route);
      assert.ok(await reflowPage.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    }
    await reflow.close();
    for (const width of [320,1440]) {
      const context = await browser.newContext({viewport:{width,height:1000},javaScriptEnabled:false});
      const page = await context.newPage();
      for (const route of routes) {
        await page.goto(origin+route);
        const links = page.locator('.site-header nav a');
        for (let i=0;i<await links.count();i++) assert.ok(await links.nth(i).isVisible());
        assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      }
      await context.close();
    }
    await fs.writeFile('browser-results/conversion-checks.json', JSON.stringify({
      scope:'checkout-local Chromium; not field performance evidence',
      observations, reflow:'720 CSS px at device scale 2, all 9 routes',
      noJavaScript:'320px and 1440px, all 9 routes'
    },null,2)+'\n');
    console.log('PASS conversion QA: 90 route/width/theme cases; menu, focus, packages, images, 2x reflow and no-JavaScript navigation');
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
