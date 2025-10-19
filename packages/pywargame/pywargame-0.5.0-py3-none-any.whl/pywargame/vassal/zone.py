## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . grid import *
## END_IMPORT

# --------------------------------------------------------------------
class ZonedGrid(Element):
    TAG=Element.BOARD+'ZonedGrid'
    def __init__(self,board,node=None):
        super(ZonedGrid,self).__init__(board,self.TAG,node=node)

    def getBoard(self):
        ## BEGIN_IMPORT
        from . board import Board
        ## END_IMPORT
        b = self.getParent(Board)
        # print(f'Get Board of Zoned: {b}')        
        return b
    def getPicker(self):
        z = self.getBoard()
        if z is not None:
            return z.getPicker()
        return None
    def getMap(self):
        z = self.getPicker()
        if z is not None:
            return z.getMap()
        return None
    def addHighlighter(self,**kwargs):
        '''Add a `Highlighter` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Highlighter
            The added element
        '''
        return self.add(ZonedGridHighlighter,**kwargs)
    def getHighlighters(self,single=True):
        '''Get all or a sole `ZonedGridHighlighter` element(s) from this
        
        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Highligter` child, otherwise fail.
            If `False` return all `Highligter` children in this element
        
        Returns
        -------
        children : list
            List of `Highligter` children (even if `single=True`)
        '''
        return self.getAllElements(ZonedGridHighlighter,single=single)
    def addZone(self,**kwargs):
        '''Add a `Zone` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Zone
            The added element
        '''
        return self.add(Zone,**kwargs)
    def getZones(self,asdict=True):
        '''Get all Zone element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Zone` elements.  If `False`, return a list of all Zone` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Zone` children
        '''
        return self.getElementsByKey(Zone,'name',asdict=asdict)

registerElement(ZonedGrid)

# --------------------------------------------------------------------
class ZonedGridHighlighter(Element):
    TAG=Element.BOARD+'mapgrid.ZonedGridHighlighter'
    def __init__(self,zoned,node=None):
        super(ZonedGridHighlighter,self).__init__(zoned,self.TAG,node=node)
    def getZonedGrid(self): return self.getParent(ZonedGrid)

    def addZoneHighlight(self,**kwargs):
        '''Add a `ZoneHighlight` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ZoneHighlight
            The added element
        '''
        return self.add(ZoneHighlight,**kwargs)
    def getZoneHighlights(self,asdict=True):
        '''Get all ZoneHighlight element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Zone` elements.  If `False`, return a list of all Zone` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Zone` children
        '''
        return self.getElementsByKey(ZoneHighlight,'name',asdict=asdict)

registerElement(ZonedGridHighlighter)

# --------------------------------------------------------------------
class ZoneHighlight(Element):
    TAG=Element.BOARD+'mapgrid.ZoneHighlight'
    FULL    = 'Entire Zone',
    BORDER  = 'Zone Border',
    PLAIN   = 'Plain',
    STRIPED = 'Striped'
    CROSS   = 'Crosshatched',
    TILES   = 'Tiled Image'
    UNIQUE  = ['name']
    def __init__(self,
                 highlighters,
                 node     = None,
                 name     = '',
                 color    = rgb(255,0,0),
                 coverage = FULL,
                 width    = 1,
                 style    = PLAIN,
                 image    = '',
                 opacity  = 50):
        super(ZoneHighlight,self).__init__(highlighters,
                                           self.TAG,
                                           node     = node,
                                           name     = name,
                                           color    = color,
                                           coverage = coverage,
                                           width    = width,
                                           style    = style,
                                           image    = image,
                                           opacity  = int(opacity))
    def getZonedGridHighlighter(self):
        return self.getParent(ZonedGridHighlighter)


registerElement(ZoneHighlight)


# --------------------------------------------------------------------
class ZoneProperty(Element):
    TAG = Element.MODULE+'properties.ZoneProperty'
    UNIQUE  = ['name']
    def __init__(self,zone,node=None,
                 name         = '',
                 initialValue = '',
                 isNumeric    = False,
                 min          = "null",
                 max          = "null",
                 wrap         = False,
                 description  = ""):
        super(ZoneProperty,self).__init__(zone,self.TAG,
                                            node         = node,
                                            name         = name,
                                            initialValue = initialValue,
                                            isNumeric    = isNumeric,
                                            min          = min,
                                            max          = max,
                                            wrap         = wrap,
                                            description  = description)

    def getZone(self):
        return self.getParent(Zone)

registerElement(ZoneProperty)

