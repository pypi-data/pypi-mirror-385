## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . withtraits import *
from . globalkey import *
## END_IMPORT

# --------------------------------------------------------------------
class MapElementService:
    def getMap(self):
        '''Get map - either a Map or WidgetMap'''
        ## BEGIN_IMPORT
        from . map import WidgetMap, Map
        ## END_IMPORT
        return self.getParentOfClass([WidgetMap,Map])
        # if self._parent is None:
        #     return None
        # 
        # if 'WidgetMap' in self._parent.tagName:
        #     return self.getParent(WidgetMap)
        #     
        # return self.getParent(Map)
    def getGame(self):
        m = self.getMap()
        if m is not None: return m.getGame()
        return None

# --------------------------------------------------------------------
class MapElement(Element,MapElementService):
    def __init__(self,map,tag,node=None,**kwargs):
        super(MapElement,self).__init__(map,tag,node=node,**kwargs)


# --------------------------------------------------------------------
class PieceLayers(MapElement):
    TAG=Element.MAP+'LayeredPieceCollection'
    UNIQUE = ['property']
    def __init__(self,map,node=None,
                 property = 'PieceLayer',
                 description = '',
                 layerOrder = []):
        super(PieceLayers,self).__init__(map,self.TAG,node=node,
                                         property    = property,
                                         description = description,
                                         layerOrder  = ','.join(layerOrder))

    def addControl(self,**kwargs):
        '''Add `LayerControl` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : LayerControl
            The added element
        '''
        return self.add(LayerControl,**kwargs)
    def getControls(self,asdict=True):
        '''Get all `LayerControl` element(s) from this

        Parameters
        ----------
        asdict : bool        
            If `True`, return a dictonary that maps name to
            `LayerControl` elements.  If `False`, return a list of all
            `LayerControl` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `LayerControl` children

        '''
        return self.getElementsByKey(LayerControl,'name',asdict)
                 
registerElement(PieceLayers)
    
# --------------------------------------------------------------------
class LayerControl(MapElement):
    TAG=Element.MAP+'LayerControl'
    CYCLE_UP='Rotate Layer Order Up'
    CYCLE_DOWN='Rotate Layer Order Down'
    ENABLE='Make Layer Active'
    DISABLE='Make Layer Inactive'
    TOGGLE='Switch Layer between Active and Inactive'
    RESET='Reset All Layers'
    UNIQUE = ['name']
    def __init__(self,col,node=None,
                 name         = '',
                 tooltip      = '',
                 text         = '',
                 hotkey       = '',
                 icon         = '',
                 canDisable   = False,
                 propertyGate = '', #Property name, disable when property false
                 disabledIcon = '',
                 command      = TOGGLE,
                 skip         = False,
                 layers       = [],
                 description = ''):
        super(LayerControl,self).__init__(col,self.TAG,node=node,
                                          name         = name,
                                          tooltip      = tooltip,
                                          text         = text,
                                          buttonText   = text,
                                          hotkey       = hotkey,
                                          icon         = icon,
                                          canDisable   = canDisable,
                                          propertyGate = propertyGate,
                                          disabledIcon = disabledIcon,
                                          command      = command,
                                          skip         = skip,
                                          layers       = ','.join(layers),
                                          description  = description)

    def getLayers(self):
        '''Get map - either a Map or WidgetMap'''
        return self.getParentOfClass([PieceLayers])
        
registerElement(LayerControl)
        

