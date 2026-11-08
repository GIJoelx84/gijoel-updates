# Cabinet profiles and remote updates

shared/ supplies common files. Cabinet folders include donkeykong (vertical), popeye (landscape), and castlevania (landscape). /home/pi/gijoel/config/cabinet.conf selects CABINET and UPDATE_REF (default main).

scripts/update.sh fetches the chosen GitHub branch, builds a release from shared plus the selected cabinet folder, installs themes/splash assets and invokes the supported cabinet configuration installer. The DK installer applies captured vertical display settings while preserving controls. Popeye and Castlevania retain their respective validated profiles.

Local overrides take precedence over GitHub files. scripts/enable-github-profile.sh performs the one-time migration for compatible DK, Popeye and Castlevania cards: verify the published profile, back up existing state, archive any local overlay, install the current updater and apply the profile.

The original DK updater only stages config files and cannot install its own replacement. Each old deployed cabinet needs this one-time bootstrap through an available management/SSH connection or an on-site method. After bootstrap, the upgraded updater also installs future updates to its own script. A GitHub connection on a cabinet is not an inbound SSH connection.

The scheduled update remains 4 a.m. in the Pi's local timezone. Updates are serialized with flock. The established behavior reboots on a new repository commit, even one affecting another cabinet's folder. UPDATE_REF can select a deployment branch; baseline branches are archival references, not the normal production channel. GIJOEL_NO_REBOOT=1 suppresses the reboot for controlled maintenance.

Popeye publication succeeded after the initial GitHub authorization errors: its full profile, artwork corrections, animation, installer and updater were published in c30886479819b81d04b2b6cd2f867255b541b917. A Popeye master cloned before that migration still needs its physical card checked and its temporary local override archived once. Its GitHub content does not need republishing.

Game ROMs remain local. Profiles can deliver supported GUI, metadata, artwork, emulator overrides, input configuration and scripts, through explicit installers. Additional OS packages/emulator binaries require their own provisioning. New NES cabinets need lr-fceumm. Validate orientation, inputs, sound, game launch and exit on a physical cabinet before shipping.

See docs/TWO-PLAYER-PI-MASTER.md for the verified dual-encoder starting point and donkeykong/README.md for the separate vertical DK master.
