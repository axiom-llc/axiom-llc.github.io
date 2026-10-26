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
        console.log(`PASS ${width}px ${theme}: image, layout, labels, destinations, keyboard focus`);
      }
    }
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });
