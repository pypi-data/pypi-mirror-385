## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
# from .. widget import *
# from .. withtraits import PieceSlot
## END_IMPORT

# --------------------------------------------------------------------
class PlaceTrait(Trait):
    ID      = 'placemark'
    STACK_TOP = 0
    STACK_BOTTOM = 1
    ABOVE = 2
    BELOW = 3

    # How the LaTeX exporter organises the units.  Format with
    # 0: the group
    # 1: the piece name 
    # SKEL_PATH = (PieceWindow.TAG +r':Counters\/'        +
    #              TabWidget.TAG   +r':Counters\/'        +
    #              PanelWidget.TAG +':{0}'         +r'\/'+
    #              ListWidget.TAG  +':{0} counters'+r'\/'+
    #              PieceSlot.TAG   +':{1}')
    @classmethod
    # @property
    def SKEL_PATH(cls):
## BEGIN_IMPORT
        from .. widget import PieceWindow, TabWidget, PanelWidget, ListWidget
        from .. withtraits import PieceSlot
## END_IMPORT

        return (PieceWindow.TAG +r':Counters\/'        +
                TabWidget.TAG   +r':Counters\/'        +
                PanelWidget.TAG +':{0}'         +r'\/'+
                ListWidget.TAG  +':{0} counters'+r'\/'+
                PieceSlot.TAG   +':{1}')
    
    def __init__(self,
                 command         = '', # Context menu name
                 key             = '', # Context menu key
                 markerSpec      = '', # Full path in module
                 markerText      = 'null', # Hard coded message
                 xOffset         = 0,
                 yOffset         = 0,
                 matchRotation   = True,
                 afterKey        = '',
                 description     = '',
                 gpid            = '', # Set in JAVA, but with warning
                 placement       = ABOVE,
                 above           = False):
        '''Create a place marker trait (VASSAL.counter.PlaceMarker)'''
        super(PlaceTrait,self).__init__()
        self.setType(command         = command,          # Context menu name
                     key             = key,              # Context menu key
                     markerSpec      = markerSpec,
                     markerText      = markerText,
                     xOffset         = xOffset,
                     yOffset         = yOffset,
                     matchRotation   = matchRotation,
                     afterKey        = afterKey,
                     description     = description,
                     gpid            = gpid,
                     placement       = placement,
                     above           = above)
        self.setState()

Trait.known_traits.append(PlaceTrait)

# --------------------------------------------------------------------
class ReplaceTrait(PlaceTrait):
    ID = 'replace'
    def __init__(self,
                 command         = '', # Context menu name
                 key             = '', # Context menu key
                 markerSpec      = '', # Full path in module
                 markerText      = 'null', # Hard message
                 xOffset         = 0,
                 yOffset         = 0,
                 matchRotation   = True,
                 afterKey        = '',
                 description     = '',
                 gpid            = '', # Set in JAVA
                 placement       = PlaceTrait.ABOVE,
                 above           = False):
        super(ReplaceTrait,self).__init__(command         = command, 
                                          key             = key,  
                                          markerSpec      = markerSpec,
                                          markerText      = markerText,
                                          xOffset         = xOffset,
                                          yOffset         = yOffset,
                                          matchRotation   = matchRotation,
                                          afterKey        = afterKey,
                                          description     = description,
                                          gpid            = gpid,
                                          placement       = placement,
                                          above           = above)
    

Trait.known_traits.append(ReplaceTrait)

#
# EOF
#
