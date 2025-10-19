## BEGIN_IMPORT
from .. common import VerboseGuard
from . features import Features
## END_IMPORT

# --------------------------------------------------------------------
class CbFont:
    def __init__(self,ar):
        '''Shared structure that holds font information'''
        # Fonts
        with VerboseGuard('Reading font definition'):
            self._size        = ar.word()
            self._flags       = ar.word()
            self._family      = ar.word()
            self._name        = ar.str()
            
    def isBold(self):
        return self._flags & 0x1

    def isItalic(self):
        return self._flags & 0x2

    def isUnderline(self):
        return self._flags & 0x4

    def __str__(self):
        return (f'Font:{self._name} ({self._family}) @ '
                f'{self._size} ({self._flags:08x})')

# --------------------------------------------------------------------
class CbManager:
    def __init__(self,ar):
        '''Base class for some managers'''
        with VerboseGuard('Reading general manager'):
            self._foreground  = ar.dword()
            self._background  = ar.dword()
            self._linewidth   = ar.word()
            self._font        = CbFont(ar)
            self._reserved    = [ar.word() for _ in range(4)]

    def _readNsub(self,ar,sub_size):
        return ar.int(sub_size)

    def _readSub(self,ar,cls,sub_size=None):
        if sub_size is None:
            sub_size = Features().sub_size
        with VerboseGuard(f'Reading sub {cls} of manager ({sub_size})'):
            n = self._readNsub(ar,sub_size)
            return [cls(ar) for _ in range(n)]

    def _strSub(self,title,subs):
        subl = '\n    '.join([str(s) for s in subs])
        return f'  # {title}: {len(subs)}\n    {subl}'

    def __str__(self):
        return (f'  Foreground:   {self._foreground:08x}\n'
                f'  Background:   {self._background:08x}\n'
                f'  Linewidth:    {self._linewidth}\n'
                f'  Font:         {self._font}\n'
                f'  Reserved:     {self._reserved}\n')

#
# EOF
#
