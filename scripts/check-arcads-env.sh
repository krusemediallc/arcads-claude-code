#!/usr/bin/env bash
# Quick connectivity check (loads .env if present). Does not print secrets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "$ROOT/.env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ROOT/.env"
  set +a
fi
BASE="${ARCADS_BASE_URL:-https://external-api.arcads.ai}"

if [[ -n "${ARCADS_BASIC_AUTH:-}" ]] && [[ "$ARCADS_BASIC_AUTH" != *"your_base64_encoded_credentials_here"* ]]; then
  AUTH_HEADER="Authorization: $ARCADS_BASIC_AUTH"
elif [[ -n "${ARCADS_API_KEY:-}" ]] && [[ "$ARCADS_API_KEY" != "your_key_here" ]]; then
  AUTH_HEADER="Authorization: Basic $(printf '%s:' "$ARCADS_API_KEY" | base64)"
else
  echo "No valid credentials found. Edit .env with your Arcads Basic auth header." >&2
  echo "Find it at: https://app.arcads.ai/settings/api" >&2
  exit 1
fi

code="$(curl -sS -o /dev/null -w "%{http_code}" -H "$AUTH_HEADER" "$BASE/v1/products")"
echo "GET /v1/products → HTTP $code"
if [[ "$code" != "200" ]]; then
  echo "Auth failed (HTTP $code). Check your credentials in .env." >&2
  exit 1
fi
echo "OK — connection verified."
