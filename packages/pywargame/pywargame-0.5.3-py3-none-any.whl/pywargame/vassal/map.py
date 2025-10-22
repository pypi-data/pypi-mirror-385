## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . mapelements import *
from . board import *
from . gameelements import *
## END_IMPORT

# --------------------------------------------------------------------
class BaseMap(Element):
    UNIQUE = ['mapName']
    def __init__(self,doc,tag,node=None,
                 mapName              = '',
                 allowMultiple        = 'false',
                 backgroundcolor      = rgb(255,255,255),
                 buttonName           = '',
                 changeFormat         = '$message$',
                 color                = rgb(0,0,0), # Selected pieces
                 createFormat         = '$pieceName$ created in $location$ *',
                 edgeHeight           = '0',
                 edgeWidth            = '0',
                 hideKey              = '',
                 hotkey               = key('M',ALT),
                 icon                 = '/images/map.gif',
                 launch               = 'false',
                 markMoved            = 'Always',
                 markUnmovedHotkey    = '',
                 markUnmovedIcon      = '/images/unmoved.gif',
                 markUnmovedReport    = '',
                 markUnmovedText      = '',
                 markUnmovedTooltip   = 'Mark all pieces on this map as not moved',
                 moveKey              = '',
                 moveToFormat         = '$pieceName$ moves $previousLocation$ &rarr; $location$ *',
                 moveWithinFormat     = '$pieceName$ moves $previousLocation$ &rarr; $location$ *',
                 showKey              = '',
                 thickness            = '3',
                 **kwargs):
        '''Create a map

        Parameters
        ----------
        doc : xml.minidom.Document
            Parent document 
        tag : str
            XML tag 
        node : xml.minidom.Node or None
            Existing node or None
        mapName : str
            Name of map 
        allowMultiple        : bool
            Allow multiple boards 
        backgroundcolor      : color
            Bckground color 
        buttonName           : str
            Name on button to show map = '',
        changeFormat         :
            Message format to show on changes 
        color                : color
            Color of selected pieces
        createFormat         : str
            Message format when creating a piece 
        edgeHeight           : int
            Height of edge (margin)
        edgeWidth            : int
            Width of edge (margin)
        hideKey              : Key
            Hot-key or key-command to hide map
        hotkey               : Key
            Hot-key or key-command to show map
        icon                 : path
            Icon image 
        launch               : bool
            Show on launch 
        markMoved            : str
            Show moved 
        markUnmovedHotkey    : key
            Remove moved markers 
        markUnmovedIcon      : path
            Icon for unmoved 
        markUnmovedReport    : str
            Message when marking as unmoved
        markUnmovedText      : str
            Text on button
        markUnmovedTooltip   : str
            Tooltip on button
        moveKey              : key
            Key to set moved marker 
        moveToFormat         : str
            Message format when moving 
        moveWithinFormat     : str
            Message when moving within map
        showKey              : str,
            Key to show map 
        thickness            : int
            Thickness of line around selected pieces 
        '''
        super(BaseMap,self).__init__(doc,tag,node=node,
                                     allowMultiple        = allowMultiple,
                                     backgroundcolor      = backgroundcolor,
                                     buttonName           = buttonName,
                                     changeFormat         = changeFormat,
                                     color                = color,
                                     createFormat         = createFormat,
                                     edgeHeight           = edgeHeight,
                                     edgeWidth            = edgeWidth,
                                     hideKey              = hideKey,
                                     hotkey               = hotkey,
                                     icon                 = icon,
                                     launch               = launch,
                                     mapName              = mapName,
                                     markMoved            = markMoved,
                                     markUnmovedHotkey    = markUnmovedHotkey,
                                     markUnmovedIcon      = markUnmovedIcon,
                                     markUnmovedReport    = markUnmovedReport,
                                     markUnmovedText      = markUnmovedText,
                                     markUnmovedTooltip   = markUnmovedTooltip,
                                     moveKey              = moveKey,
                                     moveToFormat         = moveToFormat,
                                     moveWithinFormat     = moveWithinFormat,
                                     showKey              = showKey,
                                     thickness            = thickness,
                                     **kwargs)

    def getGame(self):
        '''Get the game'''
        ## BEGIN_IMPORT
        from . game import Game
        ## END_IMPORT
        return self.getParentOfClass([Game])
    def addPicker(self,**kwargs):
        '''Add a `Picker` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Picker
            The added element
        '''
        return self.add(BoardPicker,**kwargs)
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
        return self.add(MapFolder,**kwargs)
    def getBoardPicker(self,single=True):
        '''Get all or a sole `BoardPicker` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `BoardPicker` child, otherwise fail.
            If `False` return all `BoardPicker` children in this element
        
        Returns
        -------
        children : list
            List of `BoardPicker` children (even if `single=True`)
        '''
        return self.getAllElements(BoardPicker,single)
    def getPicker(self,single=True):
        '''Get all or a sole `BoardPicker` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `BoardPicker` child, otherwise fail.
            If `False` return all `BoardPicker` children in this element
        
        Returns
        -------
        children : list
            List of `BoardPicker` children (even if `single=True`)
        '''
        return self.getAllElements(BoardPicker,single)
    def getStackMetrics(self,single=True):
        '''Get all or a sole `StackMetric` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `StackMetric` child, otherwise fail.
            If `False` return all `StackMetric` children in this element
        
        Returns
        -------
        children : list
            List of `StackMetric` children (even if `single=True`)
        '''
        return self.getAllElements(StackMetrics,single)
    def getMoveCamera(self,single=False):
        '''Get all or a sole `MoveCamera` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `MoveCamera` child, otherwise fail
            If `False` return all `MoveCamera` children in this element
        
        Returns
        -------
        children : list
            List of `MoveCamera` children (even if `single=True`)
        '''
        return self.getAllElements(MoveCamera,single)
    def getImageSaver(self,single=True):
        '''Get all or a sole `ImageSaver` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `ImageSaver` child, otherwise fail.
            If `False` return all `ImageSaver` children in this element
        
        Returns
        -------
        children : list
            List of `ImageSaver` children (even if `single=True`)
        '''
        return self.getAllElements(ImageSaver,single)
    def getTextSaver(self,single=True):
        '''Get all or a sole `TextSaver` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `TextSaver` child, otherwise fail.
            If `False` return all `TextSaver` children in this element
        
        Returns
        -------
        children : list
            List of `TextSaver` children (even if `single=True`)
        '''
        return self.getAllElements(TextSaver,single)
    def getForwardToChatter(self,single=True):
        '''Get all or a sole `ForwardToChatter` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `ForwardToChatter` child, otherwise fail.
            If `False` return all `ForwardToChatter` children in this element
        
        Returns
        -------
        children : list
            List of `ForwardToChatter` children (even if `single=True`)
        '''
        return self.getAllElements(ForwardToChatter,single)
    def getMenuDisplayer(self,single=True):
        '''Get all or a sole `MenuDi` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `MenuDi` child, otherwise fail.
            If `False` return all `MenuDi` children in this element
        
        Returns
        -------
        children : list
            List of `MenuDi` children (even if `single=True`)
        '''
        return self.getAllElements(MenuDisplayer,single)
    def getMapCenterer(self,single=True):
        '''Get all or a sole `MapCenterer` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `MapCenterer` child, otherwise fail.
            If `False` return all `MapCenterer` children in this element
        
        Returns
        -------
        children : list
            List of `MapCenterer` children (even if `single=True`)
        '''
        return self.getAllElements(MapCenterer,single)
    def getStackExpander(self,single=True):
        '''Get all or a sole `StackExpander` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `StackExpander` child, otherwise fail.
            If `False` return all `StackExpander` children in this element
        
        Returns
        -------
        children : list
            List of `StackExpander` children (even if `single=True`)
        '''
        return self.getAllElements(StackExpander,single)
    def getPieceMover(self,single=True):
        '''Get all or a sole `PieceMover` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `PieceMover` child, otherwise fail.
            If `False` return all `PieceMover` children in this element
        
        Returns
        -------
        children : list
            List of `PieceMover` children (even if `single=True`)
        '''
        return self.getAllElements(PieceMover,single)
    def getSelectionHighlighters(self,single=True):
        '''Get all or a sole `SelectionHighlighter` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `SelectionHighlighter` child, otherwise fail.
            If `False` return all `SelectionHighlighter` children in this element
        
        Returns
        -------
        children : list
            List of `SelectionHighlighter` children (even if `single=True`)
        '''
        return self.getAllElements(SelectionHighlighters,single)
    def getKeyBufferer(self,single=True):
        return self.getAllElements(KeyBufferer,single)
    def getHighlightLastMoved(self,single=True):
        '''Get all or a sole `HighlightLa` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `HighlightLa` child, otherwise fail.
            If `False` return all `HighlightLa` children in this element
        
        Returns
        -------
        children : list
            List of `HighlightLa` children (even if `single=True`)
        '''
        return self.getAllElements(HighlightLastMoved,single)
    def getCounterDetailViewer(self,single=True):
        '''Get all or a sole `CounterDetailViewer` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `CounterDetailViewer` child, otherwise fail.
            If `False` return all `CounterDetailViewer` children in this element
        
        Returns
        -------
        children : list
            List of `CounterDetailViewer` children (even if `single=True`)
        '''
        return self.getAllElements(CounterDetailViewer,single)
    def getGlobalMap(self,single=True):
        '''Get all or a sole `GlobalMap` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `GlobalMap` child, otherwise fail.
            If `False` return all `GlobalMap` children in this element
        
        Returns
        -------
        children : list
            List of `GlobalMap` children (even if `single=True`)
        '''
        return self.getAllElements(GlobalMap,single)
    def getZoomer(self,single=True):
        '''Get all or a sole `Zoomer` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Zoomer` child, otherwise fail.
            If `False` return all `Zoomer` children in this element
        
        Returns
        -------
        children : list
            List of `Zoomer` children (even if `single=True`)
        '''
        return self.getAllElements(Zoomer,single)
    def getHidePiecesButton(self,single=True):
        '''Get all or a sole `HidePiece` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `HidePiece` child, otherwise fail.
            If `False` return all `HidePiece` children in this element
        
        Returns
        -------
        children : list
            List of `HidePiece` children (even if `single=True`)
        '''
        return self.getAllElements(HidePiecesButton,single)
    def getMassKeys(self,asdict=True):
        '''Get all MassKey element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `MassKey` elements.  If `False`, return a list of all MassKey` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `MassKey` children
        '''
        return self.getElementsByKey(MassKey,'name',asdict)
    def getFlare(self,single=True):
        '''Get all or a sole `Flare` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Flare` child, otherwise fail.
            If `False` return all `Flare` children in this element
        
        Returns
        -------
        children : list
            List of `Flare` children (even if `single=True`)
        '''
        return self.getAllElements(Flare,single)
    def getAtStarts(self,single=True):
        '''Get all or a sole `AtStart` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `AtStart` child, otherwise fail.
            If `False` return all `AtStart` children in this element
        
        Returns
        -------
        children : list
            List of `AtStart` children (even if `single=True`)
        '''
        return self.getAllElements(AtStart,single)
    def getBoards(self,asdict=True):
        '''Get all Board element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board` elements.  If `False`, return a list of all Board` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children
        '''
        picker = self.getPicker()
        if picker is None:  return None
        return picker[0].getBoards(asdict=asdict)
    def getLayers(self,asdict=True):
        '''Get all `PieceLayer` element(s) from this

        Parameters
        ----------
        asdict : bool        
            If `True`, return a dictonary that maps property name
            `PieceLayers` elements.  If `False`, return a list of all
            `PieceLayers` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `PieceLayers` children

        '''
        return self.getElementsByKey(PieceLayers,'property',asdict)
    def getMenus(self,asdict=True):
        '''Get all Menu element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board`
            elements.  If `False`, return a list of all Board`
            children.

        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children

        '''
        return self.getElementsByKey(Menu,'name',asdict)
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
        return self.getElementsByKey(MapFolder,'name',asdict)
    def getLOSs(self,asdict=True):
        '''Get all Menu element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board`
            elements.  If `False`, return a list of all Board`
            children.

        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children

        '''
        return self.getElementsByKey(LineOfSight,'threadName',asdict)
    def addBoardPicker(self,**kwargs):
        '''Add a `BoardPicker` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : BoardPicker
            The added element
        '''
        return self.add(BoardPicker,**kwargs)
    def addStackMetrics(self,**kwargs):
        '''Add a `StackMetrics` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : StackMetrics
            The added element
        '''
        return self.add(StackMetrics,**kwargs)

    def addMoveCamera(self,**kwargs):
        '''Add a `MoveCamera` button to the map.

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : MoveCamera
            The added element
        '''
        return self.add(MoveCamera,**kwargs)
        
    def addImageSaver(self,**kwargs):
        '''Add a `ImageSaver` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ImageSaver
            The added element
        '''
        return self.add(ImageSaver,**kwargs)
    def addTextSaver(self,**kwargs):
        '''Add a `TextSaver` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : TextSaver
            The added element
        '''
        return self.add(TextSaver,**kwargs)
    def addForwardToChatter(self,**kwargs):
        '''Add a `ForwardToChatter` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ForwardToChatter
            The added element
        '''
        return self.add(ForwardToChatter,**kwargs)
    def addForwardKeys(self,**kwargs):
        '''Add a `ForwardKeys` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ForwardToChatter
            The added element
        '''
        return self.add(ForwardKeys,**kwargs)
    def addScroller(self,**kwargs):
        '''Add a `ForwardKeys` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ForwardToChatter
            The added element
        '''
        return self.add(Scroller,**kwargs)
    def addMenuDisplayer(self,**kwargs):
        '''Add a `MenuDisplayer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : MenuDisplayer
            The added element
        '''
        return self.add(MenuDisplayer,**kwargs)
    def addMapCenterer(self,**kwargs):
        '''Add a `MapCenterer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : MapCenterer
            The added element
        '''
        return self.add(MapCenterer,**kwargs)
    def addStackExpander(self,**kwargs):
        '''Add a `StackExpander` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : StackExpander
            The added element
        '''
        return self.add(StackExpander,**kwargs)
    def addPieceMover(self,**kwargs):
        '''Add a `PieceMover` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PieceMover
            The added element
        '''
        return self.add(PieceMover,**kwargs)
    def addSelectionHighlighters(self,**kwargs):
        '''Add a `SelectionHighlighters` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : SelectionHighlighters
            The added element
        '''
        return self.add(SelectionHighlighters,**kwargs)
    def addKeyBufferer(self,**kwargs):
        '''Add a `KeyBufferer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : KeyBufferer
            The added element
        '''
        return self.add(KeyBufferer,**kwargs)
    def addHighlightLastMoved(self,**kwargs):
        '''Add a `HighlightLastMoved` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : HighlightLastMoved
            The added element
        '''
        return self.add(HighlightLastMoved,**kwargs)
    def addCounterDetailViewer(self,**kwargs):
        '''Add a `CounterDetailViewer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : CounterDetailViewer
            The added element
        '''
        return self.add(CounterDetailViewer,**kwargs)
    def addGlobalMap(self,**kwargs):
        '''Add a `GlobalMap` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : GlobalMap
            The added element
        '''
        return self.add(GlobalMap,**kwargs)
    def addZoomer(self,**kwargs):
        '''Add a `Zoomer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Zoomer
            The added element
        '''
        return self.add(Zoomer,**kwargs)
    def addHidePiecesButton(self,**kwargs):
        '''Add a `HidePiecesButton` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : HidePiecesButton
            The added element
        '''
        return self.add(HidePiecesButton,**kwargs)
    def addMassKey(self,**kwargs):
        '''Add a `MassKey` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : MassKey
            The added element
        '''
        return self.add(MassKey,**kwargs)
    def addStartupMassKey(self,**kwargs):
        '''Add a `StartupMassKey` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : StartupMassKey
            The added element
        '''
        return self.add(MassKey,**kwargs)
    def addFlare(self,**kwargs):
        '''Add a `Flare` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Flare
            The added element
        '''
        return self.add(Flare,**kwargs)
    def addAtStart(self,**kwargs):
        '''Add a `AtStart` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : AtStart
            The added element
        '''
        return self.add(AtStart,**kwargs)


    def addLayers(self,**kwargs):
        '''Add `PieceLayers` element to this
        
        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PieceLayers
            The added element
        '''
        return self.add(PieceLayers,**kwargs)
    def addMenu(self,**kwargs):
        '''Add a `Menu` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Menu
            The added element
        '''
        return self.add(Menu,**kwargs)
    def addLOS(self,**kwargs):
        '''Add a `Menu` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Menu
            The added element
        '''
        return self.add(LineOfSight,**kwargs)
     