# --------------------------------------------------------------------
class LineOfSight(MapElement):
    TAG=Element.MAP+'LOS_Thread'
    ROUND_UP        = 'Up'
    ROUND_DOWN      = 'Down'
    ROUND_NEAREST   = 'Nearest whole number'
    FROM_LOCATION   = 'FromLocation'
    TO_LOCATION     = 'ToLocation'
    CHECK_COUNT     = 'NumberOfLocationsChecked'
    CHECK_LIST      = 'AllLocationsChecked'
    RANGE           = 'Range'
    NEVER           = 'Never'
    ALWAYS          = 'Always'
    WHEN_PERSISTENT = 'When persistent'
    CTRL_CLICK      = 'Cltr-Click & Drag'    
    UNIQUE          = ['threadName']
    
    def __init__(self,map,
                 node=None,
                 threadName         = 'LOS',
                 hotkey             = key('L',ALT),
                 tooltip            = 'Trace line of sight',
                 iconName           = '/images/thread.gif', #'los-icon.png',
                 label              = '',
                 snapLOS            = False,
                 snapStart          = True,
                 snapEnd            = True,
                 report             = (f'{{"Range from "+{FROM_LOCATION}'
                                       f'+" to "+{TO_LOCATION}+" is "'
                                       f'+{RANGE}+" (via "+{CHECK_LIST}+")"}}'),
                 persistent         = CTRL_CLICK,
                 persistentIconName = '/images/thread.gif',
                 globl              = ALWAYS,
                 losThickness       = 3,
                 threadColor        = rgb(255,0,0),
                 drawRange          = True,
                 # rangeBg            = rgb(255,255,255),
                 # rangeFg            = rgb(0,0,0),
                 rangeScale         = 0,
                 hideCounters       = True,
                 hideOpacity        = 50,
                 round              = ROUND_UP,
                 canDisable         = False,
                 propertyGate       = '',
                 disabledIcon       = ''):
        '''Make Line of Sight interface
        
        Parameters
        ----------
        threadName : str
            Name of interface
        hotkey : str
            Start LOS key
        tooltip : str
            Tool tip text
        iconName : str
            Path to button icon
        label : str
            Button text 
        snapLOS : bool
            Wether to snap both ends
        snapStart : bool
            Snap to start
        snapEnd: bool
            Snap to end
        report : str
            Report format
        persistent : str
            When persistent
        persistentIconName : str
            Icon when persistent(?)
        globl : str
            Visisble to opponents
        losThickness : int
            Thickness in pixels
        losColor : str
            Colour of line
        drawRange : bool
            Draw the range next to LOST thread
        rangeBg : str
            Range backgroung colour
        rangeFg : str
            Range foregrond colour
        rangeScale : int
            Scale of range - pixels per unit
        round : str
            How to round range
        hideCounters :bool
            If true, hide counters while making thread
        hideOpacity : int
            Opacity of hidden counters (percent)
        canDisable : bool
            IF true, then can be hidden
        propertyGate : str
            Name of property.  When that property is TRUE, then the
            interface is disabled.  Must be a property name, not an expression.
        disabledIcon : str
            Icon to use when disabled
        '''
        super(LineOfSight,self).__init__(map,self.TAG,
                                         node = node,
                                         threadName         = threadName,
                                         hotkey             = hotkey,
                                         tooltip            = tooltip,
                                         iconName           = iconName,
                                         label              = label,
                                         snapLOS            = snapLOS,
                                         snapStart          = snapStart,
                                         snapEnd            = snapEnd,
                                         report             = report,
                                         persistent         = persistent,
                                         persistentIconName = persistentIconName,
                                         losThickness       = losThickness,
                                         threadColor        = threadColor,
                                         drawRange          = drawRange,
                                         #rangeBg            = rangeBg,
                                         #rangeFg            = rangeFg,
                                         rangeScale         = rangeScale,
                                         hideCounters       = hideCounters,
                                         hideOpacity        = hideOpacity,
                                         round              = round,
                                         canDisable         = canDisable,
                                         propertyGate       = propertyGate,
                                         disabledIcon       = disabledIcon)
        self.setAttribute('global',globl)
                                     
    
registerElement(LineOfSight)
    
# --------------------------------------------------------------------
class StackMetrics(MapElement):
    TAG=Element.MAP+'StackMetrics'
    def __init__(self,map,node=None,
                 bottom               = key('(',0),
                 down                 = key('%',0),
                 top                  = key('&',0),
                 up                   = key("'",0),
                 disabled             = False,
                 exSepX               = 16,  # Expanded (after double click)
                 exSepY               = 24,  # Expanded (after double click)
                 unexSepX             = 8,   # Compact
                 unexSepY             = 16): # Compact
        super(StackMetrics,self).__init__(map,self.TAG,node=node,
                                          bottom               = bottom,
                                          disabled             = disabled,
                                          down                 = down,
                                          exSepX               = exSepX,
                                          exSepY               = exSepY,
                                          top                  = top,
                                          unexSepX             = unexSepX,
                                          unexSepY             = unexSepY,
                                          up                   = up)

registerElement(StackMetrics)

