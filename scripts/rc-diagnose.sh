#!/bin/bash
# Rocket.Chat WebSocket Diagnostic
echo "=== RC WebSocket Diagnostic ==="
echo "Time: $(date)"
echo ""

echo "1. Docker status:"
docker ps --filter "name=rocket" --format "  {{.Names}}: {{.Status}}"
echo ""

echo "2. RC HTTP test:"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
echo "  HTTP status: $HTTP_CODE"
echo ""

echo "3. RC WebSocket upgrade test:"
WS_RESULT=$(curl -s -i --max-time 3 \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  http://localhost:3000/websocket 2>&1 | head -3)
echo "  $WS_RESULT"
echo ""

echo "4. Node WebSocket test:"
node -e "
const ws = new (require('/Users/rreilly/.openclaw/extensions/openclaw-channel-rocketchat/node_modules/ws'))('ws://localhost:3000/websocket');
ws.on('open', () => { console.log('  WS: CONNECTED OK'); ws.close(); process.exit(0); });
ws.on('error', e => { console.log('  WS ERROR:', e.message); process.exit(1); });
setTimeout(() => { console.log('  WS: TIMEOUT (5s)'); process.exit(1); }, 5000);
"
echo ""

echo "5. Gateway RC logs (last 10):"
tail -10 /Users/rreilly/.openclaw/logs/gateway.log | grep -i rocket
echo ""

echo "6. Docker RC logs (last 10):"
docker logs --tail 10 rocketchat 2>&1
echo ""

echo "7. RC health endpoint:"
curl -s http://localhost:3000/health 2>&1 | head -3
echo ""

echo "=== Done ==="
