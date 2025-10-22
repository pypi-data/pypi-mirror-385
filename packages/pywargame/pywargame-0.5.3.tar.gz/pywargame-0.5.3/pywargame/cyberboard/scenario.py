## BEGIN_IMPORT
from .. common import VerboseGuard
from . head    import *
from . player  import GSNPlayerManager
from . windows import GSNWindows
from . palette import GSNTrayPalette
from . palette import GSNMarkPalette
from . board   import GSNBoardManager
from . tray    import GSNTrayManager
from . piece   import GSNPieceTable
from . gamebox import GameBox
## END_IMPORT

class GSNInfo:
    def __init__(self,ar):
        '''Scenario information'''
        self._disableOwnerTips = ar.word()
        self._reserved         = [ar.word() for _ in range(3)]
        self._gameID           = ar.dword()  # 4 -> 14
        self._majorRevs        = ar.dword()  # 4 -> 6
        self._minorRevs        = ar.dword()  # 4 -> 10
        self._gbxFilename      = ar.str()
        self._scenarioID       = ar.dword()
        self._title            = ar.str()    # Y  -> 30+X+Y
        self._author           = ar.str()    # X  -> 30+X
        self._description      = ar.str()    # Z  -> 30+X+Y+Z
        self._keepBackup       = ar.word()
        self._keepHistory      = ar.word()
        self._verifyState      = ar.word()
        self._verifySave       = ar.word()
        self._showObjectTip    = ar.word()

    def __str__(self):
        return ('Information:\n'
                f'  Disable owner tips: {self._disableOwnerTips}\n'
                f'  Reserved:           {self._reserved}\n'
                f'  Game ID:            {self._gameID}\n'
                f'  Major revision:     {self._majorRevs}\n'
                f'  Minor revision:     {self._minorRevs}\n'
                f'  Game box filename:  {self._gbxFilename}\n'
                f'  Scenario ID:        {self._scenarioID}\n'
                f'  Title:              {self._title}\n'
                f'  Author:             {self._author}\n'
                f'  Description:        {self._description}\n'
                f'  Keep backup:        {self._keepBackup}\n'
                f'  Keep history:       {self._keepHistory}\n'
                f'  Verify state:       {self._verifyState}\n'
                f'  Verify save:        {self._verifySave}\n'
                f'  Show object tips:   {self._showObjectTip}\n')
                
# ====================================================================
class Scenario:
    def __init__(self,ar,gbxfilename=None):
        '''Container of game'''
        with VerboseGuard(f'Reading scenario'):
            self._header        = GBXHeader       (ar,GBXHeader.SCENARIO)
            self._info          = GSNInfo         (ar)
            self._strings       = GSNStrings      (ar)
            self._playerManager = GSNPlayerManager(ar)
            self._windows       = GSNWindows      (ar)
            self._trayA         = GSNTrayPalette  (ar,self._header._vers,'A')
            self._trayB         = GSNTrayPalette  (ar,self._header._vers,'B')
            self._mark          = GSNMarkPalette  (ar,self._header._vers)
            self._boards        = GSNBoardManager (ar,self._header._vers)
            self._trayManager   = GSNTrayManager  (ar,self._header._vers)
            self._pieceTable    = GSNPieceTable   (ar,self._header._vers)
            # Possibly override GBX file name 
            if gbxfilename is not None and gbxfilename != '':
                self._info._gbxFilename = gbxfilename

            self.readGameBox(ar)

    def readGameBox(self,ar):
        from pathlib import Path
        with VerboseGuard(f'Read game box file {self._info._gbxFilename}') as v:
            gbxname = self._info._gbxFilename
            gbxpath = Path(gbxname)
            
            if not gbxpath.exists():
                v(f'GameBox file {gbxpath} does not exist')
                if '\\' in gbxname:
                    gbxname = gbxname.replace('\\','/')
                    gbxpath = Path(gbxname)
                gbxpath = ar.path.parent / Path(gbxpath.name)
                if not gbxpath.exists():
                    raise RuntimeError(f'GameBox file {gbxpath} cannot be found')
                
            self._gbx = GameBox.fromFile(str(gbxpath))

            if self._gbx._info._gameID != self._info._gameID:
                raise RuntimeError(f'Game IDs from GBX and GSN does not match: '
                                   f'{self._gbx._info._gameID} versus '
                                   f'{self._header._gameID}')
        
    def __str__(self):
        return (str(self._header)+      
                str(self._info)+        
                str(self._strings)+
                str(self._playerManager)+
                str(self._windows)+
                str(self._trayA)+
                str(self._trayB)+
                str(self._mark)+
                str(self._boards)+
                str(self._trayManager)+
                str(self._pieceTable)+
                str(self._gbx)+
                ''
                )

    
    @classmethod
    def fromFile(cls,filename,gbxfile=None):
        with Archive(filename,'rb') as ar:
            return Scenario(ar,gbxfile)