# --------------------------------------------------------------------
class MoveCamera(MapElement):
    TAG=Element.MAP+'MoveCameraButton'
    LOCATION = 'L'  # Pixel location
    ZONE     = 'Z'  # Zone on board
    REGION   = 'R'  # Region on board
    GRID     = 'G'  # Grid location 
    COUNTER  = 'A'  # Counter by property
    CYCLE    = 'C'  # Cycle through counters by property
    NEAREST  = 'N'  # Nearest counter by property
    def __init__(self,map,node=None,
                 name             = '',            # Comment
                 tooltip          = 'Move camera to location',
                 text             = 'Move camera', # Button text
                 hotkey           = key('C',ALT),  # Hot key
                 icon             = 'recenter.gif',# Button icon
                 canDisable       = False,         # Can be disabled
                 propertyGate     = '',            # Disable when property true
                 disabledIcon     = '',            # Hidden button icon
                 hideWhenDisabled = False,         # Do not show when hidden
                 zoom             = 0,             # Adjust zoom - 0: no chang 
                 moveCameraMode   = GRID,          # Where to move camera
                 boardName        = '',            # Board to move to
                 xPos             = 0,             # Pixel X
                 yPos             = 0,             # Pixel Y
                 zoneName         = '',            # Zone name
                 gridLocation     = '',            # Grid Location
                 regionName       = '',            # Region name
                 propertyFilter   = '',            # Piece 
                 xOffset          = 0,             # Additional offset
                 yOffset          = 0):            # Additional offset
        super(MoveCamera,self).__init__(map,self.TAG,node=node,
                                        name             = name,
                                        tooltip          = tooltip,
                                        text             = text,
                                        hotkey           = hotkey,
                                        icon             = icon,
                                        canDisable       = canDisable,
                                        propertyGate     = propertyGate,
                                        disabledIcon     = disabledIcon,
                                        hideWhenDisabled = hideWhenDisabled,
                                        zoom             = zoom,
                                        moveCameraMode   = moveCameraMode,
                                        boardName        = boardName,
                                        xPos             = xPos,
                                        yPos             = yPos,
                                        zoneName         = zoneName,
                                        gridLocation     = gridLocation,
                                        regionName       = regionName,
                                        propertyFilter   = propertyFilter,
                                        xOffset          = xOffset,
                                        yOffset          = yOffset)

registerElement(MoveCamera)

# --------------------------------------------------------------------
class ImageSaver(MapElement):
    TAG=Element.MAP+'ImageSaver'
    def __init__(self,map,node=None,
                 buttonText           = '',
                 canDisable           = False,
                 hotkey               = '',
                 icon                 = '/images/camera.gif',
                 propertyGate         = '',
                 tooltip              = 'Save map as PNG image'):
        super(ImageSaver,self).__init__(map,self.TAG,node=node,
                                        buttonText           = buttonText,
                                        canDisable           = canDisable,
                                        hotkey               = hotkey,
                                        icon                 = icon,
                                        propertyGate         = propertyGate,
                                        tooltip              = tooltip)

registerElement(ImageSaver)

# --------------------------------------------------------------------
class TextSaver(MapElement):
    TAG=Element.MAP+'TextSaver'
    def __init__(self,map,node=None,
                 buttonText           = '',
                 canDisable           = False,
                 hotkey               = '',
                 icon                 = '/images/camera.gif',
                 propertyGate         = '',
                 tooltip              = 'Save map as text'):
        super(TextSaver,self).__init__(map,self.TAG,node=node,
                                        buttonText           = buttonText,
                                        canDisable           = canDisable,
                                        hotkey               = hotkey,
                                        icon                 = icon,
                                        propertyGate         = propertyGate,
                                        tooltip              = tooltip)

registerElement(TextSaver)

# --------------------------------------------------------------------
class ForwardToChatter(MapElement):
    TAG=Element.MAP+'ForwardToChatter'
    def __init__(self,map,node=None,**kwargs):
        super(ForwardToChatter,self).__init__(map,self.TAG,node=node,**kwargs)

registerElement(ForwardToChatter)

# --------------------------------------------------------------------
class MenuDisplayer(MapElement):
    TAG=Element.MAP+'MenuDisplayer'
    def __init__(self,map,node=None,**kwargs):
        super(MenuDisplayer,self).__init__(map,self.TAG,node=node,**kwargs)

registerElement(MenuDisplayer)

# --------------------------------------------------------------------
class MapCenterer(MapElement):
    TAG=Element.MAP+'MapCenterer'
    def __init__(self,map,node=None,**kwargs):
        super(MapCenterer,self).__init__(map,self.TAG,node=node,**kwargs)

