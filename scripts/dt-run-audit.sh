#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required"
  exit 1
fi

if [ $# -lt 2 ]; then
  echo "Usage: $0 <packet.json> <agent>"
  echo 'Example: scripts/dt-run-audit.sh TP-AUDIT-057C-PROMPT-PIPELINE.json gemini'
  exit 1
fi

PACKET="$1"
AGENT="$2"

if [ ! -f "$PACKET" ]; then
  echo "Packet not found: $PACKET"
  exit 1
fi

PACKET_ID="$(jq -r '.id' "$PACKET")"
SERIES_ID="$(jq -r '.series.id' "$PACKET")"

echo "== Packet =="
echo "packet: $PACKET"
echo "packet_id: $PACKET_ID"
echo "series_id: $SERIES_ID"
echo "agent: $AGENT"
echo

set +e
dopetask tp series exec "$PACKET" --agent "$AGENT"
RC=$?
set -e

if [ $RC -eq 0 ]; then
  echo
  echo "== SUCCESS =="
  dopetask tp series status "$SERIES_ID" || true
  exit 0
fi

echo
echo "== EXECUTION FAILED =="
echo "exit_code: $RC"
echo

echo "== SERIES STATUS =="
dopetask tp series status "$SERIES_ID" || true
echo

SERIES_DIR="out/tp_series/$SERIES_ID"
PACKET_DIR="$SERIES_DIR/packets/$PACKET_ID"
EXEC_ERROR="$PACKET_DIR/EXEC_ERROR.json"

if [ -f "$EXEC_ERROR" ]; then
  echo "== EXEC_ERROR.json =="
  cat "$EXEC_ERROR"
  echo
fi

PROOF_BUNDLE="$(find "$SERIES_DIR" -type f -iname '*PROOF_BUNDLE.json' | head -n 1 || true)"
if [ -n "${PROOF_BUNDLE:-}" ] && [ -f "$PROOF_BUNDLE" ]; then
  echo "== PROOF BUNDLE PATH =="
  echo "$PROOF_BUNDLE"
  echo
  echo "== PROOF BUNDLE SUMMARY =="
  jq '.' "$PROOF_BUNDLE" || cat "$PROOF_BUNDLE"
  echo
else
  echo "No proof bundle found."
  echo
fi

echo "== FILES UNDER SERIES DIR =="
find "$SERIES_DIR" -type f | sort || true
echo

exit $RC
