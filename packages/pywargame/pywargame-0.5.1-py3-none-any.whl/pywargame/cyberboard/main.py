#!/usr/bin/env python
#
# CyberBoard GitHub page:
#
#    https://github.com/CyberBoardPBEM/cbwindows
#
            
# ====================================================================
if __name__ == '__main__':
    from argparse import ArgumentParser, FileType
    from pathlib import Path
## BEGIN_IMPORT
    from gamebox   import GameBox
    from extractor import Extractor
    from common    import Verbose
## END_IMPORT

    ap = ArgumentParser(description='Read the file')
    ap.add_argument('input', type=str, help='The file')
    ap.add_argument('output',type=str, nargs='?',help='Output',default='')
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ap.add_argument('-D','--dump',type=str,nargs='*',default='',
                    help='Dump content')

    args = ap.parse_args()
    Verbose().setVerbose(args.verbose)
    
    gbx = GameBox.fromFile(args.input)
    rat = Extractor(gbx)

    out = args.output
    if out == '':
        p = Path(args.input)
        out = p.stem+'.zip'
    
    rat.save(out)

    if 'save' in args.dump:
        print(rat)
    if 'gbx' in args.dump:
        print(gbx)

    

    
