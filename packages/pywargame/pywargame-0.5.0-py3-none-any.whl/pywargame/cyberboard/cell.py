## BEGIN_IMPORT
from .. common import VerboseGuard
from . image import GBXImage
from . draw import GBXDraw
from . features import Features
## END_IMPORT

# ====================================================================
class GBXCellGeometry:
    RECTANGLE        = 0
    HORIZONTAL_BRICK = 1
    VERTICAL_BRICK   = 2
    HEXAGON          = 3
    SIDEWAYS_HEXAGON = 4
    STAGGER_OUT      = 0
    STAGGER_IN       = 1
    TYPES = {
        RECTANGLE       : 'rectangle',
        HORIZONTAL_BRICK: 'horizontal brick',
        VERTICAL_BRICK  : 'vertical brick',
        HEXAGON         : 'hexagon',
        SIDEWAYS_HEXAGON: 'sideways hexagon'
    }
    STAGGERS = {
        STAGGER_OUT: 'out',
        STAGGER_IN:  'in'
    }

    def __init__(self,ar):
        '''The geometry of cells'''
        with VerboseGuard('Reading cell geometry'):
            from numpy import max
            
            self._type      = ar.word()
            self._stagger   = ar.word()
            self._left      = ar.word()
            self._top       = ar.word()
            self._right     = ar.word()
            self._bottom    = ar.word()
            n               = 7 if self._type > 2 else 5
            self._points    = [[ar.word(),ar.word()] for _ in range(n)]
            size            = max(self._points,axis=0)
            self._dx        = int(size[0])
            self._dy        = int(size[1])
            self._size      = [self._dx,self._dy]
            
            if self._type == self.HEXAGON:
                self._dx = int(0.75 * self._dx)
            elif self._type == self.SIDEWAYS_HEXAGON:
                self._dy = int(0.75 * self._dy)

    def toDict(self):
        from numpy import max
        return {'shape':      self.TYPES.get(self._type,''),
                'stagger':    self.STAGGERS.get(self._stagger,''),
                'size':       self._size,
                'bounding box (ltrb)':
                (self._left, self._top, self._right, self._bottom),
                'points':     self._points }

    def svgDef(self,dwg):
        with VerboseGuard('Defining SVG cell geometry'):
            if self._type in [0,1,2]:
                return dwg.defs.add(dwg.rect(id='cell',
                                             size=(self._right-self._left,
                                                   self._bottom-self._top)))
        
            return dwg.defs.add(dwg.polygon(self._points,id='cell'))

    def translate(self,row,col,center=False):
        x = col * self._dx
        y = row * self._dy
        if self._type == self.RECTANGLE: # No offset for rectangles
            return x,y
        if self._type in [self.HORIZONTAL_BRICK,self.SIDEWAYS_HEXAGON]:
            x += self._dx//2 if (row % 2) != self._stagger else 0
        if self._type in [self.VERTICAL_BRICK,self.HEXAGON]:
            y += self._dy//2 if (col % 2) != self._stagger else 0
        if center:
            x += self._size[0]//2
            y += self._size[1]//2
        return x,y

    def inverse(self,x,y):
        col = x / self._dx
        row = y / self._dy
        if self._type in [self.HORIZONTAL_BRICK,self.SIDEWAYS_HEXAGON]:
            col -= .5 if (int(row) % 2) != self._stagger else 0
        if self._type in [self.VERTICAL_BRICK,self.HEXAGON]:
            row -= .5  if (int(col) % 2) != self._stagger else 0

        # CyberBoard start at 1
        return int(row)+1, int(col)+1 
        

    def boardSize(self,nrows,ncols):
        w = ncols * self._dx
        h = nrows * self._dy

        if self._type in [2,3]:
            h += self._dy // 2
        if self._type in [1,4]:
            w += self._dx // 2
        if self._type == 3:
            w += self._dx // 3
        if self._type == 4:
            h += self._dy // 3

        return w+1,h+1
    
    def __str__(self):
        return (f'type: {self.TYPES.get(self._type,"")} '
                + f'stagger: {self.STAGGERS.get(self._stagger,"")} '
                + f'({self._left},{self._top})x({self._right},{self._bottom}) '
                + f': [{self._points}]')

        
# --------------------------------------------------------------------
class GBXCell:
    def __init__(self,ar,row,column):
        '''A single cell'''
        with VerboseGuard(f'Reading cell row={row} column={column}'):
            self._row    = row
            self._column = column
            if Features().id_size == 4:
                self._is_tile = ar.byte();
            self._tile   = ar.dword()
            if Features().id_size != 4:
                self._is_tile  = (self._tile >> 16) == 0xFFFF;
                if self._is_tile:
                    self._tile = self._tile & 0xFFFF

    def tileID(self):
        if not self._is_tile:
            return None
        return self._tile

    def color(self):
        if self._is_tile:
            return None
        return GBXDraw.hex(self._tile)

    def toDict(self,tileManager,calc=None):
        d = {'row': self._row,
             'column': self._column}
        if not self._is_tile:
            d['color'] = GBXDraw.hex(self._tile)
        else:
            d['tile'] = tileManager.store(self._tile)
        if calc is not None:
            d['pixel'] = calc.translate(self._row,self._column,True)
        return d
    
    
    def svgDef(self,dwg,tileManager,ptm):
        tileID = self.tileID()
        if tileID is None:
            return

        if tileID in ptm: # Have it
            return 

        with VerboseGuard(f'Defining SVG pattern'):
            img  = tileManager.image(tileID)
            data = GBXImage.b64encode(img)
            if data is None:
                return
            
            iden = f'terrain_{tileID:04x}'
            pat  = dwg.defs.add(dwg.pattern(id=iden,
                                            size=(img.width,img.height)))
            pat.add(dwg.image(href=(data)))
            ptm[tileID] = pat

    def svg(self,dwg,g,cell,geom,ptm):
        tileID = self.tileID()
        if tileID is not None:
            fill = ptm[tileID].get_paint_server()
        else:
            fill = self.color()

        trans = geom.translate(self._row,self._column)
        iden  = f'cell_bg_{self._column:03d}{self._row:03d}'
        g.add(dwg.use(cell,insert=trans,fill=fill,id=iden))
        
    def svgFrame(self,dwg,g,cell,geom,color):
        trans = geom.translate(self._row,self._column)
        iden  = f'cell_fg_{self._column:03d}{self._row:03d}'
        g.add(dwg.use(cell,
                      insert=trans,
                      stroke=GBXDraw.hex(color),
                      fill='none',
                      id=iden))
        

    def __str__(self):
        return f'({self._row:02d},{self._column:02d}): {self._tile:08x}'

#
# EOF
#
