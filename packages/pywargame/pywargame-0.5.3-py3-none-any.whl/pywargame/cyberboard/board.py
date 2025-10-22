## BEGIN_IMPORT
from .. common import VerboseGuard
from . draw import GBXDrawList
from . cell import GBXCell, GBXCellGeometry
from . base import CbManager, CbFont
from . head import num_version
from . features import Features
from . draw import GBXDraw
## END_IMPORT

# --------------------------------------------------------------------
class GBXBoardCalculator:
    def __init__(self,board):
        self._geometry  = board._full
        self._nRows     = board._nRows
        self._nCols     = board._nCols
        self._rowOffset = board._rowOffset
        self._colOffset = board._colOffset
        self._rowInvert = board._rowInvert
        self._colInvert = board._colInvert

    def __call__(self,x,y):
        # Shift depending on grid type and stagger
        row, col = self._geometry.inverse(x,y)
        if self._rowInvert:
            row = self._nRows - row - 1
        if self._colInvert:
            col = self._nCols - col - 1

        return row+self._rowOffset, col+self._colOffset

# --------------------------------------------------------------------
class GBXBoard:
    def __init__(self,ar):
        '''A board'''
        with VerboseGuard(f'Reading board') as g:
            self._serial          = ar.iden()
            self._visible         = ar.word()
            self._snap            = ar.word()
            self._xSnap           = ar.dword()
            self._ySnap           = ar.dword()
            self._xSnapOffset     = ar.dword()
            self._ySnapOffset     = ar.dword()
            self._maxLayer        = ar.word()
            self._background      = ar.dword()
            self._name            = ar.str()
            hasDraw               = ar.word()
            self._baseDraw        = GBXDrawList(ar) if hasDraw else None
                
            self._showCellBorder  = ar.word()
            self._topCellBorder   = ar.word()
            self._reserved        = [ar.word() for _ in range(4)]
            self._reserved2       = None
            self._rowOffset       = 0
            self._colOffset       = 0
            self._rowInvert       = False
            self._colInvert       = False
            self._nRows           = 0
            self._nCols           = 0
            self._transparent     = False
            self._numbers         = 0
            self._trackCell       = False
            self._frameColor      = 0xFF000000
            self._full            = None
            self._half            = None
            self._small           = None
            self._map             = []
            self._topDraw         = None
            
            hasArray              = ar.word()
            if hasArray != 0:
                self._reserved2   = [ar.word() for _ in range(4)]
                self._rowOffset   = ar.word()
                self._colOffset   = ar.word()
                self._rowInvert   = ar.word()
                self._colInvert   = ar.word()
                self._nRows       = ar.int(Features().sub_size)
                self._nCols       = ar.int(Features().sub_size)
                self._transparent = ar.word()
                self._numbers     = ar.word()
                self._trackCell   = ar.word()
                self._frameColor  = ar.dword()
            
                self._full        = GBXCellGeometry(ar)
                self._half        = GBXCellGeometry(ar)
                self._small       = GBXCellGeometry(ar)
            
                self._map = [[GBXCell(ar,row,col) for col in range(self._nCols)]
                             for row in range(self._nRows)]
            
            hasDraw              = ar.word()
            self._topDraw        = GBXDrawList(ar) if hasDraw else None
            g(f'Board background read: {self._background:06x}, frame color: {self._frameColor:06x}')

    def toDict(self,tileManager,markManager,strings,no,boardDigits,
               alsoMap=True):
        from io import StringIO
        
        with VerboseGuard(f'Making dict of board {self._name}') as g:
            sav = f'board_{no:0{boardDigits}d}.svg'
            g(f'File to save in: {sav}')
            dct = {'name':               self._name,
                   'serial':             self._serial,
                   'visible':            self._visible,
                   'snap':  {
                       'enable':         self._snap,
                       'x': { 
                           'distance':   self._xSnap,
                           'offset':     self._xSnapOffset
                       },
                       'y': {
                           'distance':   self._ySnap,
                           'offset':     self._ySnapOffset
                       }
                   },
                   'max layer':          self._maxLayer,
                   'cell border': {
                       'visible':        self._showCellBorder,
                       'on top layer':   self._topCellBorder,
                   },
                   'rows': {
                       'size':           self._nRows,
                       'offset':         self._rowOffset,
                       'inverted':       self._rowInvert
                   },
                   'columns': {
                       'size':           self._nCols,
                       'offset':         self._colOffset,
                       'inverted':       self._colInvert
                   },
                   'cells': {
                       'transparent':    self._transparent,
                       'foreground':     self._frameColor,
                   },
                   'numbering': {
                       'order':   'V' if self._numbers % 2 == 0 else 'H',
                       'padding': self._numbers in [2,3],
                       'first':   'A' if self._numbers in [4,5] else 'N'
                   }
                }
            if self._full is not None:
                dct['cells']['geometry'] = self._full.toDict()
            if alsoMap and self._map is not None:
                dct['cells']['list'] = [[c.toDict(tileManager,self._full)
                                         for c in row]
                                        for row in self._map]
            
            
            sav = f'board_{no:0{boardDigits}d}.svg'
            img = self.drawing(sav,
                               tileManager=tileManager,
                               markManager=markManager)
            # img.save(pretty=True)

            stream = StringIO()
            img.write(stream,pretty=True)
            
            dct['filename'] = sav
            dct['image']    = stream.getvalue()#img.tostring()
            dct['size']     = self._full.boardSize(self._nRows,self._nCols)
            
            return dct

    def drawing(self,sav,tileManager,markManager,*args,**kwargs):
        from svgwrite import Drawing
        from svgwrite.base import Title
        with VerboseGuard(f'Making SVG of board {self._name}') as g:
            size  = self._full.boardSize(self._nRows,self._nCols)
            dwg   = Drawing(filename=sav,size=size)
            frame, defMap, patMap = self.defs(dwg,tileManager,markManager)
            
            # Draw background
            g(f'Board background: {self._background:06x} {GBXDraw.hex(self._background)}')
            dwg.add(Title(self._name))
            dwg.add(dwg.rect(id='background',
                             insert=(0,0),
                             size=size,
                             fill=GBXDraw.hex(self._background)
                             #f'#{self._background:06x}')
                             ))
            # GBXDraw.hex(self._background)

            g('Drawing base layer')
            bse  = self.base (dwg, 0, defMap)
            g('Drawing cells')
            grd  = self.cells(dwg, frame, patMap)
            if self._showCellBorder and not self._topCellBorder:
                self.borders(dwg,frame)
            g('Drawing top layer')
            top1 = self.top  (dwg, 1, defMap)
            if self._showCellBorder and self._topCellBorder:
                self.borders(dwg,frame)
            top2 = self.top  (dwg, 2, defMap)
                    
            return dwg

    def defs(self,dwg,tileManager,markManager):
        defMap         = {}
        patMap         = {}
        frame          = self._full.svgDef(dwg)
        defMap['cell'] = frame

        # Get defininitions from base layer 
        if self._baseDraw:
            self._baseDraw.svgDefs(dwg,
                                   tileManager,
                                   markManager,
                                   defMap)
        # Get definitions from cell layer 
        for row in self._map:
            for cell in row:
                cell.svgDef(dwg,tileManager,patMap)
            
        # Get definitions from top layer 
        if self._topDraw:
            self._topDraw.svgDefs(dwg,
                                  tileManager,
                                  markManager,
                                  defMap)

        return frame, defMap, patMap

    def base(self,dwg,passNo,defMap):
        bse  = dwg.add(dwg.g(id=f'base_{passNo:02d}'))
        if self._baseDraw:
            self._baseDraw.svg(dwg,bse,passNo,defMap)

        return bse
        
    def cells(self,dwg,frame,patMap):
        grd  = dwg.add(dwg.g(id='grid'))
        for row in self._map:
            for cell in row:
                cell.svg(dwg,grd,frame,self._full,patMap)

        return grd

    def borders(self,dwg,frame):
        brd  = dwg.add(dwg.g(id='borders'))
        for row in self._map:
            for cell in row:
                cell.svgFrame(dwg,brd,frame,self._full,self._frameColor)

        return brd
        
    def top(self,dwg,passNo,defMap):
        top  = dwg.add(dwg.g(id=f'top_{passNo:02d}'))
        if self._topDraw:
            self._topDraw.svg (dwg,top,passNo,defMap)
        
        return top

    def __str__(self):
        return (f'GBXBoard: {self._name}\n'
                f'      serial:           {self._serial}\n'
                f'      visible:          {self._visible}\n'
                f'      snap:             {self._snap}\n'
                f'      xSnap:            {self._xSnap}\n'
                f'      ySnap:            {self._ySnap}\n'
                f'      xSnapOffset:      {self._xSnapOffset}\n'
                f'      ySnapOffset:      {self._ySnapOffset}\n'
                f'      maxLayer:         {self._maxLayer}\n'
                f'      background:       {self._background:08x}\n'
                f'      Base draws:       {self._baseDraw}\n'
                f'      Show cell border: {self._showCellBorder}\n'
                f'      Top cell border:  {self._topCellBorder}\n'
                f'      Reserved:         {self._reserved}\n'
                f'      Reserved2:        {self._reserved}\n'
                f'      Row offset:       {self._rowOffset}\n'
                f'      Column offset:    {self._colOffset}\n'
                f'      Row invert:       {self._rowInvert}\n'
                f'      Colunn invert:    {self._colInvert}\n'
                f'      # Rows:           {self._nRows}\n'
                f'      # Cols:           {self._nCols}\n'
                f'      Transparent:      {self._transparent}\n'
                f'      Numbers:          {self._numbers}\n'
                f'      Track cells:      {self._trackCell}\n'
                f'      Frame color:      {self._frameColor:08x}\n'
                f'      Full geometry:    {self._full}\n'
                f'      Half geometry:    {self._half}\n'
                f'      Small geometry:   {self._small}\n'
                f'      Top draws:        {self._topDraw}'
                )
    
            
            
        
