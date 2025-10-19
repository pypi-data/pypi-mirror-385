## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class DeselectTrait(Trait):
    ID = 'deselect'
    THIS = 'D' # Deselect only this piece
    ALL  = 'A' # Deselect all pieces 
    ONLY = 'S' # Select this piece only
    def __init__(self,
                 command     = '',
                 key         = '',
                 description = '',
                 unstack     = False,
                 deselect    = THIS):
        '''Create a deselect trait'''
        super(DeselectTrait,self).__init__()
        self.setType(command     = command,
                     key         = key,
                     description = description,
                     unstack     = unstack,
                     deselect    = deselect)
        self.setState()


Trait.known_traits.append(DeselectTrait)

#
# EOF
#
