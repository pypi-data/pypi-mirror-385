#!/usr/bin/env python
## BEGIN_IMPORTS
from pywargame.common     import Verbose
from pywargame.cyberboard.exporter    import GSNExporter
from pywargame.cyberboard.scenario    import Scenario
from pywargame.cyberboard.extractor   import GSNExtractor
from pywargame.cyberboard.head        import GBXHeader
## END_IMPORTS

# ====================================================================
def exportMain():
    
    from argparse import ArgumentParser, FileType, \
         RawDescriptionHelpFormatter 
    from textwrap import wrap, dedent
    from pathlib import Path

    w = lambda s : '\n\n'.join(['\n'.join(wrap(p))
                                for p in dedent(s).split('\n\n')])
    e = '''
    	   The script can only handle CyberBoard game boxes and scenarios
           from version 3 and up.  Use CBDesign.exe and CBPlay.exe to
           upgrade any pre-version 3 '.gbx' and '.gsn' files, respectively.

           You can override the game box files searched for by passing
           that game box file name to the option '--gamebox'.

           If the script finds the wrong main map, try passing the name
           of the main board as argument to the option '--main-board'.

           If the script adds boards (maps) to the 'Charts' menu,
           rather than as maps, pass a regular expression to match
           these board names, as argument to the option '--map-regex'.
    
           Pass a Python script with the option -p to do
           user post-processing with that script.  Use the
           pywargame VASSAL API to do all sorts of manipulations.
           '''
    
    ap = ArgumentParser(description='Create draft VASSAL module',
                        formatter_class= RawDescriptionHelpFormatter,
                        epilog=w(e))
    ap.add_argument('gsnfile',
                    help='The GSN file to data from',
                    type=FileType('rb'))
    ap.add_argument('-p','--patch',
                    help='A python script to patch generated module',
                    type=FileType('r'))
    ap.add_argument('-o','--output',
                    help='Output file to write module to',
                    type=str,
                    default='')
    ap.add_argument('-t','--title',
                    help='Override title',
                    type=str,
                    default=None)
    ap.add_argument('-v','--version',
                    help='Override version',
                    type=str,
                    default=None)
    ap.add_argument('-r','--rules',
                    help='Rules PDF file',
                    type=FileType('r'))
    ap.add_argument('-T','--tutorial',
                    help='Tutorial (v)log file',
                    type=FileType('r'))
    ap.add_argument('-W','--vassal-version',
                    help='Vassal version number',
                    type=str,
                    default='3.7.0')
    ap.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ap.add_argument('-G','--visible-grids',
                    action='store_true',
                    help='Make grids visible in the module')
    ap.add_argument('-X','--gamebox',
                    type=str,
                    default=None,
                    help='Override gamebox (.gbx) file')
    ap.add_argument('-M','--main-board',
                    type=str,
                    default=None,
                    help='Set the main board')
    ap.add_argument('-R','--map-regex',
                    type=str,
                    default=None,
                    help='Regular expression to match additional maps')
    ap.add_argument('-S','--scenario',
                    action='store_true',
                    help='Make scenario rather than at-start placements')


    args = ap.parse_args()
    
    gsnname   = args.gsnfile.name
    zipfile   = None
    vmodname  = args.output
    rulesname = args.rules.name    if args.rules    is not None else None
    tutname   = args.tutorial.name if args.tutorial is not None else None
    # Read first 4 bytes from input to see if we're dealing with a GSN file
    magic     = args.gsnfile.read(4)
    args.gsnfile.close()
    if magic != GBXHeader.SCENARIO.encode():
        if magic[:2] == 'PK'.encode():
            from zipfile import ZipFile
            zipfile = ZipFile(gsnname,'r')
    # args.output.close()

    if vmodname == '':
        p        = Path(gsnname)
        vmodname = p.stem+'.vmod'
    
    patchname = args.patch.name if args.patch is not None else None
    if args.patch is not None:
        args.patch.close()

    Verbose().setVerbose(args.verbose)
        
    try:
        scenario  = None
        if zipfile is None:
            scenario = Scenario.fromFile(gsnname,args.gamebox)
        extractor = GSNExtractor(scenario,zipfile)
        exporter  = GSNExporter(extractor._d,
                                title         = args.title,
                                version       = args.version,
                                rules         = rulesname,
                                tutorial      = tutname,
                                visible       = args.visible_grids,
                                main_board    = args.main_board,
                                map_regex     = args.map_regex,
                                vassalVersion = args.vassal_version,
                                do_scenario   = args.scenario)
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


# ====================================================================
if __name__ == '__main__':
    exportMain()

# ====================================================================
#
# EOF
#

