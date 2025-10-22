## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class CloneTrait(Trait):
    ID      = 'clone'
    def __init__(self,
                 command         = '',
                 key             = '',
                 description     = ''):
        '''Create a clone trait (VASSAL.counter.Clone)'''
        super().__init__()

        self.setType(command         = command,          # Context menu name
                     key             = key,              # Context menu key
                     description     = description)     
        self.setState(state='')

        

Trait.known_traits.append(CloneTrait)

#
# EOF
#
