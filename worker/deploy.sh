#!/usr/bin/env bash
# Despliega el servidor de avisos en Cloudflare y deja push.json (la dirección del servidor) para la web.
# Necesita los secretos CLOUDFLARE_API_TOKEN y CLOUDFLARE_ACCOUNT_ID en GitHub.
set -euo pipefail
cd "$(dirname "$0")"
W="npx --yes wrangler@3"
TITLE="ironhabits-push"
find_id() { $W kv namespace list 2>/dev/null | jq -r --arg t "$TITLE" '.[] | select(.title==$t) | .id' | head -1; }
ID=$(find_id || true)
if [ -z "$ID" ]; then
  (cd /tmp && $W kv namespace create "$TITLE" >/dev/null)   # fuera del proyecto: el nombre queda tal cual
  ID=$(find_id)
fi
[ -n "$ID" ] || { echo "No se pudo crear el almacén KV"; exit 1; }
sed -i "s/KV_ID/$ID/" wrangler.toml
$W deploy
SUB=$(curl -fsS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/workers/subdomain" | jq -r '.result.subdomain')
[ -n "$SUB" ] && [ "$SUB" != "null" ] || { echo "Falta el subdominio workers.dev: elige uno en Cloudflare › Workers & Pages"; exit 1; }
echo "{\"url\":\"https://$TITLE.$SUB.workers.dev\"}" > ../push.json
echo "Servidor de avisos: https://$TITLE.$SUB.workers.dev"
