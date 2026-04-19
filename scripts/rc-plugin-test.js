// Test if the RC plugin's monitor can start without crashing
// Run: node ~/.openclaw/workspace/scripts/rc-plugin-test.js

const WebSocket = require('/Users/rreilly/.openclaw/extensions/openclaw-channel-rocketchat/node_modules/ws');

const baseUrl = 'http://localhost:3000';
const userId = 'NyTi2Ktzzv4Q6hDoL';
const authToken = 'oeGEa58-35WlCJTkWd8BcqVWoIPOTMkkMedpCIqEPgQ';

console.log('Step 1: Testing HTTP...');
fetch(`${baseUrl}/api/v1/me`, {
  headers: { 'X-Auth-Token': authToken, 'X-User-Id': userId }
}).then(r => r.json()).then(d => {
  console.log('  HTTP OK, user:', d.username, 'status:', d.status);
  
  console.log('Step 2: Testing WebSocket...');
  const wsUrl = baseUrl.replace(/^http/, 'ws') + '/websocket';
  console.log('  Connecting to:', wsUrl);
  
  const ws = new WebSocket(wsUrl);
  
  ws.on('open', () => {
    console.log('  WS: Connected, sending DDP connect...');
    ws.send(JSON.stringify({msg: 'connect', version: '1', support: ['1']}));
  });
  
  ws.on('message', (data) => {
    const msg = JSON.parse(data.toString());
    console.log('  WS MSG:', msg.msg, msg.session ? `session=${msg.session}` : '');
    
    if (msg.msg === 'connected') {
      console.log('  DDP: Connected! Logging in...');
      ws.send(JSON.stringify({
        msg: 'method',
        method: 'login',
        id: '1',
        params: [{ resume: authToken }]
      }));
    }
    
    if (msg.msg === 'result' && msg.id === '1') {
      if (msg.error) {
        console.log('  LOGIN FAILED:', msg.error.message);
      } else {
        console.log('  LOGIN OK!');
        console.log('  Step 3: Subscribing to GENERAL...');
        ws.send(JSON.stringify({
          msg: 'sub',
          id: '2',
          name: 'stream-room-messages',
          params: ['GENERAL', false]
        }));
      }
    }
    
    if (msg.msg === 'ready') {
      console.log('  SUBSCRIBED! Ready to receive messages.');
      console.log('');
      console.log('=== ALL TESTS PASSED ===');
      console.log('WebSocket + DDP + Auth + Subscription all working.');
      console.log('The issue is in the OpenClaw plugin startup, not in RC.');
      ws.close();
      process.exit(0);
    }
    
    if (msg.msg === 'nosub') {
      console.log('  SUBSCRIPTION FAILED for id:', msg.id);
      ws.close();
      process.exit(1);
    }
  });
  
  ws.on('error', (e) => {
    console.log('  WS ERROR:', e.message);
    process.exit(1);
  });
  
  ws.on('close', (code, reason) => {
    console.log('  WS CLOSED:', code, reason?.toString());
  });
  
  setTimeout(() => { console.log('  TIMEOUT (10s)'); process.exit(1); }, 10000);
  
}).catch(e => {
  console.log('  HTTP ERROR:', e.message);
  process.exit(1);
});
