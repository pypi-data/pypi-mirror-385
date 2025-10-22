## BEGIN_IMPORT
from .. common import VerboseGuard
from . image import GBXImage
from . base import CbFont
from . features import Features
## END_IMPORT

# ====================================================================
class GBXDraw:
    def __init__(self,ar):
        '''Base class for drawing objects'''
        self._flags  = ar.dword()
        self._left   = ar.word()
        self._top    = ar.word()
        self._right  = ar.word()
        self._bottom = ar.word()

    def isSecondPass(self):
        return self._flags & 0x00000008

    def bbWidth(self):
        return self._right - self._left

    def bbHeight(self):
        return self._bottom - self._top

    def centerX(self):
        return (self._left + self._right)//2

    def centerY(self):
        return (self._top + self._bottom)//2

    def center(self):
        return (self.centerX(),self.centerY())

    def upperLeft(self):
        return (self._left,self._top)

    def lowerRight(self):
        return (self._right,self._bottom)

    def bbSize(self):
        return (self.bbWidth(),self.bbHeight())

    @classmethod
    def hex(cls,val):
        if val == 0xFF000000:
            h = 'none'
        else:
            b = (val >> 16) & 0xFF
            g = (val >>  8) & 0xFF
            r = (val >>  0) & 0xFF
            h = f'rgb({r},{g},{b})'
        return h

    def toDict(self,calc):
        return None

    def baseDict(self):
        return {
            'left':   self._left,
            'top':    self._top,
            'right':  self._right,
            'bottom': self._bottom,
            'x':      self.centerX(),
            'y':      self.centerY()
        }
    
    def svg(self,dwg,g,defmap):
        print(f'{self.__class__}.svg method not implemented')
        pass
    
    def __str__(self):
        return (f'Flags:{self._flags:08x} '
                + f'({self._left},{self._top})x({self._right},{self._bottom})')

# --------------------------------------------------------------------
class GBXRectangle(GBXDraw):
    def __init__(self,ar):
        '''Draw a rectangle'''
        with VerboseGuard(f'Reading rectangle'):
            super(GBXRectangle,self).__init__(ar)
            self._fill  = ar.dword()
            self._line  = ar.dword()
            self._width = ar.word()

    def svg(self,dwg,g,defmap):
        r = g.add(dwg.rect(insert=(self.upperLeft()),
                           size=(self.bbSize()),
                           fill=self.hex(self._fill),
                           stroke=self.hex(self._line),
                           stroke_width=self._width))
        
    def __str__(self):
        return 'Rectangle: '+super(GBXRectangle,self).__str__()

# --------------------------------------------------------------------
class GBXEllipse(GBXRectangle):
    def __init__(self,ar):
        '''Draw an ellipse'''
        with VerboseGuard(f'Reading ellipse'):
            super(GBXEllipse,self).__init__(ar)

    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        g.add(dwg.ellipse(center=(self.centerX(),self.centerY()),
                          r=(self.bbWidth(),self.bbHeight()),
                          fill=self.hex(self._fill),
                          stroke=self.hex(self._line),
                          stroke_width=self._width))
    def __str__(self):
        return 'Ellipse: '+super(GBXRectangle,self).__str__()
        
# --------------------------------------------------------------------
class GBXLine(GBXDraw):
    def __init__(self,ar):
        '''Draw a line'''
        with VerboseGuard(f'Reading line'):
            super(GBXLine,self).__init__(ar)
            self._x0    = ar.word()
            self._y0    = ar.word()
            self._x1    = ar.word()
            self._y1    = ar.word()
            self._line  = ar.dword()
            self._width = ar.word()

    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        g.add(dwg.line(start=(self._x0,self._y0),
                       end=(self._x1,self._y1),
                       stroke=self.hex(self._line),
                       stroke_width=self._width))
        
              
    def __str__(self):
        return 'Line: ' + super(GBXLine,self).__str__()
        # f'({self._x0},{self._y0}) -> ({self._x1},{self._y1})')
    
        
