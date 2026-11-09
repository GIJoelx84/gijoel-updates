# PlayChoice VS

A provisional landscape cabinet profile for a clone of Two-Player Pi Master v1. It opens to the existing Nintendo arcade library, uses a temporary PlayChoice VS title, and carries forward the verified twin encoder and arcade mappings. The boot profile displays PLAYCHOICE VS. The general game selection and final logo are pending.

For a PlayChoice VS test clone, set CABINET=playchoice-vs and UPDATE_REF=test/rom-delivery in /home/pi/gijoel/config/cabinet.conf. Bootstrap the updater from scripts/update.sh on that branch, then run it and reboot. The older updater cannot activate this cabinet profile until it has installed the branch version.

Replace themes/es-theme-GIJoel-PlayChoiceVS/_inc/logos/mame.svg when the final logo is ready. The separate NES system and local ROM library remain available.

The empty config/roms.json opts into the download step without installing games. See docs/ROM-DELIVERY.md for the manifest format. The live library can discover new ROMs on a restart, and the cabinet's gamelist can provide their display names and artwork.
