#!/usr/bin/env python
## BEGIN_IMPORTS
from pywargame.vassal import Merger
from pywargame.common import Verbose
## END_IMPORTS

# ====================================================================        
def mergeMain():
    from argparse import ArgumentParser, FileType

    ap = ArgumentParser(description='Merge two modules or extensions')
    ap.add_argument('input',type=FileType('r'),help='Input files',nargs='+')
    ap.add_argument('-o','--output',type=FileType('w'),
                    help='Output file',nargs='?',default='Merged.vmod')
    ap.add_argument('-V','--verbose',action='store_true',
                    help='Be verbose')
    ap.add_argument('-p','--patch',type=FileType('r'),
                    help='Python patch script to execute after merging')
    ap.add_argument('-O','--overwrite',action='store_true',
                    help='Overwrite elements, attributes, files, '
                    'etc. with later specified content')
    ap.add_argument('-K','--keep',action='store_false',dest='overwrite',
                    help='Keep first elements, attributes, files, etc.')
    ap.add_argument('-S','--assume-same',action='store_true',
                    help='Assume all modules are same game')


    args = ap.parse_args()

    Verbose().setVerbose(args.verbose)
    
    if len(args.input) < 2:
        raise RuntimeError('At least two inputs must be given')

    outname = args.output.name
    args.output.close()

    merger = Merger(outname,*args.input)

    try:
        merger.run(patch       = args.patch,
                   overwrite   = args.overwrite,
                   assume_same = args.assume_same)
    except:
        from pathlib import Path

        op = Path(outname)
        op.unlink(missing_ok=True)
        
        raise
    
        
# ====================================================================        
if __name__ == '__main__':
    mergeMain()
    

#
#
#
