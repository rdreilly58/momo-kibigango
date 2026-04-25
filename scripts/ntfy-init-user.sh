#!/bin/bash
# scripts/ntfy-init-user.sh
#
# One-time bootstrap: creates the ntfy user account inside the container.
# Run this ONCE after the first `docker compose up -d` in config/ntfy/.
#
# Prerequisites:
#   NTFY_USER and NTFY_PASS must be exported (sourced from ~/.openclaw/.env).
#
# Usage:
#   source ~/.openclaw/.env
#   scripts/ntfy-init-user.sh

set -Eeuo pipefail

ENV_FILE="${HOME}/.openclaw/.env"
if [[ -f "$ENV_FILE" ]]; then
    set -a; source "$ENV_FILE"; set +a
fi

: "${NTFY_USER:?NTFY_USER must be set in ~/.openclaw/.env}"
: "${NTFY_PASS:?NTFY_PASS must be set in ~/.openclaw/.env}"

CONTAINER="openclaw-ntfy"

echo "Waiting for container ${CONTAINER} to be healthy..."
for i in $(seq 1 20); do
    STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null || echo "missing")
    if [[ "$STATUS" == "healthy" ]]; then
        break
    fi
    echo "  attempt ${i}/20 — status: ${STATUS}"
    sleep 3
done

echo "Creating ntfy user '${NTFY_USER}'..."
# ntfy user add --role=admin creates the user and sets the password
docker exec -i "$CONTAINER" ntfy user add --ignore-exists --role=admin "${NTFY_USER}" <<EOF
${NTFY_PASS}
${NTFY_PASS}
EOF

echo "User created. Verifying..."
docker exec "$CONTAINER" ntfy user list

echo ""
echo "Done. Test with:"
echo "  curl -u '${NTFY_USER}:${NTFY_PASS}' -d 'hello' http://127.0.0.1:8085/openclaw"
