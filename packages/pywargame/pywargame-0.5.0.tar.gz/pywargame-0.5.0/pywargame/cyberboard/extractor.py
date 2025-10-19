## BEGIN_IMPORT
from .. common import VerboseGuard
## END_IMPORT

# ====================================================================
class CbExtractor:
    def __init__(self):
        pass
    
    def save(self,filename):
        from zipfile import ZipFile
        from copy import deepcopy
        
        with VerboseGuard(f'Saving to {filename}') as g:
            with ZipFile(filename,'w') as zfile:
                self._save(zfile)

    def saveImages(self,d,zfile):
        with VerboseGuard(f'Saving images') as g:
            for serial, board in d['boards'].items():
                g(f'Saving board: {board}')
                self.saveSVG(board,zfile)
            
            for piece in d['pieces']['map'].values():
                g(f'Saving piece: {piece}')
                for which in ['front','back']:
                    if which not in piece:
                        continue
                
                    side     = piece[which]
                    self.savePNG(side,zfile)
                    piece[which] = side['filename']
            
            for mark in d['marks']['map'].values():
                g(f'Saving marks: {mark}')
                self.savePNG(mark,zfile)
            
            for tile in d['tiles'].values():
                g(f'Saving tile: {tile}')
                self.savePNG(tile,zfile)
            
            del d['tiles']
        

    def saveSVG(self,d,zfile,removeImage=True):
        from io import StringIO
        
        with VerboseGuard(f'Saving SVG') as g:
            filename = d['filename']
            image    = d['image']
            
            # stream = StringIO()
            # image.write(stream,pretty=True)
            g(f'Saving SVG: {image}')
            zfile.writestr(filename,image)#stream.getvalue())

            if removeImage:
                del d['image']

    def savePNG(self,d,zfile,removeImage=True):
        with VerboseGuard(f'Saving PNG') as g:
            filename = d['filename']
            img      = d['image']
        
            with zfile.open(filename,'w') as file:
                g(f'Save {img}')
                img.save(file,format='PNG')

            if removeImage:
                del d['image']
        
    def _save(self,zfile):
        pass 
    
    
# ====================================================================
class GBXExtractor(CbExtractor):
    def __init__(self,gbx):
        '''Turns gambox into a more sensible structure'''
        super(GBXExtractor,self).__init__()

        with VerboseGuard(f'Extract gamebox {gbx._info._title}') as g:
            self._d = {
                'title':       gbx._info._title,
                'author':      gbx._info._author,
                'description': gbx._info._description.replace('\r',''),
                'major':       gbx._info._majorRevs,
                'minor':       gbx._info._minorRevs,
                'version':     f'{gbx._info._majorRevs}.{gbx._info._minorRevs}'
            }

            self._d['pieces'] = gbx._pieceManager.toDict(gbx._tileManager,
                                                         gbx._strings)
            self._d['marks']  = gbx._markManager.toDict(gbx._tileManager,
                                                        gbx._strings)
            self._d['boards'] = gbx._boardManager.toDict(gbx._tileManager,
                                                         gbx._markManager,
                                                         gbx._strings)
            self._d['tiles']  = gbx._tileManager._toStore
            
            g(f'Done rationalizing {gbx._info._title}')

        
    def _save(self,zfile):
        from pprint import pprint
        from io import StringIO
        from json import dumps
        from copy import deepcopy
        
        with VerboseGuard(f'Saving {self._d["title"]} to {zfile.filename}')as g:
            d = deepcopy(self._d)
            
            self.saveImages(d,zfile)
            
            zfile.writestr('info.json',dumps(d,indent=2))

            g(f'Done saving')

    def fromZipfile(self,zipfile,d):
        pass 

    def __str__(self):
        from pprint import pformat

        return pformat(self._d,depth=2)

# ====================================================================
class GSNExtractor(CbExtractor):
    def __init__(self,gsn,zipfile=None):
        '''Turns gambox into a more sensible structure'''
        super(GSNExtractor,self).__init__()

        if zipfile is not None:
            self.fromZipfile(zipfile)
            return
        
        with VerboseGuard(f'Extract scenario {gsn._info._title}') as g:
            gbxextractor = GBXExtractor(gsn._gbx)
            self._d = {
                'title':       gsn._info._title,
                'author':      gsn._info._author,
                'description': gsn._info._description.replace('\r',''),
                'major':       gsn._info._majorRevs,
                'minor':       gsn._info._minorRevs,
                'version':     f'{gsn._info._majorRevs}.{gsn._info._minorRevs}',
                'gamebox':     gbxextractor._d}
            self._d['players'] = gsn._playerManager.toDict()
            self._d['trays']   = gsn._trayManager.toDict()
            self._d['boards']  = gsn._boards.toDict(gsn._gbx._boardManager)
            
            
    def _save(self,zfile):
        from pprint import pprint
        from io import StringIO
        from json import dumps
        from copy import deepcopy
        
        with VerboseGuard(f'Saving {self._d["title"]} to {zfile.filename}')as g:
            d = deepcopy(self._d)
            
            self.saveImages(d['gamebox'],zfile)
                
            zfile.writestr('info.json',dumps(d,indent=2))

            g(f'Done saving')

    def fromZipfile(self,zipfile):
        from json import loads
        from PIL import Image as PILImage
        from io import BytesIO
        from wand.image import Image as WandImage
        with VerboseGuard(f'Reading module from zip file') as v:
            self._d = loads(zipfile.read('info.json').decode())
            
            newMap = {}
            for pieceSID,piece in self._d['gamebox']['pieces']['map'].items():
                pieceID = int(pieceSID)
                if pieceID in newMap:
                    continue
                for which in ['front', 'back']:
                    if which not in piece:
                        continue
            
                    
                    fn           = piece[which]
                    v(f'Read image {fn}')
                    bts          = BytesIO(zipfile.read(fn))
                    img          = PILImage.open(bts)
                    piece[which] = {'filename': fn,
                                    'image':    img,
                                    'size':     img.size}
            
                newMap[pieceID] = piece
                
            del self._d['gamebox']['pieces']['map']
            self._d['gamebox']['pieces']['map'] = newMap
            
            newMap = {}
            for markSID,mark in self._d['gamebox']['marks']['map'].items():
                markID       = int(markSID)
                if markID in newMap:
                    continue 
                fn             = mark['filename']
                v(f'Read image {fn}')
                bts            = BytesIO(zipfile.read(fn))
                img            = PILImage.open(bts)
                dsc            = mark.get('description',None)
                mark['image']  = img
                mark['size']   = img.size
                newMap[markID] = mark
                
            del self._d['gamebox']['marks']['map']
            self._d['gamebox']['marks']['map'] = newMap
            
            newMap = {}
            for boardSID,board in self._d['gamebox']['boards'].items():
                boardID  = int(boardSID)
                if boardID in newMap:
                    continue
                filename        = board['filename']
                v(f'Read file {filename}')
                content         = zipfile.read(filename)
                img             = WandImage(blob=content)
                board['image']  = content.decode()
                board['size']   = img.size 
                newMap[boardID] = board
            
            # del self._d['gamebox']['boards']
            # self._d['gamebox']['boards'] = newMap

        # print(self)
        
    def __str__(self):
        from pprint import pformat

        return pformat(self._d)#,depth=5)
    
#
# EOF
#
