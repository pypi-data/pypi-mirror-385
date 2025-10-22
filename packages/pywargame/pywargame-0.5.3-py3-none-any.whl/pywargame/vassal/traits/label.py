## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

class LabelTraitCodes:
    TOP    = 't'
    BOTTOM = 'b'
    CENTER = 'c'
    LEFT   = 'l'
    RIGHT  = 'r'
    PLAIN  = 0
    BOLD   = 1
    ITALIC = 2
    
# --------------------------------------------------------------------
class LabelTrait(Trait):
    ID     = 'label'
    def __init__(self,
                 label           = None,
                 labelKey        = '',
                 menuCommand     ='Change label',
                 fontSize        = 10,
                 background      = 'none',
                 foreground      = '255,255,255',
                 vertical        = LabelTraitCodes.TOP,
                 verticalOff     = 0,
                 horizontal      = LabelTraitCodes.CENTER,
                 horizontalOff   = 0,
                 verticalJust    = LabelTraitCodes.BOTTOM,
                 horizontalJust  = LabelTraitCodes.CENTER,
                 nameFormat      = '$pieceName$ ($label$)',
                 fontFamily      = 'Dialog',
                 fontStyle       = LabelTraitCodes.PLAIN,
                 rotate          = 0,
                 propertyName    = 'TextLabel',
                 description     = '',
                 alwaysUseFormat = False):
        '''Create a label trait (can be edited property)

        Note that rotation comes last in the operations.  That is,
        `horizontal...` and `vertical...` must be specified as if the
        label is not rotated, and then rotation is applied.

        Negative vertical offset moves the label _up_. 

        '''
        super(LabelTrait,self).__init__()
        if not background or background == 'none': background = ''
        if not foreground or foreground == 'none': foreground = ''
        self.setType(labelKey		= labelKey,
                     menuCommand	= menuCommand,
                     fontSize		= fontSize,
                     background		= background,
                     foreground		= foreground,
                     vertical		= vertical,
                     verticalOff	= verticalOff,
                     horizontal		= horizontal,
                     horizontalOff	= horizontalOff,
                     verticalJust	= verticalJust,
                     horizontalJust	= horizontalJust,
                     nameFormat		= nameFormat,
                     fontFamily		= fontFamily,
                     fontStyle		= fontStyle,
                     rotate		= rotate,
                     propertyName	= propertyName,
                     description	= description,
                     alwaysUseFormat	= alwaysUseFormat)
        self.setState(label = (nameFormat if label is None else label))


Trait.known_traits.append(LabelTrait)

#
# EOF
#
