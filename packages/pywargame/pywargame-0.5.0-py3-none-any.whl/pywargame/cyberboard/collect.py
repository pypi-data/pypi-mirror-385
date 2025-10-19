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
                    default='cyberboard.py',
                    help='Output script name')
    ap.add_argument('-v','--verbose',action='store_true',
                    help='Be verbose')

    args = ap.parse_args()

    Verbose().setVerbose(args.verbose)

    c = Collector(executable=False)
    c.run(args.output,
          '../common/singleton.py',
          '../common/verbose.py',
          '../common/verboseguard.py',
          'features.py',
          'archive.py',
          'base.py',
          'head.py',
          'image.py',
          'tile.py',
          'piece.py',
          'mark.py',
          'draw.py',
          'cell.py',
          'board.py',
          'gamebox.py',
          'scenario.py',
          'player.py',
          'windows.py',
          'palette.py',
          'tray.py',
          'extractor.py')

    
