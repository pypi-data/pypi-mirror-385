## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class ClickTrait(Trait):
    ID = 'button'
    def __init__(self,
                 key         = '',
                 x           = 0,
                 y           = 0,
                 width       = 0,
                 height      = 0,
                 description = '',
                 context     = False,
                 whole       = True,
                 version     = 1,
                 points      = []):
        '''Create a click trait (static property)'''
        super(ClickTrait,self).__init__()
        self.setType(key          = key,
                     x            = x,
                     y            = y,
                     width        = width,
                     height       = height,
                     description  = description,
                     context      = context,
                     whole        = whole,
                     version      = version,
                     npoints      = len(points),
                     points       = ';'.join([f'{p[0]};{p[1]}'
                                              for p in points]))            
        self.setState()


Trait.known_traits.append(ClickTrait)

#
# EOF
#
