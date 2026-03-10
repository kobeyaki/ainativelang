#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANG_FILE="${APP_DIR}/apple_price.lang"

python3 "${ROOT_DIR}/scripts/validate_ainl.py" "${LANG_FILE}" --emit ir > "${APP_DIR}/apple_price.ir.json"
cp "${APP_DIR}/apple_price.ir.json" "${APP_DIR}/ir.json"
python3 "${ROOT_DIR}/scripts/validate_ainl.py" "${LANG_FILE}" --emit react > "${APP_DIR}/apple_price.react.tsx"
python3 "${ROOT_DIR}/scripts/validate_ainl.py" "${LANG_FILE}" --emit openapi > "${APP_DIR}/openapi.json"
python3 "${ROOT_DIR}/scripts/validate_ainl.py" "${LANG_FILE}" --emit server > "${APP_DIR}/server.py"

echo "Generated files:"
echo "  - ${APP_DIR}/apple_price.ir.json"
echo "  - ${APP_DIR}/ir.json"
echo "  - ${APP_DIR}/apple_price.react.tsx"
echo "  - ${APP_DIR}/openapi.json"
echo "  - ${APP_DIR}/server.py"
