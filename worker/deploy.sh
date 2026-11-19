#!/usr/bin/env bash
# Despliega el servidor de avisos en Cloudflare y deja push.json (la dirección del servidor) para la web.
# Necesita los secretos CLOUDFLARE_API_TOKEN y CLOUDFLARE_ACCOUNT_ID en GitHub.
set -euo pipefail
cd "$(dirname "$0")"
W="npx --yes wrangler@4"
TITLE="ironhabits-push"
API="https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID"
cf() { curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json" "$@"; }
# Almacén KV por la API de Cloudflare (acepta también el creado por un intento anterior)
find_id() { cf "$API/storage/kv/namespaces?per_page=100" | jq -r '(.result // [])[] | select(.title=="ironhabits-push" or .title=="worker-ironhabits-push") | .id' | head -1; }
ID=$(find_id || true)
if [ -z "$ID" ]; then
  ID=$(cf -X POST "$API/storage/kv/namespaces" -d "{\"title\":\"$TITLE\"}" | jq -r '.result.id // empty')
fi
[ -n "$ID" ] && [ "$ID" != "null" ] || { echo "No se pudo crear el almacén KV:"; cf "$API/storage/kv/namespaces" | jq -c '.errors'; exit 1; }
sed -i "s/KV_ID/$ID/" wrangler.toml
$W deploy
SUB=$(cf "$API/workers/subdomain" | jq -r '.result.subdomain // empty')
[ -n "$SUB" ] && [ "$SUB" != "null" ] || { echo "Falta el subdominio workers.dev: elige uno en Cloudflare › Workers & Pages"; exit 1; }
echo "{\"url\":\"https://$TITLE.$SUB.workers.dev\"}" > ../push.json
echo "Servidor de avisos: https://$TITLE.$SUB.workers.dev"
