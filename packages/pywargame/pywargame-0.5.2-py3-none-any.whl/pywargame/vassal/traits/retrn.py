## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class ReturnTrait(Trait):
    ID      = 'return'
    def __init__(self,
                 command         = '',
                 key             = '',
                 deckId          = '',
                 prompt          = '',
                 description     = '',
                 version         = 2,
                 select          = False, # If true, select at run-time
                 expression      = ''
                 ):
        '''Create a return trait (VASSAL.counter.ReturnToDeck)'''
        super().__init__()

        self.setType(command         = command,          # Context menu name
                     key             = key,              # Context menu key
                     deckId          = deckId,
                     prompt          = prompt,
                     description     = description,
                     version         = version,
                     select          = select,
                     expression      = expression
                     )     
        self.setState(state='')

        

Trait.known_traits.append(ReturnTrait)

#
# EOF
#
