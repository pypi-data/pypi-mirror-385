## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class BasicTrait(Trait):
    ID = 'piece'
    def __init__(self,
                 name      = '',
                 filename  = '',  # Can be empty
                 gpid      = '',  # Can be empty
                 cloneKey  = '',  # Deprecated
                 deleteKey = ''): # Deprecated
        '''Create a basic unit (VASSAL.counters.BasicPiece)'''
        self.setType(cloneKey  = cloneKey,   # CLONEKEY
                     deleteKey = deleteKey,  # DELETEKEY
                     filename  = filename,   # IMAGE  
                     name      = name)       # NAME
        self.setState(map        = 'null', # MAPID (possibly 'null')
                      x          = 0,
                      y          = 0,
                      gpid       = gpid,
                      properties = 0) # PROPERTY COUNT (followed by [; KEY; VALUE]+)

    def getProperties(self):
        n = int(self._state[4])
        return {k: v for k, v in zip(self._state[5::2],
                                     self._state[6::2])}
        
Trait.known_traits.append(BasicTrait)

#
# EOF
#
