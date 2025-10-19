## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from . dynamicproperty import ChangePropertyTrait
## END_IMPORT

# --------------------------------------------------------------------
class GlobalPropertyTrait(ChangePropertyTrait):
    # The real value of CURRENT_ZONE causes problems when copying the
    # trait, since it contains slashes.  Maybe a solition is to make
    # it a raw string with escaped slashes?  No, that's already done
    # below when setting the type.  However, the default in the Java
    # code is the CURRENT_ZONE real value, so setting this to the
    # empty string should make it be that value.
    ID = 'setprop'
    CURRENT_ZONE = 'Current Zone/Current Map/Module'
    NAMED_ZONE   = 'Named Zone'
    NAMED_MAP    = 'Named Map'
    DIRECT       = 'P'
    def __init__(self,
                 *commands,
                 name        = '',
                 numeric     = False,
                 min         = 0,
                 max         = 100,
                 wrap        = False,
                 description = '',
                 level       = CURRENT_ZONE,
                 search      = ''):
        '''Commands are

            - menu
            - key
            - Type (only 'P' for now)
            - Expression
        '''
        super(GlobalPropertyTrait,self).__init__(*commands,
                                                 numeric = numeric,
                                                 min     = min,
                                                 max     = max,
                                                 wrap    = wrap)
        self.setType(name        = name,
                     constraints = self._constraints,
                     commands    = self._commands,
                     description = description,
                     level       = level.replace('/',r'\/'),
                     search      = search)
        self.setState()

Trait.known_traits.append(GlobalPropertyTrait)

#
# EOF
#
