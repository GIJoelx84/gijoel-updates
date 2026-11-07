# Cabinet profiles and remote updates

`shared/` supplies common files. Each cabinet has its own top-level folder, including `popeye/` and `castlevania/`. `/home/pi/gijoel/config/cabinet.conf` selects the profile with `CABINET=...`.

`scripts/update.sh` is the cabinet updater. It fetches the selected GitHub branch (`UPDATE_REF`, default `main`), builds a timestamped release from shared files plus the selected cabinet folder, optionally applies a local overlay, updates the current symlink, installs themes/splash assets and invokes the selected Popeye or Castlevania config installer.

Local overrides are staging fallbacks and take precedence over repository files. They must be archived after a tested profile is published; otherwise future GitHub profile changes will be masked. `scripts/enable-github-profile.sh` performs that one-time migration for existing Popeye/Castlevania clones after verifying the published profile exists. Original Donkey Kong updater installations require an explicit updater upgrade before they can run profile config installers.

The existing cron schedule is 4 a.m. in each Pi's local timezone. The established updater reboots on a new repository commit, including commits that change another cabinet's folder. An optional separate branch per deployment channel can be selected with `UPDATE_REF`; it is not required for these profiles.

Game ROMs remain local. Profile files provide branding, artwork, metadata and emulator configuration. New NES cabinets also require the official RetroPie lr-fceumm emulator installation, as described in the Castlevania README. Cabinet orientation, input setup and general library files should be validated on a physical cabinet before shipping.
