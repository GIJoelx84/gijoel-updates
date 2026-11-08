# Vertical Donkey Kong master

Verified source: the original vertical DK card captured November 7, 2026. See docs/DK-CARD-AUDIT-20261107.md and baseline/vertical-dk-20261107 for the unmodified source audit. The current profile adds remote installation of its exact display settings.

Set /home/pi/gijoel/config/cabinet.conf to:
```sh
CABINET=donkeykong
UPDATE_REF=main
```

The profile preserves the original portrait theme, animation, game library, metadata and controls. All 162 captured theme files matched the existing effective shared/DK repository theme. Configuration installation applies the captured global/system aspect settings, vertical CRT shader settings, HDMI rotation 3 and the three DK game display overrides. Other game/control keys are preserved. Existing shader files from this compatible RetroPie build are required; this is not a full OS/emulator installer.

Game overrides:
- Donkey Kong: aspect_ratio_index="24".
- DK Jr.: aspect_ratio_index="8".
- DK 3: aspect_ratio_index="8", custom viewport width 765, height 950, y 32.

These are raw indices for the verified installed RetroArch version. Do not reinterpret them using a different version's index list or substitute the landscape profile.

Original configuration/script bytes are archived in config/card-snapshot-20261107.json (base64). This snapshot is reference data; the installer does not overwrite a cabinet's controls or bulk-restore the snapshot.

Older DK updaters need one explicit bootstrap. On a reachable compatible cabinet, fetch this repository and run scripts/enable-github-profile.sh as pi. It verifies the selected published profile, backs up the existing updater/identity, archives any local overlay, installs the current updater, keeps CABINET=donkeykong with UPDATE_REF=main, and applies the profile. It stops the frontend and normally reboots on a new commit.

After bootstrap, the updater installs supported profile configurations and safely replaces its own script from the selected GitHub branch for the next run. Updates are serialized with flock. Existing 4 a.m. scheduling and reboot-on-new-commit behavior remain. GIJOEL_NO_REBOOT=1 is available for controlled maintenance checks; normally leave it unset.

Do not assume an existing shipped cabinet has this updater. Inspect its version and management access first; fetching GitHub alone does not enable inbound SSH. Test one deployed cabinet before wider rollout.
