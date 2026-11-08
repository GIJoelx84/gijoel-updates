# Vertical DK card audit — November 7, 2026

Status: backed up and compared. No live configuration, updater, display setting, or game mapping was changed during this audit.

## Preserved source

- Physical card identity: CABINET=donkeykong.
- Active release when captured: /home/pi/gijoel/releases/20261025-040003_6cbfd86.
- Pi backup: /home/pi/gijoel/backups/dk-card-audit-20261107-193113/configs-and-art.tgz.
- Windows copy: outputs/DK-card-20261107-configs-and-art.tgz.
- Archive size: 40,350,837 bytes; SHA-256 06deee542d00ac9fa6d87fc60eb2a0a6b607ae2dd9a83d578505da25b2bf4c39. The transferred copy was verified against the Pi checksum.
- Archive inventory: 1,416 regular files and two links, covering RetroPie configs, native arcade controls, metadata/art, themes, opening-video assets, cabinet scripts, boot display settings and active release files.
- This is a configuration/art backup, not a complete SD image. It excludes the ROM library and does not reproduce the entire operating system or installed emulator binaries.
- Repository reference branch: baseline/vertical-dk-20261107.
- donkeykong/config/card-snapshot-20261107.json preserves exact bytes for 54 selected active configuration/script/metadata files, with absolute destination paths and base64 encoding. It is archival data, not a deployment installer.
- All 162 installed theme files matched the effective donkeykong/shared GitHub theme files byte-for-byte. Their existing repository assets are retained in this baseline.

## Current game overrides

Captured files under /opt/retropie/configs/all/retroarch/config/MAME 2003-Plus:

| File | Exact saved settings |
|---|---|
| dkong.cfg | aspect_ratio_index = "24" |
| dkongjr.cfg | aspect_ratio_index = "8" |
| dkong3.cfg | aspect_ratio_index = "8"; custom_viewport_height = "950"; custom_viewport_width = "765"; custom_viewport_y = "32" |

These files were saved on November 7 and were not present in the existing GitHub DK config folder, which contained only .keep and donkeykong-test.txt.

The MAME system and global defaults use aspect_ratio_index = "11". The global RetroArch config enables /opt/retropie/emulators/retroarch/shader/crt-pi-curvature-vertical.glslp, with rotation 0 and integer scaling false. Preserve the raw values; do not replace them with a landscape profile or reinterpret aspect-ratio indices without checking this installed RetroArch version.

Power at audit: get_throttled=0x0.

## Existing updater limitation

The card's updater fetches main, merges shared and cabinet files, and installs theme/splash files. Its config step only copies release/config into /home/pi/gijoel/live/config. It does not install RetroArch game overrides, run a cabinet configuration installer, or replace its own updater script from repository scripts/update.sh.

Therefore merely placing new aspect-ratio settings in GitHub will NOT apply them to this older updater's live RetroArch configuration. Archiving the snapshot does not deploy it.

## Rollout to master and shipped cabinets

1. Keep this backup and a physical SD master image.
2. Build a DK-specific installer for the captured vertical settings, preserving unrelated existing controls and settings.
3. Upgrade the updater once on this master and validate the installer against this card.
4. Inspect a shipped cabinet's updater version and cabinet identity. If it has the same staging-only updater, upgrade it once through an available remote-management/SSH connection, or an on-site method if no remote connection exists. A cabinet fetching GitHub does not, by itself, provide an inbound SSH connection.
5. Once a compatible updater is installed, supported aspect ratios, game overrides, controller settings, scripts and GUI files can be delivered through its cabinet profile without replacing the SD card.
6. Verify one shipped cabinet before broader deployment. Do not push the landscape two-player encoder configuration to the vertical DK fleet.

The older updater cannot bootstrap its own upgrade solely by reading a new update.sh file from GitHub: it never installs or executes that file. Do not describe that path as already working on shipped cabinets until their actual version and management access have been checked.
