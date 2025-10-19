## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class DeleteTrait(Trait):
    ID = 'delete'
    def __init__(self,
                 name   = 'Delete',
                 key = key('D')):
        '''Create a delete trait (VASSAL.counters.Delete)'''
        super(DeleteTrait,self).__init__()
        self.setType(name  = name,
                     key   = key,
                     dummy = '')
        self.setState()

Trait.known_traits.append(DeleteTrait)

#
# EOF
#
