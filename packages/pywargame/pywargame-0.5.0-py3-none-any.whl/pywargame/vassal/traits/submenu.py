## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class SubMenuTrait(Trait):
    ID = 'submenu'
    def __init__(self,
                 subMenu     = '',  # Title
                 keys        = [],  # Keys
                 description = ''):
        '''Create a sub menu (VASSAL.counters.SubMenu)'''
        self.setType(subMenu     = subMenu,   # CLONEKEY
                     keys        = ','.join([k.replace(',',r'\,')
                                             for k in keys]),
                     description = description)
        self.setState() # PROPERTY COUNT (followed by [; KEY; VALUE]+)
    def setKeys(self,keys):
        '''Set the keys'''
        self['keys'] = ','.join([k.replace(',',r'\,') for k in keys])
        
Trait.known_traits.append(SubMenuTrait)

#
# EOF
#
