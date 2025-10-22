## BEGIN_IMPORT
from .. common import VerboseGuard
from . image import GBXImage
from . base import CbManager
from . features import Features
## END_IMPORT

# ====================================================================
class GBXTileLocation:
    def __init__(self,ar):
        '''Where a tile can be found'''
        with VerboseGuard('Reading tile location') as g:
            self._sheet  = (ar.word() if not Features().size_size == 8 else
                            ar.size())
            self._offset = ar.word() 
            g(f'Tile location at sheet={self._sheet} offset={self._offset}')
            if self._sheet == 65535: self._sheet = -1

    def __str__(self):
        return f'{self._sheet:3d} @ {self._offset:6d}'

        
# --------------------------------------------------------------------
class GBXTileDefinition:
    def __init__(self,ar):
        '''The definition of a tile'''
        with VerboseGuard('Reading tile definition'):
            self._full = GBXTileLocation(ar)
            self._half = GBXTileLocation(ar)
            self._fill = ar.dword()

    def __str__(self):
        return f'Full: {self._full}, Half: {self._half}, Fill: {self._fill:08x}'
    
        
# --------------------------------------------------------------------
class GBXTileSet:
    def __init__(self,ar):
        '''A set of tiles'''
        with VerboseGuard('Reading tile set'):
            self._name = ar.str()
            n = ar.word() if Features().size_size != 8 else ar.size()
            self._ids  = [ar.iden()
                          for _ in range(n)]

    def __str__(self):
        return (self._name + ':' + ','.join([str(i) for i in self._ids]))

    
# --------------------------------------------------------------------
class GBXTileSheet:
    def __init__(self,ar,transparent):
        '''A single image that has multiple tile images in it
        
        X,Y are the tile sizes
        '''
        with VerboseGuard('Reading tile sheet'):
            self._x      = ar.word()
            self._y      = ar.word()
            hasBM        = ar.word()
            self._img    = GBXImage(ar,transparent) if hasBM else None

    def sub(self,off):
        if self._img is None:
            return None

        return self._img._img.crop((0,off,self._x,off+self._y))
    
    def __str__(self):
        bm = str(self._img) if self._img is not None else 'None'
        return (f'c=({self._x:4d},{self._y:4d}) bitmap={bm}')
        

# --------------------------------------------------------------------
class GBXTileManager(CbManager):
    def __init__(self,ar):
        '''Tile manager (including tiles)'''
        with VerboseGuard('Reading tile manager'):
            self._transparent = ar.dword()
            super(GBXTileManager,self).__init__(ar)
            
            ts = lambda ar : GBXTileSheet(ar, self._transparent)
            self._tiledefs    = self._readSub(ar,GBXTileDefinition,
                                              Features().id_size)
            self._tilesets    = self._readSub(ar,GBXTileSet)
            self._tilesheets  = self._readSub(ar,ts)
            self._toStore     = {} # Used in boards, not elsewhere

    def image(self,tileID):
        if tileID is None:
            return None 
        if tileID == 0xFFFF:
            return None

        tileDef = self._tiledefs[tileID]
        tileSht = self._tilesheets[tileDef._full._sheet]
        img     = tileSht.sub(tileDef._full._offset)
        return img

    def store(self,tileID):
        filename = self._toStore.get(tileID,{}).get('filename',None)
        if filename is None:
            filename              = f'tile_{tileID:04d}.png'
            self._toStore[tileID] = {
                'filename': filename,
                'image'   : self.image(tileID)
            }

        return filename
        
        
    def __str__(self):
        return ('Tile manager:\n'
                 + f'  Transparent:  {self._transparent:08x}\n'
                 + super(GBXTileManager,self).__str__()
                 + self._strSub('tiles',self._tiledefs) + '\n'
                 + self._strSub('tile sets',self._tilesets) + '\n'
                 + self._strSub('tile sheets',self._tilesheets))

#
# EOF
#
