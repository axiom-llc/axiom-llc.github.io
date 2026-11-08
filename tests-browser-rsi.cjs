// Paired real Chromium DOM interactions; never modifies site source or deploys.
const {chromium} = require(process.env.PLAYWRIGHT_MODULE);
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const http = require('node:http');
const assert = require('node:assert/strict');

(async () => {
  const root = process.cwd();
  fs.mkdirSync('browser-results', {recursive:true});
  const proposalPath = path.join(root, 'browser-results', 'rsi-candidates.json');
  execFileSync('python', ['-m', 'rsi.native', '--output', proposalPath],
               {cwd:root, stdio:'pipe'});
  const proposal = JSON.parse(fs.readFileSync(proposalPath,'utf8'));
  assert.equal(proposal.status,'GENERATED');
  assert.equal(proposal.candidates.length,1);
  assert.equal(proposal.mutation_authority,false);
  const record = proposal.candidates[0];
  const rule = JSON.parse(fs.readFileSync('rsi/generators.json','utf8')).rules[0];
  const original = fs.readFileSync('theme.js','utf8');
  assert.equal(original.split(rule.before).length,2,'source anchor must be unique');
  const candidate = original.replace(rule.before,rule.after);
  const digest = value => crypto.createHash('sha256').update(value).digest('hex');
  assert.equal(record.source_sha256,digest(original));
  assert.equal(record.candidate_sha256,digest(candidate));
  assert.equal(record.mutation_authority,false);

  const server = http.createServer((req,res) => {
    try {
      let file = path.resolve(root,'.' + decodeURIComponent(new URL(req.url,'http://local').pathname));
      if (file !== root && !file.startsWith(root + path.sep)) {
        res.writeHead(403).end(); return;
      }
      if (fs.statSync(file).isDirectory()) file = path.join(file,'index.html');
      const extension = path.extname(file);
      const types = {'.html':'text/html','.js':'text/javascript','.css':'text/css',
        '.svg':'image/svg+xml','.woff2':'font/woff2','.png':'image/png'};
      res.writeHead(200,{'Content-Type':types[extension] || 'application/octet-stream'});
      res.end(fs.readFileSync(file));
    } catch {res.writeHead(404).end();}
  });
  await new Promise(resolve => server.listen(0,'127.0.0.1',resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({headless:true});
  const operations = 900;
  const samples = [];
  async function exercise(variant,width,routeName,colorScheme) {
    const context = await browser.newContext({viewport:{width,height:900},colorScheme});
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror',error => errors.push(String(error)));
    await page.route('**/theme.js',handler => handler.fulfill({
      status:200,contentType:'text/javascript',
      body:variant === 'baseline' ? original : candidate
    }));
    await page.goto(origin + routeName,{waitUntil:'load'});
    const reading = await page.evaluate(count => {
      const button = document.querySelector('[data-theme-toggle]');
      if (!button || button.dataset.mode !== 'system') throw Error('missing theme toggle');
      const start = performance.now();
      for (let i=0;i<count;i++) button.click();
      const elapsed = performance.now() - start;
      const snapshot = () => ({
        mode:button.dataset.mode,
        label:button.querySelector('[data-theme-label]').textContent,
        aria:button.getAttribute('aria-label'),
        title:button.getAttribute('title'),
        stored:localStorage.getItem('axiom-theme'),
        root:document.documentElement.getAttribute('data-theme'),
        meta:document.querySelector('meta[name="theme-color"]').content
      });
      const states = [snapshot()];
      for (let i=0;i<3;i++) {button.click();states.push(snapshot());}
      return {nsPerOp:elapsed * 1e6 / count,states};
    },operations);
    assert.deepEqual(reading.states.map(x=>x.mode),['system','light','dark','system']);
    assert.deepEqual(reading.states.map(x=>x.label),['System','Light','Dark','System']);
    for (const state of reading.states) {
      assert.equal(state.stored,state.mode);
      assert.equal(state.root,state.mode === 'system' ? null : state.mode);
      assert.ok(state.aria.includes('Theme: ' + state.mode + '.'));
    }
    await page.emulateMedia({colorScheme:'dark'});
    await page.waitForFunction(() => document.querySelector('meta[name="theme-color"]').content === '#03090e');
    const dark = await page.locator('meta[name="theme-color"]').getAttribute('content');
    await page.emulateMedia({colorScheme:'light'});
    await page.waitForFunction(() => document.querySelector('meta[name="theme-color"]').content === '#c5d0d6');
    const light = await page.locator('meta[name="theme-color"]').getAttribute('content');
    assert.deepEqual(errors,[]);
    await context.close();
    return {nsPerOp:reading.nsPerOp,states:reading.states,dark,light};
  }
  try {
    const routes = ['/','/director/','/engagements/reliability-control-sprint/'];
    for (let i=0;i<11;i++) {
      const width = i%2 ? 390 : 1440;
      const route = routes[i%routes.length];
      const colorScheme = i%2 ? 'dark' : 'light';
      const order = i%2 ? ['candidate','baseline'] : ['baseline','candidate'];
      const pair = {};
      for (const variant of order)
        pair[variant] = await exercise(variant,width,route,colorScheme);
      assert.deepEqual(pair.baseline.states,pair.candidate.states);
      assert.equal(pair.baseline.dark,pair.candidate.dark);
      assert.equal(pair.baseline.light,pair.candidate.light);
      samples.push({width,route,colorScheme,
        baseline_ns_per_op:pair.baseline.nsPerOp,
        candidate_ns_per_op:pair.candidate.nsPerOp,
        behavior_equivalent:true});
    }
    const receipt = {schema:'axiom-site-rsi/browser-v1',browser:'chromium',
      source_revision:proposal.source_revision,
      source_sha256:record.source_sha256,candidate_sha256:record.candidate_sha256,
      operations_per_sample:operations,samples,
      quality_equivalent:true,production_representative:false,
      promotion_authorized:false,
      scope:'Paired local synthetic Chromium DOM interactions on actual site routes; no production or field measurement'};
    fs.writeFileSync('browser-results/rsi-browser-benchmark.json',
                     JSON.stringify(receipt,null,2)+'\n');
    assert.equal(fs.readFileSync('theme.js','utf8'),original,'source modified');
    console.log('PASS Chromium: 11 paired samples, 900 operations/variant, mobile/desktop and dark/light browser interactions; promotion disabled');
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => {console.error(error);process.exitCode=1;});
