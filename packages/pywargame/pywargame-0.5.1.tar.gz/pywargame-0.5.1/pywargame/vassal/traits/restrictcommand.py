## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class RestrictCommandsTrait(Trait):
    ID = 'hideCmd'
    HIDE = 'Hide'
    DISABLE = 'Disable'
    def __init__(self,
                 name          = '',
                 hideOrDisable = HIDE,
                 expression    = '',# Restrict when true
                 keys          = []):
        '''Create a layer trait (VASSAL.counter.RestrictCommands)'''
        super(RestrictCommandsTrait,self).__init__()
        encKeys = ','.join([k.replace(',',r'\,') for k in keys])
        self.setType(name          = name,
                     hideOrDisable = hideOrDisable,
                     expression    = expression,
                     keys          = encKeys)
        self.setState(state='')
    def setKeys(self,keys):
        self['keys'] = ','.join([k.replace(',',r'\,') for k in keys])
    

Trait.known_traits.append(RestrictCommandsTrait)

#
# EOF
#
