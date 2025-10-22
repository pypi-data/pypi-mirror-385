## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class GlobalCommandTrait(Trait):
    ID = 'globalkey'
    def __init__(self,
                 commandName   = '',
                 key           = '', # Command received
                 globalKey     = '', # Command to send to targets
                 properties    = '', # Filter target on this expression
                 ranged        = False,
                 range         = 1,
                 reportSingle  = True,
                 fixedRange    = True,
                 rangeProperty = '',
                 description   = '',
                 deckSelect    = '-1',
                 target        = ''):
        '''Create a global key command in piece.  This sends a key
        command to near-by counters, as if invoked by a global key
        (module window) command.

        This is _different_ from GlobalHotkeyTrait in that this does
        not invoke and actual module window global hot key, but rather
        sends the command directly to a near-by counter (just how
        close depends on the range or rangeProperty parameter).

        The `deckSelect` select either _all_ (value -1) or specified
        number of pieces from deck.
        
        (VASSAL.counters.CounterGlobalKeyCommand)

        '''
        self.setType(commandName   = commandName,
                     key           = key,
                     globalKey     = globalKey,
                     properties    = properties,
                     ranged        = ranged,
                     range         = range,
                     reportSingle  = reportSingle,
                     fixedRange    = fixedRange,
                     rangeProperty = rangeProperty,
                     description   = description,
                     deckSelect    = deckSelect,
                     target        = target)
        self.setState()
        
Trait.known_traits.append(GlobalCommandTrait)

#
# EOF
#
