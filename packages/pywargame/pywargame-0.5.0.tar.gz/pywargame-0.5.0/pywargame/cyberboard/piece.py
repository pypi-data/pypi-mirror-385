## BEGIN_IMPORT
from .. common import VerboseGuard
from . head   import num_version
from . features import Features
## END_IMPORT
# ====================================================================
class GBXPieceDef:
    def __init__(self,ar):
        '''Definition of a piece

        FRONT and BACK are tile IDs

        FLAGS is ...
        '''
        with VerboseGuard(f'Reading piece definition'):
            if Features().piece_100:
                n = ar.size()
                self._ids = [ar.iden() for _ in range(n)]
            else:
                self._ids = [ar.word(),ar.word()]
            self._flags = ar.word()


    @property
    def _front(self):
        return self._ids[0]

    @property
    def _back(self):
        return self._ids[1] if len(self._ids) > 1 else 0
    
    def __str__(self):
        return f'Piece: {self._front:04x},{self._back:04x},{self._flags:04x}'
    
# --------------------------------------------------------------------
class GBXPieceSet:
    def __init__(self,ar):
        '''Set of pieces'''
        with VerboseGuard(f'Reading piece set'):
            self._name   = ar.str()
            n            = ar.sub_size()
            self._pieces = [ar.iden() for _ in range(n)]

    def __len__(self):
        return len(self._pieces)

    def __str__(self):
        return (f'{self._name}: '+','.join([str(p) for p in self._pieces]))
    
# --------------------------------------------------------------------
class GBXPieceManager:
    def __init__(self,ar):
        '''Manager of pieces'''
        with VerboseGuard(f'Reading piece manager') as g: 
            self._reserved     = [ar.word() for _ in range(4)]
            g(f'Reserved are {self._reserved}')
            n                  = ar.iden();
            g(f'Will read {n} pieces')
            self._pieces       = [GBXPieceDef(ar) for _ in range(n)]
            n                  = ar.sub_size()
            g(f'Will read {n} sets')
            self._sets         = [GBXPieceSet(ar) for _ in range(n)]

    def __len__(self):
        return len(self._sets)

    def toDict(self,tileManager,strings):
        from math import log10, ceil
        with VerboseGuard(f'Creating dict from piece manager') as gg:
            gg(f'Has {len(self._sets)} and {len(self._pieces)} pieces')
            setDigits   = int(ceil(log10(len(self)+.5)))
            pieceDigits = 1
            for pieceSet in self._sets:
                pieceDigits = max(pieceDigits,
                                  int(ceil(log10(len(pieceSet)+.5))))

            cnt       = 0
            piecesMap = {}
            setList   = []
            ret = {'map': piecesMap,
                   'sets': setList }

            for ips, pieceSet in enumerate(self._sets):
                with VerboseGuard(f'Creating dict from piece set '
                                  f'{pieceSet._name}') as g:
                    setPrefix = f'piece_{ips:0{setDigits}d}'
                    idList    = []
                    setDict   = { 'description': pieceSet._name.strip(),
                                  'pieces':      idList }
                    setList.append(setDict)
                    
                    for ipc, pieceID in enumerate(pieceSet._pieces):
                        
                        piecePrefix = f'{setPrefix}_{ipc:0{pieceDigits}d}'
                        pieceDef    = self._pieces[pieceID]
                        tmpStr      = strings._id2str.get(pieceID,'')
                        pieceDesc   = tmpStr.replace('\r','').replace('\n',', ').replace('/','\\/')
                        pieceDict   = {}
                        if pieceDesc != '':
                            pieceDict['description'] = pieceDesc
                        cnt += 1
                        # pieceList.append(pieceDict)
                        idList   .append(pieceID)
                        
                        # print(f'{pd}  => "{tr}"')
                        for tileId,which in zip([pieceDef._front,
                                                 pieceDef._back],
                                                ['front',
                                                 'back']):                    
                            img = tileManager.image(tileId)
                    
                            if img is None:
                                continue
                    
                            sav     = f'{piecePrefix}_{which}.png'
                            setname = pieceSet._name.strip()\
                                .replace('\n',' ')\
                                .replace('\r',' ')\
                                .replace('/','\\/')
                            gg(f'Set name, escaped: "{setname}"')
                            pieceDict[which] = {
                                'image':     img,
                                'filename':  sav,
                                'set':       setname }
                        piecesMap[pieceID] = pieceDict
                        g(f'{pieceID}: {pieceDict}')

            gg(f'{list(piecesMap.keys())}')
            return ret
    
        
    def __str__(self):
        return ('Piece manager:\n'
                +f'Reserved: {self._reserved}\n'
                +f'# pieces: {len(self._pieces)}\n  '
                +'\n  '.join([str(p) for p in self._pieces])+'\n'
                +f'# piece sets: {len(self._sets)}\n  '
                +'\n  '.join([str(p) for p in self._sets])
                )

# --------------------------------------------------------------------
class GSNPieceEntry:
    def __init__(self,ar,vers,i):
        '''Manager of pieces'''
        with VerboseGuard(f'Reading piece # {i:3d} ({vers//256}.{vers%256})'):
            self._side   = ar.byte()
            self._facing = ar.word()
            self._owner  = ar.word() if vers < num_version(3,10) else ar.dword()

    def __str__(self):
        return f'Piece: {self._side}, {self._facing:3d}, {self._owner:08x}'
    
# --------------------------------------------------------------------
class GSNPieceTable:
    def __init__(self,ar,vers):
        '''Manager of pieces'''
        with VerboseGuard(f'Reading piece table'):
            self._reserved     = [ar.word() for _ in range(4)] 
            n                  = ar.word()#sub_size()
            if Features().piece_100:
                dummy          = ar.word();
            self._pieces       = [GSNPieceEntry(ar,vers,i) for i in range(n)]
            
    def __str__(self):
        pl = '\n    '.join([str(s) for s in self._pieces])
        return (f'Piece table: {self._reserved} {len(self._pieces)}'
                f'\n    {pl}\n')
#
# EOF
#
