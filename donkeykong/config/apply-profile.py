#!/usr/bin/env python3
"""Apply the verified vertical DK display profile; preserve cabinet controls."""
from pathlib import Path
import hashlib, json, os, pwd, re, shutil

ROOT=Path(__file__).parent
settings=json.loads((ROOT/'display-settings.json').read_text())
user=pwd.getpwnam('pi')
changed=[]
def write(path,text):
    path=Path(path)
    old=path.read_text() if path.exists() else None
    if old==text:
        return
    if old is not None:
        digest=hashlib.sha256(old.encode()).hexdigest()[:12]
        backup=Path('/home/pi/gijoel/backups/dk-profile')/digest/str(path).lstrip('/')
        if not backup.exists():
            backup.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(str(path),str(backup))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text)
    if str(path).startswith(('/home/pi/','/opt/retropie/configs/')):
        os.chown(str(path),user.pw_uid,user.pw_gid)
    changed.append(str(path))

def configure(path,values):
    path=Path(path)
    text=path.read_text() if path.exists() else ''
    for key,value in values.items():
        pattern=r'^'+re.escape(key)+r'\s*=.*$'
        line=key+' = "'+value+'"'
        if re.search(pattern,text,re.M):
            text=re.sub(pattern,lambda m:line,text,flags=re.M)
        else:
            text+=('\n' if text and not text.endswith('\n') else '')+line+'\n'
    write(path,text)

shader=Path(settings['global']['video_shader'])
if not shader.is_file():
    raise SystemExit('Missing required vertical CRT shader: '+str(shader))
configure('/opt/retropie/configs/all/retroarch.cfg',settings['global'])
configure('/opt/retropie/configs/mame-libretro/retroarch.cfg',{'aspect_ratio_index':settings['global']['aspect_ratio_index']})
for path,text in settings['gameOverrides'].items():
    values=dict(re.findall(r'^([a-zA-Z0-9_]+)\s*=\s*"([^"]*)"',text,re.M))
    configure(path,values)

boot=Path('/boot/config.txt')
text=boot.read_text()
key='display_hdmi_rotate'
line=key+'='+settings[key]
if re.search(r'^'+key+r'\s*=',text,re.M):
    text=re.sub(r'^'+key+r'\s*=.*$',lambda m:line,text,flags=re.M)
else:
    text=line+'\n'+text
write(boot,text)

es=Path('/opt/retropie/configs/all/emulationstation/es_settings.cfg')
text=es.read_text()
# This ES version saves sibling elements without a single XML root.
pattern=r'<string\b[^>]*\bname="ThemeSet"[^>]*/?>'
def theme_tag(match):
    return re.sub(r'(\bvalue=")[^"]*(")',lambda m:m.group(1)+settings['theme']+m.group(2),match.group(0))
if re.search(pattern,text):
    text=re.sub(pattern,theme_tag,text)
else:
    text+='\n<string name="ThemeSet" value="'+settings['theme']+'" />\n'
write(es,text)
print('Vertical DK display profile applied; changed '+str(len(changed))+' files.')
for path in changed:
    print('Updated '+path)
