#!/usr/bin/env python
## BEGIN_IMPORT
from pywargame.cyberboard.gamebox import GBXInfo
from pywargame.cyberboard.head    import GBXHeader
from pywargame.cyberboard.archive import Archive
from pywargame                    import version_string
## END_IMPORT

# --------------------------------------------------------------------
nullpwd = b'\xee\n\xcbg\xbc\xdb\x92\x1a\x0c\xd2\xf1y\x83*\x96\xc9'

# --------------------------------------------------------------------
def zeropwd(filename):
    from pathlib import Path
    
    pos = None
    with Archive(filename,'rb') as ar:
        header       = GBXHeader(ar,GBXHeader.BOX)
        box          = GBXInfo(ar)
        pos          = ar.tell() - 4*2 - 2 - 2 - 16
        bid          = box._boxID

    # Zero password by md5 sum of game box ID
    from hashlib import md5
    nullpwd = md5(bid).digest()

    with open(filename,'rb') as file:
        cnt = file.read()
        old = cnt[pos:pos+16]
        # print(f'old password: {old}')
        # print(f'new password: {nullpwd}')
        # print(f'gamebox id:   {bid}')

    lcnt = list(cnt)
    lcnt[pos:pos+16] = list(nullpwd)
    ncnt = bytes(lcnt)

    on = Path(filename)
    on = on.with_stem(on.stem + '-new')
    with open(on,'wb') as file:
        file.write(ncnt)

# --------------------------------------------------------------------
def zeroPwdMain():        
    from argparse import ArgumentParser, FileType
    ap = ArgumentParser(description='Disable password in gamebox')
    ap.add_argument('input', type=str, help='The game box file')
    ap.add_argument('--version',action='store_true',
                    help='Show version number and exit')
    
    args = ap.parse_args()

    if args.version:
        print(version_string)
        return

    zeropwd(args.input)

# --------------------------------------------------------------------
if __name__ == '__main__':
    zeroPwdMain()
    
# --------------------------------------------------------------------
#
# EOF
#

