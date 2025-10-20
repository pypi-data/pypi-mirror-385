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
                    default='vassal.py',
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
          '../common/dicedraw.py',
          'xmlns.py',
          'base.py',
          'element.py',
          'folder.py',
          'globalkey.py',
          'gameelements.py',
          'mapelements.py',
          'globalproperty.py',
          'turn.py',
          'documentation.py',
          'player.py',
          'chessclock.py',
          'widget.py',
          'grid.py',
          'zone.py',
          'board.py',
          'map.py',
          'chart.py',
          'command.py',
          'trait.py',
          'withtraits.py',
          'extension.py',
          'traits/area.py',
          'traits/clone.py',
          'traits/dynamicproperty.py',
          'traits/globalproperty.py',
          'traits/prototype.py',
          'traits/place.py',
          'traits/report.py',
          'traits/calculatedproperty.py',
          'traits/restrictcommand.py',
          'traits/label.py',
          'traits/layer.py',
          'traits/globalcommand.py',
          'traits/globalhotkey.py',
          'traits/nostack.py',
          'traits/deselect.py',
          'traits/restrictaccess.py',
          'traits/rotate.py',
          'traits/stack.py',
          'traits/mark.py',
          'traits/mask.py',
          'traits/trail.py',
          'traits/delete.py',
          'traits/sendto.py',
          'traits/moved.py',
          'traits/skel.py',
          'traits/submenu.py',
          'traits/basic.py',
          'traits/trigger.py',
          'traits/nonrect.py',
          'traits/click.py',
          'traits/mat.py',
          'traits/cargo.py',
          'traits/movefixed.py',
          'traits/sheet.py',
          'traits/hide.py',
          'traits/retrn.py',
          'game.py',
          'buildfile.py',
          'moduledata.py',
          'save.py',
          'vsav.py',
          'vmod.py',
          'upgrade.py',
          'exporter.py',
          'merger.py')

    