# --------------------------------------------------------------------
class Zone(Element):
    TAG = Element.BOARD+'mapgrid.Zone'
    UNIQUE  = ['name']
    def __init__(self,zoned,node=None,
                 name              = "",
                 highlightProperty = "",
                 locationFormat    = "$gridLocation$",
                 path              = "0,0;976,0;976,976;0,976",
                 useHighlight      = False,
                 useParentGrid     = False):
        super(Zone,self).\
            __init__(zoned,self.TAG,node=node,
                     name              = name,
                     highlightProperty = highlightProperty,
                     locationFormat    = locationFormat,
                     path              = path,
                     useHighlight      = useHighlight,
                     useParentGrid     = useParentGrid)

    def getZonedGrid(self):
        z = self.getParent(ZonedGrid)
        # print(f'Get Zoned of Zone {self["name"]}: {z}')        
        return z
    
    def getBoard(self):
        z = self.getZonedGrid()
        if z is not None:
            return z.getBoard()
        return None
    def getPicker(self):
        z = self.getBoard()
        if z is not None:
            return z.getPicker()
        return None
    def getMap(self):
        z = self.getPicker()
        if z is not None:
            return z.getMap()
        return None    
    def addHexGrid(self,**kwargs):
        '''Add a `HexGrid` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : HexGrid
            The added element
        '''
        return self.add(HexGrid,**kwargs)
    def addSquareGrid(self,**kwargs):
        '''Add a `SquareGrid` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : SquareGrid
            The added element
        '''
        return self.add(SquareGrid,**kwargs)
    def addRegionGrid(self,**kwargs):
        '''Add a `RegionGrid` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : RegionGrid
            The added element
        '''
        return self.add(RegionGrid,**kwargs)
    def addProperty(self,**kwargs):
        '''Add a `Property` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Property
            The added element
        '''
        return self.add(ZoneProperty,**kwargs)
    def getHexGrids(self,single=True):
        '''Get all or a sole `HexGrid` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `HexGrid` child, otherwise fail.
            If `False` return all `HexGrid` children in this element
        
        Returns
        -------
        children : list
            List of `HexGrid` children (even if `single=True`)
        '''
        return self.getAllElements(HexGrid,single=single)
    def getSquareGrids(self,single=True):
        '''Get all or a sole `SquareGrid` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `SquareGrid` child, otherwise fail.
            If `False` return all `SquareGrid` children in this element
        
        Returns
        -------
        children : list
            List of `SquareGrid` children (even if `single=True`)
        '''
        return self.getAllElements(SquareGrid,single=single)
    def getRegionGrids(self,single=True):
        '''Get all or a sole `RegionGrid` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `RegionGrid` child, otherwise fail.
            If `False` return all `RegionGrid` children in this element
        
        Returns
        -------
        children : list
            List of `RegionGrid` children (even if `single=True`)
        '''
        return self.getAllElements(RegionGrid,single=single)
    def getGrids(self,single=True):
        '''Get all or a sole `Grid` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Grid` child, otherwise fail.
            If `False` return all `Grid` children in this element
        
        Returns
        -------
        children : list
            List of `Grid` children (even if `single=True`)
        '''
        g = self.getHexGrids(single=single)
        if g is not None: return g

        g = self.getSquareGrids(single=single)
        if g is not None: return g

        g = self.getRegionGrids(single=single)
        if g is not None: return g

        return g
    def getProperties(self):
        '''Get all `Property` element from this

        Returns
        -------
        children : dict
            dict of `Property` children
        '''
        return getElementsByKey(ZoneProperty,'name')
    
    def getPath(self):
        p  = self['path'].split(';')
        r  = []
        for pp in p:
            c = pp.split(',')
            r.append([int(c[0]),int(c[1])])
        return r
    
    def getBB(self):
        from functools import reduce
        path = self.getPath()
        llx  = reduce(lambda old,point:min(point[0],old),path,100000000000)
        lly  = reduce(lambda old,point:min(point[1],old),path,100000000000)
        urx  = reduce(lambda old,point:max(point[0],old),path,-1)
        ury  = reduce(lambda old,point:max(point[1],old),path,-1)
        return llx,lly,urx,ury
    def getWidth(self):
        llx,_,urx,_ = self.getBB()
        return urx-llx
    def getHeight(self):
        _,lly,_,ury = self.getBB()
        return ury-lly
    def getXOffset(self):
        return self.getBB()[0]
    def getYOffset(self):
        return self.getBB()[1]

registerElement(Zone)

#
# EOF
#
