## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT


class MatTrait(Trait):
    ID = 'mat'

    def __init__(self,
                 name = 'Mat',
                 description = ''):
        '''Create mat trait

        '''
        self.setType(name        = name,
                     description = description)
        self.setState(content='0')

    def setContent(self,*args):
        # Not sure this is correct 
        self.setState(content=str(len(args))+';'+';'.joint(args))


Trait.known_traits.append(MatTrait)
	        
#
# EOF
#
