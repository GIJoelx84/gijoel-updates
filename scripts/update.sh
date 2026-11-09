#!/bin/bash
set -e

BASE="/home/pi/gijoel"
REPO="$BASE/gijoel-updates"
CONFIG="$BASE/config/cabinet.conf"
RELEASES="$BASE/releases"
CURRENT_LINK="$BASE/current"
LIVE="$BASE/live"
THEMEDEST="/home/pi/.emulationstation/themes"
SPLASHDEST="/home/pi/RetroPie/splashscreens"

STATUS_DIR="/opt/gijoel/boot"
STATUS_FILE="$STATUS_DIR/update-status.txt"
BUILD_FILE="$STATUS_DIR/build-version.txt"

mkdir -p "$STATUS_DIR"

if [ ! -f "$CONFIG" ]; then
  echo "Missing cabinet config: $CONFIG"
  exit 1
fi

source "$CONFIG"

exec 9>"$BASE/update.lock"
if ! flock -n 9; then
  echo "Another cabinet update is already running."
  exit 0
fi

if [ -z "$CABINET" ]; then
  echo "CABINET is empty in $CONFIG"
  exit 1
fi

echo "----------------------------------"
echo "GIJoel update starting"
echo "Cabinet type: $CABINET"
echo "----------------------------------"

OLD_COMMIT="$(git -C "$REPO" rev-parse HEAD 2>/dev/null || echo none)"

cd "$REPO"
git merge --abort 2>/dev/null || true
git fetch origin
UPDATE_REF="${UPDATE_REF:-main}"
git check-ref-format --branch "$UPDATE_REF" >/dev/null
git reset --hard "origin/$UPDATE_REF"
git clean -fd

NEW_COMMIT="$(git rev-parse HEAD)"
SHORTSHA="$(git rev-parse --short HEAD)"

if [ "$OLD_COMMIT" != "$NEW_COMMIT" ]; then
  UPDATE_HAPPENED=1
  UPDATE_STATUS="UPDATED"
else
  UPDATE_HAPPENED=0
  UPDATE_STATUS="CURRENT"
fi

VERSIONFILE="$REPO/version.txt"
if [ -f "$VERSIONFILE" ]; then
  echo "Update version:"
  cat "$VERSIONFILE"
  echo ""
fi

mkdir -p "$RELEASES"

STAMP=$(date +%Y%m%d-%H%M%S)
NEWREL="$RELEASES/${STAMP}_${SHORTSHA}"

echo "Creating new release folder:"
echo "$NEWREL"

mkdir -p "$NEWREL"

echo "Applying shared files first..."
rsync -av --exclude='.keep' "$REPO/shared/" "$NEWREL/"

echo "Applying cabinet-specific files on top..."
if [ -d "$REPO/$CABINET" ]; then
  rsync -av --exclude='.keep' "$REPO/$CABINET/" "$NEWREL/"
elif [ ! -d "$BASE/local-overrides/$CABINET" ]; then
  echo "Missing cabinet profile: $CABINET"
  exit 1
fi

LOCAL_PROFILE="$BASE/local-overrides/$CABINET"
if [ -d "$LOCAL_PROFILE" ]; then
  echo "Applying local cabinet profile overlay..."
  rsync -av --exclude='.keep' "$LOCAL_PROFILE/" "$NEWREL/"
fi

ROM_MANIFEST="$NEWREL/config/roms.json"
if [ -f "$ROM_MANIFEST" ]; then
  echo "Installing verified ROMs for $CABINET..."
  python3 "$REPO/scripts/install-roms.py" "$ROM_MANIFEST" /home/pi/RetroPie/roms
  # A failed download may have advanced Git HEAD without activating the release.
  if [ "$(cat "$BUILD_FILE" 2>/dev/null || true)" != "$SHORTSHA" ]; then
    UPDATE_HAPPENED=1
    UPDATE_STATUS="UPDATED"
  fi
fi

echo "Updating current symlink..."
if [ -d "$CURRENT_LINK" ] && [ ! -L "$CURRENT_LINK" ]; then
  rm -rf "$CURRENT_LINK"
fi
ln -sfn "$NEWREL" "$CURRENT_LINK"

mkdir -p "$LIVE/config"
mkdir -p "$THEMEDEST"
mkdir -p "$SPLASHDEST"

echo "Installing config files into live staging area..."
rsync -av --exclude='.keep' "$CURRENT_LINK/config/" "$LIVE/config/" 2>/dev/null || true

echo "Installing theme files into EmulationStation themes folder..."
rsync -av --delete --exclude='.keep' "$CURRENT_LINK/themes/" "$THEMEDEST/" 2>/dev/null || true

echo "Installing splash files into RetroPie splashscreens folder..."
rsync -av --exclude='.keep' "$CURRENT_LINK/splash/" "$SPLASHDEST/" 2>/dev/null || true

if { [ "$CABINET" = "donkeykong" ] || [ "$CABINET" = "popeye" ] || [ "$CABINET" = "castlevania" ]; } && [ -f "$CURRENT_LINK/config/apply-profile.py" ]; then
  echo "Applying $CABINET cabinet configuration..."
  sudo python3 "$CURRENT_LINK/config/apply-profile.py"
fi

if [ -f "$VERSIONFILE" ]; then
  cp "$VERSIONFILE" "$BASE/installed-version.txt"
fi

echo "$UPDATE_STATUS" > "$STATUS_FILE"
echo "$SHORTSHA" > "$BUILD_FILE"

echo "Cleaning old releases (keeping newest 5)..."
ls -1dt "$RELEASES"/* 2>/dev/null | tail -n +6 | xargs -r rm -rf

echo "Done."

# Once bootstrapped, future updater changes arrive through the same channel.
if [ -f "$REPO/scripts/update.sh" ] && ! cmp -s "$REPO/scripts/update.sh" "$BASE/update.sh"; then
  bash -n "$REPO/scripts/update.sh"
  mkdir -p "$BASE/backups/updater"
  cp -p "$BASE/update.sh" "$BASE/backups/updater/update-before-$SHORTSHA.sh"
  cp "$REPO/scripts/update.sh" "$BASE/update.sh.next"
  chmod +x "$BASE/update.sh.next"
  mv "$BASE/update.sh.next" "$BASE/update.sh"
  echo "Updated cabinet updater for the next run."
fi
echo "Current release points to:"
readlink -f "$CURRENT_LINK"

if [ "$UPDATE_HAPPENED" -eq 1 ] && [ "${GIJOEL_NO_REBOOT:-0}" != "1" ]; then
  echo "Update installed. Rebooting system in 5 seconds..."
  sleep 5
  sudo reboot
fi

