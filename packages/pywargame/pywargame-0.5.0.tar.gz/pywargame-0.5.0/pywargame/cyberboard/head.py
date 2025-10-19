## BEGIN_IMPORT
from .. common import VerboseGuard
from . archive import Archive
from . features import Features
## END_IMPORT

def num_version(major,minor):
    return major * 256 + minor

def readVector(ar,cls):
    with VerboseGuard('Reading vector') as g:
        if Features().size_size == 8:
            n = ar.size()
        else:
            n                   = ar.word()
            if n == 0xFFFF:
                n               = ar.dword()
                if n == 0xFFFFFFFF:
                    n           = ar.int(64)
        g(f'{n} elements')
    return [cls(ar) for _ in range(n)]

# ====================================================================
class GBXHeader:
    BOX      = 'GBOX'
    SCENARIO = 'GSCN'
    def __init__(self,ar,expect=BOX):
        '''GBXHeader of file 

        4 bytes format ID
        4x1 byte format and program version

        8 bytes in total 
        '''
        with VerboseGuard('Reading header') as g:
            sig = ar.chr(len(expect))
            assert sig == expect, f'Not a {expect} file: {sig}'

            self._major        = ar.byte()
            self._minor        = ar.byte()
            self._programMajor = ar.byte()
            self._programMinor = ar.byte()
            self._vers         = num_version(self._major,self._minor)
            g(f'Version {self._major}.{self._minor}')

            assert self._vers >= num_version(3,0),\
                f'{self._major}.{self._minor} format not supported'

            if self._vers >= num_version(4,0):
                g(f'Detected version 4.0 or newer, setting some features')
                Features().id_size       = 4
                Features().size_size     = 8
                Features().sub_size      = 8
                Features().square_cells  = True
                Features().rotate_unit   = True
                Features().piece_100     = True
                Features().private_board = True
                Features().roll_state    = True
                
                
            


    def __str__(self):
        return ('Header:\n'
                f'  Format major version:  {self._major}\n'
                f'  Format minor version:  {self._minor}\n'
                f'  Program major version: {self._programMajor}\n'
                f'  Program minor version: {self._programMinor}\n')


# --------------------------------------------------------------------
class GBXStrings:
    def __init__(self,ar):
        '''Map IDs to strings'''
        with VerboseGuard(f'Reading string mappings'):
            strMapN = ar.size()
            
            self._id2str = {}
            for _ in range(strMapN):
                key = ar.dword()
                val = ar.str()
            
                self._id2str[key] = val

    def __str__(self):
        return ('Strings:\n'+
                '\n'.join([f'  {key:8x}: {val}'
                           for key,val in self._id2str.items()]))

# --------------------------------------------------------------------
class GSNStrings:
    def __init__(self,ar):
        '''Map IDs to strings'''
        with VerboseGuard(f'Reading string mappings'):
            strMapN = ar.size()
            
            self._id2str = {}
            for _ in range(strMapN):
                key = ar.size()
                val = ar.str()
            
                self._id2str[key] = val

    def __str__(self):
        return ('Strings:\n'+
                '\n'.join([f'  {key:8x}: {val}'
                           for key,val in self._id2str.items()]))
    
#
# EOF
#
