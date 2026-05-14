#!/usr/bin/env bash
# Deploy custom_components/magister_school to Home Assistant over SMB, then restart Core.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$(dirname "$0")/config.sh"

[[ -f "$CONFIG" ]] || { echo "Missing .local/config.sh — copy from .local/config.sh.example" >&2; exit 1; }
# shellcheck source=/dev/null
source "$CONFIG"

: "${HA_HOST:?Set HA_HOST in .local/config.sh}"
: "${HA_URL:?Set HA_URL in .local/config.sh}"
: "${HA_USER:?Set HA_USER in .local/config.sh}"
: "${HA_PASS:?Set HA_PASS in .local/config.sh}"
: "${HA_TOKEN:?Set HA_TOKEN in .local/config.sh}"

COMPONENT="magister_school"
SRC="$ROOT/custom_components/$COMPONENT"

[[ -d "$SRC" ]] || { echo "Missing: $SRC" >&2; exit 1; }
command -v rsync >/dev/null || { echo "rsync not found" >&2; exit 1; }
command -v smbclient >/dev/null || { echo "smbclient not found — brew install samba" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl not found" >&2; exit 1; }

export SMB_CONF_PATH="${SMB_CONF_PATH:-/dev/null}"

STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

rsync -a --delete \
  --exclude '.DS_Store' --exclude '__pycache__' --exclude '*.pyc' --exclude '._*' \
  "$SRC/" "$STAGE/$COMPONENT/"

echo "Uploading $COMPONENT to //$HA_HOST/config ..."
set +e
smbclient "//$HA_HOST/config" -U "${HA_USER}%${HA_PASS}" -m SMB3 -q \
  -c "lcd \"$STAGE\"; cd custom_components; recurse; prompt; mput $COMPONENT" \
  2> >(grep -v 'NT_STATUS_OBJECT_NAME_COLLISION' >&2)
smb_rc=$?
set -e
[[ "$smb_rc" -eq 0 ]] || { echo "smbclient failed (exit $smb_rc)" >&2; exit 1; }

echo "Restarting Home Assistant..."
curl_rc=0
code=$(curl -sS -m 120 -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer ${HA_TOKEN}" \
  -H "Content-Type: application/json" \
  -X POST -d "{}" \
  "${HA_URL%/}/api/services/homeassistant/restart") || curl_rc=$?

if [[ "$curl_rc" -eq 52 || "$curl_rc" -eq 56 ]]; then
  echo "Connection closed mid-restart — this is normal."
elif [[ "$curl_rc" -ne 0 ]]; then
  echo "curl failed (exit $curl_rc)" >&2; exit 1
elif [[ "$code" == 401 || "$code" == 403 || "$code" == 404 ]]; then
  echo "Restart API returned HTTP $code — check HA_URL and HA_TOKEN." >&2; exit 1
fi

echo "Done. Give Home Assistant a minute to finish restarting."
