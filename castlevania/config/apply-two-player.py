#!/usr/bin/env python3
"""Configure the measured 0810:e001 two-player cabinet encoder only."""
from pathlib import Path
import os, pwd, re, shutil
import xml.etree.ElementTree as ET

HOME = Path('/home/pi')
devices = Path('/sys/bus/usb/devices')
present = any((p/'idVendor').exists() and (p/'idProduct').exists()
              and (p/'idVendor').read_text().strip().lower() == '0810'
              and (p/'idProduct').read_text().strip().lower() == 'e001'
              for p in devices.iterdir())
if not present:
    print('Twin encoder not connected; existing controls preserved.')
    raise SystemExit(0)

user = pwd.getpwnam('pi')
backup = HOME/'gijoel/backups/before-no-name-twin'
backup.mkdir(parents=True, exist_ok=True)
def save(path, text):
    path = Path(path)
    if path.exists() and path.read_text() == text:
        return
    old = backup/str(path).lstrip('/')
    if path.exists() and not old.exists():
        old.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(path),str(old))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if str(path).startswith('/home/pi/') or str(path).startswith('/opt/retropie/configs/'):
        os.chown(str(path),user.pw_uid,user.pw_gid)
    print('Updated twin controls: '+str(path))

# The descriptor contains two application collections with report IDs 1 and 2.
cmdline = Path('/boot/cmdline.txt')
parts = cmdline.read_text().strip().split()
token = next((x for x in parts if x.startswith('usbhid.quirks=')), None)
quirks = token.split('=',1)[1].split(',') if token else []
found = False
for i,q in enumerate(quirks):
    values = q.split(':')
    if len(values)==3 and int(values[0],16)==0x0810 and int(values[1],16)==0xe001:
        quirks[i] = '0x0810:0xe001:0x%08x' % (int(values[2],16)|0x40)
        found = True
if not found:
    quirks.append('0x0810:0xe001:0x00000040')
replacement = 'usbhid.quirks='+','.join(quirks)
parts = [replacement if x==token else x for x in parts]
if token is None:
    parts.append(replacement)
save(cmdline,' '.join(parts)+'\n')

name = 'NoName Generic USB Joystick'
guid = '030000001008000001e0000001010000'
es = HOME/'.emulationstation/es_input.cfg'
tree = ET.parse(str(es))
root = tree.getroot()
for entry in list(root.findall('inputConfig')):
    if entry.get('deviceGUID') == guid:
        root.remove(entry)
entry = ET.SubElement(root,'inputConfig',{'type':'joystick','deviceName':name,'deviceGUID':guid})
for label,kind,index,value in [
    ('up','axis',1,-1),('down','axis',1,1),('left','axis',0,-1),('right','axis',0,1),
    ('a','button',1,1),('b','button',0,1),('start','button',2,1),('select','button',3,1),
    ('righttrigger','button',5,1),('hotkeyenable','button',4,1)]:
    ET.SubElement(entry,'input',{'name':label,'type':kind,'id':str(index),'value':str(value)})
save(es,'<?xml version="1.0"?>\n'+ET.tostring(root,encoding='unicode')+'\n')

auto = {
 'input_device':name,'input_driver':'udev','input_vendor_id':'2064','input_product_id':'57345',
 'input_a_btn':'1','input_b_btn':'0','input_start_btn':'2','input_select_btn':'3',
 'input_r2_btn':'5','input_enable_hotkey_btn':'4','input_exit_emulator_btn':'2',
 'input_menu_toggle_btn':'5','input_reset_btn':'nul',
 'input_left_axis':'-0','input_right_axis':'+0','input_up_axis':'-1','input_down_axis':'+1',
}
save(HOME/'.config/retroarch/autoconfig'/ (name+'.cfg'), ''.join(k+' = "'+v+'"\n' for k,v in auto.items()))

# Measured board sides: report 2/js1 is physical P1; report 1/js0 is physical P2.
settings = {
 'input_player1_joypad_index':'1','input_player2_joypad_index':'0',
 'input_libretro_device_p1':'1','input_libretro_device_p2':'1',
 'input_enable_hotkey_btn':'4','input_exit_emulator_btn':'2','input_menu_toggle_btn':'5',
 'input_reset_btn':'nul',
}
for player in (1,2):
    prefix='input_player%d_'%player
    for button in ('a','b','x','y','l','r','l2','r2','l3','r3','start','select'):
        settings[prefix+button+'_btn']='nul'
    for direction,axis in [('up','-1'),('down','+1'),('left','-0'),('right','+0')]:
        settings[prefix+direction+'_axis']=axis
    settings[prefix+'analog_dpad_mode']='0'
settings.update({
 'input_player1_a_btn':'1','input_player1_b_btn':'0','input_player1_start_btn':'2',
 'input_player1_select_btn':'3','input_player1_r2_btn':'5',
 'input_player2_a_btn':'0','input_player2_b_btn':'1',
})
cfg=Path('/opt/retropie/configs/all/retroarch.cfg')
text=cfg.read_text()
for key,value in settings.items():
    pattern=r'^'+re.escape(key)+r'\s*=.*$'
    line=key+' = "'+value+'"'
    if re.search(pattern,text,re.M):
        text=re.sub(pattern,lambda m:line,text,flags=re.M)
    else:
        text+='\n'+line+'\n'
save(cfg,text)
print('Twin encoder configured: P1 device 1; P2 device 0. Hotkey+Start exits; Hotkey+R/T opens menu.')
