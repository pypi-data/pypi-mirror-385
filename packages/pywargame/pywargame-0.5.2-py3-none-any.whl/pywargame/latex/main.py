#!/usr/bin/env python
## BEGIN_IMPORTS
from pywargame.latex.latexexporter import LaTeXExporter
from pywargame.vassal.vmod import VMod
from pywargame.common import Verbose
## END_IMPORTS

from argparse import ArgumentParser

class DefaultSubcommandArgParse(ArgumentParser):
    _default_subparser = None

    def set_default_subparser(self, name):
        self._default_subparser = name

    def _parse_known_args(self, arg_strings, *args, **kwargs):
        from argparse import _SubParsersAction
        in_args = set(arg_strings)
        d_sp    = self._default_subparser
        if d_sp is not None and not {'-h', '--help'}.intersection(in_args):
            for x in self._subparsers._actions:
                subparser_found = (
                    isinstance(x, _SubParsersAction) and
                    in_args.intersection(x._name_parser_map.keys())
                )
                if subparser_found:
                    break
            else:
                # insert default in first position, this implies no
                # global options without a sub_parsers specified
                arg_strings = [d_sp] + arg_strings
        return super(DefaultSubcommandArgParse, self)._parse_known_args(
            arg_strings, *args, **kwargs
        )
# ====================================================================
def patchIt(args):
    vmodname  = args.output.name
    patchname = args.patch.name
    args.output.close()
    args.patch .close()
    
    VMod.patch(vmodname, patchname, args.verbose)

# ====================================================================
def exportIt(args):

    vmodname  = args.output.name
    patchname = args.patch.name if args.patch is not None else None

    args.output.close()
    if args.patch is not None:
        args.patch.close()

    Verbose().setVerbose(args.verbose)

    try:
        if args.version.lower() == 'draft':
            args.visible_grids = True
            
        rulesname = args.rules.name    if args.rules    is not None else None
        tutname   = args.tutorial.name if args.tutorial is not None else None
        
        exporter  = LaTeXExporter(vmodname      = vmodname,
                                  pdfname       = args.pdffile.name,
                                  infoname      = args.infofile.name,
                                  title         = args.title,
                                  version       = args.version,
                                  description   = args.description,
                                  rules         = rulesname,
                                  tutorial      = tutname,
                                  patch         = patchname,
                                  visible       = args.visible_grids,
                                  vassalVersion = args.vassal_version,
                                  nonato        = args.no_nato_prototypes,
                                  nochit        = args.no_chit_information,
                                  resolution    = args.resolution,
                                  counterScale  = args.counter_scale,
                                  imageFormat   = args.image_format)
        exporter.run()
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
def exportMain():
    from argparse import ArgumentParser, FileType

    ap = DefaultSubcommandArgParse(description='Create draft VASSAL module')
    ap.set_default_subparser('export')
    sp = ap.add_subparsers(dest='mode')

    pp = sp.add_parser('patch',help='Patch VMod')
    pp.add_argument('output',
                    help='Module to patch',
                    type=FileType('r'),
                    default='Draft.vmod')
    pp.add_argument('patch',
                    help='A python script to patch generated module',
                    type=FileType('r'),
                    default='patch.py')
    pp.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')


    ep = sp.add_parser('export',help='Export from PDF and JSON to VMod')
    ep.add_argument('pdffile',
                    help='The PDF file to read images from',
                    type=FileType('r'),
                    default='export.pdf',
                    nargs='?')
    ep.add_argument('infofile',
                    help='The JSON file to read image information from',
                    type=FileType('r'),
                    default='export.json',
                    nargs='?')
    ep.add_argument('-o','--output',
                    help='Output file to write module to',
                    type=FileType('w'),
                    default='Draft.vmod')
    ep.add_argument('-p','--patch',
                    help='A python script to patch generated module',
                    type=FileType('r'))
    ep.add_argument('-V','--verbose',
                    help='Be verbose',
                    action='store_true')
    ep.add_argument('-t','--title',
                    help='Module title', default='Draft',
                    type=str)
    ep.add_argument('-v','--version',
                    help='Module version',
                    type=str,
                    default='draft')
    ep.add_argument('-r','--rules',
                    help='Rules PDF file',
                    type=FileType('r'))
    ep.add_argument('-T','--tutorial',
                    help='Tutorial (v)log file',
                    type=FileType('r'))
    ep.add_argument('-d','--description',
                    help='Short description of module',
                    type=str,
                    default='draft of module')
    ep.add_argument('-W','--vassal-version',
                    help='Vassal version number',
                    type=str,
                    default='3.7.12')
    ep.add_argument('-G','--visible-grids',
                    action='store_true',
                    help='Make grids visible in the module')
    ep.add_argument('-N','--no-nato-prototypes',
                    action='store_true',
                    help='Do not make prototypes for types,echelons,commands')
    ep.add_argument('-C','--no-chit-information',
                    action='store_true',
                    help='Do not make properties from chit information')
    ep.add_argument('-S','--counter-scale',
                    type=float, default=1,
                    help='Scale counters by factor')
    ep.add_argument('-R','--resolution',
                    type=int, default=150,
                    help='Resolution of images')
    ep.add_argument('-I','--image-format',
                    choices = ['png','svg'], default='png',
                    help='Image format to use')
    
    args = ap.parse_args()
    
    if args.mode == 'patch':
        patchIt(args)
    else:
        exportIt(args)
    
# ====================================================================
if __name__ == '__main__':
    exportMain()
    
#
# EOF
#
