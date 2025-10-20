## BEGIN_IMPORT
from .. common import VerboseGuard
from . head import *
from . tile import GBXTileManager
from . piece import GBXPieceManager
from . mark import GBXMarkManager
from . board import GBXBoardManager
from . archive import Archive
from . features import Features
## END_IMPORT

# --------------------------------------------------------------------
class GBXInfo:
    def __init__(self,ar):
        '''GameBox information'''
        with VerboseGuard('Reading information') as g:
            self._bitsPerPixel = ar.word()   # 2 -> 2
            self._majorRevs    = ar.dword()  # 4 -> 6
            self._minorRevs    = ar.dword()  # 4 -> 10
            self._gameID       = ar.dword()  # 4 -> 14
            self._boxID        = ar.read(16) # 16 -> 30
            self._author       = ar.str()    # X  -> 30+X
            self._title        = ar.str()    # Y  -> 30+X+Y
            self._description  = ar.str()    # Z  -> 30+X+Y+Z
            self._password     = ar.read(16) # 16 -> 46+X+Y+Z
            self._stickyDraw   = ar.word()   # 2  -> 48+X+Y+Z
            self._compression  = ar.word()   # 2  -> 50+X+Y+Z
            self._reserved     = [ar.word() for _ in range(4)] # 4x2 -> 58+X+Y+Z
            g(f'GameBox is {self._title} by {self._author} (password: {self._password})')
        
    def __str__(self):
        return ('Information:\n'
                f'  Bits/pixel:         {self._bitsPerPixel}\n'
                f'  Major revision:     {self._majorRevs}\n'
                f'  Minor revision:     {self._minorRevs}\n'
                f'  Game ID:            {self._gameID}\n'
                f'  Box ID:             {self._boxID}\n'
                f'  Author:             {self._author}\n'
                f'  Title:              {self._title}\n'
                f'  Description:        {self._description}\n'
                f'  Password:           {self._password}\n'
                f'  Sticky Draw tools:  {self._stickyDraw}\n'
                f'  Compression level:  {self._compression}\n'
                f'  Reserved:           {self._reserved}')

    
# ====================================================================
class GameBox:
    def __init__(self,ar):
        '''Container of game'''
        with VerboseGuard(f'Reading gamebox'):
            self._header       = GBXHeader(ar,GBXHeader.BOX)
            self._info         = GBXInfo(ar)
            self._strings      = GBXStrings(ar)
            self._tileManager  = GBXTileManager(ar)
            self._boardManager = GBXBoardManager(ar)
            self._pieceManager = GBXPieceManager(ar)
            self._markManager  = GBXMarkManager(ar)

        # print(self._strings)
        # print(self._markManager)
        
    def __str__(self):
        return (str(self._header)+      
                str(self._info)+        
                str(self._strings)+     
                str(self._tileManager)+ 
                str(self._boardManager)+
                str(self._pieceManager)+
                str(self._markManager)) 

    
    @classmethod
    def fromFile(cls,filename):
        with VerboseGuard(f'Read gamebox from {filename}'):
            with Archive(filename,'rb') as ar:
                return GameBox(ar)

#
# EOF
#
