#!/usr/bin/env python3
"""Preserve cabinet saves; edit only P2 Button 2 and requested Coin/VS SMB B."""
from pathlib import Path
import base64, hashlib, json, os, pwd, shutil, struct

ROOT=Path(__file__).parent
CFG=Path('/home/pi/RetroPie/roms/mame-libretro/mame2003-plus/cfg')
BACKUP=Path('/home/pi/gijoel/backups/before-p2-button2-and-coin')
user=pwd.getpwnam('pi')
DEFAULT=0x10008002
P2_BUTTON2=0x1000007d  # JOYCODE_2_BUTTON1: counterpart of saved P1 B / 0x6d.
COIN=0x1000006f        # JOYCODE_1_BUTTON3 (RetroPad Y); arcade physical button 6.
B=0x1000006d           # JOYCODE_1_BUTTON1; physical P1 B.

def write(path,data):
    if path.exists() and path.read_bytes()==data:
        return
    old=BACKUP/str(path).lstrip('/')
    if path.exists() and not old.exists():
        old.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(str(path),str(old))
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    os.chown(str(path),user.pw_uid,user.pw_gid)

def seq(data,offset):
    count=struct.unpack_from('>H',data,offset)[0]
    end=offset+2+count*4
    if count>16 or end>len(data):
        raise ValueError('Invalid input sequence')
    return list(struct.unpack_from('>'+str(count)+'I',data,offset+2)),end

def replacement(values):
    return struct.pack('>H',len(values))+b''.join(struct.pack('>I',v) for v in values)

def patch(data,name):
    edits=[]
    if data[:8]==b'MAMEDEF\x07':
        offset=8
        while offset<len(data):
            kind=struct.unpack_from('>I',data,offset)[0]
            original,after_original=seq(data,offset+4)
            current,end=seq(data,after_original)
            target=None
            if kind&0x700ff==0x10010:
                target=[P2_BUTTON2]
            elif kind&0xff==0x2c:
                target=[COIN]
            elif kind&0x700ff==0x10 and not current:
                target=[B]
            elif kind&0x700ff==0x1000f and current in ([],[0x1000006e]):
                target=[0x1000007e]  # P2 A; the old single-deck binding used P1 A.
            if target is not None and current!=target:
                edits.append((after_original,end,replacement(target),hex(kind)))
            offset=end
    elif data[:8]==b'MAMECFG\x09':
        count=struct.unpack_from('>I',data,8)[0]
        offset=12
        for bank in range(2):
            for i in range(count):
                kind=struct.unpack_from('>I',data,offset)[0]
                current,end=seq(data,offset+8)
                target=None
                if bank==1:
                    if name=='suprmrio.cfg' and kind&0x700ff in (0xf,0x10,0x1000f,0x10010):
                        # VS SMB alone: swap A/B on both players; keep Coin separate.
                        target=[{0xf:0x1000006d,0x10:0x1000006e,
                                 0x1000f:0x1000007d,0x10010:0x1000007e}[kind&0x700ff]]
                    elif kind&0x700ff==0x10010:
                        target=[P2_BUTTON2]
                    elif kind&0xff==0x2c and current!=[DEFAULT]:
                        target=[COIN]
                if target is not None and current!=target:
                    edits.append((offset+8,end,replacement(target),hex(kind)))
                offset=end
    else:
        raise ValueError('Unrecognized MAME config: '+name)
    # Keep driver defaults, other inputs, DIP switches, coins and mixer byte-identical.
    result=data
    for start,end,value,kind in reversed(edits):
        result=result[:start]+value+result[end:]
    return result,[kind for start,end,value,kind in edits]

snapshot=ROOT/'saved-inputs.json'
if snapshot.exists():
    for path,encoded in json.loads(snapshot.read_text()).items():
        path=Path(path)
        allowed=(str(path).startswith(str(CFG)+'/') or
                 str(path).startswith('/opt/retropie/configs/nes/') or
                 str(path).startswith('/opt/retropie/configs/all/retroarch/config/FCEUmm/') or
                 path.suffix=='.rmp' and str(path).startswith('/opt/retropie/configs/'))
        if allowed and not path.exists():
            write(path,base64.b64decode(encoded))
            print('Restored missing saved input config: '+str(path))

audit=[]
for path in sorted(CFG.glob('*.cfg')):
    data=path.read_bytes()
    result,changes=patch(data,path.name)
    if changes:
        write(path,result)
        audit.append({'file':path.name,'inputs':changes,'before':hashlib.sha256(data).hexdigest(),
                      'after':hashlib.sha256(result).hexdigest()})
        print('Updated requested inputs: '+path.name+' '+','.join(changes))
if audit:
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/'changes.json').write_text(json.dumps(audit,indent=2)+'\n')
print('P2 Button 2, missing action inputs and dedicated arcade Coin configured; other native inputs preserved.')
