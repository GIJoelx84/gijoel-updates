#!/usr/bin/env python3
"""Install Castlevania cabinet branding and metadata; ROMs stay on the cabinet."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HOME = Path('/home/pi')
ROOT = Path(__file__).resolve().parent.parent
identity = HOME / 'gijoel/config/cabinet.conf'
if not re.search(r'^CABINET=[\"\x27]?castlevania[\"\x27]?\s*$', identity.read_text(), re.M):
    raise SystemExit('Refusing Castlevania configuration on another cabinet type')

def write(path, text):
    path = Path(path)
    if not path.exists() or path.read_text() != text:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        print('Updated ' + str(path))

write('/opt/gijoel/config/cabinet-id.txt', 'castlevania\n')
intro = Path('/opt/gijoel/scripts/show-boot-intro.sh')
data = intro.read_bytes()
updated = data.replace(b'POPEYE CABINET', b'CASTLEVANIA CABINET').replace(b'DONKEY KONG CABINET', b'CASTLEVANIA CABINET')
if updated != data:
    intro.write_bytes(updated)

settings = Path('/opt/retropie/configs/all/emulationstation/es_settings.cfg')
text = settings.read_text()
for key, value in [('ThemeSet','es-theme-GIJoel-Castlevania'), ('StartupSystem','favorites'), ('GamelistViewStyle','detailed')]:
    pattern = r'(<string name="' + key + r'" value=")[^"]*("\s*/>)'
    if not re.search(pattern, text):
        raise SystemExit('Missing setting: ' + key)
    text = re.sub(pattern, lambda m: m.group(1) + value + m.group(2), text)
write(settings, text)

# Copy managed art only. Existing Nintendo artwork is otherwise unchanged.
for source in (ROOT / 'art').rglob('*.png'):
    target = HOME / '.emulationstation/downloaded_images' / source.relative_to(ROOT / 'art')
    data = source.read_bytes()
    if not target.exists() or target.read_bytes() != data:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print('Updated artwork: ' + str(target))

SHARED_IMAGE = '/home/pi/.emulationstation/downloaded_images/castlevania/castlevania-image.png'
games = {
    'mame-libretro': [('cstlevna.zip', 'Vs. Castlevania'), ('hcastle.zip', 'Haunted Castle')],
    'nes': [('castlevania2.nes', "Castlevania II - Simon's Quest"), ('castlevania3.nes', "Castlevania III - Dracula's Curse")],
}

def child(element, name, value):
    item = element.find(name)
    if item is None:
        item = ET.SubElement(element, name)
    item.text = value

for system, entries in games.items():
    path = HOME / '.emulationstation/gamelists' / system / 'gamelist.xml'
    tree = ET.parse(str(path)) if path.exists() else ET.ElementTree(ET.Element('gameList'))
    root = tree.getroot()
    wanted = {filename for filename, _ in entries}
    for game in root.findall('game'):
        filename = Path(game.findtext('path', '')).name
        if game.find('favorite') is not None and filename not in wanted:
            child(game, 'favorite', 'false')
    for filename, title in entries:
        rom = HOME / 'RetroPie/roms' / system / filename
        if not rom.exists():
            print('ROM not installed; skipping metadata: ' + str(rom))
            continue
        game = next((g for g in root.findall('game') if Path(g.findtext('path','')).name == filename), None)
        if game is None:
            game = ET.SubElement(root, 'game')
        child(game, 'path', './' + filename)
        child(game, 'name', title)
        child(game, 'image', SHARED_IMAGE)
        child(game, 'favorite', 'true')
    write(path, '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding='unicode') + '\n')

# Keep every existing system and add NES support if provisioning a compatible clone.
systems = Path('/etc/emulationstation/es_systems.cfg')
tree = ET.parse(str(systems))
root = tree.getroot()
if not any(s.findtext('name') == 'nes' for s in root.findall('system')):
    system = ET.SubElement(root, 'system')
    for name, value in [('name','nes'),('fullname','Nintendo Entertainment System'),('path','/home/pi/RetroPie/roms/nes'),('extension','.nes .NES .zip .ZIP'),('command','/opt/retropie/supplementary/runcommand/runcommand.sh 0 _SYS_ nes %ROM%'),('platform','nes'),('theme','nes')]:
        child(system,name,value)
    write(systems,'<?xml version="1.0"?>\n'+ET.tostring(root,encoding='unicode')+'\n')

nescfg = Path('/opt/retropie/configs/nes/retroarch.cfg')
text = nescfg.read_text() if nescfg.exists() else '#include "/opt/retropie/configs/all/retroarch.cfg"\n'
text = re.sub(r'^aspect_ratio_index\s*=.*\n?', '', text, flags=re.M)
write(nescfg,'aspect_ratio_index = "22"\n'+text)
write('/opt/retropie/configs/nes/emulators.cfg', 'lr-fceumm = "/opt/retropie/emulators/retroarch/bin/retroarch -L /opt/retropie/libretrocores/lr-fceumm/fceumm_libretro.so --config /opt/retropie/configs/nes/retroarch.cfg %ROM%"\ndefault = "lr-fceumm"\n')

for core, rom in [('MAME 2003-Plus','cstlevna'), ('MAME 2003-Plus','hcastle'), ('FCEUmm','castlevania2'), ('FCEUmm','castlevania3')]:
    write(HOME / '.config/retroarch/config' / core / (rom+'.cfg'), 'aspect_ratio_index = "22"\nvideo_rotation = "0"\nvideo_scale_integer = "false"\n')

# Preserve GIJoel animation before the existing POST/COINCORE boot sequence.
for path in ('/etc/splashscreen.list','/etc/splashscreen.list.backup'):
    write(path,'/home/pi/RetroPie/splashscreens/gijoel-boot.mp4\n')
print('Castlevania profile applied. Landscape and existing game library preserved.')
