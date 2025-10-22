## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class HideTrait(Trait):
    ID           = 'hide'
    ANY_SIDE     = 'side:'
    ANY_PLAYER   = 'player:'
    SIDES        = 'sides:'
    @classmethod
    def encodeAccess(cls,spec):
        if isinstance(spec,list) and len(spec) == 1:
            spec = spec[0]
        if isinstance(spec,str):
            if spec == cls.ANY_SIDE: return cls.ANY_SIDE
            if spec == cls.ANY_PLAYER: return cls.ANY_PLAYER
            return cls.SIDES+":"+spec
        return cls.SIDES+':'.join(spec)

    @classmethod
    def decodeAccess(cls,spec):
        if spec.startswith(cls.ANY_SIDE):   return cls.ANY_SIDE
        if spec.startswith(cls.ANY_PLAYER): return cls.ANY_PLAYER
        if spec.startswith(cls.SIDES):      return spec.split(':')[1:]
        return None
        
    def __init__(self,
                 key                   = '',
                 command               = '',
                 bgColor               = rgb(0x0,0x0,0x0),
                 access                = [],
                 transparency          = 1, # between 0 and 1
                 description           = '',
                 disableAutoReportMove = False,
                 state                 = 'null'):
        '''Create a hide trait (VASSAL.counter.Hideable)'''

        super().__init__()
        spec = self.encodeAccess(access)
        
        self.setType(key                   = key,      # Context menu key
                     command               = command,  # Context menu name
                     bgColor               = bgColor,
                     access                = spec,
                     transparency          = transparency,
                     description           = description,
                     disableAutoReportMove = disableAutoReportMove)     
        self.setState(hiddenBy = state)

    def getAccess(self):
        return self.decodeAccess(self['access'])

    def setAccess(self, access = []):
        self['access'] = self.encodeAccess(access)

        

        

Trait.known_traits.append(HideTrait)

#
# EOF
#
