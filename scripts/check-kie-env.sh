#!/usr/bin/env bash
# Quick connectivity check for kie.ai (loads .env if present). Does not print secrets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT/.env"
  set +a
fi
BASE="${KIE_BASE_URL:-https://api.kie.ai}"

if [[ -z "${KIE_API_KEY:-}" ]] || [[ "$KIE_API_KEY" == "your_kie_api_key_here" ]]; then
  echo "No valid credentials found. Edit .env and set KIE_API_KEY." >&2
  echo "Create a key at: https://kie.ai/api-key" >&2
  exit 1
fi

# kie.ai doesn't expose a public unauthenticated health endpoint. Instead we
# fire an intentionally-empty POST to /api/v1/jobs/createTask: the server
# validates the Bearer token before validating the body, so a bad key
# returns 401, a good key returns 400/422 (empty body rejected). Either of
# those latter codes confirms the key works.
code="$(curl -sS -o /dev/null -w "%{http_code}" \
  -X POST "$BASE/api/v1/jobs/createTask" \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' || echo "000")"

echo "POST /api/v1/jobs/createTask (probe) → HTTP $code"

case "$code" in
  401)
    echo "Auth failed (HTTP 401). Check KIE_API_KEY in .env." >&2
    exit 1
    ;;
  200|400|402|422)
    # 400/422 = key accepted, body rejected (expected for the empty probe).
    # 402 = payment required (out of credits, but key is valid).
    # 200 = unlikely for an empty body, but key valid.
    echo "OK — connection verified."
    ;;
  *)
    echo "Unexpected response (HTTP $code). Check your network or base URL." >&2
    exit 1
    ;;
esac
