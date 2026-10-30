// Run against the checkout; no production service or browser credentials required.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);
const path = require('node:path');
const { pathToFileURL } = require('node:url');
(async () => {
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage();
    for (const width of [1440, 768, 390, 320]) {
      for (const theme of ['light', 'dark']) {
        await page.setViewportSize({width, height:1000});
        await page.goto(pathToFileURL(path.resolve('index.html')).href);
        await page.evaluate(theme => document.documentElement.dataset.theme = theme, theme);
        await page.evaluate(() => document.fonts.ready);
        const palette = await page.evaluate(() => {
          const root = getComputedStyle(document.documentElement);
          const luminance = hex => {
            const values = hex.match(/[a-f0-9]{2}/gi).map(v => parseInt(v, 16) / 255)
              .map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4);
            return values.reduce((sum, v, i) => sum + v * [.2126, .7152, .0722][i], 0);
          };
          const get = name => root.getPropertyValue(name).trim();
          const ratios = ['--text', '--text-strong', '--muted', '--accent-strong'].flatMap(fg =>
            ['--bg', '--bg-2', '--surface-solid'].map(bg => {
              const a = luminance(get(fg)), b = luminance(get(bg));
              return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
            }));
          const title = document.querySelector('#hero-title');
          const accent = title.querySelector('.hero-accent');
          return {
            minContrast: Math.min(...ratios),
            accented: accent?.textContent === 'structure' &&
              getComputedStyle(accent).color !== getComputedStyle(title).color &&
              Number(getComputedStyle(accent).fontWeight) > Number(getComputedStyle(title).fontWeight),
            colorScheme: root.colorScheme,
            overflow: document.documentElement.scrollWidth > innerWidth,
          };
        });
        if (palette.minContrast < 4.5 || !palette.accented || palette.overflow || palette.colorScheme !== theme)
          throw Error('Palette, hero accent, or readability failed: ' + JSON.stringify(palette));
        await page.locator('.home-hero').screenshot({path:`browser-results/hero-${width}-${theme}.png`});
        const section = page.locator('.featured-demo');
        await section.scrollIntoViewIfNeeded();
        await page.waitForFunction(() => document.querySelector('.featured-demo img').naturalWidth > 0);
        const valid = await section.evaluate(el => {
          const image = el.querySelector('img');
          const rect = el.getBoundingClientRect();
          return document.documentElement.scrollWidth <= innerWidth &&
            rect.left >= 0 && rect.right <= innerWidth && image.naturalWidth === 1080 &&
            el.previousElementSibling.classList.contains('home-hero') &&
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
          const chrome = await page.evaluate(() => ({
            meta: document.querySelector('meta[name="theme-color"]').content,
            bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()
          }));
          if (chrome.meta !== chrome.bg) throw Error('Browser theme color mismatch');
          await toggle.click();
        }
        console.log(`PASS ${width}px ${theme}: image, layout, labels, destinations, keyboard focus, mode icons, logo blend`);
      }
    }
    for (const scheme of ['light', 'dark']) {
      await page.emulateMedia({colorScheme: scheme});
      await page.evaluate(() => { try { localStorage.removeItem('axiom-theme'); } catch (_) {} });
      await page.reload();
      const system = await page.evaluate(() => ({
        explicit: document.documentElement.hasAttribute('data-theme'),
        scheme: getComputedStyle(document.documentElement).colorScheme,
        meta: document.querySelector('meta[name="theme-color"]').content,
        bg: getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()
      }));
      if (system.explicit || system.scheme !== scheme || system.meta !== system.bg)
        throw Error('System theme resolution failed: ' + JSON.stringify(system));
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
