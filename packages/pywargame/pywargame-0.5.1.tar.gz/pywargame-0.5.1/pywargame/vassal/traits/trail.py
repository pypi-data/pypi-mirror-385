## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class TrailTrait(Trait):
    ID = 'footprint'
    def __init__(self,
                 key             = key('T'),
                 name            = 'Movement Trail',
                 localVisible    = False, # Start on
                 globalVisible   = True, # Visible to all players
                 radius          = 10,
                 fillColor       = rgb(255,255,255),
                 lineColor       = rgb(0,0,0),
                 activeOpacity   = 100,
                 inactiveOpacity = 50,
                 edgesBuffer     = 20,
                 displayBuffer   = 30,
                 lineWidth       = 5,
                 turnOn          = key(NONE,0)+',wgTrailsOn',
                 turnOff         = key(NONE,0)+',wgTrailsOff',
                 reset           = '',
                 description     = 'Enable or disable movement trail'):        
        ''' Create a movement trail trait ( VASSAL.counters.Footprint)'''
        super(TrailTrait,self).__init__()
        lw = (lineWidth
              if isinstance(lineWidth,str) and lineWidth.startswith('{') else
              int(lineWidth))
        ra = (radius
              if isinstance(radius,str) and radius.startswith('{') else
              int(radius))
        
        self.setType(key               = key,# ENABLE KEY
                     name              = name,# MENU 
                     localVisible      = localVisible,# LOCAL VISABLE
                     globalVisible     = globalVisible,# GLOBAL VISABLE
                     radius            = ra,# RADIUS
                     fillColor         = fillColor,# FILL COLOR
                     lineColor         = lineColor,# LINE COLOR 
                     activeOpacity     = activeOpacity,# ACTIVE OPACITY
                     inactiveOpacity   = inactiveOpacity,# INACTIVE OPACITY
                     edgesBuffer       = edgesBuffer,# EDGES BUFFER
                     displayBuffer     = displayBuffer,# DISPLAY BUFFER
                     lineWidth         = lw,# LINE WIDTH 
                     turnOn            = turnOn,# TURN ON KEY
                     turnOff           = turnOff,# TURN OFF KEY
                     reset             = reset,# RESET KEY
                     description       = description)       # DESC
        self.setState(isGlobal  = False,
                      map       = '',
                      points    = 0,     # POINTS (followed by [; [X,Y]*]
                      init      = False) 

Trait.known_traits.append(TrailTrait)

#
# EOF
#
