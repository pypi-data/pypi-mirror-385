## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT


class MoveFixedTrait(Trait):
    ID = 'translate'

    def __init__(self,
                 command        = '',   # menu command,
                 key            = '',   # Hotkey or command
                 dx             = 0,    # X distance (int or expr))
                 dy             = 0,    # Y distance (int or expr))
                 stack          = False,# Move entire stack
                 xStepFactor    = 0,    # Factor on X offset (int or expr)
                 yStepFactor    = 0,    # Factor on Y offset (int or expr)
                 xStep          = 0,    # X offset (int or expr)
                 yStep          = 0,    # Y offset (int or expr)
                 description    = '',   # str 
                 ):
        '''Move a fixed distance.

           x' = dx + xStepFactor * xStep 
           y' = dy + yStepFactor * yStep 

        If piece can rotate, and this is trait is given _after_ (more
        recent in the traits list), then the piece will move according
        to the direction faced. If given _before_ (later in the traits list),
        then the move is relative  to the current map. 
        
        (VASSAL.counters.Translate)

        '''
        self.setType(command     = command,
                     key         = key,
                     dx          = dx,
                     dy          = dy,
                     stack       = stack,
                     xStepFactor = xStepFactor,
                     yStepFactor = yStepFactor,
                     xStep       = xStep,
                     yStep       = yStep,
                     description = description)
        self.setState()


Trait.known_traits.append(MoveFixedTrait)
#
# EOF
#
