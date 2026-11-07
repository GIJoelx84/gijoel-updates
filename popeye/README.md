# GIJoel COINCORE Popeye cabinet

Tested landscape Popeye cabinet profile. The opening Favorites menu features Popeye while the existing Nintendo arcade library remains available.

The profile preserves the original GIJoel opening animation, boot/POST sequence, character and branding, black background and CRT/scanline overlay. Normal menu text is white; the selected game is yellow. The GIJoel wordmark is 25% smaller than the first landscape layout. The supplied white Popeye logo is used for the opening menu. Game artwork extends one quarter beyond the right edge, with its existing vertical position preserved.

The Dr. Mario and Donkey Kong 3 artwork corrections remove only their left-edge fringes. The retained artwork pixels were verified unchanged.

Cabinet identity in `/home/pi/gijoel/config/cabinet.conf`:

```sh
CABINET=popeye
UPDATE_REF=main
```

Use the repository's `scripts/update.sh` for profile configuration installation. Older original updaters only stage config files. A master cloned before GitHub publication may also contain `/home/pi/gijoel/local-overrides/popeye/`, which takes precedence over GitHub. Run `scripts/enable-github-profile.sh` once on that cabinet to archive its local overlay and enable updates from the published profile.

ROMs are not included. The cabinet must already have a compatible `popeye.zip`. The original opening video is included as `gijoel-boot.mp4`; both splash-list files are maintained consistently so the later COINCORE animation restores the opening selection correctly.

Physical checks on the Popeye master confirmed landscape orientation, sound, coin/start, movement, punch and exit-to-menu.
