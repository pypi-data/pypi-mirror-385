## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . gameelements import GameElement
## END_IMPORT

# --------------------------------------------------------------------
class PlayerRoster(GameElement):
    TAG = Element.MODULE+'PlayerRoster'
    def __init__(self,doc,node=None,buttonKeyStroke='',
               buttonText='Retire',
               buttonToolTip='Switch sides, become observer, or release faction'):
        '''Add a player roster to the module
        
        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        buttonText : str
            Text on button
        buttonTooltip : str
            Tool tip to show when hovering over button
        '''
        super(PlayerRoster,self).__init__(doc,self.TAG,node=node,
                                          buttonKeyStroke = buttonKeyStroke,
                                          buttonText      = buttonText,
                                          buttonToolTip   = buttonToolTip)
    def addSide(self,name):
        '''Add a `Side` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Side
            The added element
        '''
        return self.add(PlayerSide,name=name)
    def getSides(self):
        '''Get all sides'''
        return self.getAllElements(PlayerSide,False)
    def encode(self):
        '''Encode for save'''
        return ['PLAYER\ta\ta\t<observer>']

registerElement(PlayerRoster)

# --------------------------------------------------------------------
class PlayerSide(Element):
    TAG = 'entry'
    UNIQUE = ['name']
    def __init__(self,doc,node=None,name=''):
        '''Adds a side to the player roster

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        name : str
            Name of side 
        '''
        super(PlayerSide,self).__init__(doc,self.TAG,node=node)
        if node is None:
            self.addText(name)

    def getPlayerRoster(self):
        '''Get Parent element'''
        return self.getParent(PlayerRoster)

registerElement(PlayerSide)


#
# EOF
#
