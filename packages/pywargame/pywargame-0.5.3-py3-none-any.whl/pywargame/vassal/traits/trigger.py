## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class TriggerTrait(Trait):
    ID      = 'macro'
    WHILE   = 'while'
    UNTIL   = 'until'
    COUNTED = 'counted' # - Always one "do ... while"
    def __init__(self,
                 name            = '',
                 command         = '', # Context menu name
                 key             = '', # Context menu key
                 property        = '', # Enable/Disable
                 watchKeys       = [],
                 actionKeys      = [], # What to do
                 loop            = False,
                 preLoop         = '', # Key
                 postLoop        = '', # Key
                 loopType        = COUNTED, # Loop type
                 whileExpression = '',
                 untilExpression = '',
                 count           = 0,
                 index           = False,
                 indexProperty   = '',
                 indexStart      = '',
                 indexStep       = ''):
        '''Create a layer trait (VASSAL.counter.Trigger)'''
        super(TriggerTrait,self).__init__()
        encWKeys = Trait.encodeKeys(watchKeys, ',')
        encAKeys = Trait.encodeKeys(actionKeys,',')
        self.setType(name            = name,            
                     command         = command,          # Context menu name
                     key             = key,              # Context menu key
                     property        = property,         # Enable/Disable
                     watchKeys       = encWKeys,       
                     actionKeys      = encAKeys,         # What to do
                     loop            = loop,            
                     preLoop         = preLoop,          # Key
                     postLoop        = postLoop,         # Key
                     loopType        = loopType,         # Loop type
                     whileExpression = whileExpression, 
                     untilExpression = untilExpression, 
                     count           = count,           
                     index           = index,           
                     indexProperty   = indexProperty,   
                     indexStart      = indexStart,      
                     indexStep       = indexStep)       
        self.setState(state='')

    def getActionKeys(self):
        return Trait.decodeKeys(self['actionKeys'],',')
    
    def getWatchKeys(self):
        return Trait.decodeKeys(self['watchKeys'],',')
    
    def setActionKeys(self,keys):
        self['actionKeys'] = Trait.encodeKeys(keys,',')
        
    def setWatchKeys(self,keys):
        self['watchKeys'] = Trait.encodeKeys(keys,',')
        
        

Trait.known_traits.append(TriggerTrait)

#
# EOF
#