# --------------------------------------------------------------------
class GBXTile(GBXDraw):
    def __init__(self,ar):
        '''Draw a tile'''
        with VerboseGuard(f'Reading tile'):
            super(GBXTile,self).__init__(ar)
            self._id = ar.word()

    def svgDef(self,dwg,tileManager,markManager,defmap):
        '''Create SVG definition from image'''
        if self._id in defmap:
            return

        img  = tileManager.image(self._id)
        data = GBXImage.b64encode(img)
        if data is None:
            return

        iden = f'tile_{self._id:04x}'
        img  = dwg.defs.add(dwg.image(id=iden,href=(data),
                                      size=(img.width,img.height)))
        defmap[self._id] = img
        
    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        if self._id not in defmap: return
        
        g.add(dwg.use(defmap[self._id],
                      insert=(self._left,self._top)))
        
    def __str__(self):
        return f'Tile: {self._id} ' + super(GBXTile,self).__str__()
    
# --------------------------------------------------------------------
class GBXText(GBXDraw):
    def __init__(self,ar):
        '''Draw text'''
        with VerboseGuard(f'Reading text'):
            super(GBXText,self).__init__(ar)
            self._angle   = ar.word()
            self._color   = ar.dword()
            self._text    = ar.str()
            self._font    = CbFont(ar)

    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        g.add(dwg.text(self._text,
                       insert=(self._left,self._bottom),
                       rotate=[self._angle],
                       fill=self.hex(self._color),
                       font_family='monospace' if self._font._name == '' else self._font._name,
                       font_size=self._font._size,
                       font_weight='bold' if self._font.isBold() else 'normal',
                       font_style='italic' if self._font.isItalic() else 'normal',
                       text_decoration='underline' if self._font.isUnderline() else 'none'))
        
    def __str__(self):
        return f'Text: "{self._text}" '+super(GBXText,self).__str__()
    
# --------------------------------------------------------------------
class GBXPolyline(GBXDraw):
    def __init__(self,ar):
        '''Draw a polyline'''
        with VerboseGuard(f'Reading polyline'):
            super(GBXPolyline,self).__init__(ar)
            self._fill   = ar.dword()
            self._line   = ar.dword()
            self._width  = ar.word()
            n            = (ar.word() if Features().size_size != 8 else
                            ar.size())
            self._points = [[ar.word(),ar.word()] for _ in range(n)]

    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        g.add(dwg.polyline(self._points,
                           fill=self.hex(self._fill),
                           stroke=self.hex(self._line),
                           stroke_width=self._width))

    def __str__(self):
        return f'Polyline: {len(self._points)} '+super(GBXPolyline,self).__str__()
    
# --------------------------------------------------------------------
class GBXBitmap(GBXDraw):
    CNT = 0
    
    def __init__(self,ar):
        '''Draw a bitmap'''
        with VerboseGuard(f'Reading bitmap'):
            super(GBXBitmap,self).__init__(ar)
            sav = f'B{GBXBitmap.CNT:04d}.png'
            GBXBitmap.CNT += 1
            self._scale = ar.word()
            self._img   = GBXImage(ar,save=None)

    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        data = GBXImage.b64encode(self._img._img)
        size = self._img._img.width, self._img._img.height
        g.add(dwg.image(insert=(self._left,self._top),
                        size=size,
                        href=(data)))
        
    def __str__(self):
        return f'Bitmap: {self._img} ' + super(GBXBitmap,self).__str__()
    
# --------------------------------------------------------------------
class GBXPiece(GBXDraw):
    def __init__(self,ar):
        '''Draw a piece'''
        with VerboseGuard(f'Reading piece (draw)'):
            super(GBXPiece,self).__init__(ar)
            self._id = ar.iden()

    def toDict(self,calc=None):
        d = {'type': 'Piece',
             'id':    self._id,
             'pixel': self.baseDict()
             }
        if calc is not None:
            d['grid'] = calc(*self.center())
        return d

    def __str__(self):
        return f'Piece: {self._id} ' + super(GBXPiece,self).__str__()
    
