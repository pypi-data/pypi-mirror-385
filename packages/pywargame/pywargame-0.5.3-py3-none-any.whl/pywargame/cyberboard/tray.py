## BEGIN_IMPORT
from .. common import VerboseGuard
from . head import num_version, readVector
from . features import Features
## END_IMPORT
    
class GSNTraySet:
    def __init__(self,ar,vers):
        with VerboseGuard(f'Reading tray set') as g:
            self._name          = ar.str()
            g(f'Tray set: {self._name}')
            self._random        = (ar.word() if Features().piece_100 else 0)
            self._visibleFlags  = ar.dword()
            self._ownerMask     = (ar.word() if vers < num_version(3,10) else
                                   ar.dword())
            self._restrict      = ar.word()
            self._pieces        = readVector(ar,lambda ar: ar.iden())

    def __len__(self):
        return len(self._pieces)

    def toDict(self):
        viz = self._visibleFlags & ~0xFFFF8000
        # print(f'{self._visibleFlags:08x} -> {viz}')
        vizStr = {0: 'all',
                  1: 'owner',
                  2: 'generic',
                  3: 'none'}.get(viz,'')
        return {'name':     self._name,
                'visible':  vizStr,
                'owner':    self._ownerMask,
                'restrict': self._restrict,
                'pieces':   self._pieces }
    
    def __str__(self):
        return (f'Tray set: {self._name} '
                f'[visible={self._visibleFlags},'
                f'ownerMask={self._ownerMask},'
                f'resrict={self._restrict}] '
                f'({len(self)}): {self._pieces}')


class GSNTrayManager:
    def __init__(self,ar,vers,iden=''):
        with VerboseGuard(f'Reading tray {iden} manager @ {ar.tell()}') as g:
            self._iden     = iden
            self._reserved = [ar.word() for _ in range(4)]
            g(f'{self._reserved}')
            self._dummy    = (ar.byte() if vers >= num_version(4,0) else 0)
            self._sets     = readVector(ar, lambda ar : GSNTraySet(ar,vers))

    def __len__(self):
        return len(self._sets)

    def toDict(self):
        return [s.toDict() for s in self._sets]
    
    def __str__(self):
        pl = '\n    '.join([str(s) for s in self._sets])
        return f'TrayManager: {self._iden} ({len(self)})\n    {pl}\n'


#
# EOF
#

        
            
            