# --------------------------------------------------------------------
class GBXBoardManager(CbManager):
    def __init__(self,ar):
        '''Manager of boards'''
        with VerboseGuard(f'Reading board manager'):
            self._nextSerial  = ar.iden()
            super(GBXBoardManager,self).__init__(ar)
            # print(Features().id_size)
            self._boards = self._readSub(ar,GBXBoard)

    def __len__(self):
        return len(self._boards)

    def bySerial(self,serial):
        for b in self._boards:
            if b._serial == serial:
                return b

        return None
    
    def toDict(self,tileManager,markManager,strings):
        from math import log10, ceil
        with VerboseGuard(f'Making dict board manager'):
            boardDigits = int(ceil(log10(len(self)+.5)))

            return {b._serial:
                    b.toDict(tileManager,markManager,strings,no,boardDigits)
                    for no, b in enumerate(self._boards)}
    
    def __str__(self):
        return ('GBXBoard manager:\n'
                + f'  Next serial:  {self._nextSerial:08x}\n'
                + super(GBXBoardManager,self).__str__()
                + self._strSub('boards',self._boards))

# --------------------------------------------------------------------
class GSNGeomorphicElement:
    def __init__(self,ar):
        with VerboseGuard('Reading geomorphic element'):
            self._serial = ar.word()
        
    def __str__(self):
        return f'GSNGeomorphicElement: {self._serial}'
    
