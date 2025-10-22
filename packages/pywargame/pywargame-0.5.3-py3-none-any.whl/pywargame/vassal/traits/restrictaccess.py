## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class RestrictAccessTrait(Trait):
    ID = 'restrict'
    def __init__(self,
                 sides         = [],
                 byPlayer      = False,
                 noMovement    = True,
                 description   = '',
                 owner         = '',):
        '''Create a layer trait (VASSAL.counter.Restricted)'''
        super(RestrictAccessTrait,self).__init__()
        encSides = ','.join(sides)
        self.setType(sides         = encSides,
                     byPlayer      = byPlayer,
                     noMovement    = noMovement,
                     description   = description)
        self.setState(owner=owner)

Trait.known_traits.append(RestrictAccessTrait)

#
# EOF
#
