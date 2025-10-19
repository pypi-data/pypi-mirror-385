## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
## END_IMPORT

class BaseFolder(Element):
    UNIQUE = ['name']
    
    def __init__(self,parent,tag,node=None,name='',description='',**kwargs):
        '''Create a folder'''
        super().__init__(parent,
                         tag,
                         node = node,
                         name = name,
                         desc = description,
                         **kwargs)

# --------------------------------------------------------------------
class GlobalPropertyFolder(BaseFolder):
    TAG = Element.FOLDER+'GlobalPropertySubFolder'
    def __init__(self,
                 parent,
                 node=None,
                 name='',
                 description=''):
        super().__init__(parent,
                         tag = self.TAG,
                         node = node,
                         name = name,
                         description = description)

registerElement(GlobalPropertyFolder)
    
# --------------------------------------------------------------------
class DeckFolder(BaseFolder):
    TAG = Element.FOLDER+'DeckSubFolder'
    def __init__(self,
                 parent,
                 node=None,
                 name='',
                 description=''):
        super().__init__(parent,
                         tag = self.TAG,
                         node = node,
                         name = name,
                         description = description)

registerElement(DeckFolder)
        
# --------------------------------------------------------------------
class MapFolder(BaseFolder):
    TAG = Element.FOLDER+'MapSubFolder'
    def __init__(self,
                 parent,
                 node=None,
                 name='',
                 description=''):
        super().__init__(parent,
                         tag = self.TAG,
                         node = node,
                         name = name,
                         description = description)
        
registerElement(MapFolder)

# --------------------------------------------------------------------
class ModuleFolder(BaseFolder):
    TAG = Element.FOLDER+'ModuleSubFolder'
    def __init__(self,
                 parent,
                 node=None,
                 name='',
                 description=''):
        super().__init__(parent,
                         tag = self.TAG,
                         node = node,
                         name = name,
                         description = description)
        
registerElement(ModuleFolder)

# --------------------------------------------------------------------
class PrototypeFolder(BaseFolder):
    TAG = Element.FOLDER+'PrototypeSubFolder'
    def __init__(self,
                 parent,
                 node=None,
                 name='',
                 description=''):
        super().__init__(parent,
                         tag = self.TAG,
                         node = node,
                         name = name,
                         description = description)
        
registerElement(PrototypeFolder)

# --------------------------------------------------------------------
#
# EOF
#

