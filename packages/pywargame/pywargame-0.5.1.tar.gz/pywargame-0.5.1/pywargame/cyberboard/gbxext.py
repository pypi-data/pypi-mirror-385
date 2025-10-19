#!/usr/bin/env python
#
# CyberBoard GitHub page:
#
#    https://github.com/CyberBoardPBEM/cbwindows
#
#
## BEGIN_IMPORT
from pywargame.cyberboard.gamebox   import GameBox
from pywargame.cyberboard.extractor import GBXExtractor
from pywargame.common               import Verbose
## END_IMPORT

# ====================================================================
def extractMain():
    from argparse import ArgumentParser, FileType
    from pathlib import Path

    ap = ArgumentParser(description='Extract information from a '
                        'CyberBoard GameBox file and store in ZIP archive',
                        epilog='Default output file name is input file name '
                        'with .gbx replaced by .zip')
    ap.add_argument('input', type=str, help='The file')
    ap.add_argument('output',type=str, nargs='?',help='Output',default='')
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ap.add_argument('-D','--dump',type=str,nargs='*',default='',
                    help='Dump content')
    ap.add_argument('-S','--size-bytes',type=int,choices=[4,8],
                    default=4, help='The size of size counts')
    ap.add_argument('-I','--id-bytes',type=int,choices=[2,4],
                    default=2, help='The size of identifiers')
    ap.add_argument('-P','--password',action='store_true',
                    help='Show password')

    args = ap.parse_args()
    Verbose().setVerbose(args.verbose)

    Features().size_size = args.size_bytes
    Features().id_size   = args.id_bytes
    
    gbx = GameBox.fromFile(args.input)
    if args.password:
        print(f'Password is "{gbx._info._password.decode()}"')
        
    rat = GBXExtractor(gbx)

    out = args.output
    if out == '':
        p = Path(args.input)
        out = p.stem+'.zip'
    
    rat.save(out)

    if 'save' in args.dump:
        print(rat)
    if 'gbx' in args.dump:
        print(gbx)
    

# ====================================================================
if __name__ == '__main__':
    extractMain()

#
# EOF
#
