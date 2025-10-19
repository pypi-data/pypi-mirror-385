## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . game import Game
from . xmlns import xmlns
## END_IMPORT

# --------------------------------------------------------------------
class BuildFile(Element):
    def __init__(self,root=None):
        '''Construct from a DOM object, if given, otherwise make new'''
        # from xml.dom.minidom import Document
        super(BuildFile,self).__init__(None,'',None)
        
        self._root = root
        self._tag  = 'buildFile'
        if self._root is None:
            self._root = xmlns.Document()

        self._node = self._root

    def addGame(self,**kwargs):
        '''Add a `Game` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Game
            The added element
        '''
        return Game(self,**kwargs)

    def getGame(self):
        '''Get the `Game`'''
        try:
            return Game(self,
                        node=self._root.\
                        getElementsByTagName('VASSAL.build.GameModule')[0])
        except:
            pass

        return Game(self,
                    node=self._root.\
                    getElementsByTagName('VASSAL.launch.BasicModule')[0])
                    

    def encode(self):
        '''Encode into XML'''
        return self._root.toprettyxml(indent=' ',
                                      encoding="UTF-8",
                                      standalone=False)


#
# EOF
#
