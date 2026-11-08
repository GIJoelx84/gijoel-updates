# Two-Player Pi Master v1

Approved by GIJoel on November 7, 2026. This is our internal starting point for future two-stick Raspberry Pi cabinets using the same dual-player encoder, including upcoming VS and Mario Bros. builds.

## Verified baseline

- Repository: GIJoelx84/gijoel-updates.
- Working configuration revision: e997fcf5d7e77151fb031f548d456acc544cd6c4.
- Reference branch: baseline/two-player-pi-v1. Keep this branch as the v1 reference; develop future cabinet profiles on main.
- Physical source: the current, working Castlevania Pi card. Clone/image this card to produce the two-player master SD image; the GitHub repository contains configuration/assets, not a complete SD-card image or ROM library.
- User confirmed the Coin/action and two-player changes worked, then confirmed the VS Super Mario Bros. A/B swap was better.
- The final VS Super Mario swap was applied live after the b23fb7b release. Its installer and snapshot are saved in e997fcf. A cloned card's updater will fetch the current source from GitHub.
- Existing Donkey Kong/Popeye master is a separate, earlier baseline. Preserve it for its own hardware/builds.

## Standard hardware

One USB cable connects one dual-player board. USB vendor/product ID 0810:e001; Linux name NoName Generic USB Joystick. A previous board was faulty; the working replacement was tested.

The boot command line must contain usbhid.quirks=0x0810:0xe001:0x00000040, retaining other existing boot options. This splits the board's two HID application collections into independent controllers.

With this board as the only gamepad:
- Physical P1 = js1 / RetroArch index 1, 10 buttons.
- Physical P2 = js0 / RetroArch index 0, 12 buttons.
- SDL GUID for both = 030000001008000001e0000001010000.
- Both sticks use X axis 0 (left negative/right positive) and Y axis 1 (up negative/down positive).
- Final power check after replacing the supply: get_throttled=0x0.

## Measured physical wiring

| Side | Control | Raw button |
|---|---|---|
| P1 | A / yellow action | 1 |
| P1 | B / red action | 0 |
| P1 | Right blue / Start | 2 |
| P1 | Left blue / Select | 3 |
| P1 | White / Hotkey | 4 |
| P1 | Black / R/T | 5 |
| P1 | Separate Coin button | 6 |
| P2 | A | 0 |
| P2 | B | 1 |

P2 has its joystick and A/B only. Preserve the tested native arcade start mappings associated with the blue buttons; frontend/NES logical Select and Start retain the table above. Hotkey + Start exits an emulator; Hotkey + R/T opens its menu.

Coin is independent of B. In arcade system configuration only, raw P1 button 6 drives RetroPad Y, which the Classic MAME layout exposes as JOYCODE_1_BUTTON3. MAME Coin 1 uses that virtual input. NES and frontend Select remain separate.

## Game mappings to preserve

Default arcade actions: P1 Button 1 uses P1 A; P1 Button 2 uses P1 B. P2 Button 1 uses P2 A; P2 Button 2 uses P2 B. Existing saved game P2 Button 2 entries were corrected where supported; games without saved files inherit the corrected defaults.

Keep the user's native VS Castlevania, VS Excitebike, Mario Bros. and Haunted Castle mappings. NES A/B and game settings were inspected and preserved.

VS Super Mario Bros. is the deliberate exception: swap A/B on BOTH players, only in suprmrio.cfg. Its specific rule takes precedence over the generic P2 Button 2 rule. Keep its separate Coin mapping.

Exact saved game configurations are in castlevania/config/saved-inputs.json. Existing local game saves are preserved; the snapshot seeds missing configurations. apply-game-inputs.py changes only the requested action/Coin bindings and preserves other native records, driver defaults and non-input data. Display-profile application preserves other RetroArch override settings.

## Reuse for the next cabinet

1. Make and retain an SD-card image of this verified card, labelled GIJoel Two-Player Pi Master v1.
2. Clone the master for the next cabinet and connect the same encoder with the same wiring.
3. Start a cabinet-specific profile for VS, Mario Bros. or the requested game family. Reuse the proven hardware split, mappings, opening animation, CRT/scanline effects and existing artwork/layout as the starting point.
4. Change only that cabinet's branding, featured/startup collection, game order and explicit game-specific requirements. Preserve the existing Nintendo library unless requested otherwise.
5. Reuse the encoder/input helpers when provisioning a new profile: they currently live under castlevania/config and are invoked by the Castlevania installer. A different cabinet profile must explicitly call/package them; changing CABINET alone does not provision their wiring.
6. Test each stick, both action buttons, Coin, the blue start buttons, Hotkey exits, and a simultaneous two-player game before shipping. Confirm any game-specific exception.
7. Keep CABINET and UPDATE_REF configured for that cabinet. Do not point production cabinets at the baseline branch just to label them; that would pin future updates to v1.

Backups and audit: original controls are in /home/pi/gijoel/backups/before-no-name-twin and /home/pi/gijoel/backups/before-p2-button2-and-coin. The immediate pre-swap VS Super Mario file is /home/pi/gijoel/castlevania-prep/suprmrio-before-button-swap.cfg. The Windows workspace also retains the original input snapshot and verification report in outputs/controls-before-p2-fix.
