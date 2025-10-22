## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . documentation import Documentation
from . gameelements import *
from . widget import *
from . player import *
from . globalproperty import *
from . chessclock import *
from . turn import TurnTrack
from . map import Map
from . mapelements import *
from . chart import *
from . board import *
## END_IMPORT

# --------------------------------------------------------------------
class Game(Element):
    TAG = Element.BUILD+'GameModule'
    UNIQUE = ['name']
    def __init__(self,build,node=None,
                 name            = '',
                 version         = '', 
                 ModuleOther1    = "",
                 ModuleOther2    = "",
                 VassalVersion   = "3.6.7",
                 description     = "",
                 nextPieceSlotId = 20):
        '''Create a new Game object

        Parameters
        ----------
        build : xml.dom.Document
            root note
        node : xml.dom.Node
            To read from, or None
        name : str
            Name of module
        version : str
            Version of module
        ModuleOther1 : str
            Free form string 
        ModuleOther2 : str
            Free form string
        VassalVersion : str
            VASSAL version this was created for
        description : str
            Speaks volumes
        nextPieceSlotId : int
            Starting slot ID.
        '''
        super(Game,self).__init__(build, self.TAG,
                                  node            = node,
                                  name            = name,
                                  version         = version,
                                  ModuleOther1    = ModuleOther1,
                                  ModuleOther2    = ModuleOther2,
                                  VassalVersion   = VassalVersion,
                                  description     = description,
                                  nextPieceSlotId = nextPieceSlotId)
    def nextPieceSlotId(self):
        '''Increment next piece slot ID'''
        ret = int(self.getAttribute('nextPieceSlotId'))
        self.setAttribute('nextPieceSlotId',str(ret+1))
        return ret
    #
    def addBasicCommandEncoder(self,**kwargs):
        '''Add a `BasicCommandEncoder` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : BasicCommandEncoder
            The added element
        '''
        return self.add(BasicCommandEncoder,**kwargs)
    def addGlobalTranslatableMessages(self,**kwargs):
        '''Add a `GlobalTranslatableMessages` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : GlobalTranslatableMessages
            The added element
        '''
        return self.add(GlobalTranslatableMessages,**kwargs)
    def addPlayerRoster(self,**kwargs):
        '''Add a `PlayerRoster` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PlayerRoster
            The added element
        '''
        return self.add(PlayerRoster,**kwargs)
    def addChessClock(self,**kwargs):
        '''Add a `ChessClockControl` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PlayerRoster
            The added element
        '''
        return self.add(ChessClockControl,**kwargs)
    def addLanguage(self,**kwargs):
        '''Add a `Language` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Language
            The added element
        '''
        return self.add(Language,**kwargs)
    def addChatter(self,**kwargs):
        '''Add a `Chatter` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Chatter
            The added element
        '''
        return self.add(Chatter,**kwargs)
    def addKeyNamer(self,**kwargs):
        '''Add a `KeyNamer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : KeyNamer
            The added element
        '''
        return self.add(KeyNamer,**kwargs)
    def addNotes(self,**kwargs):
        '''Add a `Notes` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Notes
            The added element
        '''
        return self.add(Notes,**kwargs)
    def addLanguage(self,**kwargs):
        '''Add a `Language` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Language
            The added element
        '''
        return self.add(Language,**kwargs)
    def addChatter(self,**kwargs):
        '''Add a `Chatter` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Chatter
            The added element
        '''
        return self.add(Chatter,**kwargs)
    def addKeyNamer(self,**kwargs):
        '''Add a `KeyNamer` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : KeyNamer
            The added element
        '''
        return self.add(KeyNamer,**kwargs)
    def addGlobalProperties(self,**kwargs):
        '''Add a `GlobalProperties` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : GlobalProperties
            The added element
        '''
        return self.add(GlobalProperties,**kwargs)
    def addGlobalOptions(self,**kwargs):
        '''Add a `GlobalOptions` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : GlobalOptions
            The added element
        '''
        return self.add(GlobalOptions,**kwargs)
    def addTurnTrack(self,**kwargs):
        '''Add a `TurnTrack` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : TurnTrack
            The added element
        '''
        return self.add(TurnTrack,**kwargs)
    def addDocumentation(self,**kwargs):
        '''Add a `Documentation` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Documentation
            The added element
        '''
        return self.add(Documentation,**kwargs)
    def addPrototypes(self,**kwargs):
        '''Add a `Prototypes` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Prototypes
            The added element
        '''
        return self.add(Prototypes,**kwargs)
    def addPieceWindow(self,**kwargs):
        '''Add a `PieceWindow` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PieceWindow
            The added element
        '''
        return self.add(PieceWindow,**kwargs)
    def addChartWindow(self,**kwargs):
        '''Add a `ChartWindow` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ChartWindow
            The added element
        '''
        return self.add(ChartWindow,**kwargs)
    def addInventory(self,**kwargs):
        '''Add a `Inventory` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Inventory
            The added element
        '''
        return self.add(Inventory,**kwargs)
    def addMap(self,**kwargs):
        '''Add a `Map` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Map
            The added element
        '''
        return self.add(Map,**kwargs)
    def addDiceButton(self,**kwargs):
        '''Add a `DiceButton` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : DiceButton
            The added element
        '''
        return self.add(DiceButton,**kwargs)
    def addPredefinedSetup(self,**kwargs):
        '''Add a `PredefinedSetup` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : PredefinedSetup
            The added element
        '''
        return self.add(PredefinedSetup,**kwargs)
    def addGameMassKey(self,**kwargs):
        '''Add a `GameMassKey` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : GameMassKey
            The added element
        '''
        return self.add(GameMassKey,**kwargs)
    def addStartupMassKey(self,**kwargs):
        '''Add a `StartupMassKey` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : StartupMassKey
            The added element
        '''
        return self.add(StartupMassKey,**kwargs)
    def addMenu(self,**kwargs):
        '''Add a `Menu` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Menu
            The added element
        '''
        return self.add(Menu,**kwargs)
    def addSymbolicDice(self,**kwargs):
        '''Add a `SymbolicDice` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : SymbolicDice
            The added element
        '''
        return self.add(SymbolicDice,**kwargs)

    def addFolder(self,**kwargs):
        '''Add a `ModuleFolder` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ModuleFolder
            The added element
        '''
        return self.add(ModuleFolder,**kwargs)
    
    
    # ----------------------------------------------------------------
    def getGlobalProperties(self,single=True):
        '''Get all or a sole `GlobalPropertie` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `GlobalPropertie` child, otherwise fail.
            If `False` return all `GlobalPropertie` children in this element
        
        Returns
        -------
        children : list
            List of `GlobalPropertie` children (even if `single=True`)
        '''
        return self.getAllElements(GlobalProperties,single)
    def getBasicCommandEncoder(self,single=True):
        '''Get all or a sole `Ba` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Ba` child, otherwise fail.
            If `False` return all `Ba` children in this element
        
        Returns
        -------
        children : list
            List of `Ba` children (even if `single=True`)
        '''
        return self.getAllElements(BasicCommandEncoder,single)
    def getGlobalTranslatableMessages(self,single=True):
        '''Get all or a sole `GlobalTranslatableMessage` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `GlobalTranslatableMessage` child, otherwise fail.
            If `False` return all `GlobalTranslatableMessage` children in this element
        
        Returns
        -------
        children : list
            List of `GlobalTranslatableMessage` children (even if `single=True`)
        '''
        return self.getAllElements(GlobalTranslatableMessages,single)
    def getLanguages(self,single=False):
        '''Get all or a sole `Language` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Language` child, otherwise fail.
            If `False` return all `Language` children in this element
        
        Returns
        -------
        children : list
            List of `Language` children (even if `single=True`)
        '''
        return self.getAllElements(Language,single)
    def getChessClocks(self,asdict=False):
        '''Get all or a sole `Language` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Language` child, otherwise fail.
            If `False` return all `Language` children in this element
        
        Returns
        -------
        children : list
            List of `Language` children (even if `single=True`)
        '''
        return self.getElementsByKey(ChessClockControl,'name',asdict)
    def getChatter(self,single=True):
        '''Get all or a sole `Chatter` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Chatter` child, otherwise fail.
            If `False` return all `Chatter` children in this element
        
        Returns
        -------
        children : list
            List of `Chatter` children (even if `single=True`)
        '''
        return self.getAllElements(Chatter,single)
    def getKeyNamer(self,single=True):
        '''Get all or a sole `KeyNamer` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `KeyNamer` child, otherwise fail.
            If `False` return all `KeyNamer` children in this element
        
        Returns
        -------
        children : list
            List of `KeyNamer` children (even if `single=True`)
        '''
        return self.getAllElements(KeyNamer,single)
    def getDocumentation(self,single=True):
        '''Get all or a sole `Documentation` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Documentation` child, otherwise fail.
            If `False` return all `Documentation` children in this element
        
        Returns
        -------
        children : list
            List of `Documentation` children (even if `single=True`)
        '''
        return self.getAllElements(Documentation,single)
    def getPrototypes(self,single=True):
        '''Get all or a sole `Prototypes` (i.e., the containers of
        prototypes, not a list of actual prototypes) element(s) from
        this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Prototypes` child, otherwise fail.
            If `False` return all `Prototypes` children in this element
        
        Returns
        -------
        children : list
            List of `Prototype` children (even if `single=True`)

        '''
        return self.getAllElements(Prototypes,single)
    def getPlayerRoster(self,single=True):
        '''Get all or a sole `PlayerRo` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `PlayerRo` child, otherwise fail.
            If `False` return all `PlayerRo` children in this element
        
        Returns
        -------
        children : list
            List of `PlayerRo` children (even if `single=True`)
        '''
        return self.getAllElements(PlayerRoster,single)
    def getGlobalOptions(self,single=True):
        '''Get all or a sole `GlobalOption` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `GlobalOption` child, otherwise fail.
            If `False` return all `GlobalOption` children in this element
        
        Returns
        -------
        children : list
            List of `GlobalOption` children (even if `single=True`)
        '''
        return self.getAllElements(GlobalOptions,single)
    def getInventories(self,asdict=True):
        '''Get all Inventorie element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Inventorie` elements.  If `False`, return a list of all Inventorie` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Inventorie` children
        '''
        return self.getElementsByKey(Inventory,'name',asdict)
    def getPieceWindows(self,asdict=True):
        '''Get all PieceWindow element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `PieceWindow` elements.  If `False`, return a list of all PieceWindow` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `PieceWindow` children
        '''
        return self.getElementsByKey(PieceWindow,'name',asdict)
    def getChartWindows(self,asdict=True):
        '''Get all ChartWindow element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `ChartWindow` elements.  If `False`, return a list of all ChartWindow` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `ChartWindow` children
        '''
        return self.getElementsByKey(ChartWindow,'name',asdict)
    def getDiceButtons(self,asdict=True):
        '''Get all DiceButton element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `DiceButton` elements.  If `False`, return a list of all DiceButton` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `DiceButton` children
        '''
        return self.getElementsByKey(DiceButton,'name',asdict)
    def getPredefinedSetups(self,asdict=True):
        '''Get all PredefinedSetup element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `PredefinedSetup` elements.  If `False`, return a list of all PredefinedSetup` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `PredefinedSetup` children
        '''
        return self.getElementsByKey(PredefinedSetup,'name',asdict)
    def getNotes(self,single=True):
        '''Get all or a sole `Note` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Note` child, otherwise fail.
            If `False` return all `Note` children in this element
        
        Returns
        -------
        children : list
            List of `Note` children (even if `single=True`)
        '''
        return self.getAllElements(Notes,single)
    def getTurnTracks(self,asdict=True):
        '''Get all TurnTrack element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `TurnTrack` elements.  If `False`, return a list of all TurnTrack` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `TurnTrack` children
        '''
        return self.getElementsByKey(TurnTrack,'name',asdict)
    def getPieces(self,asdict=False):
        '''Get all Piece element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Piece` elements.  If `False`, return a list of all Piece` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Piece` children
        '''
        return self.getElementsByKey(PieceSlot,'entryName',asdict)
    def getCards(self,asdict=False):
        '''Get all Cards element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Piece` elements.  If `False`, return a list of all Piece` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Piece` children
        '''
        return self.getElementsByKey(CardSlot,'entryName',asdict)
    def getSpecificPieces(self,*names,asdict=False):
        '''Get all SpecificPiece element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `SpecificPiece` elements.  If `False`, return a list of all SpecificPiece` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `SpecificPiece` children
        '''
        return self.getSpecificElements(PieceSlot,'entryName',
                                        *names,asdict=asdict)
    def getMap(self,asdict=False):
        return self.getElementsByKey(Map,'mapName',asdict)
    def getWidgetMaps(self,asdict=True):
        '''Get all WidgetMap element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `WidgetMap` elements.  If `False`, return a list of all WidgetMap` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `WidgetMap` children
        '''
        return self.getElementsByKey(WidgetMap,'mapName',asdict=asdict)
    def getMaps(self,asdict=True):
        '''Get all Map element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Map` elements.  If `False`, return a list of all Map` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Map` children
        '''
        maps = self.getMap(asdict=asdict)
        wmaps = self.getWidgetMaps(asdict=asdict)
        if asdict:
            maps.update(wmaps)
        else:
            maps.extend(wmaps)
        return maps
    def getBoards(self,asdict=True):
        '''Get all Board element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board`
            elements.  If `False`, return a list of all Board`
            children.

        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children

        '''
        return self.getElementsByKey(Board,'name',asdict)
    def getGameMassKeys(self,asdict=True):
        '''Get all GameMassKey element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board`
            elements.  If `False`, return a list of all Board`
            children.

        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children

        '''
        return self.getElementsByKey(GameMassKey,'name',asdict)
    def getStartupMassKeys(self,asdict=True):
        '''Get all StartupMassKey element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board`
            elements.  If `False`, return a list of all Board`
            children.

        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children

        '''
        return self.getElementsByKey(StartupMassKey,'name',asdict)
    def getMenus(self,asdict=True):
        '''Get all Menu element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Board`
            elements.  If `False`, return a list of all Board`
            children.

        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Board` children

        '''
        return self.getElementsByKey(Menu,'text',asdict)
    def getSymbolicDices(self,asdict=True):
        '''Get all Menu element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `SymbolicDice`
            elements.  If `False`, return a list of all `SymbolicDice`
            children.

        Returns
        -------
        children : dict or list
            Dictionary or list of `SymbolicDice` children

        '''
        return self.getElementsByKey(SymbolicDice,'name',asdict)
    def getFolders(self,asdict=True):
        '''Get all Menu element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Folder`
            elements.  If `False`, return a list of all `Folder`
            children.

        Returns
        -------
        children : dict or list
            Dictionary or list of `Folder` children

        '''
        return self.getElementsByKey(ModuleFolder,'name',asdict)
    
    def getAtStarts(self,single=False):
        '''Get all or a sole `AtStart` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `AtStart` child, otherwise fail.
            If `False` return all `AtStart` children in this element
        
        Returns
        -------
        children : list
            List of `AtStart` children (even if `single=True`)
        '''
        return self.getAllElements(AtStart,single)

registerElement(Game)

# --------------------------------------------------------------------
# Old game module class
class OldGame(Game):
    TAG = 'VASSAL.launch.BasicModule'
    def __init__(self,build,**kwargs):
        super().__init__(build,**kwargs)
    
registerElement(OldGame)

# --------------------------------------------------------------------
class BasicCommandEncoder(GameElement):
    TAG = Element.MODULE+'BasicCommandEncoder'
    def __init__(self,doc,node=None):
        super(BasicCommandEncoder,self).__init__(doc,self.TAG,node=node)

registerElement(BasicCommandEncoder)

#
# EOF
#
