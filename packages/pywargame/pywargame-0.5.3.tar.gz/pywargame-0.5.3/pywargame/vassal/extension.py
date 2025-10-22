## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . game import Game
## END_IMPORT

# ====================================================================
class Extension(Element):
    TAG = Element.MODULE+'ModuleExtension'
    def __init__(self,
                 parent          = None,
                 node            = None,
                 anyModule       = False,
                 version         = '',
                 description     = '',
                 module          = '',
                 moduleVersion   = '',
                 vassalVersion   = '',
                 nextPieceSlotId = 0,
                 extensionId     = 0,
                 asDocument      = False):
        super().__init__(parent,self.TAG,node)

        self._tag  = 'extension'
        if self._node is None:
            #from xml.dom.minidom import Document


            self._root = xmlns.Document()
            self._node = self._root
            self.setAttributes(
                anyModule       = anyModule,
                version         = version,
                description     = description,
                module          = module,
                moduleVersion   = moduleVersion,
                vassalVersion   = vassalVersion,
                nextPieceSlotId = nextPieceSlotId,
                extensionId     = extensionId)

    def addExtensionElement(self,**kwargs):
        '''Add an extension element'''

        return self.add(ExtensionElement,**kwargs)
        
    # ----------------------------------------------------------------
    def getExtensionElements(self,asdict=True):
        '''Get all or a sole `GlobalPropertie` element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to
            `ExtensionElement` elements.  If `False`, return a list of
            all `ExtensionElement` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Extension` children

        '''
        return self.getElementsByKey(ExtensionElement,'target',asdict)

registerElement(Extension)
    
# --------------------------------------------------------------------
class ExtensionElement(Element):
    TAG    = Element.MODULE + 'ExtensionElement'
    UNIQUE = ['target']
    
    def __init__(self,
                 extension,
                 node         = None,
                 target       = ''):
        super().__init__(extension,
                         self.TAG,
                         node = node,
                         target = target)


    def getTarget(self):
        return self['target']

    @property 
    def target(self):
        return self.getTarget()
    
    def getSelect(self):
        parts = self.target.split('/')
        specs = [p.split(':') for p in parts]
        return specs


registerElement(ExtensionElement)
        
# --------------------------------------------------------------------
#
# EOF
#
