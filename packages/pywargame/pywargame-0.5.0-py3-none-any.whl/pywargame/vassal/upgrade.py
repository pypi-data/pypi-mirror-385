## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . command import *
from . trait import Trait
from . save import SaveIO
from . vmod import VMod
from . buildfile import BuildFile
from . game import Game
from . withtraits import PieceSlot
## END_IMPORT


class VLogUpgrader:
    def __init__(self,
                 vmodFileName,
                 vlogFileName,
                 verbose=False):
        self._readVModFile(vmodFileName,verbose)
        self._readVLogFile(vlogFileName,verbose)

    def _readVModFile(self,vmodFileName,verbose=False):
        with VMod(vmodFileName, 'r') as vmod:
            self._build = BuildFile(vmod.getBuildFile())
            self._game  = self._build.getGame()

        self._vmod_pieces = {}
        for piece in self._game.getPieces():
            name, piece             = self._expandPiece(piece,verbose)
            self._vmod_pieces[name] = piece

    def _expandPiece(self,piece,verbose=False):
        traits    = piece.getTraits();
        newTraits = Trait.flatten(traits, game=self._game,verbose=verbose)

        piece.setTraits(*newTraits)

        name = newTraits[-1]['name']

        return name, piece

    def _readVLogFile(self,vlogFileName,verbose=False):
        key, lines, sdata, mdata = SaveIO.readSave(vlogFileName,
                                                   alsometa=True)

        self._key         = key
        self._lines       = lines
        self._save_data   = sdata
        self._meta_data   = mdata
        self._vlog_pieces = {}
        
        for line in self._lines:
            iden, name, piece = self._vlogPiece(line,verbose)
            if piece is None:
                continue

            vmod_piece        = self._vmod_pieces.get(name,None)
            if vmod_piece is None:
                print(f'Did not find piece "{name}" in vmod')
                vmod_piece = piece

            vmod_piece.copyStates(piece)
            self._vlog_pieces[iden] = {'name': name,
                                       'vlog': piece,
                                       'vmod': vmod_piece}        


    def _vlogPiece(self,line,verbose=False):
        from re import match

        m = match(r'^\+/([0-9]+)/.*;([a-z0-9_]+)\.png.*',line)
        if m is None:
            return None,None,None

        iden  = int(m.group(1))
        piece = PieceSlot(None)
        piece.setTraits(*piece.decodeAdd(line,verbose),iden=iden)
        basic = piece.getTraits()[-1]
        
        return iden,basic['name'],piece
        

    def _newLine(self,line,verbose):
        self._new_lines.append(line)
        if verbose:
            print(line)
        
    def upgrade(self,shownew=False,verbose=False):
        self._new_lines = []
        for line in self._lines:
            add_line = self.newDefine(line,verbose)
            if add_line:
                self._newLine(add_line,shownew)
                continue

            cmd_line = self.newCommand(line,verbose)
            if cmd_line:
                self._newLine(cmd_line,shownew)
                continue 

            oth_line = self.other(line,verbose)
            if oth_line:
                self._newLine(oth_line,shownew)
                continue

            self._newLine(line,shownew)

    def newCommand(self,line,verbose=False):
        from re import match

        m = match(r'LOG\s+([+MD])/([0-9]+)/([^/]+)(.*)',line)
        if not m:
            return None
    
        cmd  = m.group(1)
        iden = int(m.group(2))
        more = m.group(3)

        if more == 'stack':
            return None

        vp = self._vlog_pieces.get(iden,None)
        if vp is None:
            print(f'Piece {iden} not found: "{line}"')
            return None

        if cmd == '+' or cmd == 'M':
            return None 

        # Get the code
        code = more + m.group(4)

        # Decode the states from the code into the old piece 
        vp['vlog'].decodeStates(code,verbose)

        # Get the previsous state from the new piece 
        old = vp['vmod'].encodedStates()

        # Copy states from the old piece to the new piece 
        vp['vmod'].copyStates(vp['vlog'],verbose)
    
        # Get the new state code from the new piece 
        new = vp['vmod'].encodedStates()

        newline = 'LOG\t'+cmd+'/'+str(iden)+'/'+new+'/'+old+'\\\\'
        # print('WAS',line)
        # print('NOW',newline)
        return newline

    def newDefine(self,line,verbose):
        from re import match
    
        m = match(r'\+/([0-9]+)/([^/]+).*',line)

        if not m:
            return False

        iden = int(m.group(1))
        more = m.group(2)
        if more == 'stack':
            return False

        vp = self._vlog_pieces.get(iden,None)
        if vp is None:
            print(f'Piece {iden} not known')

        old = vp['vlog']
        new = vp['vmod']

        old_add = old._node.childNodes[0].nodeValue;
        new_add = new.encodeAdd(*new.getTraits(),iden=iden,verbose=verbose);

        return new_add
        
    def other(self,line,verbose=False):
        return None
    

    def write(self,outFileName,verbose=False):
        SaveIO.writeSave(outFileName,
                         key         = 0xAA,
                         lines       = self._new_lines,
                         savedata    = self._save_data,
                         moduledata  = self._meta_data)

        
        
#
# EOF
#
