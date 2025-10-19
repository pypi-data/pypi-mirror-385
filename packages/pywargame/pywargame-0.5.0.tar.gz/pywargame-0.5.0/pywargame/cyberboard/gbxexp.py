#!/usr/bin/env python
## BEGIN_IMPORTS
from exporter    import GBXExporter
from common      import Verbose
from gamebox     import GameBox
from extractor   import GBXExtractor
## END_IMPORTS

# ====================================================================
if __name__ == '__main__':
    from argparse import ArgumentParser, FileType

    ap = ArgumentParser(description='Create draft VASSAL module')
    ap.add_argument('gbxfile',
                    help='The GBX file to data from',
                    type=FileType('r'))
    ap.add_argument('-p','--patch',
                    help='A python script to patch generated module',
                    type=FileType('r'))
    ap.add_argument('-o','--output',
                    help='Output file to write module to',
                    type=FileType('w'),
                    default='Draft.vmod')
    ap.add_argument('-r','--rules',
                    help='Rules PDF file',
                    type=FileType('r'))
    ap.add_argument('-T','--tutorial',
                    help='Tutorial (v)log file',
                    type=FileType('r'))
    ap.add_argument('-W','--vassal-version',
                    help='Vassal version number',
                    type=str,
                    default='3.6.7')
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ap.add_argument('-G','--visible-grids',
                    action='store_true',
                    help='Make grids visible in the module')


    args = ap.parse_args()

    gbxname   = args.gbxfile.name
    vmodname  = args.output.name
    rulesname = args.rules.name    if args.rules    is not None else None
    tutname   = args.tutorial.name if args.tutorial is not None else None
    args.output.close()
    args.gbxfile.close()

    patchname = args.patch.name if args.patch is not None else None
    if args.patch is not None:
        args.patch.close()

    Verbose().setVerbose(args.verbose)
        
    try:
        gamebox   = GameBox.fromFile(gbxname)
        extractor = GBXExtractor(gamebox)
        exporter  = GBXExporter(extractor._d,
                                rules         = rulesname,
                                tutorial      = tutname,
                                visible       = args.visible_grids,
                                vassalVersion = args.vassal_version)
        exporter.run(vmodname,patchname)
    except Exception as e:
        from sys import stderr 
        print(f'Failed to build {vmodname}: {e}',file=stderr)
        from os import unlink
        try:
            unlink(vmodname)
        except:
            pass

        raise e