# --------------------------------------------------------------------
class GSNGeomorphicBoard:
    def __init__(self,ar):
        with VerboseGuard('Reading geomorphic board'):
            self._name     = ar.str()
            self._nRows    = ar.word()
            self._nCols    = ar.word()
            n              = ar.word()
            self._elements = [GSNGeomorphicElement(ar) for _ in range(n)]
        
    def __str__(self):
        pl = '\n    '.join([str(s) for s in self._elements])
        return (f'GeomorphicBoard: {self._name}\n'
                f'  Size: {self._nRows}x{self._nCols}\n'
                f'  Elements:\n    {pl}\n')
    
# --------------------------------------------------------------------
class GSNBoard:
    def __init__(self,ar,vers):
        with VerboseGuard(f'Reading scenario board {vers//256}.{vers%256}'):
            hasGeo                 = ar.byte()
            self._geo              = GSNGeomorphicBoard(ar) if hasGeo else None
            self._serial           = ar.iden()
            self._snap             = ar.word()
            self._xSnap            = ar.dword()
            self._ySnap            = ar.dword()
            self._xSnapOffset      = ar.dword()
            self._ySnapOffset      = ar.dword()
            self._xStagger         = ar.word()
            self._yStagger         = ar.word()
            self._piecesVisible    = ar.word()
            self._blockBeneath     = ar.word()
            self._rotate180        = ar.word()
            self._showTiny         = ar.word()
            self._indicatorsVisible= ar.word()
            self._cellBorders      = ar.word()
            self._smallCellBorders = ar.word()
            self._enforceLocks     = ar.word()
            self._plotLineColor    = ar.dword()
            self._plotLineWidth    = ar.word()
            self._lineColor        = ar.dword()
            self._lineWidth        = ar.word()
            self._textColor        = ar.dword()
            self._textBoxColor     = ar.dword()
            self._font             = CbFont(ar)
            self._gridCenters      = ar.word()
            self._snapMove         = ar.word()
            self._indactorsTop     = ar.word()
            self._openOnLoad       = ar.word()
            self._prevPlotMode     = ar.word()
            self._prevPlotX        = ar.word()
            self._prevPlotY        = ar.word()
            self._ownerMask        = (ar.word() if vers < num_version(3,10) else
                                      ar.dword())
            self._restrictToOwner  = ar.word()
            self._pieces           = GBXDrawList(ar)
            self._indicators       = GBXDrawList(ar)
        
        
    def toDict(self,boardManager):
        board = (None if boardManager is None else
                 boardManager.bySerial(self._serial))
        geom  = None if board is None else board._full
        calc  = None if geom  is None else GBXBoardCalculator(board)
        
        return {
            'onload':             self._openOnLoad != 0,
            'snap':  {
                'enable':         self._snap,
                'onmove':         self._snapMove != 0,
                'gridCenter':     self._gridCenters != 0,
                'x': { 
                    'distance':   self._xSnap,
                    'offset':     self._xSnapOffset
                },
                'y': {
                    'distance':   self._ySnap,
                    'offset':     self._ySnapOffset
                }
            },
            'moves': {
                'color':          self._plotLineColor,
                'width':          self._plotLineWidth
            },
            'stacking':           [self._xStagger, self._yStagger],
            'owner':              self._ownerMask,
            'restrict':           self._restrictToOwner != 0,
            'grid': {
                'show':           self._cellBorders != 0,
                'color':          self._lineColor,
                'width':          self._lineWidth
            },
            'pieces':             self._pieces.toDict(calc),
            'indicators':         self._indicators.toDict(calc)
        }
    
    def __str__(self):
        return (f'ScenarioBoard: {self._serial}'
                f'      Geomorphic: {"None" if self._geo is None else self._geo}\n'
                f'      Font:       {self._font}\n'
                f'      Pieces:\n{str(self._pieces)}\n'
                f'      Indicators:\n{str(self._indicators)}')
    
# --------------------------------------------------------------------
class GSNBoardManager:    
    def __init__(self,ar,vers):
        with VerboseGuard(f'Reading scenario board manager') as g:
            self._nextGeoSerial = ar.iden()
            self._reserved      = [ar.word() for _ in range(3)]
            n                   = ar.sub_size()
            g(f'Got {n} boards to read')
            self._boards        = [GSNBoard(ar,vers) for _ in range(n)]

    def toDict(self,boardManager):
        hasStart = False
        for b in self._boards:
            if b._openOnLoad:
                hasStart = True

        # Make sure at least one map is loaded 
        if not hasStart and len(self._boards) > 0:
            self._boards[0]._openOnLoad = True
            
        return {b._serial: b.toDict(boardManager) for b in self._boards }

    def __str__(self):
        pl = '\n    '.join([str(s) for s in self._boards])
        return f'GSNBoardManager: {self._nextGeoSerial}\n    {pl}\n'
    
#
# EOF
#

