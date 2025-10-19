#!/usr/bin/env python
import sys
sys.path.append('..')

from common import Verbose, VerboseGuard
from common.collector import Collector

        
if __name__ == '__main__':
    from argparse import ArgumentParser, FileType  

    ap = ArgumentParser(description='Collect to single script')
    ap.add_argument('output',
                    type=FileType('w'),
                    nargs='?',
                    default='gbxextract.py',
                    help='Output script name')
    ap.add_argument('-v','--verbose',action='store_true',
                    help='Be verbose')

    args = ap.parse_args()

    Verbose().setVerbose(args.verbose)

    c = Collector()
    c.run(args.output,
          'cyberboard.py',
          'gbxext.py')

    
