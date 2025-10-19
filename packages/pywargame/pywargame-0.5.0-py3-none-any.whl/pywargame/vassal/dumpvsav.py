#!/usr/bin/env python
## BEGIN_IMPORT
from pywargame.vassal import SaveIO
## END_IMPORT

# ====================================================================
def dumpMain():
    from argparse import ArgumentParser 

    ap = ArgumentParser(description='Dump VASSAL save or log')
    ap.add_argument('input',type=str,help='Input save')
    ap.add_argument('-m','--meta',action='store_true',help='Also metadata')
    
    args = ap.parse_args()

    ret  = SaveIO.readSave(args.input,args.meta)

    key, lines = ret[0], ret[1]
    if args.meta:
        savemeta, modulemeta = ret[2], ret[3]

    print('\n'.join(lines))

# ====================================================================
if __name__ == '__main__':
    dumpMain()
#
#
#

    

    
