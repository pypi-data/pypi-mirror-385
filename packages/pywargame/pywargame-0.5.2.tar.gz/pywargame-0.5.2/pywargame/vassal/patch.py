#!/usr/bin/env python
#
# Patch a module
## BEGIN_IMPORTS
from pywargame.vassal import VMod
from pywargame.common import Verbose
## END_IMPORT

# ====================================================================
def patchIt(args):
    Verbose().setVerbose(args.verbose)
    
    vmodname  = args.output.name
    patchname = args.patch.name
    args.output.close()
    args.patch .close()
    
    VMod.patch(vmodname, patchname, args.verbose)

# ====================================================================
def patchMain():
    from argparse import ArgumentParser, FileType

    ap = ArgumentParser(description='Patch a module with a Python script')
    ap.add_argument('output',
                    help='Module to patch, will be overwritten',
                    type=FileType('r'))
    ap.add_argument('patch',
                    help='Python script to patch module',
                    type=FileType('r'),
                    nargs='?',
                    default='patch.py')
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')

    args = ap.parse_args()
    
    patchIt(args)
    
# ====================================================================
if __name__ == '__main__':
    patchMain()
    
#
# EOF
#