registerElement(MapCenterer)

# --------------------------------------------------------------------
class StackExpander(MapElement):
    TAG=Element.MAP+'StackExpander'
    def __init__(self,map,node=None,**kwargs):
        super(StackExpander,self).__init__(map,self.TAG,node=node,**kwargs)

registerElement(StackExpander)

# --------------------------------------------------------------------
class PieceMover(MapElement):
    TAG=Element.MAP+'PieceMover'
    def __init__(self,map,node=None,**kwargs):
        super(PieceMover,self).__init__(map,self.TAG,node=node,**kwargs)

registerElement(PieceMover)

# --------------------------------------------------------------------
class SelectionHighlighters(MapElement):
    TAG=Element.MAP+'SelectionHighlighters'
    def __init__(self,map,node=None,**kwargs):
        super(SelectionHighlighters,self).\
            __init__(map,self.TAG,node=node,**kwargs)

registerElement(SelectionHighlighters)

# --------------------------------------------------------------------
class KeyBufferer(MapElement):
    TAG=Element.MAP+'KeyBufferer'
    def __init__(self,map,node=None,**kwargs):
        super(KeyBufferer,self).__init__(map,self.TAG,node=node,**kwargs)

registerElement(KeyBufferer)

# --------------------------------------------------------------------
class HighlightLastMoved(MapElement):
    TAG=Element.MAP+'HighlightLastMoved'
    def __init__(self,map,node=None,
                 color     = rgb(255,0,0),
                 enabled   = True,
                 thickness = 2):
        super(HighlightLastMoved,self).__init__(map,self.TAG,node=node,
                                                color     = color,
                                                enabled   = enabled,
                                                thickness = thickness)

registerElement(HighlightLastMoved)

# --------------------------------------------------------------------
class CounterDetailViewer(MapElement):
    TAG=Element.MAP+'CounterDetailViewer'
    TOP_LAYER  = 'from top-most layer only'
    ALL_LAYERS = 'from all layers'
    INC_LAYERS = 'from listed layers only'
    EXC_LAYERS = 'from layers other than those listed'
    FILTER     = 'by using a property filter'
    ALWAYS     = 'always'
    NEVER      = 'never'
    IF_ONE     = 'ifOne'
    UNIQUE     = ['description']
    def __init__(self,map,node=None,
                 borderWidth            = 0, # Horizontal padding between pieces
                 borderThickness        = 2, # Outer border thickness
                 borderInnerThickness   = 2, # Inner borders thickness
                 borderColor            = None,
                 centerAll              = False,
                 centerText             = False,
                 centerPiecesVertically = True,
                 combineCounterSummary  = False,
                 counterReportFormat    = '',
                 delay                  = 700,
                 description            = '',
                 display                = TOP_LAYER,
                 emptyHexReportForma    = '$LocationName$',
                 enableHTML             = True,
                 extraTextPadding       = 0,
                 bgColor                = None,
                 fgColor                = rgb(0,0,0),
                 fontSize               = 11,
                 graphicsZoom           = 1.0,# Zoom on counters
                 hotkey                 = key('\n'),
                 layerList              = [],
                 minDisplayPieces       = 2,
                 propertyFilter         = '',
                 showDeck               = False,
                 showDeckDepth          = 1,
                 showDeckMasked         = False,
                 showMoveSelected       = False,
                 showNoStack            = False,
                 showNonMovable         = False,
                 showOverlap            = False,
                 showgraph              = True,
                 showgraphsingle        = False,
                 showtext               = True,
                 showtextsingle         = False,
                 stretchWidthSummary    = False,
                 summaryReportFormat    = '$LocationName$',
                 unrotatePieces         = False,
                 version                = 4,
                 verticalOffset         = 2,
                 verticalTopText        = 0,
                 zoomlevel              = 1.0,
                 stopAfterShowing       = False,
                 showTerrainBeneath     = NEVER,
                 showTerrainSnappy      = True,
                 showTerrainWidth       = 120,
                 showTerrainHeight      = 120,
                 showTerrainZoom        = None,
                 showTerrainText        = ''
                 ): # showTerrain attributes

        bg = '' if bgColor is None else bgColor
        fg = '' if fgColor is None else fgColor
        bc = '' if borderColor is None else borderColor
        ll = ','.join(layerList)
        showTerrainZoom = zoomlevel if showTerrainZoom == None else showTerrainZoom
        super(CounterDetailViewer,self)\
            .__init__(map,self.TAG,node=node,
                      borderWidth            = borderWidth,
                      borderThickness        = borderThickness,
                      borderInnerThickness   = borderInnerThickness,
                      borderColor            = bc,
                      centerAll              = centerAll,
                      centerText             = centerText,
                      centerPiecesVertically = centerPiecesVertically,
                      combineCounterSummary = combineCounterSummary,
                      counterReportFormat   = counterReportFormat,
                      delay                 = delay,
                      description           = description,
                      display               = display, # How to show from layers
                      emptyHexReportForma   = emptyHexReportForma,
                      enableHTML            = enableHTML,
                      extraTextPadding      = extraTextPadding,
                      bgColor               = bg,
                      fgColor               = fg,
                      fontSize              = fontSize,
                      graphicsZoom          = graphicsZoom, # pieces at zoom
                      hotkey                = hotkey,
                      layerList             = ll,
                      minDisplayPieces      = minDisplayPieces,
                      propertyFilter        = propertyFilter,
                      showDeck              = showDeck,
                      showDeckDepth         = showDeckDepth,
                      showDeckMasked        = showDeckMasked,
                      showMoveSelectde      = showMoveSelected,
                      showNoStack           = showNoStack,
                      showNonMovable        = showNonMovable,
                      showOverlap           = showOverlap,
                      showgraph             = showgraph,
                      showgraphsingle       = showgraphsingle,
                      showtext              = showtext,
                      showtextsingle        = showtextsingle,
                      stretchWidthSummary   = stretchWidthSummary,
                      summaryReportFormat   = summaryReportFormat,
                      unrotatePieces        = unrotatePieces,
                      version               = version,
                      verticalOffset        = verticalOffset,
                      verticalTopText       = verticalTopText,
                      zoomlevel             = zoomlevel,
                      stopAfterShowing      = stopAfterShowing,
                      showTerrainBeneath    = showTerrainBeneath,
                      showTerrainSnappy     = showTerrainSnappy,
                      showTerrainWidth      = showTerrainWidth,
                      showTerrainHeight     = showTerrainHeight,
                      showTerrainZoom       = showTerrainZoom,
                      showTerrainText       = showTerrainText)

