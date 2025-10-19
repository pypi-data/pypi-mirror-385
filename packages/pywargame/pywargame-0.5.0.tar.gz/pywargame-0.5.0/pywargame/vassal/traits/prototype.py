## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class PrototypeTrait(Trait):
    ID = 'prototype'
    def __init__(self,name=''):
        '''Create a prototype trait (VASSAL.counter.UsePrototype)'''
        super(PrototypeTrait,self).__init__()
        self.setType(name = name)
        self.setState(ignored = '')


Trait.known_traits.append(PrototypeTrait)

#
# EOF
#
