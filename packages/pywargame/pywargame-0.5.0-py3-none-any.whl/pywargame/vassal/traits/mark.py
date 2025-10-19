## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class MarkTrait(Trait):
    ID = 'mark'
    def __init__(self,name='',value=''):
        '''Create a mark trait (static property)'''
        super(MarkTrait,self).__init__()
        self.setType(name = name)
        self.setState(value = value)


Trait.known_traits.append(MarkTrait)

#
# EOF
#
