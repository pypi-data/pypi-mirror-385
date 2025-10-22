## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

class CargoTrait(Trait):
    ID = 'matPiece'
    NO_MAT = 'noMat'

    def __init__(self,
                 description = '',
                 maintainRelativeFacing = True,
                 detectionDistanceX     = 0,
                 detectionDistanceY     = 0,
                 attachKey              = '',
                 detachKey              = ''):
        '''Create cargo trait

        '''
        self.setType(description            = description,
                     maintainRelativeFacing = maintainRelativeFacing,
                     detectionDistanceX     = detectionDistanceX,
                     detectionDistanceY     = detectionDistanceY,
                     attachKey              = attachKey,
                     detachKey              = detachKey)
        self.setState(mat = CargoTrait.NO_MAT)

Trait.known_traits.append(CargoTrait)
        
#
# EOF
#