# --------------------------------------------------------------------
class Map(BaseMap):
    TAG = Element.MODULE+'Map'
    def __init__(self,doc,node=None,
                 mapName              = '',
                 allowMultiple        = 'false',
                 backgroundcolor      = rgb(255,255,255),
                 buttonName           = '',
                 changeFormat         = '$message$',
                 color                = rgb(0,0,0),
                 createFormat         = '$pieceName$ created in $location$ *',
                 edgeHeight           = '0',
                 edgeWidth            = '0',
                 hideKey              = '',
                 hotkey               = key('M',ALT),
                 icon                 = '/images/map.gif',
                 launch               = 'false',
                 markMoved            = 'Always',
                 markUnmovedHotkey    = '',
                 markUnmovedIcon      = '/images/unmoved.gif',
                 markUnmovedReport    = '',
                 markUnmovedText      = '',
                 markUnmovedTooltip   = 'Mark all pieces on this map as not moved',
                 moveKey              = '',
                 moveToFormat         = '$pieceName$ moves $previousLocation$ &rarr; $location$ *',
                 moveWithinFormat     = '$pieceName$ moves $previousLocation$ &rarr; $location$ *',
                 showKey              = '',
                 thickness            = '3'):
        super(Map,self).__init__(doc,self.TAG,node=node,
                                 allowMultiple        = allowMultiple,
                                 backgroundcolor      = backgroundcolor,
                                 buttonName           = buttonName,
                                 changeFormat         = changeFormat,
                                 color                = color,
                                 createFormat         = createFormat,
                                 edgeHeight           = edgeHeight,
                                 edgeWidth            = edgeWidth,
                                 hideKey              = hideKey,
                                 hotkey               = hotkey,
                                 icon                 = icon,
                                 launch               = launch,
                                 mapName              = mapName,
                                 markMoved            = markMoved,
                                 markUnmovedHotkey    = markUnmovedHotkey,
                                 markUnmovedIcon      = markUnmovedIcon,
                                 markUnmovedReport    = markUnmovedReport,
                                 markUnmovedText      = markUnmovedText,
                                 markUnmovedTooltip   = markUnmovedTooltip,
                                 moveKey              = moveKey,
                                 moveToFormat         = moveToFormat,
                                 moveWithinFormat     = moveWithinFormat,
                                 showKey              = showKey,
                                 thickness            = thickness)

    def getGame(self):
        ## BEGIN_IMPORT
        from . game import Game
        ## END_IMPORT
        return self.getParent(Game)

