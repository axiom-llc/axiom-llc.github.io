// Run against the checkout; no production service or browser credentials required.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);
const path = require('node:path');
const http = require('node:http');
const fs = require('node:fs/promises');
(async () => {
  // One HTTP origin gives every page the same localStorage, as in production.
  const root = process.cwd();
  const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript',
    '.svg':'image/svg+xml', '.png':'image/png', '.woff2':'font/woff2'};
  const server = http.createServer(async (req, res) => {
    try {
      const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
      let file = path.resolve(root, '.' + pathname);
      if (file !== root && !file.startsWith(root + path.sep)) {
        res.writeHead(403).end(); return;
      }
      if ((await fs.stat(file)).isDirectory()) file = path.join(file, 'index.html');
      const data = await fs.readFile(file);
      res.writeHead(200, {'Content-Type': types[path.extname(file)] || 'application/octet-stream'});
      res.end(data);
    } catch (_) { res.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage();
    for (const width of [1440, 768, 390, 320]) {
      for (const theme of ['light', 'dark']) {
        await page.setViewportSize({width, height:1000});
        await page.goto(origin + '/');
        await page.evaluate(theme => document.documentElement.dataset.theme = theme, theme);
        await page.evaluate(() => document.fonts.ready);
        if (!(await page.evaluate(() => document.fonts.check('16px "Inter"') && document.fonts.check('12px "IBM Plex Mono"')))) throw Error('Local fonts failed to load');
        const accent = await page.locator('#hero-title').evaluate(el => {
          const word = el.querySelector('.hero-accent');
          return word?.textContent === 'structure' &&
            getComputedStyle(word).color !== getComputedStyle(el).color &&
            Number(getComputedStyle(word).fontWeight) > Number(getComputedStyle(el).fontWeight);
        });
        if (!accent) throw Error('Structure accent missing: ' + width + '/' + theme);
        const director = page.locator('.director-feature');
        const directorFits = await director.evaluate(el =>
          [...el.querySelectorAll('article'), el].every(node => {
            const rect = node.getBoundingClientRect();
            return rect.width > 0 && rect.left >= 0 && rect.right <= innerWidth;
          }));
        if (!directorFits) throw Error('Director layout failed: ' + width + '/' + theme);
        await director.screenshot({path:`browser-results/director-home-${width}-${theme}.png`});
        const section = page.locator('.featured-demo');
        await section.scrollIntoViewIfNeeded();
        await page.waitForFunction(() => document.querySelector('.featured-demo img').naturalWidth > 0);
        const valid = await section.evaluate(el => {
          const image = el.querySelector('img');
          const rect = el.getBoundingClientRect();
          return document.documentElement.scrollWidth <= innerWidth &&
            rect.left >= 0 && rect.right <= innerWidth && image.naturalWidth === 1080 &&
            el.previousElementSibling.classList.contains('director-feature') &&
            el.querySelector('h2').id === el.getAttribute('aria-labelledby');
        });
        if (!valid) throw Error(`Layout or accessible label failed: ${width}/${theme}`);
        const demo = page.getByRole('link', {name:'Run the demo'});
        const source = page.getByRole('link', {name:'Read the code', exact:true});
        if (await demo.getAttribute('href') !== 'https://github.com/axiom-llc/axiom-apex#try-the-recovery-demo') throw Error('Wrong demo destination');
        if (!(await source.getAttribute('href')).endsWith('/examples/recovery.py')) throw Error('Wrong source destination');
        await demo.focus();
        await page.keyboard.press('Tab');
        if (!(await source.evaluate(el => el === document.activeElement && getComputedStyle(el).outlineStyle !== 'none'))) throw Error('Keyboard focus failed');
        await section.screenshot({path:`browser-results/apex-${width}-${theme}.png`});
        const toggle = page.locator('[data-theme-toggle]');
        await page.evaluate(() => { try { localStorage.removeItem('axiom-theme'); } catch (_) {} });
        await page.reload();
        const modes = ['system', 'light', 'dark'];
        for (const mode of modes) {
          const actual = await toggle.getAttribute('data-mode');
          if (actual !== mode) throw Error(`Theme mode mismatch: ${width}/${actual}, wanted ${mode}`);
          const icons = await toggle.locator('svg').evaluateAll(elements =>
            elements.map(el => getComputedStyle(el).display !== 'none'));
          const expected = modes.map(x => x === mode);
          if (JSON.stringify(icons) !== JSON.stringify(expected))
            throw Error(`Theme icon mismatch: ${width}/${mode}`);
          const fallback = (await toggle.locator('[data-theme-label]').textContent()).trim();
          if (fallback.toLowerCase() !== mode) throw Error(`Theme label missing: ${mode}`);
          const expectedBlend = mode === 'light' ? 'multiply' : 'normal';
          if (mode !== 'system') {
            const blend = await page.locator('.brand img').evaluate(el => getComputedStyle(el).mixBlendMode);
            if (blend !== expectedBlend) throw Error(`Logo blend mismatch: ${width}/${mode}, got ${blend}`);
            const filter = await page.locator('.brand img').evaluate(el => getComputedStyle(el).filter);
            if (mode === 'light' && filter === 'none') throw Error(`Logo inversion missing: ${width}/${mode}`);
          }
          await toggle.click();
        }
        console.log(`PASS ${width}px ${theme}: image, layout, labels, destinations, keyboard focus, mode icons, logo blend`);
        await page.goto(origin + '/director/');
        await page.evaluate(theme => localStorage.setItem('axiom-theme', theme), theme);
        await page.reload();
        const controlPlane = page.locator('#director');
        const fits = await controlPlane.evaluate(el =>
          [...el.querySelectorAll('article'), el].every(node => {
            const rect = node.getBoundingClientRect();
            return rect.width > 0 && rect.left >= 0 && rect.right <= innerWidth;
          }));
        if (!fits) throw Error('Director page layout failed: ' + width + '/' + theme);
        await controlPlane.screenshot({path:`browser-results/director-page-${width}-${theme}.png`});

      }
    }
    const routes = ['/', '/director/', '/systems/', '/research/', '/engineering/', '/contact/',
      '/engagements/', '/engagements/reliability-control-sprint/', '/case-studies/'];
    for (const deviceTheme of ['light', 'dark']) {
      await page.emulateMedia({colorScheme: deviceTheme});
      for (const mode of ['system', 'light', 'dark']) {
        await page.goto(origin + '/');
        const toggle = page.locator('[data-theme-toggle]');
        for (let clicks = 0; await toggle.getAttribute('data-mode') !== mode; clicks++) {
          if (clicks >= 3) throw Error('Cannot select theme: ' + mode);
          await toggle.click();
        }
        for (const route of routes) {
          await page.goto(origin + route);
          for (const reload of [false, true]) {
            if (reload) await page.reload();
            const saved = await page.evaluate(() => ({
              mode: document.querySelector('[data-theme-toggle]').dataset.mode,
              stored: localStorage.getItem('axiom-theme'),
              explicit: document.documentElement.dataset.theme || 'system',
              background: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim(),
              meta: document.querySelector('meta[name="theme-color"]').content
            }));
            const resolved = mode === 'system' ? deviceTheme : mode;
            const background = resolved === 'dark' ? '#03090e' : '#c5d0d6';
            if (saved.mode !== mode || saved.stored !== mode || saved.explicit !== mode ||
                saved.background !== background || saved.meta !== background)
              throw Error('Theme persistence failed: ' + JSON.stringify({route, mode, deviceTheme, reload, saved}));
          }
        }
        console.log('PASS theme persistence: ' + mode + ', device ' + deviceTheme + ', all 9 pages and reloads');
      }
    }
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error); process.exitCode=1; });
