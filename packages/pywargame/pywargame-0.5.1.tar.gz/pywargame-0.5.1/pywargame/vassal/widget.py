## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . gameelements import GameElement
from . map import WidgetMap
from . withtraits import *
## END_IMPORT

# --------------------------------------------------------------------
class WidgetElement:
    UNIQUE = ['entryName']
    def __init__(self):
        pass

    def addTabs(self,**kwargs):
        '''Add a `Tabs` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Tabs
            The added element
        '''
        return self.add(TabWidget,**kwargs)
    def addCombo(self,**kwargs):
        '''Add a drop-down menu to this

        Parameters
        ----------
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Combo
            The added element
        '''
        return self.add(ComboWidget,**kwargs)
    def addPanel(self,**kwargs):
        '''Add a `Panel` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Panel
            The added element
        '''
        return self.add(PanelWidget,**kwargs)
    def addList(self,**kwargs):
        '''Add a `List` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : List
            The added element
        '''
        return self.add(ListWidget,**kwargs)
    def addMapWidget(self,**kwargs):
        '''Add a `MapWidget` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : MapWidget
            The added element
        '''
        return self.add(MapWidget,**kwargs)
    def addChart(self,**kwargs):
        '''Add a `Chart` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Chart
            The added element
        '''
        ## BEGIN_IMPORT
        from . chart import Chart
        ## END_IMPORT
        return self.add(Chart,**kwargs)
    def addPieceSlot(self,**kwargs):
        '''Add a `PieceSlot` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PieceSlot
            The added element
        '''
        return self.add(PieceSlot,**kwargs)
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
        if not isinstance(piece,PieceSlot):
            print(f'Trying to add {type(piece)} to ListWidget')
            return None
            
        p = piece.clone(self)
        return p
    def getTabs(self,asdict=True):
        '''Get all Tab element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Tab` elements.  If `False`, return a list of all Tab` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Tab` children
        '''
        return self.getElementsByKey(TabWidget,'entryName',asdict)
    def getCombos(self,asdict=True):
        '''Get all Combo element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Tab` elements.  If `False`, return a list of all Tab` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Tab` children
        '''
        return self.getElementsByKey(ComboWidget,'entryName',asdict)
    def getLists(self,asdict=True):
        '''Get all List element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `List` elements.  If `False`, return a list of all List` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `List` children
        '''
        return self.getElementsByKey(ListWidget,'entryName',asdict)
    def getPanels(self,asdict=True):
        '''Get all Panel element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Panel` elements.  If `False`, return a list of all Panel` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Panel` children
        '''
        return self.getElementsByKey(PanelWidget,'entryName',asdict)
    def getMapWidgets(self,asdict=True):
        '''Get all MapWidget element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `MapWidget` elements.  If `False`, return a list of all MapWidget` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `MapWidget` children
        '''
        return self.getElementsByKey(MapWidget,'entryName',asdict)
    def getCharts(self,asdict=True):
        '''Get all Chart element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Chart` elements.  If `False`, return a list of all Chart` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Chart` children
        '''
        return self.getElementsByKey(Chart,'chartName',asdict)
    def getPieceSlots(self,asdict=True):
        '''Get all PieceSlot element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `PieceSlot` elements.  If `False`, return a list of all PieceSlot` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `PieceSlot` children
        '''
        return self.getElementsByKey(PieceSlot,'entryName',asdict)

# --------------------------------------------------------------------
class PieceWindow(GameElement,WidgetElement):
    TAG=Element.MODULE+'PieceWindow'
    UNIQUE = ['name']
    def __init__(self,elem,node=None,
                 name         = '',
                 defaultWidth = 0,
                 hidden       = False,
                 hotkey       = key('C',ALT),
                 scale        = 1.,
                 text         = '',
                 tooltip      = 'Show/hide piece window',
                 icon         = '/images/counter.gif'):
        super(PieceWindow,self).__init__(elem,self.TAG,node=node,
                                         name         = name,
                                         defaultWidth = defaultWidth,
                                         hidden       = hidden,
                                         hotkey       = hotkey,
                                         scale        = scale,
                                         text         = text,
                                         tooltip      = tooltip,
                                         icon         = icon)

registerElement(PieceWindow)

# --------------------------------------------------------------------
class ComboWidget(Element,WidgetElement):
    TAG=Element.WIDGET+'BoxWidget'
    def __init__(self,elem,node=None,entryName='',width=0,height=0):
        super(ComboWidget,self).__init__(elem,
                                       self.TAG,
                                       node = node,
                                       entryName = entryName,
                                       width     = width,
                                       height    = height)
        
registerElement(ComboWidget)

# --------------------------------------------------------------------
class TabWidget(Element,WidgetElement):
    TAG=Element.WIDGET+'TabWidget'
    def __init__(self,elem,node=None,entryName=''):
        super(TabWidget,self).__init__(elem,
                                       self.TAG,
                                       node      = node,
                                       entryName = entryName)

registerElement(TabWidget)

# --------------------------------------------------------------------
class ListWidget(Element,WidgetElement):
    TAG=Element.WIDGET+'ListWidget'
    def __init__(self,elem,node = None,
                 entryName = '',
                 height    = 0,
                 width     = 300,
                 scale     = 1.,
                 divider   = 150):
        super(ListWidget,self).__init__(elem,self.TAG,node=node,
                                        entryName = entryName,
                                        height    = height,
                                        width     = width,
                                        scale     = scale,
                                        divider   = divider)

registerElement(ListWidget)

# --------------------------------------------------------------------
class PanelWidget(Element,WidgetElement):
    TAG=Element.WIDGET+'PanelWidget'
    def __init__(self,elem,node=None,
                 entryName = '',
                 fixed     = False,
                 nColumns  = 1,
                 vert      = False):
        super(PanelWidget,self).__init__(elem,self.TAG,node=node,
                                         entryName = entryName,
                                         fixed     = fixed,
                                         nColumns  = nColumns,
                                         vert      = vert)

registerElement(PanelWidget)

# --------------------------------------------------------------------
class MapWidget(Element):
    TAG=Element.WIDGET+'MapWidget'
    def __init__(self,elem,node=None,entryName=''):
        super(MapWidget,self).__init__(elem,self.TAG,
                                       node      = node,
                                       entryName = entryName)

    def addWidgetMap(self,**kwargs):
        '''Add a `WidgetMap` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : WidgetMap
            The added element
        '''
        return self.add(WidgetMap,**kwargs)
    def getWidgetMaps(self,asdict=True):
        '''Get all WidgetMap element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `WidgetMap` elements.  If `False`, return a list of all WidgetMap` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `WidgetMap` children
        '''
        return self.getElementsByKey(WidgetMap,'mapName',asdict=asdict)
    
registerElement(MapWidget)

#
# EOF
#
