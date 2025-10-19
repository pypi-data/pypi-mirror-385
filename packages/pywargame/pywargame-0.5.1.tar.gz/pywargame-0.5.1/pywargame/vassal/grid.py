## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
## END_IMPORT

# --------------------------------------------------------------------
HEX_WIDTH = 88.50779626676963
HEX_HEIGHT = 102.2
RECT_WIDTH  = 80
RECT_HEIGHT = 80
# --------------------------------------------------------------------
class BaseGrid(Element):
    def __init__(self,zone,tag,node=None,
                 color        = rgb(0,0,0),
                 cornersLegal = False,
                 dotsVisible  = False,
                 dx           = HEX_WIDTH,  # Meaning seems reversed!
                 dy           = HEX_HEIGHT,
                 edgesLegal   = False,
                 sideways     = False,
                 snapTo       = True,
                 visible      = True,
                 x0           = 0,
                 y0           = 32):
        super(BaseGrid,self).__init__(zone,tag,node=node,
                                      color        = color,
                                      cornersLegal = cornersLegal,
                                      dotsVisible  = dotsVisible,
                                      dx           = dx,
                                      dy           = dy,
                                      edgesLegal   = edgesLegal,
                                      sideways     = sideways,
                                      snapTo       = snapTo,
                                      visible      = visible,
                                      x0           = x0,
                                      y0           = y0)
    def getZone(self):
        ## BEGIN_IMPORT
        from . zone import Zone
        ## END_IMPORT
        z = self.getParent(Zone)
        return z
    def getZonedGrid(self):
        z = self.getZone()
        if z is not None:
            return z.getZonedGrid()
        return None
    def getBoard(self):
        z = self.getZonedGrid()
        if z is not None:
            return z.getBoard()
        return self.getParent(Board)
    def getPicker(self):
        z = self.getBoard()
        if z is not None:
            return z.getPicker()
        return None
    def getMap(self):
        b = self.getPicker()
        if b is not None:
            return b.getMap()
        return None
    def getNumbering(self):
        pass 
    def getLocation(self,loc):
        numbering = self.getNumbering()
        if numbering is None or len(numbering) < 1:
            return None

        return numbering[0].getLocation(loc)
    
# --------------------------------------------------------------------
class BaseNumbering(Element):
    def __init__(self,grid,tag,node=None,
                 color                = rgb(255,0,0),
                 first                = 'H',
                 fontSize             = 24,
                 hDescend             = False,
                 hDrawOff             = 0,
                 hLeading             = 1,
                 hOff                 = 0,
                 hType                = 'A',
                 locationFormat       = '$gridLocation$',
                 rotateText           = 0,
                 sep                  = '',
                 stagger              = True,
                 vDescend             = False,
                 vDrawOff             = 32,
                 vLeading             = 0,
                 vOff                 = 0,
                 vType                = 'N',
                 visible              = True):
        super(BaseNumbering,self).__init__(grid,tag,node=node,
                                           color           = color,
                                           first           = first,
                                           fontSize        = fontSize,
                                           hDescend        = hDescend,
                                           hDrawOff        = hDrawOff,
                                           hLeading        = hLeading,
                                           hOff            = hOff,
                                           hType           = hType,
                                           locationFormat  = locationFormat,
                                           rotateText      = rotateText,
                                           sep             = sep,
                                           stagger         = stagger,
                                           vDescend        = vDescend,
                                           vDrawOff        = vDrawOff,
                                           vLeading        = vLeading,
                                           vOff            = vOff,
                                           vType           = vType,
                                           visible         = visible)
    def getGrid(self): return getParent(BaseGrid)

    def _getMatcher(self,tpe,leading):
        if tpe == 'A':
            return \
                '-?(?:A+|B+|C+|D+|E+|F+|G+|H+|I+|'  + \
                'J+|K+|L+|M+|N+|O+|P+|Q+|R+|S+|T+|' + \
                'U+|V+|W+|X+|Y+|Z+)'

        return f'-?[0-9]{{{int(leading)+1},}}'

    def _getIndex(self,name,tpe):
        if tpe == 'A':
            negative = name.startswith('-')
            if negative:
                name = name[1:]

            value = 0
            for num,let in enumerate(name):
                if not let.isupper():
                    continue
                if num < len(name) - 1:
                    value += 26
                else:
                    value += ord(let)-ord('A')

            if negative:
                value *= -1

            return value

        return int(name)

    def _getCenter(self,col,row):
        '''Convert col and row index to picture coordinates'''
        print('Dummy GetCenter')
        pass
    
    def getLocation(self,loc):
        '''Get picture coordinates from grid location'''
        from re import match

        first   = self['first']
        vType   = self['vType']
        hType   = self['hType']
        vOff    = int(self['vOff'])
        hOff    = int(self['hOff'])
        sep     = self['sep']
        colPat  = self._getMatcher(hType,self['hLeading'])
        rowPat  = self._getMatcher(vType,self['vLeading'])
        patts   = ((colPat,rowPat) if first == 'H' else (rowPat,colPat))
        colGrp  = 1 if first == 'H' else 2
        rowGrp  = 2 if first == 'H' else 1
        patt    = sep.join([f'({p})' for p in patts])
        matched = match(patt,loc)
        if not matched:
            return None

        rowStr  = matched[rowGrp]
        colStr  = matched[colGrp]
        rowNum  = self._getIndex(rowStr,vType)
        colNum  = self._getIndex(colStr,hType)

        ret = self._getCenter(colNum-hOff, rowNum-vOff);
        #print(f'Get location of "{loc}" -> {rowNum},{colNum} -> {ret}')
        return ret
       
    
