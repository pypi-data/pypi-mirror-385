## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . gameelements import GameElement
from . mapelements import MapElement
from . zone import *
from . grid import *
## END_IMPORT

# --------------------------------------------------------------------
class BoardPicker(MapElement):
    TAG = Element.MAP+'BoardPicker'
    def __init__(self,doc,node=None,
                 addColumnText        = 'Add column',
                 addRowText           = 'Add row',
                 boardPrompt          = 'Select board',
                 slotHeight           = 125,
                 slotScale            = 0.2,
                 slotWidth            = 350,
                 title                = 'Choose Boards'):
        super(BoardPicker,self).__init__(doc,self.TAG,node=node,
                                         addColumnText        = addColumnText,
                                         addRowText           = addRowText,
                                         boardPrompt          = boardPrompt,
                                         slotHeight           = slotHeight,
                                         slotScale            = slotScale,
                                         slotWidth            = slotWidth,
                                         title                = title,
                                         selected             = '')

    def addSetup(self,**kwargs):
        '''Add a `Setup` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Setup
            The added element
        '''
        if 'mapName' not in kwargs:
            m = self.getMap()
            kwargs['mapName'] = m.getAttribute('mapName')
            
        return self.add(Setup,**kwargs)
    def getSetups(self,single=False):
        '''Get all or a sole `Setup` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Setup` child, otherwise fail.
            If `False` return all `Setup` children in this element
        
        Returns
        -------
        children : list
            List of `Setup` children (even if `single=True`)
        '''
        return self.getAllElements(Setup,single=single)
    def addBoard(self,**kwargs):
        '''Add a `Board` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Board
            The added element
        '''
        return self.add(Board,**kwargs)
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
        return self.getElementsByKey(Board,'name',asdict=asdict)
    
    def selectBoard(self,name):
        if name is None:
            self.setAttribute('selected','')
            return
        
        if name not in self.getBoards():
            print(f'Board "{name}" not in "{self.getMap()["mapName"]}" picker')
            return

        escname = name.replace('|',' ')
        self.setAttribute('selected',f'{self["selected"]}|{name}|')
        #print(f'Added "{name}" to selected boards: {self["selected"]}')
        
    def encode(self):
        setups = self.getSetups()
        if setups is not None and len(setups)>0:
            return [setups[0]._node.childNodes[0].nodeValue]
        
        ret    = []
        selected = self['selected']
        #print(f'Selected boards: {selected}')
        for bn in self.getBoards().keys():
            escname = '|'+bn.replace('|',' ')+'|'
            # if selected != '':
            #     print(f'Ignore board "{bn}" in map '
            #           f'{self.getMap()["mapName"]} '
            #           f'"{selected}" -> '
            #           f'{escname not in selected}')
            if escname not in selected:
                continue 
            ret.append(self.getMap()['mapName']+'BoardPicker\t'+bn+'\t0\t0')

        return ret

registerElement(BoardPicker)

# --------------------------------------------------------------------
class Setup(Element):
    TAG = 'setup'
    def __init__(self,picker,node=None,
                 mapName = '',
                 maxColumns = 1,
                 boardNames = []):
        super(Setup,self).__init__(picker,self.TAG,node=node)
        col = 0
        row = 0
        lst = [f'{mapName}BoardPicker']
        for bn in boardNames:
            lst.extend([bn,str(col),str(row)])
            col += 1
            if col >= maxColumns:
                col = 0
                row += 1
                
        txt = r'	'.join(lst)
        self.addText(txt)

    def getPicker(self): return self.getParent(BoardPicker)

registerElement(Setup)
    
# --------------------------------------------------------------------
class Board(Element):
    TAG = Element.PICKER+'Board'
    UNIQUE = ['name']
    def __init__(self,picker,node=None,
                 name       = '',
                 image      = '',
                 reversible = False,
                 color      = rgb(255,255,255),
                 width      = 0,
                 height     = 0):
        super(Board,self).__init__(picker,self.TAG,node=node,
                                   image      = image,
                                   name       = name,
                                   reversible = reversible,
                                   color      = color,
                                   width      = width,
                                   height     = height)

    def getPicker(self): return self.getParent(BoardPicker)
    def getMap(self):
        z = self.getPicker()
        if z is not None:
            return z.getMap()
        return None
    def addZonedGrid(self,**kwargs):
        '''Add a `ZonedGrid` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ZonedGrid
            The added element
        '''
        return self.add(ZonedGrid,**kwargs)
    def getZonedGrids(self,single=True):
        '''Get all or a sole `ZonedGrid` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `ZonedGrid` child, otherwise fail.
            If `False` return all `ZonedGrid` children in this element
        
        Returns
        -------
        children : list
            List of `ZonedGrid` children (even if `single=True`)
        '''
        return self.getAllElements(ZonedGrid,single=single)
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
        zoned = self.getZonedGrids(single=True)
        if zoned is None: return None

        return zoned[0].getZones(asdict=asdict)

    def getWidth(self):
        # print(f'Getting width of {self}: {self["width"]}')
        if 'width' in self and int(self['width']) != 0:
            return int(self['width'])
        return 0

    def getHeight(self):
        # print(f'Getting height of {self}: {self["height"]}')
        if 'height' in self and int(self['height']) != 0:
            return int(self['height'])
        return 0

registerElement(Board)

#
# EOF
#
