const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

async function collect(failDetails = false) {
  const sent = [];
  let listener, finish;
  const done = new Promise(resolve => { finish = resolve; });
  const window = {
    location: {origin: 'https://portal.tradeville.ro'},
    localStorage: {getItem: key => JSON.stringify(key === 'usersitoken'
      ? {coduser: 'fixture', idp: 'fixture'} : {persoana: 'A'})},
    addEventListener: (_, fn) => { listener = fn; },
    postMessage: data => finish(data),
  };
  class Socket {
    constructor() { this.handlers = {}; this.person = 'A'; }
    addEventListener(type, fn) {
      this.handlers[type] = fn;
      if (type === 'open') queueMicrotask(fn);
    }
    send(raw) {
      const req = JSON.parse(raw);
      if (req.cmd === 'persoana') this.person = req.persoana;
      sent.push({person: this.person, ...req});
      let data = [];
      if (req.cmd === 'persoana') data = [{persoana:'A',nume:'Personal'}, {persoana:'B',nume:'Company'}];
      if (req.cmd === 'portof') data = [{simbol:'TVBETETF',sold:10}];
      if (req.cmd === 'ordineActive') data = [{idord:'C1',simbol:'TVBETETF',csauv:'V',tipord:'P',cant:-10,pret:0}];
      if (req.cmd === 'ordine') data = [{idord:'C1',simbol:'TVBETETF',obs:this.person === 'A' ? 'P<54' : 'P<55'}];
      if (req.cmd === 'activit') data = [{simbol:'TVBETETF',op:'cump',cant:10,data:'2026-09-01T00:00:00Z'}];
      if (req.cmd === 'graf_pers_brut') data = [{data:'2026-10-08',nav:100}];
      const fail = failDetails && req.cmd === 'ordine';
      queueMicrotask(() => this.handlers.message({data:JSON.stringify({cmd:req.cmd,prm:req.prm,OK:fail?0:1,err:fail?'unavailable':null,data})}));
    }
    close() {}
  }
  const context = vm.createContext({window, document:{cookie:'legatura=fixture'},
    WebSocket:Socket, Date, Intl, setTimeout, clearTimeout});
  vm.runInContext(fs.readFileSync('tradeville_bridge/page_ws_client.js','utf8'), context);
  listener({source:window,origin:window.location.origin,data:{
    source:'market-scanner-tradeville-extension-v2',type:'SYNC',historyStart:'2025-09-16'}});
  return {result:await done,sent};
}

test('reads order details and complete activity under the correct account', async () => {
  const {result,sent} = await collect();
  assert.equal(result.ok,true);
  assert.equal(result.snapshot.accounts[0].order_details[0].obs,'P<54');
  assert.equal(result.snapshot.accounts[1].order_details[0].obs,'P<55');
  assert.equal(result.snapshot.accounts[0].transactions[0].op,'cump');
  const activity = sent.filter(x=>x.cmd === 'activit');
  assert.equal(activity.length,2);
  assert.equal(activity[0].prm.opt,'toate');
  assert.equal(activity[0].prm.d1,'2025-09-16');
  assert.deepEqual([...new Set(sent.map(x=>x.cmd))].sort(),
    ['activit','cursbnr','get_Sume_inDecontare','graf_pers_brut','infocont','login','ordine','ordineActive','persoana','portof'].sort());
});

test('optional detail failure preserves positions and reports missing enrichment', async () => {
  const {result} = await collect(true);
  assert.equal(result.ok,true);
  assert.equal(result.snapshot.accounts[0].portfolio[0].sold,10);
  assert.equal(result.snapshot.accounts[0].order_details.length,0);
  assert.ok(result.snapshot.accounts[0].enrichment_errors.length > 0);
});