# --------------------------------------------------------------------
class HexGrid(BaseGrid):
    TAG = Element.BOARD+'HexGrid'
    def __init__(self,zone,node=None,**kwargs):
        super(HexGrid,self).__init__(zone,self.TAG,node=node,**kwargs)

    def addNumbering(self,**kwargs):
        '''Add a `Numbering` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Numbering
            The added element
        '''
        return self.add(HexNumbering,**kwargs)
    def getNumbering(self):
        return self.getAllElements(HexNumbering)
    def getDeltaX(self):
        return float(self['dx'])
    def getDeltaY(self):
        return float(self['dy'])
    def getXOffset(self):
        return int(self['x0'])
    def getYOffset(self):
        return int(self['y0'])
    def getMaxRows(self):
        from math import floor
        height    = self.getZone().getHeight()
        return floor(height / self.getDeltaX() + .5)
    def getMaxCols(self):
        from math import floor
        width    = self.getZone().getWidth()
        return floor(width / self.getDeltaY()  + .5)

registerElement(HexGrid)

# --------------------------------------------------------------------
class SquareGrid(BaseGrid):
    TAG = Element.BOARD+'SquareGrid'
    def __init__(self,zone,node=None,
                 dx           = RECT_WIDTH,
                 dy           = RECT_HEIGHT,
                 edgesLegal   = False,
                 x0           = 0,
                 y0           = int(0.4*RECT_HEIGHT),
                 **kwargs):
        super(SquareGrid,self).__init__(zone,self.TAG,node=node,
                                        dx         = dx,
                                        dy         = dy,
                                        edgesLegal = edgesLegal,
                                        x0         = x0,
                                        y0         = y0,
                                        **kwargs)
    def addNumbering(self,**kwargs):
        '''Add a `Numbering` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Numbering
            The added element
        '''
        return self.add(SquareNumbering,**kwargs)
    def getNumbering(self):
        return self.getAllElements(SquareNumbering)
    def getDeltaX(self):
        return float(self['dx'])
    def getDeltaY(self):
        return float(self['dy'])
    def getXOffset(self):
        return int(self['x0'])
    def getYOffset(self):
        return int(self['y0'])
    def getMaxRows(self):
        from math import floor
        height    = self.getZone().getHeight()
        return floor(height / self.getDeltaY() + .5)
    def getMaxCols(self):
        from math import floor
        width    = self.getZone().getWidth()
        return floor(width / self.getDeltaX()  + .5)

registerElement(SquareGrid)