registerElement(CounterDetailViewer)

# --------------------------------------------------------------------
class GlobalMap(MapElement):
    TAG=Element.MAP+'GlobalMap'
    def __init__(self,map,node=None,
                 buttonText           = '',
                 color                = rgb(255,0,0),
                 hotkey               = key('O',CTRL_SHIFT),
                 icon                 = '/images/overview.gif',
                 scale                = 0.2,
                 tooltip              = 'Show/Hide overview window'):
        super(GlobalMap,self).\
            __init__(map,self.TAG,node=node,
                     buttonText           = buttonText,
                     color                = color,
                     hotkey               = hotkey,
                     icon                 = icon,
                     scale                = scale,
                     tooltip              = 'Show/Hide overview window')

registerElement(GlobalMap)

# --------------------------------------------------------------------
class Zoomer(MapElement):
    TAG = Element.MAP+'Zoomer'
    def __init__(self,map,node=None,
                 inButtonText         = '',
                 inIconName           = '/images/zoomIn.gif',
                 inTooltip            = 'Zoom in',
                 outButtonText        = '',
                 outIconName          = '/images/zoomOut.gif',
                 outTooltip           = 'Zoom out',
                 pickButtonText       = '',
                 pickIconName         = '/images/zoom.png',
                 pickTooltip          = 'Select Zoom',
                 zoomInKey            = key('=',CTRL_SHIFT),
                 zoomLevels           = [0.2,0.25,0.333,0.4,0.5,
                                         0.555,0.625,0.75,1.0,1.25,1.6],
                 zoomOutKey           = key('-'),
                 zoomPickKey          = key('='),
                 zoomStart            = 3):

        '''Zoom start is counting from the back (with default zoom levels,
        and zoom start, the default zoom is 1'''
        lvls = ','.join([str(z) for z in zoomLevels])
        super(Zoomer,self).\
            __init__(map,self.TAG,node=node,
                     inButtonText         = inButtonText,
                     inIconName           = inIconName,
                     inTooltip            = inTooltip,
                     outButtonText        = outButtonText,
                     outIconName          = outIconName,
                     outTooltip           = outTooltip,
                     pickButtonText       = pickButtonText,
                     pickIconName         = pickIconName,
                     pickTooltip          = pickTooltip,
                     zoomInKey            = zoomInKey,
                     zoomLevels           = lvls,
                     zoomOutKey           = zoomOutKey,
                     zoomPickKey          = zoomPickKey,
                     zoomStart            = zoomStart)

