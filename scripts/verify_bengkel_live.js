const fs = require('fs');

async function testBengkelVercel() {
  const targetsRes = await fetch('http://127.0.0.1:9222/json');
  const targets = await targetsRes.json();
  const pageTarget = targets.find(t => t.type === 'page' && !t.url.startsWith('chrome-untrusted:'));
  if (!pageTarget) return;

  const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
  let msgId = 1;
  const pending = new Map();
  ws.onmessage = (e) => {
    const d = JSON.parse(e.data);
    if (d.id && pending.has(d.id)) {
      pending.get(d.id).resolve(d.result);
      pending.delete(d.id);
    }
  };
  await new Promise(r => ws.onopen = r);
  function send(method, params = {}) {
    return new Promise(res => {
      const id = msgId++;
      pending.set(id, { resolve: res });
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await send('Page.enable');
  await send('Runtime.enable');

  console.log('Navigating to https://dashboard-bengkel-kiaracondong.vercel.app/...');
  await send('Page.navigate', { url: 'https://dashboard-bengkel-kiaracondong.vercel.app/' });
  await new Promise(r => setTimeout(r, 4000));

  const state = await send('Runtime.evaluate', {
    expression: `({
      url: window.location.href,
      title: document.title,
      kpis: document.querySelectorAll('.kpi-card, .metric-card, .card').length
    })`,
    returnByValue: true
  });
  console.log('Live Bengkel Dashboard State:', state.result.value);

  const scr = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('screenshot_bengkel_vercel_live.png', Buffer.from(scr.data, 'base64'));
  console.log('Saved screenshot_bengkel_vercel_live.png');

  ws.close();
}

testBengkelVercel().catch(console.error);
