## BEGIN_IMPORT
from . base import *
from . element import ToolbarElement
## END_IMPORT

# --------------------------------------------------------------------
class GlobalKey(ToolbarElement):
    ## Fast filters
    ##
    ## Format:
    ##
    ##   GKCTYPE|LOCATION|<location>|PROPERTY|<property>
    ##
    ## where
    ##
    ##    GKCTYPE: MAP    (from Global),
    ##             MODULE (from GameGlobal)
    ##             DECK
    ##             COUNTER (from CounterGlobal)
    ##
    ##    LOCATION: true - filter on location
    ##              false - do not filter on location
    ##
    ##    PROPERTY: true - filter on property
    ##              false - do not filter on property
    ##
    ##    <location> is
    ##
    ##       TARGETTYPE|TARGETMAP|TARGETBOARD|TARGETZONE|TARGETLOCATION|TARGETX|TARGETY|TARGETDECK
    ##
    ##    <property> is
    ##
    ##       PROPERTYNAME|PROPERTYVALUE|COMPARE
    ##
    ##    TARGETTYPE: CURSTACK current stack or deck
    ##                CURMAP   current map
    ##                CURZONE  current zone
    ##                CURLOC   current location 
    ##                MAP      specified map      (TARGETMAP)
    ##                ZONE     specified zone     (TARGETZONE)
    ##                LOCATION specified location (TARGETLOCATION)
    ##                XY       specified X,Y      (TARGETBOARD,TARGETX,TARGETY)
    ##                DECK     specified deck     (TARGETDECK)
    ##                CURMAT   current mat
    ##                
    ##    PROPERTYNAME
    ##
    ##    PROPERTYVALUE: A constant
    ##    
    ##    COMPARE: EQUALS:         ==
    ##             NOT_EQUALS:     !=
    ##             GREATER:        >
    ##             GREATER_EQUALS: >=
    ##             LESS:           <
    ##             LESS_EQUALS:    <=
    ##             MATCH:          =~
    ##             NOT_MATCH       !~
    ##
    ## 
    SELECTED = 'MAP|false|MAP|||||0|0||true|Selected|true|EQUALS'
    UNIQUE = ['name']
    def __init__(self,
                 parent,
                 tag,
                 node                 = None,
                 name                 = '',                
                 icon                 = '',
                 tooltip              = '',
                 buttonHotkey         = '',
                 buttonText           = '',
                 canDisable           = False,
                 propertyGate         = '',
                 disabledIcon         = '',
                 # Local
                 hotkey               = '',
                 deckCount            = '-1',
                 filter               = '',
                 reportFormat         = '',
                 reportSingle         = False,
                 singleMap            = True,
                 target               = SELECTED):
        '''
        Parameters
        ----------
        - tag          The XML tag to use
        - parent       Parent node
        - node         Optionally existing node
        - name         Name of key
        - buttonHotkey Key in "global" scope
        - hotkey       Key to send to targeted pieces
        - buttonText   Text on button
        - canDisable   If true, disabled when propertyGate is true
        - deckCount    Number of decks (-1 is all)
        - filter       Which units to target
        - propertyGate When true, disable
        - reportFormat Chat message
        - reportSingle Also show single piece reports
        - singleMap    Only originating map if True
        - target       Preselection filter (default selected pieces)
        - tooltip      Hover-over message
        - icon         Image to use as icon

        Default targets are selected units
        '''
        
        super(GlobalKey,self).\
            __init__(parent,
                     tag,
                     node                 = node,
                     name                 = name,
                     icon                 = icon,
                     tooltip              = tooltip,
                     buttonHotkey         = buttonHotkey, # This hot key
                     buttonText           = buttonText,
                     canDisable           = canDisable,
                     propertyGate         = propertyGate,
                     disabledIcon         = disabledIcon,
                     hotkey               = hotkey,       # Target hot key
                     deckCount            = deckCount,
                     filter               = filter,
                     reportFormat         = reportFormat,
                     reportSingle         = reportSingle,
                     singleMap            = singleMap,
                     target               = target)
#
# EOF
# 