registerElement(Zoomer)

# --------------------------------------------------------------------
class HidePiecesButton(MapElement):
    TAG=Element.MAP+'HidePiecesButton'
    def __init__(self,map,node=None,
                 buttonText           = '',
                 hiddenIcon           = '/images/globe_selected.gif',
                 hotkey               = key('O'),
                 showingIcon          = '/images/globe_unselected.gif',
                 tooltip              = 'Hide all pieces on this map'):
        super(HidePiecesButton,self).\
            __init__(map,self.TAG,node=node,
                     buttonText           = buttonText,
                     hiddenIcon           = hiddenIcon,
                     hotkey               = hotkey,
                     showingIcon          = showingIcon,
                     tooltip              = tooltip)
        
registerElement(HidePiecesButton)

# --------------------------------------------------------------------
class MassKey(GlobalKey,MapElementService):
    TAG = Element.MAP+'MassKeyCommand'
    UNIQUE     = ['name']
    def __init__(self,map,node=None,
                 name                 = '',                
                 buttonHotkey         = '',
                 hotkey               = '',
                 buttonText           = '',
                 canDisable           = False,
                 deckCount            = '-1',
                 filter               = '',
                 propertyGate         = '',
                 reportFormat         = '',
                 reportSingle         = False,
                 singleMap            = True,
                 target               = GlobalKey.SELECTED,
                 tooltip              = '',
                 icon                 = ''):
        '''Default targets are selected units'''
        super(MassKey,self).\
            __init__(map,self.TAG,node=node,
                     name                 = name,                
                     buttonHotkey         = buttonHotkey, # This hot key
                     hotkey               = hotkey,       # Target hot key
                     buttonText           = buttonText,
                     canDisable           = canDisable,
                     deckCount            = deckCount,
                     filter               = filter,
                     propertyGate         = propertyGate,
                     reportFormat         = reportFormat,
                     reportSingle         = reportSingle,
                     singleMap            = singleMap,
                     target               = target,
                     tooltip              = tooltip,
                     icon                 = icon)

registerElement(MassKey)

# --------------------------------------------------------------------
class Flare(MapElement):
    TAG=Element.MAP+'Flare'
    def __init__(self,map,node=None,
                 circleColor          = rgb(255,0,0),
                 circleScale          = True,
                 circleSize           = 100,
                 flareKey             = 'keyAlt',
                 flareName            = 'Map Flare',
                 flarePulses          = 6,
                 flarePulsesPerSec    = 3,
                 reportFormat         = ''):
        super(Flare,self).__init__(map,self.TAG,node=node,
                                   circleColor          = circleColor,
                                   circleScale          = circleScale,
                                   circleSize           = circleSize,
                                   flareKey             = flareKey,
                                   flareName            = flareName,
                                   flarePulses          = flarePulses,
                                   flarePulsesPerSec    = flarePulsesPerSec,
                                   reportFormat         = '')

registerElement(Flare)

