#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required"
  exit 1
fi

if [ $# -lt 2 ]; then
  echo "Usage: $0 <source.json> <new_suffix>"
  echo "Example: scripts/dt-bump-packet.sh TP-AUDIT-057C-PROMPT-PIPELINE.json D"
  exit 1
fi

SRC="$1"
SUFFIX="$2"

if [ ! -f "$SRC" ]; then
  echo "Source packet not found: $SRC"
  exit 1
fi

BASENAME="$(basename "$SRC" .json)"
DIRNAME="$(dirname "$SRC")"

NEW_PACKET_ID="$(jq -r '.id' "$SRC" | sed -E "s/(TP-AUDIT-057)[A-Z]?(-PROMPT-PIPELINE)/\\1${SUFFIX}\\2/")"
NEW_SERIES_ID="$(jq -r '.series.id' "$SRC" | sed -E "s/(SERIES-AUDIT-057)[A-Z]?(-PROMPT-PIPELINE)/\\1${SUFFIX}\\2/")"
NEW_FILE="${DIRNAME}/${NEW_PACKET_ID}.json"

jq \
  --arg pid "$NEW_PACKET_ID" \
  --arg sid "$NEW_SERIES_ID" \
  '.id = $pid | .series.id = $sid' \
  "$SRC" > "$NEW_FILE"

echo "Wrote: $NEW_FILE"
echo "packet_id: $NEW_PACKET_ID"
echo "series_id: $NEW_SERIES_ID"