# --------------------------------------------------------------------
class HexNumbering(BaseNumbering):
    TAG = Element.BOARD+'mapgrid.HexGridNumbering'
    def __init__(self,grid,node=None,**kwargs):
        super(HexNumbering,self).__init__(grid,self.TAG,node=node,**kwargs)
        
    def getGrid(self):
        g = self.getParent(HexGrid)
        return g

    def _getCenter(self,col,row):
        '''Convert col and row index to picture coordinates'''
        from math import floor
        
        stagger  = self['stagger'] == 'true'
        sideways = self.getGrid()['sideways'] == 'true'
        hDesc    = self['hDescend'] == 'true'
        vDesc    = self['vDescend'] == 'true'
        xOff     = self.getGrid().getXOffset()
        yOff     = self.getGrid().getYOffset()
        hexW     = self.getGrid().getDeltaX()
        hexH     = self.getGrid().getDeltaY()
        zxOff    = self.getGrid().getZone().getXOffset()
        zyOff    = self.getGrid().getZone().getYOffset()
        maxRows  = self.getGrid().getMaxRows()
        maxCols  = self.getGrid().getMaxCols()
        # print(f'  Col:         {col}')
        # print(f'  Row:         {row}')
        # print(f'  Stagger:     {stagger}')
        # print(f'  Sideways:    {sideways}')
        # print(f'  hDesc:       {hDesc}')
        # print(f'  vDesc:       {vDesc}')
        # print(f'  maxRows:     {maxRows}')
        # print(f'  maxCols:     {maxCols}')

        # This code from HexGridNumbering.java
        if stagger:
            if sideways:
                if col % 2 != 0:
                    if hDesc:
                        row += 1
                    else:
                        row -= 1
            else:
                if col % 2 != 0:
                    if vDesc:
                        row += 1
                    else:
                        row -= 1

        if sideways:
            if vDesc:
                col = maxRows - col
            if hDesc:
                row = maxCols - row
        else:
            if hDesc:
                col = maxCols - col
            if vDesc:
                row = maxRows - row


        x = col * hexW + xOff
        if col % 2 == 0:
            y = row * hexH
        else:
            y = row * hexH + hexH / 2
        y += yOff

        # print(f'  Col:         {col}')
        # print(f'  Row:         {row}')
        # print(f'  hexW:        {hexW}')
        # print(f'  hexH:        {hexH}')
        # print(f'  xOff:        {xOff}')
        # print(f'  yOff:        {yOff}')
        # print(f'  x:           {x}')
        # print(f'  y:           {y}')
        
        if sideways:
            x, y = y, x

        return int(floor(x+.5)),int(floor(y+.5))
            
        # if sideways:
        #     maxRows, maxCols = maxCols, maxRows
        #     
        # if stagger:
        #     if sideways:
        #         if col % 2 != 0:
        #             row += 1 if hDesc else -1
        #     else:
        #         if col % 2 != 0:
        #             row += 1 if vDesc else -1
        # 
        # if hDesc:
        #     col = maxCols - col
        # if vDesc:
        #     row = maxRows - row
        # 
        # print(f'  Col:         {col}')
        # print(f'  Row:         {row}')
        # print(f'  hexW:        {hexW}')
        # print(f'  hexH:        {hexH}')
        # print(f'  xOff:        {xOff}')
        # print(f'  yOff:        {yOff}')
        # 
        # x = col * hexW + xOff
        # y = row * hexH + yOff + (hexH/2 if col % 2 != 0 else 0)
        # 
        # print(f'  Col:         {col}')
        # print(f'  Row:         {row}')
        # print(f'  hexW:        {hexW}')
        # print(f'  hexH:        {hexH}')
        # print(f'  xOff:        {xOff}')
        # print(f'  yOff:        {yOff}')
        # print(f'  x:           {x}')
        # print(f'  y:           {y}')
        # 
        # x = int(floor(x + .5))
        # y = int(floor(y + .5))
        # if sideways:
        #     # print(f'Swap coordinates because {sideways}')
        #     x, y = y, x
        # 
        # return x,y

registerElement(HexNumbering)

# --------------------------------------------------------------------
class SquareNumbering(BaseNumbering):
    TAG = Element.BOARD+'mapgrid.SquareGridNumbering'
    def __init__(self,grid,node=None,hType='N',**kwargs):
        super(SquareNumbering,self).__init__(grid,self.TAG,node=node,
                                             hType=hType,**kwargs)
    def getGrid(self):
        return self.getParent(SquareGrid)

    def getCenter(self,col,row):
        hDesc    = self['hDescend'] == 'true'
        vDesc    = self['vDescend'] == 'true'
        xOff     = self.getGrid().getXOffset()
        yOff     = self.getGrid().getYOffset()
        squareW  = self.getGrid().getDeltaX()
        squareH  = self.getGrid().getDeltaY()
        maxRows  = self.getGrid().getMaxRows()
        maxCols  = self.getGrid().getMaxCols()

        if vDesc:  row = maxRows - row
        if hDesc:  col = maxCols - col

        x = col * squareW + xOff
        y = row * squareH + yOff

        return x,y
        
