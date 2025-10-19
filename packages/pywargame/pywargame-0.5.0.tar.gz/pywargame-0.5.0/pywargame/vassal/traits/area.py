## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import rgb, key
## END_IMPORT

class AreaTrait(Trait):
    ID = 'AreaOfEffect'
    def __init__(self,
                 transparancyColor = rgb(0x77,0x77,0x77),
                 transparancyLevel = 30,
                 radius            = 1,
                 alwaysActive      = False,
                 activateCommand   = 'Toggle area of effect',
                 activateKey       = key('A'), # Ctrl-A
                 mapShaderName     = '',
                 fixedRadius       = True,
                 radiusMarker      = '', # Property
                 description       = 'Show area of effect',
                 name              = 'EffectArea',
                 onMenuText        = '', # Show area of effect
                 onKey             = '', # key('A')
                 offMenuText       = '', # Hide area of effect
                 offKey            = '', # key(A,SHIFT)
                 globallyVisible   = True):
        super(AreaTrait,self).__init__()
        self.setType(
                 transparancyColor = transparancyColor,
                 transparancyLevel = int(transparancyLevel),
                 radius            = radius,
                 alwaysActive      = alwaysActive,
                 activateCommand   = activateCommand,
                 activateKey       = activateKey,
                 mapShaderName     = mapShaderName,
                 fixedRadius       = fixedRadius,
                 radiusMarker      = radiusMarker,
                 description       = description,
                 name              = name,
                 onMenuText        = onMenuText,
                 onKey             = onKey,
                 offMenuText       = offMenuText,
                 offKey            = offKey,
                 globallyVisible   = globallyVisible)
        '''Create an area effect trait

        '''
        self.setState(active = alwaysActive or not globallyVisible)

Trait.known_traits.append(AreaTrait)
#
# EOF
#
