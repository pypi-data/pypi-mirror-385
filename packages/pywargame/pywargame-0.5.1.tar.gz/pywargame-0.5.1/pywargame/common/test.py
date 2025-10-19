#!/usr/bin/env python

from . verboseguard import VerboseGuard
from . verbose import Verbose

def inner():
    with VerboseGuard('Entering inner') as g:
        g('Message from inner')
        
def test():
    with VerboseGuard('Entering test'):
        inner()
    

if __name__ == '__main__':
    from argparse import ArgumentParser

    ap = ArgumentParser('test verbose')
    ap.add_argument('-v','--verbose',help='Be verbose',action='store_true')

    args = ap.parse_args()

    Verbose().setVerbose(args.verbose)
    
    test()
