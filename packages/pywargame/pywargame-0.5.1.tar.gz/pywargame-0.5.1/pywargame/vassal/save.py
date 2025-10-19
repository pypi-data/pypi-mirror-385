## BEGIN_IMPORT
from . moduledata import ModuleData
from . withtraits import PieceSlot, DummyWithTraits
from . trait import Trait
from . traits import BasicTrait, StackTrait
from . element import DummyElement
from . mapelements import AtStart
## END_IMPORT

# ====================================================================
class SaveIO:
    '''Wrapper around a save file 
    
    Save file is
    
        "!VCSK" KEY content
    
    Key is two bytes drawn as a random number in 0-255.  Content is
    two bytes per character.  Content characters are encoded with the
    random key.
    
    Save file (.vsav) content is
    
        "begin_save" ESC
        "\" ESC
        [commands]* ESC
        "PLAYER" name password side ESC
        [map+"BoardPicker" name x y ESC]+
        "SETUP_STACK" ESC
        "TURN"+name state ESC
        "end_save"
    
    Commands are
    
        "+/" id "/" body "\"
    
    where body are
    
        "stack" "/" mapName ; x ; y ; ids "\"
        piece_type "/" piece_state   (x and y set here too) "\"
    
    x and y are pixel coordinates (sigh!).  This means we have to know
    
    - the pixel location of a hex
    - the hex coordinates of that hex
    - whether rows and columns are descending
    - if even hexes are higher or not
    
    The two first items _must_ be user supplied (I think).  When we
    add stacks or pieces, we must then get the numerical hex
    coordinates - not what the user specified in the VASSAL editor or
    the like.  Of course, this means opening the module before writing
    the patch.py script.
    
    It seems like every piece is added in a stack.
    
    The id is a numerical value.  Rather big (e.g., 1268518000806). It
    is the current number of miliseconds since epoch, with offset to
    disambiguate.
    
    The ID is the current time, taken from a milisecond clock,
    possibly adjusted up if there is a clash.  This is all managed by
    the GameState class.

    '''
    VCS_HEADER = b'!VCSK'
    VK_ESC     = chr(27)
    DEC_MAP    = {
        # 0-9
        0x30: 0x30,
        0x31: 0x30,
        0x32: 0x30,
        0x33: 0x30,
        0x34: 0x30,
        0x35: 0x30,
        0x36: 0x30,
        0x37: 0x30,
        0x38: 0x30,
        0x39: 0x30,
        # A-F
        0x41: 0x37,
        0x42: 0x37,
        0x43: 0x37,
        0x44: 0x37,
        0x45: 0x37,
        0x46: 0x37,
        # a-f
        0x61: 0x57,
        0x62: 0x57,
        0x63: 0x57,
        0x64: 0x57,
        0x65: 0x57,
        0x66: 0x57
    }
    ENC_MAP = [b'0',b'1',b'2',b'3',b'4',b'5',b'6',b'7',b'8',b'9',
               b'a',b'b',b'c',b'd',b'e',b'f']

    # ----------------------------------------------------------------
    @classmethod
    def decHex(cls,b):
        '''Decode a single char into a number

        If the encoded number is b, then the decoded number is
        
            b - off
    
        where off is an offset that depends on b
    
           off = 0x30   if 0x30 <= b <= 0x39
                 0x37   if 0x41 <= b <= 0x46
                 0x57   if 0x61 <= b <= 0x66
        '''
        return b - cls.DEC_MAP[b]
    # --------------------------------------------------------------------
    @classmethod
    def readByte(cls,inp,key):
        '''Read a single byte of information from input stream
    
        Two characters (c1 and c2) are read from input stream, and the
        decoded byte is then
    
            ((dechex(c1) << 4 | dechex(c2)) ^ key) & 0xFF
        
        Parameters
        ----------
        inp : stream
            Input to read from
        key : int
            Key to decode the input
    
        Returns
        -------
        b : int
            The read byte
        '''
        try:
            pair = inp.read(2)
        except Exception as e:
            from sys import stderr
            print(e,file=stderr)
            return None
    
        if len(pair) < 2:
            return None
    
        return ((cls.decHex(pair[0]) << 4 | cls.decHex(pair[1])) ^ key) & 0xFF
    # --------------------------------------------------------------------
    @classmethod
    def readSave(cls,file,alsometa=False):
        '''Read data from save file.  The data is read into lines
        returned as a list.

        '''
        from zipfile import ZipFile
        
        # We open the save file as a zip file 
        with ZipFile(file,'r') as z:
            # open the save file in the archive
            save = z.open('savedGame','r')
            
            # First, we check the header
            head = save.read(len(cls.VCS_HEADER))
            assert head == cls.VCS_HEADER, \
                f'Read header {head} is not {cls.VCS_HEADER}'
    
            # Then, read the key
            pair = save.read(2)
            key  = (cls.decHex(pair[0]) << 4 | cls.decHex(pair[1]))
    
            # Now read content, one byte at a time 
            content = ''
            while True:
                byte = cls.readByte(save,key)
                if byte is None:
                    break
    
                # Convert byte to character 
                content += chr(byte)
    
            lines = content.split(cls.VK_ESC)

            if alsometa:
                savedata = z.read(VSav.SAVE_DATA)
                moduledata = z.read(VMod.MODULE_DATA)

        if not alsometa:
            return key, lines

        return key,lines,savedata,moduledata

    # --------------------------------------------------------------------
    @classmethod
    def writeByte(cls,out,byte,key):
        '''Write a single byte

        Parameters
        ----------
        out : IOStream
            Stream to write to
        byte : char
            Single byte to write
        key : int
            Key to encode with (defaults to 0xAA - alternating 0's and 1's)
        '''
        b    = ord(byte) ^ key
        pair = cls.ENC_MAP[(b & 0xF0) >> 4], cls.ENC_MAP[b & 0x0F]
        out.write(pair[0])
        out.write(pair[1])

    # --------------------------------------------------------------------
    @classmethod
    def writeInZip(cls,z,key,lines,filename='savedGame'):
        '''Write a save file in a zip file (VMod)'''
        # open the save file in the archive
        with z.open(filename,'w') as save:
            # Write header
            save.write(cls.VCS_HEADER)
    
            # Split key
            pair = cls.ENC_MAP[(key & 0xF0) >> 4], cls.ENC_MAP[(key & 0x0F)]
            save.write(pair[0])
            save.write(pair[1])
    
            # Form content
            content = cls.VK_ESC.join(lines)
    
            # Write each character as two
            for c in content:
                cls.writeByte(save, c, key)
        
    # --------------------------------------------------------------------
    @classmethod
    def writeSave(cls,file,key,lines,savedata=None,moduledata=None):
        '''Write a save file'''
        from zipfile import ZipFile, ZIP_DEFLATED
        
        # We open the save file as a zip file 
        with ZipFile(file,'w',ZIP_DEFLATED) as z:
            cls.writeInZip(z,key,lines,filename='savedGame')

            if savedata is not None:
                z.writestr(VSav.SAVE_DATA,savedata)
                z.writestr(VMod.MODULE_DATA,moduledata)
        
