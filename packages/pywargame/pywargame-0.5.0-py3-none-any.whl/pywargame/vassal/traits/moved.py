## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class MovedTrait(Trait):
    ID = 'markmoved'
    def __init__(self,
                 image      = 'moved.gif',
                 xoff       = 36,
                 yoff       = -38,
                 name       = 'Mark moved',
                 key        = key('M'),
                 dummy      = ''  # Description
                 # ignoreSame = True
                 ):
        '''Create a moved trait (VASSAL.counters.MovementMarkable)'''
        super(MovedTrait,self).__init__()
        self.setType(image    = image,
                     xoff     = xoff,
                     yoff     = yoff,
                     name     = name,
                     key      = key,
                     dummy    = dummy, # Description
                     # ignoreSame = ignoreSame
                     )
        self.setState(moved = False)

Trait.known_traits.append(MovedTrait)

#
# EOF
#