# --------------------------------------------------------------------
class GBXMark(GBXDraw):
    def __init__(self,ar):
        '''Draw a mark tile'''
        with VerboseGuard(f'Reading mark (draw)'):
            super(GBXMark,self).__init__(ar)
            self._id  = ar.size()
            self._mid = ar.iden()
            self._ang = ar.word()

    def toDict(self,calc=None):
        d = {'type': 'Mark',
             'id':    self._mid,
             'pixel': self.baseDict()
             }
        if calc is not None:
            d['grid'] = calc(*self.center())
        return d
    def svgDef(self,dwg,tileManager,markManager,defmap):
        '''Create SVG def from mark'''
        if self._id in defmap:
            return

        data = GBXImage.b64encode(tileManager.image(self._id))
        if data is None:
            return

        iden = f'mark_{self._id:04x}'
        img  = dwg.defs.add(dwg.image(id=iden,href=(data)))
        defmap[self._id] = img
        
    def svg(self,dwg,g,defmap):
        '''Create SVG object'''
        if self._id not in defmap: return
        
        g.add(dwg.use(defmap[self._id],
                      insert=(self._left,self._top)))
        
    def __str__(self):
        return f'Mark: {self._id}/{self._mid} ' + super(GBXMark,self).__str__()
    
# --------------------------------------------------------------------
class GBXLineObj(GBXLine):
    def __init__(self,ar):
        '''Line object via reference'''
        with VerboseGuard(f'Reading line object'):
            super(GBXLineObj,self).__init__(ar)

            self._id  = ar.iden()

    def __str__(self):
        return f'Line: {self._id} ' + super(GBXLineObj,self).__str__()

    
# --------------------------------------------------------------------
class GBXDrawList:
    RECT     = 0
    ELLIPSE  = 1
    LINE     = 2
    TILE     = 3
    TEXT     = 4
    POLYLINE = 5
    BITMAP   = 6
    PIECE    = 0x80
    MARK     = 0x81
    LINEOBJ  = 0x82

    TMAP    = { RECT:      GBXRectangle,
                ELLIPSE:   GBXEllipse,
                LINE:      GBXLine,
                TILE:      GBXTile,
                TEXT:      GBXText,
                POLYLINE:  GBXPolyline,
                BITMAP:    GBXBitmap,
                PIECE:     GBXPiece,
                MARK:      GBXMark,
                LINEOBJ:   GBXLineObj}

    def __init__(self,ar):
        '''A list of drawn objects'''
        with VerboseGuard(f'Reading draw list'):
            n = ar.sub_size()

            self._obj = [self._readObj(ar) for n in range(n)]

    def toDict(self,calc=None):
        with VerboseGuard(f'Making dictionary from draw list at pass'):
            ret = []
            for i in self._obj:
                d = i.toDict(calc)
                if d is None:
                    continue

                ret.append(d)

            return ret
        
    def _readObj(self,ar):
        '''Read one object'''
        tpe  = ar.word()
        cls  = self.TMAP.get(tpe,None)
        if cls is None:
            raise RuntimeError(f'Unknown type of draw: {tpe}')

        return cls(ar)

    def svgDefs(self,dwg,tileManager,markManager,defmap):
        '''Create SVG defs'''
        with VerboseGuard(f'Create SVG defs from draw list'):
            for i in self._obj:
                if type(i) not in [GBXTile,GBXMark]: continue

                i.svgDef(dwg,tileManager,markManager,defmap)

    def svg(self,dwg,g,passNo,defmap):
        '''Create SVG objects'''
        with VerboseGuard(f'Drawing SVG from draw list at pass {passNo}'
                          f' ({len(self._obj)} objects)') as gg:
            for i in self._obj:
                if passNo == 1 and i.isSecondPass():
                    continue
                elif passNo == 2 and not i.isSecondPass():
                    continue
                gg(f'Drawing {i}')
                i.svg(dwg,g,defmap)
            
    def __str__(self):
        return '\n        '.join([str(o) for o in self._obj])

#
# EOF
#