registerElement(Map)

# --------------------------------------------------------------------
class WidgetMap(BaseMap):
    TAG = Element.WIDGET+'WidgetMap'
    def __init__(self,doc,node=None,**attr):
        super(WidgetMap,self).__init__(doc,self.TAG,node=node,**attr)

    def getGame(self):
        ## BEGIN_IMPORT
        from . game import Game
        ## END_IMPORT
        return self.getParentOfClass([Game])
    def getMapWidget(self):
        return self.getParent(MapWidget)

registerElement(WidgetMap)

# --------------------------------------------------------------------
class BasePrivateMap(BaseMap):
    def __init__(self,
                 doc,
                 tag,                  
                 node                 = None,
                 mapName              = '',
                 allowMultiple        = 'false',
                 backgroundcolor      = rgb(255,255,255),
                 buttonName           = '',
                 changeFormat         = '$message$',
                 color                = rgb(0,0,0),
                 createFormat         = '$pieceName$ created in $location$ *',
                 edgeHeight           = '0',
                 edgeWidth            = '0',
                 hideKey              = '',
                 hotkey               = key('M',ALT),
                 icon                 = '/images/map.gif',
                 launch               = 'false',
                 markMoved            = 'Always',
                 markUnmovedHotkey    = '',
                 markUnmovedIcon      = '/images/unmoved.gif',
                 markUnmovedReport    = '',
                 markUnmovedText      = '',
                 markUnmovedTooltip   = 'Mark all pieces on this map as not moved',
                 moveKey              = '',
                 moveToFormat         = '$pieceName$ moves $previousLocation$ &rarr; $location$ *',
                 moveWithinFormat     = '$pieceName$ moves $previousLocation$ &rarr; $location$ *',
                 showKey              = '',
                 thickness            = '3',
                 side                 = [],
                 visible              = False,
                 use_boards           = ''):
        lsides = [side] if isinstance(side,str) else ','.join(side)
        super().__init__(doc,
                         self.TAG,
                         node                 = node,
                         allowMultiple        = allowMultiple,
                         backgroundcolor      = backgroundcolor,
                         buttonName           = buttonName,
                         changeFormat         = changeFormat,
                         color                = color,
                         createFormat         = createFormat,
                         edgeHeight           = edgeHeight,
                         edgeWidth            = edgeWidth,
                         hideKey              = hideKey,
                         hotkey               = hotkey,
                         icon                 = icon,
                         launch               = launch,
                         mapName              = mapName,
                         markMoved            = markMoved,
                         markUnmovedHotkey    = markUnmovedHotkey,
                         markUnmovedIcon      = markUnmovedIcon,
                         markUnmovedReport    = markUnmovedReport,
                         markUnmovedText      = markUnmovedText,
                         markUnmovedTooltip   = markUnmovedTooltip,
                         moveKey              = moveKey,
                         moveToFormat         = moveToFormat,
                         moveWithinFormat     = moveWithinFormat,
                         showKey              = showKey,
                         thickness            = thickness,
                         side                 = lsides,
                         visible              = visible,
                         use_boards           = use_boards)

    def getSides(self):
        return self['side'].split(',')

    def setSides(self,*sides):
        self['side'] = ','.join(sides)

    def getMap(self):
        game = self.getGame()
        maps = game.getMaps()
        return maps.get(self['use_boards'])

    def setMap(self,map):
        self['use_boards'] = map if isinstance(map,str) else map['mapName']

# --------------------------------------------------------------------
class PrivateMap(BasePrivateMap):
    TAG = Element.MODULE+'PrivateMap'
    def __init__(self,
                 doc,
                 **kwargs):
        super().__init__(doc,self.TAG,**kwargs)
        
registerElement(PrivateMap)

# --------------------------------------------------------------------
class PlayerHand(BasePrivateMap):
    TAG = Element.MODULE + 'PlayerHand'
    def __init__(self,doc,**kwargs):
        super().__init__(doc,self.TAG,**kwargs)

registerElement(PlayerHand)

#
# EOF
#
