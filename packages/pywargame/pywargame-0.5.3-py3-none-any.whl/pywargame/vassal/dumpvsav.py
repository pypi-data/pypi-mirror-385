#!/usr/bin/env python
## BEGIN_IMPORT
from pywargame.vassal import SaveIO
from pywargame import version_string
## END_IMPORT

# ====================================================================
def dumpMain():
    from argparse import ArgumentParser 

    ap = ArgumentParser(description='Dump VASSAL save or log')
    ap.add_argument('input',type=str,help='Input save')
    ap.add_argument('-m','--meta',action='store_true',
                    help='Also show metadata')
    ap.add_argument('-n','--line-numbers',action='store_true',
                    help='Prefix each line with a line number')
    ap.add_argument('--version',action='version',version=version_string)
    
    args = ap.parse_args()

    SaveIO.dumpSave(args.input,
                    alsometa=args.meta,
                    linenumbers=args.line_numbers)


# ====================================================================
if __name__ == '__main__':
    dumpMain()
#
#
#

    

    
