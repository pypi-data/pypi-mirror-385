## BEGIN_IMPORT
from .. common import VerboseGuard
## END_IMPORT

class GSNWindow:
    def __init__(self,ar):
        with VerboseGuard('Reading window state') as g:
            self._code   = ar.word()
            self._user   = ar.word()
            self._board  = ar.iden()
            self._state  = [ar.dword() for _ in range(10)]
            n            = ar.size()
            g(f'Read {self._code} {self._user} {self._board} {self._state}')
            g(f'Reading {n} bytes at {ar.tell()}')
            self._buffer = ar.read(n)

    def __str__(self):
        return (f'code={self._code:04x} '
                f'user={self._user:04x} '
                f'board={self._board:04x} '
                f'buffer={len(self._buffer)}')
        
class GSNWindows:
    def __init__(self,ar):
        with VerboseGuard(f'Reading window states') as g: 
            self._savePositions = ar.word()
            self._enable        = ar.byte()
            n                   = ar.size() if self._enable else 0
            g(f'Save position: {self._savePositions}, '
              f'enable {self._enable} '
              f'n={n}')
            self._states        = [GSNWindow(ar) for _ in range(n)]

    def __str__(self):
        pl = '\n    '.join([str(s) for s in self._states])
        return f'Windows states ({len(self._states)})\n    {pl}\n'
    

#
# EOF
#
