#!/usr/bin/env python
## BEGIN_IMPORT
from pywargame.vassal import SaveIO
from pywargame import version_string
## END_IMPORT

# ====================================================================
def str2pair(inp,asdict=True):
    inner = inp.split(':')
    if len(inner) == 1:
        inner = inp.split('=')

    return inner

# ====================================================================
def zeroMain():
    from argparse import ArgumentParser,  RawDescriptionHelpFormatter 
    from textwrap import wrap, dedent
    from pathlib import Path

    w = lambda s : '\n\n'.join(['\n'.join(wrap(p))
                                for p in dedent(s).split('\n\n')])
    e = '''
        USER, PASSWORD, and SIDE mappings are given as one or more
        elements in the format

        	user:new-value

        where "new-value" may be the new user name, password, or
        side. For example, to change a user from "alice" to "bob",
        pass

        	--user alice:bob

        If you also want to change user "charlie" to "daniella", then
        pass

        	--user alice:bob charlie:daniella

        or 
    
        	--user alice:bob --user charlie:daniella

        and similar for the "--password" and "--side" options.

        You can use the utility "vsavdump.py" to see the content of a
        Vassal save or log file.
    
        When mapping a user name to a new password or side, new
        effective user name is used.
    
        For example, if you map the user "alice" to the new user
        "bob", and you want to set the password of "bob" to be
        "secret", then you should give options like

        	--user alice:bob --password bob:secret
    
        Of course, if you want to change the of existing user
        "charlie" to "hello", then you simply pass
    
        	--password charlie:hello

        and similar when you are mapping sides.

        The output file, if not specified by the option "--output",
        defaults to the same as in the input filename with "-new"
        attached to the stem of the filename.  For example, if you are
        processing "Example.vsav", then you will get
        "Example-new.vsav"
        '''
    ap = ArgumentParser(description='Zero passwords/key VASSAL save or log',
                        formatter_class= RawDescriptionHelpFormatter,
                        epilog=w(e))
    ap.add_argument('input',type=str,help='Input save')
    ap.add_argument('-u','--user',type=str2pair,nargs='*',action='extend',
                    default=[], help='Map input user name to new user name')
    ap.add_argument('-p','--password',type=str2pair,nargs='*',action='extend',
                    default=[],help='Map new user name to new password')
    ap.add_argument('-s','--side',type=str2pair,nargs='*',action='extend',
                    default=[],help='Map new user name to new side')
    ap.add_argument('-k','--key',type=int,default=None,
                    help='Key to encode output save, in range 0-255')
    ap.add_argument('-o','--output',type=str,default=None,
                    help='Output file name')
    ap.add_argument('-V','--verbose',action='store_true',
                    help='Be verbose')
    ap.add_argument('--version',action='version',version=version_string)
    
    args = ap.parse_args()
    
    player_map = {a[0] : a[1] for a in args.user}
    passwd_map = {a[0] : a[1] for a in args.password}
    side_map   = {a[0] : a[1] for a in args.side}
        
    SaveIO.zeroSave(input      = args.input,
                    output     = args.output,
                    player_map = player_map,
                    passwd_map = passwd_map,
                    side_map   = side_map,
                    newkey     = args.key,
                    verbose    = args.verbose)

# ====================================================================
if __name__ == '__main__':
    zeroMain()
#
#
#

    

    
