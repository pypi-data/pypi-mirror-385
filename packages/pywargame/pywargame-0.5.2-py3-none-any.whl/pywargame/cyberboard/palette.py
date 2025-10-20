## BEGIN_IMPORT
from .. common import VerboseGuard
from . head import num_version, readVector
from . features import Features
## END_IMPORT

class GSNPalette:
    def __init__(self,ar):
        with VerboseGuard('Reading palette'):
            self._visible    = ar.word()
            self._comboIndex = ar.dword()
            self._topIndex   = ar.dword()
            
class GSNTrayPalette(GSNPalette):
    def __init__(self,ar,vers,iden):
        with VerboseGuard(f'Reading scenario tray palette {iden}'):
            super(GSNTrayPalette,self).__init__(ar)
            self._iden       = iden
            self._listSel    = readVector(ar,lambda ar : ar.dword())
            
    def __str__(self):
        return f'GSNTrayPalette: {self._comboIndex} '\
            f'{self._topIndex} {self._listSel}\n'

class GSNMarkPalette(GSNPalette):
    def __init__(self,ar,vers):
        with VerboseGuard(f'Reading scenario mark palette'):
            super(GSNMarkPalette,self).__init__(ar)
            self._listSel    = ar.dword()
    def __str__(self):
        return f'GSNMarkPalette: {self._comboIndex} '\
            f'{self._topIndex} {self._listSel}\n'

#
# EOF
#

