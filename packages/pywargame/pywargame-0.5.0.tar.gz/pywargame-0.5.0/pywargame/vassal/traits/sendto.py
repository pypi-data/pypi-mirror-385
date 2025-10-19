## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class SendtoTrait(Trait):
    ID = 'sendto'
    LOCATION = 'L'
    ZONE     = 'Z'
    REGION   = 'R'
    GRID     = 'G'
    COUNTER  = 'A'
    def __init__(self,
                 mapName     = '',
                 boardName   = '',
                 name        = '',
                 key         = key('E'),
                 restoreName = 'Restore',
                 restoreKey  = key('R'),
                 x           = 200,# Location
                 y           = 200,# Location
                 xidx        = 0,  # All - extra x
                 yidx        = 0,  # All - extra y
                 xoff        = 1,  # All - factor on xidx
                 yoff        = 1,  # All - factor on yidx
                 description = '',
                 destination = LOCATION,
                 zone        = '',  # Zone and region - expression
                 region      = '',  # Region - expression
                 expression  = '',  # Counter - expression?
                 position    = ''): # Grid - Fixed
        '''Create a send to trait (VASSAL.counter.SendToLocation)'''
        self.setType(name           = name,# NAME
                     key            = key,# KEY , MODIFIER
                     mapName        = mapName,# MAP
                     boardName      = boardName,# BOARD
                     x              = x,
                     y              = y,# X ; Y
                     restoreName    = restoreName,# BACK
                     restoreKey     = restoreKey,# KEY , MODIFIER
                     xidx           = xidx,
                     yidx           = yidx,# XIDX ; YIDX
                     xoff           = xoff,
                     yoff           = yoff,# XOFF ; YOFF
                     description    = description,# DESC
                     destination    = destination,# DEST type
                     zone           = zone,# ZONE
                     region         = region,# REGION
                     expression     = expression,# EXPRESSION
                     position       = position)                   # GRIDPOS
        self.setState(backMap = '', backX = '', backY = '')

Trait.known_traits.append(SendtoTrait)

#
# EOF
#
