#!/usr/bin/env python
#
# CyberBoard GitHub page:
#
#    https://github.com/CyberBoardPBEM/cbwindows
#
#
# ====================================================================
## BEGIN_IMPORT
from pywargame.cyberboard.scenario  import Scenario
from pywargame.cyberboard.extractor import GSNExtractor
from pywargame.common               import Verbose
## END_IMPORT
    

# ====================================================================
def extractMain():
    from argparse import ArgumentParser, FileType
    from pathlib import Path

    ap = ArgumentParser(description='Extract information from a '
                        'CyberBoard Scenario file and store in ZIP archive',
                        epilog='Default output file name is input file name '
                        'with .gsn replaced by .zip')
    ap.add_argument('input', type=str, help='The file')
    ap.add_argument('output',type=str, nargs='?',help='Output',default='')
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ap.add_argument('-D','--dump',type=str,nargs='*',default='',
                    help='Dump content')
    ap.add_argument('-X','--gamebox',
                    type=str,
                    default=None,
                    help='Override gamebox (.gbx) file')

    args = ap.parse_args()
    Verbose().setVerbose(args.verbose)
    
    gsn = Scenario.fromFile(args.input,args.gamebox)
    rat = GSNExtractor(gsn)

    out = args.output
    if out == '':
        p = Path(args.input)
        out = p.stem+'.zip'
    rat.save(out)

    if 'save' in args.dump:
        print(rat)
    if 'gsn' in args.dump:
        print(gsn)

# ====================================================================
if __name__ == '__main__':
    extractMain()
    
#
# EOF
#

    

    
