#!/bin/bash
echo "=== SDK Function Check ==="
node -e "
try {
  const sdk = require('openclaw/plugin-sdk');
  console.log('createReplyPrefixContext:', typeof sdk.createReplyPrefixContext);
  console.log('Available exports:', Object.keys(sdk).filter(k => k.includes('reply') || k.includes('Reply') || k.includes('prefix') || k.includes('Prefix')).join(', '));
} catch(e) {
  console.log('SDK import error:', e.message);
}
"
echo ""
echo "=== WebSocket Test ==="
node -e "
const ws = new (require('/Users/rreilly/.openclaw/extensions/openclaw-channel-rocketchat/node_modules/ws'))('ws://localhost:3000/websocket');
ws.on('open', () => { console.log('WS: CONNECTED'); ws.close(); process.exit(0); });
ws.on('error', e => { console.log('WS ERROR:', e.message); process.exit(1); });
setTimeout(() => { console.log('WS: TIMEOUT'); process.exit(1); }, 5000);
"
echo ""
echo "=== Plugin Import Test ==="
node -e "
try {
  require('/Users/rreilly/.openclaw/extensions/openclaw-channel-rocketchat/index.ts');
  console.log('Plugin: loaded OK');
} catch(e) {
  console.log('Plugin CRASH:', e.message);
  console.log('Stack:', e.stack?.split('\n').slice(0,5).join('\n'));
}
"
