## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import CbManager
## END_IMPORT

# ====================================================================
class GBXMarkDef:
    def __init__(self,ar):
        '''Definition of a mark'''
        with VerboseGuard(f'Reading mark definition'):
            self._id    = ar.iden()
            self._flags = ar.word()

    def __str__(self):
        return f'Mark: {self._id:04x},{self._flags:04x}'
    
# --------------------------------------------------------------------
class GBXMarkSet:
    def __init__(self,ar):
        '''Set of marks'''
        with VerboseGuard(f'Reading mark set'):
            self._name   = ar.str()
            self._viz    = ar.word()
            n            = ar.sub_size()
            self._marks = [ar.iden() for _ in range(n)]

    def __len__(self):
        return len(self._marks)

    def __str__(self):
        return (f'{self._name}: '+','.join([str(p) for p in self._marks]))
    
# --------------------------------------------------------------------
class GBXMarkManager:
    def __init__(self,ar):
        '''Manager of marks'''
        with VerboseGuard(f'Reading mark manager'):
            self._reserved     = [ar.word() for _ in range(4)] 
            n                  = ar.iden()
            self._marks        = [GBXMarkDef(ar) for _ in range(n)]
            n                  = ar.sub_size()
            self._sets         = [GBXMarkSet(ar) for _ in range(n)]
        
    def __len__(self):
        return len(self._sets)

    def toDict(self,tileManager,strings):
        from math import log10, ceil
        with VerboseGuard(f'Creating dict from mark manager'):
            setDigits  = int(ceil(log10(len(self)+.5)))
            markDigits = 1
            for markSet in self._sets:
                markDigits = max(markDigits,
                                 int(ceil(log10(len(markSet)+.5))))

            marksMap  = {}
            setList   = []
            ret = {'map': marksMap,
                   'sets': setList }
            
            for ips, markSet in enumerate(self._sets):
                with VerboseGuard(f'Creating dict mark set {markSet._name}'):
                    setPrefix = f'mark_{ips:0{setDigits}d}'
                    idList    = []
                    setDict   = { 'description': markSet._name.strip(),
                                  'marks':       idList }
                    setList.append(setDict)
                    
                    for ipc, markID in enumerate(markSet._marks):
                        markPrefix = f'{setPrefix}_{ipc:0{markDigits}d}'
                        markDef    = self._marks[markID]
                        tmpStr     = strings._id2str.get(markID|0xF0000000,'')
                        markDesc   = tmpStr.replace('\r','').replace('\n',', ')
                        markDict   = {}
                        if markDesc != '':
                            markDict['description'] = markDesc
                        marksMap[markID] = markDict
                        idList  .append(markID)
                        
                        img = tileManager.image(markDef._id)
                    
                        if img is None:
                            continue
                    
                        sav     = f'{markPrefix}.png'
                        markDict.update({'image':     img,
                                         'filename':  sav })

            return ret
    
    def __str__(self):
        return ('Mark manager:\n'
                +f'Reserved: {self._reserved}\n'
                +f'# marks: {len(self._marks)}\n  '
                +'\n  '.join([str(p) for p in self._marks])+'\n'
                +f'# mark sets: {len(self._sets)}\n  '
                +'\n  '.join([str(p) for p in self._sets])
                )

#
# EOF
#
