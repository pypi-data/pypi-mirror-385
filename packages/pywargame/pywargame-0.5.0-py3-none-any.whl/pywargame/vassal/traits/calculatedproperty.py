## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class CalculatedTrait(Trait):
    ID = 'calcProp'
    def __init__(self,name='',expression='',description=''):
        '''Define a trait that calculates a property'''
        super(CalculatedTrait,self).__init__()
        self.setType(name        = name,
                     expression  = expression,
                     description = description)
        self.setState()


Trait.known_traits.append(CalculatedTrait)

#
# EOF
#
