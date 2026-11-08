#!/bin/bash
# One-time migration from the locally staged cabinet profile to GitHub-managed files.
set -euo pipefail
BASE=/home/pi/gijoel
REPO="$BASE/gijoel-updates"
source "$BASE/config/cabinet.conf"
case "$CABINET" in donkeykong|popeye|castlevania) ;; *) echo 'No supported cabinet profile selected.'; exit 1;; esac
git -C "$REPO" fetch origin main
git -C "$REPO" cat-file -e "origin/main:$CABINET/config/apply-profile.py"
BACKUP="$BASE/backups/enable-github-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp "$BASE/update.sh" "$BACKUP/update.sh"
cp "$BASE/config/cabinet.conf" "$BACKUP/cabinet.conf"
git -C "$REPO" show origin/main:scripts/update.sh > "$BACKUP/new-update.sh"
bash -n "$BACKUP/new-update.sh"
if [ -d "$BASE/local-overrides/$CABINET" ]; then
  mv "$BASE/local-overrides/$CABINET" "$BACKUP/local-profile"
fi
cp "$BACKUP/new-update.sh" "$BASE/update.sh"
chmod +x "$BASE/update.sh"
printf 'CABINET=%s\nUPDATE_REF=main\n' "$CABINET" > "$BASE/config/cabinet.conf"
pkill -TERM -f '^/opt/retropie/supplementary/emulationstation/emulationstation ' || true
sleep 2
echo "Archived local profile in $BACKUP"
"$BASE/update.sh"
