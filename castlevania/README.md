# GIJoel COINCORE Castlevania cabinet

Castlevania cabinet profile based on the tested landscape Popeye master. The GIJoel opening animation, character, wordmark, black background, original CRT/scanline overlay and artwork positioning are preserved. The supplied white Castlevania logo replaces the featured-page Popeye logo.

The startup Favorites menu contains:

| Game | Local file | Emulator |
|---|---|---|
| Vs. Castlevania | `mame-libretro/cstlevna.zip` | lr-mame2003-plus |
| Haunted Castle | `mame-libretro/hcastle.zip` | lr-mame2003-plus |
| Castlevania II - Simon's Quest | `nes/castlevania2.nes` | lr-fceumm |
| Castlevania III - Dracula's Curse | `nes/castlevania3.nes` | lr-fceumm |

All four metadata entries point to the same Castlevania game artwork. Other existing Nintendo games remain installed and accessible. The two corrected Dr. Mario/Donkey Kong 3 artwork files are preserved.

## Installation and update channel

The cabinet identity is `/home/pi/gijoel/config/cabinet.conf`:

```sh
CABINET=castlevania
```

The updated `scripts/update.sh` supports both Popeye and Castlevania profile installers. It applies shared files, the selected GitHub cabinet folder, then an optional local profile overlay. A newly staged cabinet may have a local overlay at `/home/pi/gijoel/local-overrides/castlevania/` until GitHub publication and verification are complete. A local overlay takes precedence over GitHub; archive it out of `local-overrides` after the published profile has been verified so future GitHub changes reach this cabinet.

The updater retains the established 4 a.m. cron schedule and reboot-on-new-commit behavior. Other cabinet types retain their current installation behavior.

For another compatible clone, first install the required NES core using the official RetroPie setup:

```sh
sudo /home/pi/RetroPie-Setup/retropie_packages.sh lr-fceumm install_bin
sudo /home/pi/RetroPie-Setup/retropie_packages.sh lr-fceumm configure
```

Install the local ROMs listed above before applying this profile. This repository/package contains branding, metadata configuration and updater support; ROM files are not included. NES archives supplied for this cabinet were extracted without altering their content. Haunted Castle's supplied audio ROM was verified by SHA-1 and renamed from `768e01.e4` to the equivalent MAME 2003 filename `768.e01` inside the installed copy.

Back up the cabinet configuration, quit EmulationStation, install the updated updater, set the cabinet identity, and run the updater. Firmware orientation is deliberately left unchanged. The original GIJoel opening animation remains selected in both splash-list files.

## Validation

Verify four startup Favorites, matching artwork, Nintendo library access, sound, start/coin, movement/action buttons and exit-to-menu on the physical cabinet before cloning or shipping. Automated launch tests and title-screen captures are recorded separately in the cabinet handoff.
