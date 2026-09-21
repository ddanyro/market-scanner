const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('tradeville_bridge/content_bridge.js', 'utf8');

function harness() {
  let now = 1000;
  let polls = 0;
  let poll;
  let listener;
  let nextJob = {id: 'first', token: 'one', expiresAt: 2000};
  const posted = [];
  const messages = [];
  const window = {
    location: {origin: 'https://portal.tradeville.ro'},
    addEventListener: (_, fn) => { listener = fn; },
    postMessage: (data) => posted.push(data),
  };
  const context = vm.createContext({window, Date: {now: () => now},
    setInterval: fn => { poll = fn; }, setTimeout: () => 1, clearTimeout() {},
    chrome: {runtime: {sendMessage: async message => {
      messages.push(message);
      if (message.type === 'TRADEVILLE_BRIDGE_POLL') {
        polls++;
        const job = nextJob;
        nextJob = null;
        return {ok: true, job};
      }
      return {ok: true};
    }}}
  });
  vm.runInContext(source, context);
  return {posted, messages, window, context,
    poll: () => poll(), polls: () => polls,
    advance: (value, job) => { now = value; nextJob = job; },
    result: data => listener({source: window, origin: window.location.origin,
      data: {source: 'market-scanner-tradeville-page-v2', type: 'SYNC_RESULT', ...data}}),
  };
}
const settle = () => new Promise(resolve => setImmediate(resolve));

test('expired unanswered job does not block next sync; late results ignored', async () => {
  const h = harness();
  await settle();
  assert.equal(h.posted[0].jobId, 'first');
  await h.poll();
  assert.equal(h.polls(), 1);
  h.advance(2100, {id: 'second', token: 'two', expiresAt: 5000});
  await h.poll();
  assert.equal(h.posted[1].jobId, 'second');
  await h.result({jobId: 'first', token: 'one', ok: true});
  assert.equal(h.messages.filter(x => x.type === 'TRADEVILLE_BRIDGE_RESULT').length, 0);
  await h.result({jobId: 'second', token: 'two', ok: true});
  assert.equal(h.messages.filter(x => x.type === 'TRADEVILLE_BRIDGE_RESULT').length, 1);
  await h.poll();
  assert.equal(h.polls(), 3);
});

test('duplicate injection does not start a second polling loop', async () => {
  const h = harness();
  await settle();
  vm.runInContext(source, h.context);
  await settle();
  assert.equal(h.polls(), 1);
});

test('expired jobs received late are not dispatched to Tradeville', async () => {
  const h = harness();
  await settle();
  h.advance(3000, {id: 'expired', expiresAt: 2500});
  await h.poll();
  assert.equal(h.posted.length, 1);
});