# --------------------------------------------------------------------
class Deck(MapElement):
    TAG = Element.MODULE+'map.DrawPile'
    ALWAYS     = 'Always'
    NEVER      = 'Never',
    VIA_MOUSE2 = 'Via right-click Menu'
    UNIQUE     = ['name','owningBoard']
    def __init__(self,map,
                 node                  = None,
                 name                  = 'deckName',
                 owningBoard           = '',
                 x                     = 0,   # int
                 y                     = 0,   # int
                 width                 = 200, # int
                 height                = 200, # int
                 #
                 allowMultiple         = False,
                 drawMultipleMessage   = 'Draw multiple cards',
                 #
                 allowSelect           = False,
                 drawSpecificMessage   = 'Draw specific cards',
                 selectDisplayProperty = '$BasicName$',
                 selectSortProperty    = 'BasicName',
                 #
                 faceDown              = ALWAYS,#ALWAYS,VIA_MOUSE2
                 faceFlipHotkey        = key('F'),
                 faceDownFormat        = '',
                 faceDownHotkey        = '',
                 faceDownMessage       = 'Face down',
                 faceUpHotkey          = '',
                 faceUpMessage         = 'Face up',
                 faceUpReportFormat    = '',
                 drawFaceUp            = False,
                 #
                 shuffle               = VIA_MOUSE2,#ALWAYS,NEVER
                 shuffleCommand        = 'Shuffle',
                 shuffleFormat         = '$playerSide$ shuffles $deckName$',
                 shuffleHotkey         = key('S',ALT),
                 #
                 reversible            = False,
                 reverseCommand        = 'Reverse',
                 reverseFormat         = '',
                 reverseHotkey         = '',
                 #
                 draw                  = True,
                 color                 = rgb(255,51,51),
                 hotkeyOnEmpty         = False,
                 emptyHotkey           = key(NONE,0)+',DeckEmpty',
                 #
                 reshufflable          = False,
                 reshuffleCommand      = '',
                 reshuffleHotkey       = '',
                 reshuffleMessage      = '',
                 reshuffleTarget       = '',
                 #
                 canSave               = False,
                 saveHotkey            = '',
                 saveMessage           = 'Save Deck',
                 saveReportFormat      = 'Deck Saved',
                 loadHotkey            = '',
                 loadMessage           = 'Load Deck',
                 loadReportFormat      = 'Deck Loaded',
                 #
                 maxStack              = 15,
                 #
                 expressionCounting    = False,
                 countExpressions      = '',
                 #
                 restrictExpression    = '',
                 restrictOption        = False,
                 #
                 deckOwners            = '',
                 deckRestrictAccess    = False
                 ): # int
        pass
        super(Deck,self).\
            __init__(map,self.TAG,node=node,
                     name                  = name,
                     owningBoard           = owningBoard,
                     x                     = int(x),      # int
                     y                     = int(y),      # int
                     width                 = int(width),  # int
                     height                = int(height), # int
                     #
                     allowMultiple         = allowMultiple,
                     drawMultipleMessage   = drawMultipleMessage,
                     #
                     allowSelect           = allowSelect,
                     drawSpecificMessage   = drawSpecificMessage,
                     selectDisplayProperty = selectDisplayProperty,
                     selectSortProperty    = selectSortProperty,
                     #
                     faceDown              = faceDown,
                     faceFlipHotkey        = faceFlipHotkey,
                     faceDownFormat        = faceDownFormat,
                     faceDownHotkey        = faceDownHotkey,
                     faceDownMessage       = faceDownMessage,
                     faceUpHotkey          = faceUpHotkey,
                     faceUpMessage         = faceUpMessage,
                     faceUpReportFormat    = faceUpReportFormat,
                     drawFaceUp            = drawFaceUp,
                     #
                     shuffle               = shuffle,
                     shuffleCommand        = shuffleCommand,
                     shuffleFormat         = shuffleFormat,
                     shuffleHotkey         = shuffleHotkey,
                     #
                     reversible            = reversible,
                     reverseCommand        = reverseCommand,
                     reverseFormat         = reverseFormat,
                     reverseHotkey         = reverseHotkey,
                     #
                     draw                  = draw,
                     color                 = color,
                     hotkeyOnEmpty         = hotkeyOnEmpty,
                     emptyHotkey           = emptyHotkey,
                     #
                     reshufflable          = reshufflable,
                     reshuffleCommand      = reshuffleCommand,
                     reshuffleHotkey       = reshuffleHotkey,
                     reshuffleMessage      = reshuffleMessage,
                     reshuffleTarget       = reshuffleTarget,
                     #
                     canSave               = canSave,
                     saveHotkey            = saveHotkey,
                     saveMessage           = saveMessage,
                     saveReportFormat      = saveReportFormat,
                     loadHotkey            = loadHotkey,
                     loadMessage           = loadMessage,
                     loadReportFormat      = loadReportFormat,
                     #
                     maxStack              = maxStack,
                     #
                     expressionCounting    = expressionCounting,
                     countExpressions      = countExpressions,
                     #
                     restrictExpression    = restrictExpression,
                     restrictOption        = restrictOption,
                     #
                     deckOwners            = deckOwners,
                     deckRestrictAccess    = deckRestrictAccess
                     )

    def addCard(self,**kwargs):
        '''Add a `Card` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Card
            The added element
        '''
        if not isinstance(card,CardSlot):
            print(f'Trying to add {type(card)} to Deck')
            return None
            
        p = card.clone(self)
        # self._node.appendChild(p._node)
        return p
    def addFolder(self,**kwargs):
        '''Add a `ModuleFolder` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ModuleFolder
            The added element
        '''
        return self.add(DeckFolder,**kwargs)
        
    def getCards(self,asdict=True):
        '''Get all Card element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Card`
            elements.  If `False`, return a list of all Card`
            children.

        Returns
        -------
        children : dict or list
            Dictionary or list of `Card` children

        '''
        return self.getElementsByKey(CardSlot,'entryName',asdict)
    def getFolders(self,asdict=True):
        '''Get all Menu element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Folder`
            elements.  If `False`, return a list of all `Folder`
            children.

        Returns
        -------
        children : dict or list
            Dictionary or list of `Folder` children

        '''
        return self.getElementsByKey(DeckFolder,'name',asdict)

    
