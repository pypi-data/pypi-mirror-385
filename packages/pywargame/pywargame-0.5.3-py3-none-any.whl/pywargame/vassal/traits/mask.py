## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
# Inset
# obs;88,130;ag_hide_1.png;Reveal;I;?;sides:Argentine;Peek;;true;;
# obs;88,130;ag_hide_1.png;Reveal;I;?;side:Argentine;;;true;;
#
# Peek
# obs;88,130;ag_hide_1.png;Reveal;P89,130;?;sides:Argentine;Peek;;true;;
#
# Image
#
class MaskTrait(Trait):
    ID = 'obs'
    INSET = 'I'
    BACKGROUND = 'B'
    PEEK = 'P'
    IMAGE = 'G'
    INSET2 = '2'
    PLAYER = 'player:'
    SIDE = 'side:'
    SIDES = 'sides:'
    def __init__(self,
                 keyCommand   = '',
                 imageName    = '',
                 hideCommand  = '',
                 displayStyle = '',
                 peekKey      = '',
                 ownerImage   = '',
                 maskedName   = '?',
                 access       = '',#?
                 peekCommand  = '',
                 description  = '',
                 autoPeek     = True,
                 dealKey      = '',
                 dealExpr     = ''):
        '''Create a masking trait'''
        super(MaskTrait,self).__init__()
        disp = displayStyle
        if displayStyle == self.PEEK:
            disp += peekKey
        elif displayStyle == self.IMAGE:
            disp += ownerImage
            
        acc = self.PLAYER
        if isinstance(access,list):
            acc = self.SIDES + ':'.join(access)
        elif access.startswith('player'):
            acc = self.PLAYER
        elif access.startswith('side'):
            acc = self.SIDE
                
        self.setType(keyCommand   = keyCommand,
                     imageImage   = imageName,
                     hideCommand  = hideCommand,
                     displayStyle = disp,
                     maskedName   = maskedName,
                     access       = acc, # ?
                     peekCommand  = peekCommand,
                     description  = description,
                     autoPeek     = autoPeek,
                     dealKey      = dealKey,
                     dealExpr     = dealExpr)
        self.setState(value='null')

    @classmethod
    def peekDisplay(cls,key):#Encoded key
        return cls.PEEK + key
    
    @classmethod
    def peekImage(cls,ownerImage):
        return cls.IMAGE + ownerImage

    @classmethod
    def sides(cls,*names):
        return cls.SIDES+':'.join(names)

Trait.known_traits.append(MaskTrait)

#
# EOF
#
