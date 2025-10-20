#!/usr/bin/env python
## BEGIN_IMPORTS
from pywargame.zuntzu.gamebox  import ZTGameBox
from pywargame.zuntzu.exporter import ZTExporter
from pywargame.common          import Verbose
from pywargame.zuntzu.base     import ZTImage
## END_IMPORTS

# ====================================================================
def exportMain():
    from argparse import ArgumentParser, FileType, \
         RawDescriptionHelpFormatter 
    from pathlib import Path
    from textwrap import wrap, dedent

    w = lambda s : '\n\n'.join(['\n'.join(wrap(p))
                                for p in dedent(s).split('\n\n')])
    e = '''
           If the script fails with "cache resources exhausted",
           try reducing the resolution (-r).

           If the ZunTzu game box does not have selectable
           boards, use the -a option to add all boards to
           the generated VASSAL module.

           Pass a Python script with the option -p to do
           user post-processing with that script.  Use the
           pywargame VASSAL API to do all sorts of manipulations.
           '''
    
    ap = ArgumentParser(description='Read in a ZunTzu GameBox',
                        formatter_class= RawDescriptionHelpFormatter,
                        epilog=w(e))
    ap.add_argument('input', type=FileType('rb'), 
                    help='Input ZunTzu GameBox')
    ap.add_argument('--output', '-o', type=str, nargs='?',
                    default='', help='Output VASSAL module')
    ap.add_argument('-p','--patch',
                    help='A python script to patch generated module',
                    type=FileType('r'))
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ap.add_argument('-r','--resolution',help='Set target DPI',type=int,
                    choices=[75,150,300,600],default=150)
    ap.add_argument('-a','--all-maps',action='store_true',
                    help='Generate all maps')
    ap.add_argument('-1','--one-map',action='store_false',dest='all_maps',
                    help='All maps are different versions of main map')
    ap.add_argument('-R','--n-rotations',type=int,
                    help='Number of rotations to allow. Set to 1 for '
                    'arbitrary rotations',default=12)
    ap.add_argument('-W','--vassal-version',
                    help='Vassal version number',
                    type=str,
                    default='3.7.0')
    ap.add_argument('-S','--symbolic-dice',
                    help='Use symbolic dice',
                    action='store_true')
    ap.add_argument('-T','--text-dice',
                    help='Use normal text dice',
                    dest='symbolic_dice',
                    action='store_false')
    ap.add_argument('-v','--version',
                    help='Override version',
                    type=str,
                    default='0.0.1')
    ap.set_defaults(symbolic_dice=True,
                    all_maps=False)


    args = ap.parse_args()

    Verbose().setVerbose(args.verbose)

    ZTImage.target_dpi = args.resolution
    output = args.output
    patch  = args.patch 
    if output == '':
        p      = Path(args.input.name)
        output = p.with_suffix('.vmod')
    if patch is not None:
        tmp = patch.name
        patch.close()
        patch = tmp
        
    gb = ZTGameBox(args.input)
    # gb.write_images()
    
    try:
        exporter = ZTExporter(gb,
                              version=args.version,
                              vassalVersion=args.vassal_version,
                              allmaps=args.all_maps,
                              nrotations=args.n_rotations,
                              symbolic_dice=args.symbolic_dice)
        exporter.run(output,patch)
    except Exception as e:
        from sys import stderr 
        from os import unlink
        
        print(f'Failed to build {output}: {e}',file=stderr)

        try:
            unlink(vmodname)
        except:
            pass

        raise e
    
# ====================================================================
if __name__ == '__main__':
    exportMain()
        
#
# EOF
#