registerElement(Deck)
        
                 
# --------------------------------------------------------------------
class AtStart(MapElement):
    TAG = Element.MODULE+'map.SetupStack'
    UNIQUE     = ['name','location','owningBoard']
    def __init__(self,map,
                 node            = None,
                 name            = '',
                 location        = '',
                 useGridLocation = True,
                 owningBoard     = '',
                 x               = 0,
                 y               = 0):
        '''Pieces are existing PieceSlot elements


        Parameters
        ----------
        node : xml.minidom.Node
            Existing node or None
        name : str
            Name of node
        location : str
            Where the at-start element is put if `useGridLocation`
        useGridLocation : bool
            If true, use maps grid
        owningBoard : str
            Board that owns the at-start (can be empty)
        x : float
            Coordinate (ignored if `useGridLocation`)
        y : float
            Coordinate (ignored if `useGridLocation`)
        '''
        super(AtStart,self).\
            __init__(map,self.TAG,node=node,
                     name            = name,
                     location        = location,
                     owningBoard     = owningBoard,
                     useGridLocation = useGridLocation,
                     x               = x,
                     y               = y)

    def addPieces(self,*pieces):
        '''Add a `Pieces` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Pieces
            The added element
        '''
        # copy pieces here
        copies = []
        for p in pieces:
            c = self.addPiece(p)
            if c is not None:
                copies.append(c)
        return copies
        
    def addPiece(self,piece):
        '''Add a `Piece` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Piece
            The added element
        '''
        if not isinstance(piece,WithTraitsSlot):
            # Next is a bit of a hack - not nice
            if piece.__class__.__name__ not in ['PieceSlot','CardSlot']:
                print(f'Trying to add {type(piece)} to AtStart, '
                      f'not a {isinstance(piece,WithTraitsSlot)}')
                return None
            
        p = piece.clone(self)
        # self._node.appendChild(p._node)
        return p
    
    def getPieces(self,asdict=True):
        '''Get all Piece element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Piece`
            elements.  If `False`, return a list of all Piece`
            children.

        Returns
        -------
        children : dict or list
            Dictionary or list of `Piece` children

        '''
        return self.getElementsByKey(PieceSlot,'entryName',asdict)

registerElement(AtStart)

# --------------------------------------------------------------------
class ForwardKeys(MapElement):
    TAG = Element.MODULE+'map.ForwardToKeyBuffer'
    def __init__(self,map,
                 node            = None):
        '''Forward keys to key buffer from where it is distributed to
        selected pieces.  Don't know how I missed this!

        ''' 
        
        super(ForwardKeys,self).\
            __init__(map,self.TAG,node=node)

registerElement(ForwardKeys)

# --------------------------------------------------------------------
class Scroller(MapElement):
    TAG = Element.MODULE+'map.Scroller'
    ALWAYS = 'always'
    NEVER  = 'never'
    PROMPT = 'prompt'
    def __init__(self,map,
                 node           = None,
                 useArrows      = PROMPT):
        '''This component listens to key events on a Map window and
        scrolls the map.  Depending on the useArrows attribute, will
        use number keypad or arrow keys, or will offer a preferences
        setting for the user to choose
        ''' 
        
        super(Scroller,self).\
            __init__(map,self.TAG,node=node,
                     useArrows = useArrows)

registerElement(Scroller)

#
# EOF
#