# ====================================================================
#
# VSave file
#
class SaveFile:
    def __init__(self,game,firstid=None):
        '''Creates a save file to add positions to'''
        from time import time
        self._game     = game
        self._counters = {}
        self._stacks   = {}
        self._pieces   = self._game.getPieces(asdict=True)
        self._nextId   = (int(time()*1000) - 360000
                          if firstid is None else firstid)
        
    def add(self,grid,mapname,**kwargs):
        '''Add pieces to the save.

        Parameters
        ----------
        grid : BaseGrid
            Grid to add pieces to 
        kwargs : dict
            Either a map from piece name to hex position,
            Or a map from hex position to list of pieces
        '''
        for k,v in kwargs.items():
            # print('Add to save',k,v)
            self._add(grid,mapname,k,v)

    def addNoGrid(self,mapName,mapping):
        for k,v in mapping.items():
            # print('Add to save',k,v)
            self._add(None,mapName,k,v)
        

    def _add(self,grid,mapName,k,v):

        '''Add to the save'''
        with VerboseGuard(f'Adding piece(s) to save: {len(k)}') as vg:
            # print(f'Adding {k} -> {v}')
            loc       = None
            piece     = self._pieces.get(k,None)
            pieces    = []
            boardName = (grid.getMap()['mapName']
                         if mapName is None else mapName)
            # print(f'Map name: {mapName}')
            vg(f'Adding to {boardName}')
            if piece is not None:
                vg(f'Key {k} is a piece')
                #print(f'Key is piece: {k}->{piece}')
                pieces.append(piece)
                loc = v
            else:
                vg(f'Key {k} is a location')
                # Key is not a piece name, so a location
                loc = k
                # Convert value to iterable 
                try:
                    iter(v)
                except:
                    v = list(v)
                
                for vv in v:
                    if isinstance(vv,PieceSlot):
                        pieces.append(vv)
                        continue
                    if isinstance(vv,str):
                        piece = self._pieces.get(vv,None)
                        if piece is None:
                            continue
                        pieces.append(piece)
            
            vg(f'Loc: {loc} -> {pieces}')
            if len(pieces) < 1:
                return
            
            if (mapName,loc) not in self._stacks:
                vg(f'Adding stack {mapName},{loc}')
                coord = grid.getLocation(loc) if grid is not None else loc
                if coord is None:
                    print(f'did not get coordinates from {loc}')
                    return
                self._stacks[(mapName,loc)] = {
                    'x': coord[0],
                    'y': coord[1],
                    'pids': [] }
                    
            place = self._stacks[(mapName,loc)]
            for piece in pieces:
                name    = piece['entryName']
                gpid    = piece['gpid']
                counter = self._counters.get((name,gpid),None)
                vg(f'Got counter {counter} for {name},{gpid}')

                if counter is None:
                    if gpid == 0:
                        print(f'making new counter with pid={self._nextId}: '
                              f'{gpid}')
                        gpid = self._nextId
                        self._nextId += 1
                        
            
                    vg(f'Save adding counter with pid={gpid}')
                    counter = {'pid':   gpid,
                               'piece': piece,
                               'board': mapName,
                               'x':     place['x'],
                               'y':     place['y'],
                               }
                    self._counters[(name,gpid)] = counter
                    
                vg(f'Adding to stack {mapName},{loc}: {counter}')
                place['pids'].append(counter['pid'])

    def getLines(self,update=None):
        '''Get the final lines of code'''
        key   = 0xAA # fixed key
        
        lines = ['begin_save',
                 '',
                 '\\']

        self._pieceLines(lines,update=update)
        self._otherLines(lines)
        
        lines.append('end_save')
        return lines

    def _pieceLines(self,lines,update=lambda t:t):
        '''Add piece lines to save file

        Parameters
        ----------
        lines : list
            The lines to add
        '''
        # print(self._counters)
        for (name,gpid),counter in self._counters.items():
            iden   = counter['pid']
            piece  = counter['piece']
            traits = piece.getTraits()
            traits = Trait.flatten(traits,self._game)
            # Get last - trait (basic piece), and modify coords
            basic  = traits[-1]
            basic['map'] = counter['board']
            basic['x']   = counter['x']
            basic['y']   = counter['y']
            # Set old location if possible
            parent = piece.getParent(DummyElement,checkTag=False)
            if parent is not None and parent._node.nodeName == AtStart.TAG:
                oldLoc   = parent['location']
                oldBoard = parent['owningBoard']
                oldMap   = self._game.getBoards()[oldBoard].getMap()['mapName']
                oldX     = parent['x']
                oldY     = parent['y']
                oldZone  = None
                zones    = self._game.getBoards()[oldBoard].getZones()
                for zone in zones.values():
                    grid = zone.getGrids()[0]
                    if grid is None: continue
                    
                    coord = grid.getLocation(oldLoc)
                    if coord is None: continue

                    oldZone = zone['name']
                    oldX    = coord[0]
                    oldY    = coord[1]
                    break

                if oldZone is not None:
                    basic['properties'] = \
                        f'8;'+\
                        f'UniqueID;{iden};'+\
                        f'OldZone;{oldZone};'+\
                        f'OldLocationName;{oldLoc};'+\
                        f'OldDeckName;;'+\
                        f'OldX;{oldX};'+\
                        f'OldY;{oldY};'+\
                        f'OldBoard;{oldBoard};'+\
                        f'OldMap;{oldMap}'
                else:
                    basic['properties'] = \
                        f'7;'+\
                        f'UniqueID;{iden};'+\
                        f'OldLocationName;{oldLoc};'+\
                        f'OldDeckName;;'+\
                        f'OldX;{oldX};'+\
                        f'OldY;{oldY};'+\
                        f'OldBoard;{oldBoard};'+\
                        f'OldMap;{oldMap}'

                for trait in traits:
                    if trait.ID == TrailTrait.ID:
                        trait['map']    = oldMap
                        trait['points'] = f'1;{oldX},{oldY}'
                        trait['init']   = True

            # Let user code update the flattened traits
            if update is not None:
                update(name,traits)
            # Wrapper 
            wrap   = DummyWithTraits(self._game,traits=[])
            wrap.setTraits(*traits,iden=str(iden))
            lines.append(wrap._node.childNodes[0].nodeValue+'\\')

        layer = -1
        for key,dat in self._stacks.items():
            pids = dat.get('pids',None)
            x    = dat['x']
            y    = dat['y']
            if pids is None or len(pids) < 1:
                print(f'No pieces at {key[0]},{key[1]}')
                continue
            
            iden         =  self._nextId
            self._nextId += 1
            stack        =  StackTrait(board=key[0],x=x,y=y,pieceIds=pids,layer=layer)
            layer        = 1
            wrap         =  DummyWithTraits(self._game,traits=[])
            wrap.setTraits(stack,iden=iden)
            lines.append(wrap._node.childNodes[0].nodeValue+'\\')
            
    def _otherLines(self,lines):
        '''Add other lines to save'''
        lines.append('UNMASK\tnull')
        if self._game.getPlayerRoster():
            for r in self._game.getPlayerRoster():
                lines.extend(r.encode())
        if self._game.getNotes(single=False):
            for n in self._game.getNotes(single=False):
                lines.extend(n.encode())
        setupStack = False
        for m in self._game.getMaps(asdict=False):
            for bp in m.getBoardPicker(single=False):
                lines.extend(bp.encode())
            if not setupStack:
                atstart = m.getAtStarts(single=False)
                if atstart and len(atstart) > 0:
                    lines.append('SETUP_STACK')
                    setupStack = True
                
        # for tk,tt in self._game.getTurnTracks(asdict=True):
        #     lines.extend(tt.encode())

            
# --------------------------------------------------------------------
class SaveData(ModuleData):
    def __init__(self,root=None):
        '''Convinience wrapper'''
        super(SaveData,self).__init__(root=root)
