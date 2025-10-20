## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class NoStackTrait(Trait):
    ID                    = 'immob'
    NORMAL_SELECT         = ''
    SHIFT_SELECT          = 'i'
    CTRL_SELECT           = 't'
    ALT_SELECT            = 'c'
    NEVER_SELECT          = 'n'
    NORMAL_BAND_SELECT    = ''
    ALT_BAND_SELECT       = 'A'
    ALT_SHIFT_BAND_SELECT = 'B'
    NEVER_BAND_SELECT     = 'Z'
    NORMAL_MOVE           = 'N'
    SELECT_MOVE           = 'I'
    NEVER_MOVE            = 'V'
    NORMAL_STACK          = 'L'
    NEVER_STACK           = 'R'
    IGNORE_GRID           = 'g'
    def __init__(self,
                 select      = NORMAL_SELECT,
                 bandSelect  = NORMAL_BAND_SELECT,
                 move        = NORMAL_MOVE,
                 canStack    = False,
                 ignoreGrid  = False,
                 description = ''):
        '''No stacking trait

        (VASSAL.counter.Immobilized)
        '''
        selectionOptions = (select +
                            (self.IGNORE_GRID if ignoreGrid else '') +
                            bandSelect)
        movementOptions  = move
        stackingOptions  = self.NORMAL_STACK if canStack else self.NEVER_STACK
                 
        '''Create a mark trait (static property)'''
        super(NoStackTrait,self).__init__()
        
        self.setType(selectionOptions = selectionOptions,
                     movementOptions  = movementOptions,
                     stackingOptions  = stackingOptions,
                     description      = description)
        self.setState()


Trait.known_traits.append(NoStackTrait)

#
# EOF
#
