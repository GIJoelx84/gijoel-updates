#!/usr/bin/env python3
"""Apply PlayChoice VS branding to a clone of the two-player master."""
import re
import runpy
import xml.etree.ElementTree as ET
from pathlib import Path


HOME = Path("/home/pi")
identity = HOME / "gijoel/config/cabinet.conf"
if not re.search(r"^CABINET=playchoice-vs\s*$", identity.read_text(), re.M):
    raise SystemExit("PlayChoice VS installer requires CABINET=playchoice-vs")


def write(path, text):
    path = Path(path)
    if path.read_text() != text:
        path.write_text(text)
        print("Updated " + str(path))


settings = Path("/opt/retropie/configs/all/emulationstation/es_settings.cfg")
settings_text = settings.read_text()
for key, value in {
    "ThemeSet": "es-theme-GIJoel-PlayChoiceVS",
    "StartupSystem": "mame-libretro",
    "GamelistViewStyle": "detailed",
}.items():
    pattern = r'(<string name="' + key + r'" value=")[^"]*("\s*/>)'
    settings_text, count = re.subn(pattern, lambda match: match[1] + value + match[2], settings_text)
    if not count:
        raise SystemExit("Missing EmulationStation setting: " + key)

systems = Path("/etc/emulationstation/es_systems.cfg")
tree = ET.parse(str(systems))
arcade = next((node for node in tree.getroot().findall("system")
               if node.findtext("name") == "mame-libretro"), None)
if arcade is None or arcade.find("fullname") is None:
    raise SystemExit("Missing arcade system on the two-player clone")
if arcade.findtext("fullname") != "PlayChoice VS":
    arcade.find("fullname").text = "PlayChoice VS"
    write(systems, '<?xml version="1.0" encoding="utf-8"?>\n' +
          ET.tostring(tree.getroot(), encoding="unicode") + "\n")

write(settings, settings_text)
write("/opt/gijoel/config/cabinet-id.txt", "playchoice-vs\n")
intro = Path("/opt/gijoel/scripts/show-boot-intro.sh")
intro_data = intro.read_bytes()
updated_intro = re.sub(rb"(?:CASTLEVANIA|POPEYE|DONKEY KONG) CABINET",
                       b"PLAYCHOICE VS CABINET", intro_data)
if updated_intro != intro_data:
    intro.write_bytes(updated_intro)
runpy.run_path(str(Path(__file__).with_name("apply-two-player.py")), run_name="__main__")
print("PlayChoice VS profile applied.")
