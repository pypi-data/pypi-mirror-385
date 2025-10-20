## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class GlobalHotkeyTrait(Trait):
    ID = 'globalhotkey'
    def __init__(self,
                 name          = '', # Command received
                 key           = '', # Command key received
                 globalHotkey  = '', # Key to send
                 description   = ''):
        '''Create a global key command in piece
        (VASSAL.counters.GlobalHotkey)'''
        self.setType(name          = name,
                     key           = key,
                     globalHotkey  = globalHotkey,
                     description   = description)
        self.setState()
        
Trait.known_traits.append(GlobalHotkeyTrait)

#
# EOF
#
