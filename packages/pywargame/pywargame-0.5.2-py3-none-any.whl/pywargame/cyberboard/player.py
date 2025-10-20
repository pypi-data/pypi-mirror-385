## BEGIN_IMPORT
from .. common import VerboseGuard
## END_IMPORT

class GSNPlayerManager:
    def __init__(self,ar):
        with VerboseGuard(f'Reading players mappings'):
            self._enable  = ar.byte()
            self._players = []
            if self._enable:
                n             = ar.sub_size()
                self._players = [GSNPlayer(ar) for _ in range(n)]

    def toDict(self):
        return [p._name for p in self._players]

    def __str__(self):
        pl = '\n    '.join([str(s) for s in self._players])
        return ('Players:\n'
                f'  Enabled:      {self._enable}\n'
                f'  # players:    {len(self._players)}\n    {pl}\n')

class GSNPlayer:
    def __init__(self,ar):
        with VerboseGuard(f'Reading player'):
            self._key  = ar.dword()
            self._name = ar.str()


    def __str__(self):
        return f'Player: {self._name} (0x{self._key:08x})'

#
# EOF
#