registerElement(SquareNumbering)
    
# --------------------------------------------------------------------
class RegionGrid(Element):
    TAG = Element.BOARD+'RegionGrid'
    def __init__(self,zone,node=None,snapto=True,fontsize=9,visible=True):
        super(RegionGrid,self).__init__(zone,self.TAG,node=node,
                                        snapto   = snapto,
                                        fontsize = fontsize,
                                        visible  = visible)

    def getZone(self):
        ## BEGIN_IMPORT
        from . zone import Zone
        ## END_IMPORT
        return self.getParent(Zone)
    def getZoneGrid(self):
        z = self.getZone()
        if z is not None:
            return z.getBoard()
        return None
    def getBoard(self):
        z = self.getZonedGrid()
        if z is not None:
            return z.getBoard()
        return self.getParent(Board)
    def getMap(self):
        b = self.getBoard()
        if b is not None:
            return b.getMap()
        return None
    def getRegions(self):
        return self.getElementsByKey(Region,'name')    
    def checkName(self,name):
        '''Get unique name'''
        poss = len([e for e in self.getRegions()
                    if e == name or e.startswith(name+'_')])
        if poss == 0:
            return name

        return name + f'_{poss}'
    def addRegion(self,**kwargs):
        '''Add a `Region` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Region
            The added element
        '''
        return self.add(Region,**kwargs)
    def getLocation(self,loc):
        for r in self.getRegions().values():
            if loc == r['name']:
                return int(r['originx']),int(r['originy'])

        return None
        
registerElement(RegionGrid)

# --------------------------------------------------------------------
class Region(Element):
    TAG = Element.BOARD+'Region'
    UNIQUE = ['name']
    def __init__(self,grid,node=None,
                 name      = '',
                 originx   = 0,
                 originy   = 0,
                 alsoPiece = True,
                 piece     = None,
                 prefix    = ''):
        fullName = name + ("@"+prefix if len(prefix) else "")
        realName = grid.checkName(fullName) if node is None else fullName
        super(Region,self).__init__(grid,
                                    self.TAG,
                                    node    = node,
                                    name    = realName,
                                    originx = originx,
                                    originy = originy)

        if node is None and alsoPiece:
            m = self.getMap()
            b = self.getBoard()
            if m is not None and b is not None:
                if piece is None:
                    g      = m.getGame()
                    pieces = g.getSpecificPieces(name,asdict=False)
                    piece  = pieces[0] if len(pieces) > 0 else None
             
                if piece is not None:
                    # bname = m['mapName']
                    bname = b['name']
                    #print(f'Adding at-start name={name} location={realName} '
                    #      f'owning board={bname}')
                    a = m.addAtStart(name            = name,
                                     location        = realName,
                                     useGridLocation = True,
                                     owningBoard     = bname,
                                     x               = 0,
                                     y               = 0)
                    p = a.addPiece(piece)
                    if p is None:
                        print(f'EEE Failed to add piece {name} ({piece}) to add-start {a}')
                    #if p is not None:
                    #    print(f'Added piece {name} in region')
                #else:
                #    print(f'Could not find piece {name}')
            
    def getGrid(self):
        return self.getParent(RegionGrid)
    def getZone(self):
        g = self.getGrid()
        if g is not None:
            return g.getZone()
        return None
    def getZonedGrid(self):
        z = self.getZone()
        if z is not None:
            return z.getZonedGrid()
        return None
    def getBoard(self):
        z = self.getZonedGrid()
        if z is not None:
            return z.getBoard()
        return self.getParent(Board)
    def getPicker(self):
        z = self.getBoard()
        if z is not None:
            return z.getPicker()
        return None
    def getMap(self):
        b = self.getPicker()
        if b is not None:
            return b.getMap()
        return None

registerElement(Region)

#
# EOF
#
