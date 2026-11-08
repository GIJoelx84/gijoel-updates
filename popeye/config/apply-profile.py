#!/usr/bin/env python3
"""Install only the Popeye profile. Called after the cabinet updater stages it."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HOME = Path('/home/pi')
CONFIG = HOME / 'gijoel/config/cabinet.conf'
if not re.search(r'^CABINET=[\"\x27]?popeye[\"\x27]?\s*$', CONFIG.read_text(), re.M):
    raise SystemExit('Popeye installer refused: cabinet is not popeye')

def write_if_changed(path, text):
    path = Path(path)
    if not path.exists() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print('Updated ' + str(path))

boot = Path('/boot/config.txt')
text = boot.read_text()
if re.search(r'^display_hdmi_rotate\s*=', text, re.M):
    text = re.sub(r'^display_hdmi_rotate\s*=.*$', 'display_hdmi_rotate=0', text, flags=re.M)
else:
    text = 'display_hdmi_rotate=0\n' + text
write_if_changed(boot, text)
write_if_changed('/opt/gijoel/config/cabinet-id.txt', 'popeye\n')

intro = Path('/opt/gijoel/scripts/show-boot-intro.sh')
intro_bytes = intro.read_bytes()
new_intro = intro_bytes.replace(b'DONKEY KONG CABINET', b'POPEYE CABINET')
if new_intro != intro_bytes:
    intro.write_bytes(new_intro)
    print('Updated ' + str(intro))

settings = Path('/opt/retropie/configs/all/emulationstation/es_settings.cfg')
text = settings.read_text()
for key, value in [('ThemeSet', 'es-theme-GIJoel-Popeye'), ('StartupSystem', 'favorites'), ('GamelistViewStyle', 'detailed')]:
    pattern = r'(<string name="' + key + r'" value=")[^"]*("\s*/>)'
    if not re.search(pattern, text):
        raise SystemExit('Missing EmulationStation setting: ' + key)
    text = re.sub(pattern, lambda m: m.group(1) + value + m.group(2), text)
write_if_changed(settings, text)

gamelist = HOME / '.emulationstation/gamelists/mame-libretro/gamelist.xml'
text = gamelist.read_text()
def favorite(match):
    game = match.group(0)
    path = re.search(r'<path>(.*?)</path>', game)
    if path is None:
        return game
    name = Path(path.group(1)).name.lower()
    if name not in ('popeye.zip', 'dkong.zip', 'dkongjr.zip', 'dkong3.zip'):
        return game
    value = 'true' if name == 'popeye.zip' else 'false'
    if '<favorite>' in game:
        return re.sub(r'<favorite>.*?</favorite>', '<favorite>' + value + '</favorite>', game)
    return game.replace('</game>', '\t<favorite>' + value + '</favorite>\n\t</game>')
text = re.sub(r'<game>.*?</game>', favorite, text, flags=re.S)
ET.fromstring(text)
write_if_changed(gamelist, text)

# RetroArch 1.10: 22 is Core Provided. Respect each Nintendo game's native shape.
system_cfg = Path('/opt/retropie/configs/mame-libretro/retroarch.cfg')
text = re.sub(r'^aspect_ratio_index\s*=.*$', 'aspect_ratio_index = "22"', system_cfg.read_text(), flags=re.M)
write_if_changed(system_cfg, text)
override = '/opt/retropie/configs/all/retroarch/config/MAME 2003-Plus/popeye.cfg'
override_path = Path(override)
text = override_path.read_text() if override_path.exists() else ''
for key, value in [('aspect_ratio_index','22'), ('video_rotation','0'), ('video_scale_integer','false')]:
    pattern = r'^'+key+r'\s*=.*$'
    line = key+' = "'+value+'"'
    if re.search(pattern, text, re.M):
        text = re.sub(pattern, lambda m: line, text, flags=re.M)
    else:
        text += ('\n' if text and not text.endswith('\n') else '') + line + '\n'
write_if_changed(override, text)

# Restore the original GIJoel opening animation.
splash = '/home/pi/RetroPie/splashscreens/gijoel-boot.mp4\n'
write_if_changed('/etc/splashscreen.list', splash)
write_if_changed('/etc/splashscreen.list.backup', splash)
scfg = Path('/opt/retropie/configs/all/splashscreen.cfg')
text = scfg.read_text()
text = re.sub(r'^DURATION=.*\n?', '', text, flags=re.M).rstrip() + '\nDURATION=3\n'
write_if_changed(scfg, text)
print('Popeye profile applied.')

# Correct only the two artwork files with a transparent white fringe at the left edge.
profile_root = Path(__file__).resolve().parent.parent
for name in ('dkong3-image.png', 'drmario-image.png'):
    source = profile_root / 'art/mame-libretro' / name
    target = HOME / '.emulationstation/downloaded_images/mame-libretro' / name
    if source.exists():
        data = source.read_bytes()
        if not target.exists() or target.read_bytes() != data:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            print('Updated artwork: ' + name)
