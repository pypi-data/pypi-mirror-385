## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class RotateTrait(Trait):
    ID = 'rotate'
    def __init__(self,
                 nangles          = 6,
                 rotateCWKey      = key(']'),
                 rotateCCWKey     = key('['),
                 rotateCW         = 'Rotate CW',
                 rotateCCW        = 'Rotate CCW',
                 rotateFree       = 'Rotate ...',
                 rotateFreeKey    = key(']'),
                 rotateRndKey     = '',
                 rotateRnd        = '',
                 name             = 'Rotate',
                 description      = 'Rotate piece',
                 rotateDirectKey  = '',
                 rotateDirect     = '',
                 directExpression = '',
                 directIsFacing   = True,
                 angle            = 0):
        '''Create a Rotate trait'''
        super(RotateTrait,self).__init__()
        if nangles == 1:
            self.setType(nangles          = nangles,
                         rotateKey        = rotateFreeKey,
                         rotate           = rotateFree,
                         rotateRndKey     = rotateRndKey,
                         rotateRnd        = rotateRnd,
                         name             = name,
                         description      = description,
                         rotateDirectKey  = rotateDirectKey,
                         rotateDirect     = rotateDirect,
                         directExpression = directExpression,
                         directIsFacing   = directIsFacing)
        else:
            self.setType(nangles          = nangles,
                         rotateCWKey      = rotateCWKey,
                         rotateCCWKey     = rotateCCWKey,
                         rotateCW         = rotateCW,
                         rotateCCW        = rotateCCW,
                         rotateRndKey     = rotateRndKey,
                         rotateRnd        = rotateRnd,
                         name             = name,
                         description      = description,
                         rotateDirectKey  = rotateDirectKey,
                         rotateDirect     = rotateDirect,
                         directExpression = directExpression,
                         directIsFacing   = directIsFacing)
            
        self.setState(angle = int(angle) if nangles > 1 else float(angle))

Trait.known_traits.append(RotateTrait)

#
# EOF
#
