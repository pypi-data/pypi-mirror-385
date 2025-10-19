## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . withtraits import *
from . globalkey import *
## END_IMPORT

# --------------------------------------------------------------------
class GameElementService:
    def getGame(self):
        return self.getParentOfClass(Game)

# --------------------------------------------------------------------
class GameElement(Element,GameElementService):
    def __init__(self,game,tag,node=None,**kwargs):
        super(GameElement,self).__init__(game,tag,node=node,**kwargs)

# --------------------------------------------------------------------
class Notes(ToolbarElement,GameElementService):
    TAG = Element.MODULE+'NotesWindow'
    UNIQUE = ['name']
    def __init__(self,elem,node=None,
                 name         = 'Notes', # Toolbar element name
                 tooltip      = 'Show notes window', # Tool tip
                 text         = '', # Button text
                 icon         = '/images/notes.gif', # Button icon,
                 hotkey       = key('N',ALT), # Named key or key stroke
                 canDisable   = False,
                 propertyGate = '',
                 disabledIcon = '',
                 description  = ''):
        super(Notes,self).__init__(elem,self.TAG,
                                   node         = node,
                                   name         = name,
                                   tooltip      = tooltip,
                                   text         = text,
                                   icon         = icon,
                                   hotkey       = hotkey,
                                   canDisable   = canDisable,
                                   propertyGate = propertyGate,
                                   disabledIcon = disabledIcon,
                                   description  = description)
    def encode(self):
        return ['NOTES\t\\','PNOTES']

registerElement(Notes)

# --------------------------------------------------------------------
class PredefinedSetup(GameElement):
    TAG = Element.MODULE+'PredefinedSetup'
    UNIQUE = ['name'] #,'file','useFile']
    def __init__(self,elem,node=None,
                 name             = '',
                 file             = '',
                 useFile          = False,
                 isMenu           = False,
                 description      = ''):
        useFile = ((useFile or not isMenu) and
                   (file is not None and len(file) > 0))
        if file is None: file = ''
        super(PredefinedSetup,self).__init__(elem,self.TAG,node=node,
                                             name        = name,
                                             file        = file,
                                             useFile     = useFile,
                                             isMenu      = isMenu,
                                             description = description)
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
        
    
        
                   
registerElement(PredefinedSetup)
                  
# --------------------------------------------------------------------
class GlobalTranslatableMessages(GameElement):
    TAG=Element.MODULE+'properties.GlobalTranslatableMessages'
    UNIQUE = ['name']
    def __init__(self,elem,node=None,
                 name='',
                 initialValue = '',
                 description = ''):
        '''Translations

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        '''
        super(GlobalTranslatableMessages,self).\
            __init__(elem,self.TAG,node=node,
                     name = name,
                     initialValue = initialValue,
                     description = description)

registerElement(GlobalTranslatableMessages)
        
# --------------------------------------------------------------------
class Language(GameElement):
    TAG = 'VASSAL.i18n.Language'
    def __init__(self,elem,node=None,**kwargs):
        super(Language,self).__init__(elem,self.TAG,node=node,**kwargs)

registerElement(Language)
        
# --------------------------------------------------------------------
class Chatter(GameElement):
    TAG=Element.MODULE+'Chatter'
    def __init__(self,elem,node=None,**kwargs):
        '''Chat

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        kwargs : dict
            Attributes
        '''
        super(Chatter,self).__init__(elem,self.TAG,node=node,**kwargs)

registerElement(Chatter)
        
# --------------------------------------------------------------------
class KeyNamer(GameElement):
    TAG=Element.MODULE+'KeyNamer'
    def __init__(self,elem,node=None,**kwargs):
        '''Key namer (or help menu)

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        kwargs : dict
            Attributes
        '''
        super(KeyNamer,self).__init__(elem,self.TAG,node=node,**kwargs)
        
registerElement(KeyNamer)
        

# --------------------------------------------------------------------
#    <VASSAL.build.module.GlobalOptions
#      autoReport="Always"
#      centerOnMove="Use Preferences Setting"
#      chatterHTMLSupport="Always"
#      hotKeysOnClosedWindows="Always"
#      inventoryForAll="Never"
#      nonOwnerUnmaskable="Always"
#      playerIdFormat="$PlayerName$"
#      promptString="Opponents can unmask pieces"
#      sendToLocationMoveTrails="Always"
#      storeLeadingZeroIntegersAsStrings="true">
#        <option name="stepIcon">/images/StepForward16.gif</option>
#        <option name="stepHotKey">39,130</option>
#        <option name="undoIcon">/images/Undo16.gif</option>
#        <option name="undoHotKey">90,130</option>
#        <option name="serverControlsIcon">/images/connect.gif</option>
#        <option name="serverControlsHotKey">65,195</option>
#        <option name="debugControlsIcon"/>
#        <option name="debugControlsHotKey">68,195</option>
#    </VASSAL.build.module.GlobalOptions>
class GlobalOptions(GameElement):
    NEVER  = 'Never'
    ALWAYS = 'Always'
    PROMPT = 'Use Preferences Setting'
    TAG    = Element.MODULE+'GlobalOptions'
    def __init__(self,doc,node=None,
                 autoReport               = PROMPT,
                 centerOnMove             = PROMPT,
                 chatterHTMLSupport       = ALWAYS,
                 hotKeysOnClosedWindows   = NEVER,
                 inventoryForAll          = ALWAYS,
                 nonOwnerUnmaskable       = PROMPT,
                 playerIdFormat           = "$playerName$",
                 promptString             = "Opponents can unmask pieces",
                 sendToLocationMoveTrails = NEVER,
                 storeLeadingZeroIntegersAsStrings = False,
                 description                       = 'Global options',
                 dragThreshold                     = 10):
        '''Set global options on the module

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        
        autoReport                        : str='always'
        centerOnMove                      : str Option
        chatterHTMLSupport                : str='never'
        hotKeysOnClosedWindows            : str='never'
        inventoryForAll                   : str='always' 
        nonOwnerUnmaskable                : str='never'
        playerIdFormat                    : str='$PlayerName$'
        promptString                      : str=?
        sendToLocationMoveTrails          : bool=false
        storeLeadingZeroIntegersAsStrings : bool=False
        '''
        super(GlobalOptions,self).\
            __init__(doc,self.TAG,node=node,
                     autoReport               = autoReport,
                     centerOnMove             = centerOnMove,
                     chatterHTMLSupport       = chatterHTMLSupport,
                     hotKeysOnClosedWindows   = hotKeysOnClosedWindows,
                     inventoryForAll          = inventoryForAll,
                     nonOwnerUnmaskable       = nonOwnerUnmaskable,
                     playerIdFormat           = playerIdFormat,
                     promptString             = promptString,
                     sendToLocationMoveTrails = sendToLocationMoveTrails,
                     storeLeadingZeroIntegersAsStrings = storeLeadingZeroIntegersAsStrings,
                     dragThreshold            = dragThreshold,
                     description              = description)

    def addOption(self,**kwargs):
        '''Add a `Option` element to this

        Options known
        - newHotKey - key  - start new log
        - endHotKey - key  - end current log
        - stepIcon - image file name (/images/StepForward16.gif)
        - stepHotKey - key 
        - undoIcon - image file name (/images/Undo16.gif)
        - undoHotKey - key
        - serverControlsIcon - image file name (/images/connect.gif)
        - serverControlsHotKey - key
        - debugControlsIcon - image file name 
        - debugControlsHotKey - key 
        - scenarioPropertiesIcon - image file name
        - scenarioPropertiesHotKey - key

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
            - name : str
            - value : str
        
        Returns
        -------
        element : Option
            The added element
        '''
        return self.add(Option,**kwargs)
    def getOptions(self):
        return self.getElementsByKey(Option,'name')

    def addPreference(self,cls,**kwargs):
        return self.add(cls,**kwargs)

    def addIntPreference(self,**kwargs):
        return self.add(IntPreference,**kwargs)

    def addFloatPreference(self,**kwargs):
        return self.add(FloatPreference,**kwargs)
    
    def addBoolPreference(self,**kwargs):
        return self.add(BoolPreference,**kwargs)
    
    def addStrPreference(self,**kwargs):
        return self.add(StrPreference,**kwargs)
    
    def addTextPreference(self,**kwargs):
        return self.add(TextPreference,**kwargs)
    
    def addEnumPreference(self,**kwargs):
        return self.add(EnumPreference,**kwargs)
    
    def getIntPreferences(self):
        return self.getElementsByKey(IntPreference,'name')

    def getFloatPreferences(self):
        return self.getElementsByKey(FloatPreference,'name')

    def getBoolPreferences(self):
        return self.getElementsByKey(BoolPreference,'name')

    def getStrPreferences(self):
        return self.getElementsByKey(StrPreference,'name')

    def getTextPreferences(self):
        return self.getElementsByKey(TextPreference,'name')

    def getEnumPreferences(self):
        return self.getElementsByKey(EnumPreference,'name')

    def getPreferences(self):
        retd = {}
        for cls in [IntPreference,
                    FloatPreference,
                    BoolPreference,
                    StrPreference,
                    TextPreference,
                    EnumPreference]:
            retd.update(self.getElementsByKey(cls,'name'))

        return retd
    
registerElement(GlobalOptions)

# --------------------------------------------------------------------
class Option(Element):
    TAG = 'option'
    UNIQUE = ['name']
    def __init__(self,doc,node=None,name='',value=''):
        super(Option,self).__init__(doc,tag=self.TAG,node=node,name=name)
        self.addText(value)

    def getGlobalOptions(self):
        return self.getParent(GlobalOptions)

registerElement(Option)
    
# --------------------------------------------------------------------
class Preference(Element):
    PREFS = 'VASSAL.preferences.'
    UNIQUE = ['name','tab']
    def __init__(self,
                 doc,
                 tag,
                 node    = None,
                 name    = '',
                 default = '',
                 desc    = '',
                 tab     = '',
                 **kwargs):
        '''Add a preference

        Parameters
        ----------
        name : str
            Name of property
        default : str
            Default value
        desc : str
            Description
        tab : str
            Preference tab to put in to
        '''
        super(Preference,self).__init__(doc,
                                        tag     = tag,
                                        node    = node,
                                        name    = name,
                                        default = default,
                                        desc    = desc,
                                        tab     = tab)

    def getGlobalOptions(self):
        return self.getParent(GlobalOptions)
    
# --------------------------------------------------------------------
class IntPreference(Preference):
    TAG = Preference.PREFS+'IntegerPreference'
    def __init__(self,
                 doc,
                 node    = None,
                 name    = '',
                 default = 0,
                 desc    = '',
                 tab     = ''):
        super(IntPreference,self).__init__(doc,
                                           tag     = self.TAG,
                                           node    = node,
                                           name    = name,
                                           default = str(default),
                                           desc    = desc,
                                           tab     = tab)

registerElement(IntPreference)
    
# --------------------------------------------------------------------
class FloatPreference(Preference):
    TAG = Preference.PREFS+'DoublePreference'
    def __init__(self,
                 doc,
                 node    = None,
                 name    = '',
                 default = 0.,
                 desc    = '',
                 tab     = ''):
        super(FloatPreference,self).__init__(doc,
                                             tag     = self.TAG,
                                             node    = node,
                                             name    = name,
                                             default = str(default),
                                             desc    = desc,
                                             tab     = tab)

registerElement(FloatPreference)
    
# --------------------------------------------------------------------
class BoolPreference(Preference):
    TAG = Preference.PREFS+'BooleanPreference'
    def __init__(self,
                 doc,
                 node    = None,
                 name    = '',
                 default = False,
                 desc    = '',
                 tab     = ''):
        super(BoolPreference,self).__init__(doc,
                                            tag     = self.TAG,
                                            node    = node,
                                            name    = name,
                                            default = ('true' if default
                                                       else 'false'),
                                            desc    = desc,
                                            tab     = tab)

registerElement(BoolPreference)
    
# --------------------------------------------------------------------
class StrPreference(Preference):
    TAG = Preference.PREFS+'StringPreference'
    def __init__(self,
                 doc,
                 node    = None,
                 name    = '',
                 default = '',
                 desc    = '',
                 tab     = ''):
        super(StrPreference,self).__init__(doc,
                                           tag     = self.TAG,
                                           node    = node,
                                           name    = name,
                                           default = default,
                                           desc    = desc,
                                           tab     = tab)

registerElement(StrPreference)
    
# --------------------------------------------------------------------
class TextPreference(Preference):
    TAG = Preference.PREFS+'TextPreference'
    def __init__(self,
                 doc,
                 node    = None,
                 name    = '',
                 default = '',
                 desc    = '',
                 tab     = ''):
        super(TextPreference,self).__init__(doc,
                                            tag     = self.TAG,
                                            node    = node,
                                            name    = name,
                                            default = (default
                                                       .replace('\n','&#10;')),
                                            desc    = desc,
                                            tab     = tab)

registerElement(TextPreference)
    
# --------------------------------------------------------------------
class EnumPreference(Preference):
    TAG = Preference.PREFS+'EnumPreference'
    def __init__(self,
                 doc,
                 node    = None,
                 name    = '',
                 values  = [],
                 default = '',
                 desc    = '',
                 tab     = ''):
        ce = lambda v : str(v).replace(',',r'\,')
        sl = [ce(v) for v in values]
        df = ce(v)
        assert df in sl, \
            f'Default value "{default}" not in list {":".join(values)}'
        super(EnumPreference,self).__init__(doc,
                                            tag     = self.TAG,
                                            node    = node,
                                            name    = name,
                                            default = df,
                                            desc    = desc,
                                            tab     = tab,
                                            list    = sl)


registerElement(EnumPreference)
    
    
# --------------------------------------------------------------------
# CurrentMap == &quot;Board&quot;
class Inventory(ToolbarElement,GameElementService):
    TAG = Element.MODULE+'Inventory'
    ALPHA = 'alpha'
    LENGTH = 'length',
    NUMERIC = 'numeric'
    UNIQUE = ['name']
    def __init__(self,doc,node=None,
                 name                = '',
                 icon                = '/images/inventory.gif',
                 text                = '',
                 tooltip             = 'Show inventory of all pieces',
                 hotkey              = key('I',ALT),
                 canDisable          = False,
                 propertyGate        = '',
                 disabledIcon        = '',                 
                 centerOnPiece       = True,
                 drawPieces          = True,
                 foldersOnly         = False,
                 forwardKeystroke    = True,
                 groupBy             = '',
                 include             = '{}',
                 launchFunction      = 'functionHide',
                 leafFormat          = '$PieceName$',
                 nonLeafFormat       = '$PropertyValue$',
                 pieceZoom           = '0.33',
                 pieceZoom2          = '0.5',
                 pieceZoom3          = '0.6',
                 refreshHotkey       = key('I',ALT_SHIFT),
                 showMenu            = True,
                 sides               = '',
                 sortFormat          = '$PieceName$',
                 sortPieces          = True,
                 sorting             = ALPHA,
                 zoomOn              = False):
        super(Inventory,self).__init__(doc,self.TAG,node=node,
                                       canDisable          = canDisable,
                                       centerOnPiece       = centerOnPiece,
                                       disabledIcon        = disabledIcon,
                                       drawPieces          = drawPieces,
                                       foldersOnly         = foldersOnly,
                                       forwardKeystroke    = forwardKeystroke,
                                       groupBy             = groupBy,
                                       hotkey              = hotkey,
                                       icon                = icon,
                                       include             = include,
                                       launchFunction      = launchFunction,
                                       leafFormat          = leafFormat,
                                       name                = name,
                                       nonLeafFormat       = nonLeafFormat,
                                       pieceZoom           = pieceZoom,
                                       pieceZoom2          = pieceZoom2,
                                       pieceZoom3          = pieceZoom3,
                                       propertyGate        = propertyGate,
                                       refreshHotkey       = refreshHotkey,
                                       showMenu            = showMenu,
                                       sides               = sides,
                                       sortFormat          = sortFormat,
                                       sortPieces          = sortPieces,
                                       sorting             = sorting,
                                       text                = text,
                                       tooltip             = tooltip,
                                       zoomOn              = zoomOn)
                  
registerElement(Inventory)

# --------------------------------------------------------------------
class Prototypes(GameElement):
    TAG = Element.MODULE+'PrototypesContainer'
    def __init__(self,game,node=None,**kwargs):
        super(Prototypes,self).\
            __init__(game,self.TAG,node=node,**kwargs)

    def addPrototype(self,**kwargs):
        '''Add a `Prototype` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Prototype
            The added element
        '''
        return self.add(Prototype,**kwargs)
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
        return self.add(PrototypeFolder,**kwargs)
    def getPrototypes(self,asdict=True):
        '''Get all Prototype element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Prototype` elements.  If `False`, return a list of all Prototype` children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Prototype` children
        '''
        return self.getElementsByKey(Prototype,'name',asdict=asdict)
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
        return self.getElementsByKey(PrototypeFolder,'name',asdict)
        
registerElement(Prototypes)

# --------------------------------------------------------------------
class DiceButton(ToolbarElement,GameElementService):
    TAG=Element.MODULE+'DiceButton'
    UNIQUE = ['name']
    def __init__(self,elem,node=None,
                 name                 = '1d6',
                 tooltip              = 'Roll a 1d6',
                 text                 = '1d6',
                 icon                 = '/images/die.gif',
                 hotkey               = key('6',ALT),
                 canDisable           = False,
                 propertyGate         = '',
                 disabledIcon         = '',
                 addToTotal           = 0,
                 keepCount            = 1,
                 keepDice             = False,
                 keepOption           = '>',
                 lockAdd              = False,
                 lockDice             = False,
                 lockPlus             = False,
                 lockSides            = False,
                 nDice                = 1,
                 nSides               = 6,
                 plus                 = 0,
                 prompt               = False,
                 reportFormat         = '$name$ = $result$',
                 reportTotal          = False,
                 sortDice             = False):
        super(DiceButton,self).\
            __init__(elem,self.TAG,node=node,
                     addToTotal           = addToTotal,
                     canDisable           = canDisable,
                     disabledIcon         = disabledIcon,
                     hotkey               = hotkey,
                     icon                 = icon,
                     keepCount            = keepCount,
                     keepDice             = keepDice,
                     keepOption           = keepOption,
                     lockAdd              = lockAdd,
                     lockDice             = lockDice,
                     lockPlus             = lockPlus,
                     lockSides            = lockSides,
                     nDice                = nDice,
                     nSides               = nSides,
                     name                 = name,
                     plus                 = plus,
                     prompt               = prompt,
                     propertyGate         = propertyGate,
                     reportFormat         = reportFormat,
                     reportTotal          = reportTotal,
                     sortDice             = sortDice,
                     text                 = text,
                     tooltip              = tooltip)

registerElement(DiceButton)

# --------------------------------------------------------------------
class GameMassKey(GlobalKey,GameElementService):
    TAG = Element.MODULE+'GlobalKeyCommand'
    def __init__(self,map,node=None,
                 name                 = '',                
                 buttonText           = '',
                 tooltip              = '',
                 icon                 = '',
                 canDisable           = False,
                 propertyGate         = '',
                 disabledIcon         = '',
                 buttonHotkey         = '',
                 hotkey               = '',
                 deckCount            = '-1',
                 filter               = '',
                 reportFormat         = '',
                 reportSingle         = False,
                 singleMap            = True,
                 target               = GlobalKey.SELECTED):
        '''Default targets are selected units'''
        super(GameMassKey,self).\
            __init__(map,
                     self.TAG,
                     node                 = node,
                     name                 = name,                
                     buttonHotkey         = buttonHotkey, # This hot key
                     hotkey               = hotkey,       # Target hot key
                     buttonText           = buttonText,
                     canDisable           = canDisable,
                     deckCount            = deckCount,
                     filter               = filter,
                     propertyGate         = propertyGate,
                     reportFormat         = reportFormat,
                     reportSingle         = reportSingle,
                     singleMap            = singleMap,
                     target               = target,
                     tooltip              = tooltip,
                     icon                 = icon)
        
registerElement(GameMassKey)

# --------------------------------------------------------------------
class StartupMassKey(GlobalKey,GameElementService):
    TAG = Element.MODULE+'StartupGlobalKeyCommand'
    FIRST_LAUNCH = 'firstLaunchOfSession'
    EVERY_LAUNCH = 'everyLaunchOfSession'
    START_GAME   = 'startOfGameOnly'
    def __init__(self,
                 map,
                 node                 = None,
                 name                 = '',                
                 buttonHotkey         = '',
                 hotkey               = '',
                 buttonText           = '',
                 canDisable           = False,
                 deckCount            = '-1',
                 filter               = '',
                 propertyGate         = '',
                 reportFormat         = '',
                 reportSingle         = False,
                 singleMap            = True,
                 target               = GlobalKey.SELECTED,
                 tooltip              = '',
                 icon                 = '',
                 whenToApply          = EVERY_LAUNCH):
        '''Default targets are selected units'''
        super(StartupMassKey,self).\
            __init__(map,
                     self.TAG,
                     node                 = node,
                     name                 = name,                
                     buttonHotkey         = buttonHotkey, # This hot key
                     hotkey               = hotkey,       # Target hot key
                     buttonText           = buttonText,
                     canDisable           = canDisable,
                     deckCount            = deckCount,
                     filter               = filter,
                     propertyGate         = propertyGate,
                     reportFormat         = reportFormat,
                     reportSingle         = reportSingle,
                     singleMap            = singleMap,
                     target               = target,
                     tooltip              = tooltip,
                     icon                 = icon)
        if node is None:
            self['whenToApply'] = whenToApply

registerElement(StartupMassKey)

# --------------------------------------------------------------------
class Menu(GameElement):
    TAG = Element.MODULE+'ToolbarMenu'
    UNIQUE = ['name']
    def __init__(self,
                 game,
                 node                 = None,
                 name                 = '',
                 tooltip              = '',
                 text                 = '', # Menu name
                 canDisable           = False,
                 propertyGate         = '',
                 disabledIcon         = '',
                 description          = '',
                 hotkey               = '',
                 icon                 = '',
                 menuItems            = []):
        if len(description) <= 0 and len(tooltip) > 0:
            description = tooltip
        if len(tooltip) <= 0 and len(description) > 0:
            tooltip = description 
        super(Menu,self).\
            __init__(game,
                     self.TAG,
                     node                 = node,
                     name                 = name,
                     canDisable           = canDisable,
                     description          = description,
                     disabledIcon         = disabledIcon,
                     hotkey               = hotkey,
                     icon                 = icon,
                     menuItems            = ','.join(menuItems),
                     propertyGate         = propertyGate,
                     text                 = text,
                     tooltip              = tooltip)
                     
registerElement(Menu)

        
# --------------------------------------------------------------------
class SymbolicDice(GameElement):
    TAG = Element.MODULE+'SpecialDiceButton'
    UNIQUE = ['name']
    def __init__(self,
                 game,
                 node                    = None,
                 canDisable	         = False,
                 disabledIcon            = '',
                 hotkey                  = key('6',ALT),
                 name                    = "Dice",  # GP prefix
                 text                    = '', # Text on button
                 icon                    = '/images/die.gif', # Icon on button
                 format                  = '{name+": "+result1}', # Report 
                 tooltip                 = 'Die roll', # Help
                 propertyGate            = '', # Property to disable when T
                 resultButton            = False, # Result on button?
                 resultChatter           = True,  # Result in Chatter?
                 resultWindow            = False, # Result window?
                 backgroundColor	 = rgb(0xdd,0xdd,0xdd),  # Window background
                 windowTitleResultFormat = "$name$", # Window title
                 windowX                 = '67', # Window size
                 windowY                 = '65',
                 doHotkey                = False,
                 doLoop                  = False,
                 doReport                = False,
                 doSound                 = False,
                 hideWhenDisabled        = False,
                 hotkeys                 = '',
                 index                   = False,
                 indexProperty           = '',
                 indexStart              = 1,
                 indexStep               = 1,
                 loopCount               = 1,
                 loopType                = 'counted',
                 postLoopKey             = '',
                 reportFormat            = '',
                 soundClip               = '',
                 untilExpression         = '',
                 whileExpression         = ''
                 ):
        super(SymbolicDice,self).\
            __init__(game,
                     self.TAG,
                     node                    = node,
                     canDisable	             = canDisable,
                     disabledIcon            = disabledIcon,
                     hotkey                  = hotkey,
                     name                    = name,
                     text                    = text,
                     icon                    = icon,
                     format                  = format,
                     tooltip                 = tooltip,
                     propertyGate            = propertyGate,
                     resultButton            = resultButton,
                     resultChatter           = resultChatter,
                     resultWindow            = resultWindow,
                     backgroundColor	     = backgroundColor,
                     windowTitleResultFormat = windowTitleResultFormat,
                     windowX                 = windowX,
                     windowY                 = windowY,
                     doHotkey                = doHotkey,
                     doLoop                  = doLoop,
                     doReport                = doReport,
                     doSound                 = doSound,
                     hideWhenDisabled        = hideWhenDisabled,
                     hotkeys                 = hotkeys,
                     index                   = index,
                     indexProperty           = indexProperty,
                     indexStart              = indexStart,
                     indexStep               = indexStep,
                     loopCount               = loopCount,
                     loopType                = loopType,
                     postLoopKey             = postLoopKey,
                     reportFormat            = reportFormat,
                     soundClip               = soundClip,
                     untilExpression         = untilExpression,
                     whileExpression         = whileExpression)
        

    def addDie(self,**kwargs):
        return self.add(SpecialDie,**kwargs)

    def getSymbolicDice(self):
        return self.getParent(SymbolicDice)
        
registerElement(SymbolicDice)

        
# --------------------------------------------------------------------
class SpecialDie(GameElement):
    TAG = Element.MODULE+'SpecialDie'
    UNIQUE = ['name']
    def __init__(self,
                 symbolic,               # Symblic dice 
                 node                    = None,
                 name                    = '', # Name of dice (no GP)
                 report                  = '{name+": "+result}',
                 faces                   = None):
        super(SpecialDie,self).\
            __init__(symbolic,
                     self.TAG,
                     node = node,
                     name = name,
                     report = report)
        if node is not None or faces is None:
            return
        if isinstance(faces,list):
            faces = {i+1: f for i,f in enumerate(faces)}
        for v,f in faces:
            self.addFace(text = str(v), value = v, icon = f)

    def addFace(self,**kwargs):
        self.add(DieFace,**kwargs)

    def getSymbolicDice(self):
        return self.getParent(SymbolicDice)

    def getFaces(self):
        return self.getAllElements(DieFace,single=False)
        
registerElement(SpecialDie)
                     
# --------------------------------------------------------------------
class DieFace(GameElement):
    TAG = Element.MODULE+'SpecialDieFace'
    # Is this OK? Multiple faces can have the same icon, text and value 
    UNIQUE = ['icon','text','value']
    def __init__(self,
                 special,               # Special dice
                 node,                  # existing node
                 icon      = '',        # graphical representation
                 text      = '',        # Text representation
                 value     = 0):        # Value representation
        super(DieFace,self).\
            __init__(special,
                     self.TAG,
                     node      = node,
                     icon      = icon,
                     text      = text,
                     value     = value)
                     
    def getSpecialDie(self):
        return self.getParent(SpecialDie)

    # -- This one is tricky! --
    # def __hash__(self):
    #     return super().__hash__()+getSpecialDie()

registerElement(DieFace)

# --------------------------------------------------------------------
class ImageDefinitions(GameElement):
    #TAG = Element.MODULE+'gamepieceimage.GamePieceImageDefinitions'
    TAG = Element.MODULE+'gamepieceimage.GamePieceImageDefinitions'
    def __init__(self,
                 game,
                 node,
                 **kwargs):
        super().__init__(game,self.TAG,node=node,**kwargs)

registerElement(ImageDefinitions)

# --------------------------------------------------------------------
class LayoutsContainer(GameElement):
    #TAG = Element.MODULE+'gamepieceimage.GamePieceLayoutsContainer'
    TAG = Element.MODULE+'gamepieceimage.GamePieceLayoutsContainer'
    def __init__(self,
                 game,
                 node,
                 **kwargs):
        super().__init__(game,self.TAG,node=node,**kwargs)

registerElement(LayoutsContainer)

# --------------------------------------------------------------------
class ColorManager(GameElement):
    #TAG = Element.MODULE+'gamepieceimage.ColorManager'
    TAG = Element.MODULE+'gamepieceimage.ColorManager'
    def __init__(self,
                 game,
                 node,
                 **kwargs):
        super().__init__(game,self.TAG,node=node,**kwargs)

registerElement(ColorManager)

# --------------------------------------------------------------------
class FontManager(GameElement):
    #TAG = Element.MODULE+'gamepieceimage.FontManager'
    TAG = Element.MODULE+'gamepieceimage.FontManager'
    def __init__(self,
                 game,
                 node,
                 **kwargs):
        super().__init__(game,self.TAG,node=node,**kwargs)

registerElement(FontManager)

# --------------------------------------------------------------------
class FontStyle(GameElement):
    #TAG = Element.MODULE+'gamepieceimage.FontStyle'
    TAG = Element.MODULE+'gamepieceimage.FontStyle'
    def __init__(self,
                 game,
                 node,
                 **kwargs):
        super().__init__(game,self.TAG,node=node,**kwargs)

registerElement(FontStyle)

# --------------------------------------------------------------------
class MultiActionButton(GameElement):
    TAG = Element.MODULE+'MultiActionButton'
    def __init__(self,
                 game,
                 node,
                 description  = '',    # Reminder
                 text         = '',    # Text on button
                 tooltip      = '',    # Button tooltip 
                 icon         = '',    # Image on button
                 hotkey       = '',    # Key-stroke or command
                 canDisable   = False, # Can it be disabled
                 propertyGate = '',    # Disable when propety true
                 disabledIcon = '',    # image when disabled
                 menuItems    = []):   # Button texts
        '''
        A button that executes other buttons (by `buttonText` name)

        Parameters
        ----------
        game : pywargame.vassal.Game
            The game parent
        node : xml.dom.minidom.Node
            Possible node
        description : str
            Description (comment)
        text : str
            Text on button
        tooltip : str
            Button tool-tip
        icon : str
            Icon on button
        hotkey : str
            Hotkey or named command to execute button
        canDisable : bool
            If this can be disabled
        propertyGate : str
            When property (not expression) is `true`, then disable
            this button
        disabledIcon : str
            Icon to use when disabled
        menuItems : list of str
            `buttonText` of other buttons to execute
            (note, not named commands or hotkeys). 
        '''
        super().__init__(game,
                         self.TAG,
                         node    = node,
                         description  = description,
                         text         = text,
                         tooltip      = tooltip,
                         icon         = icon,
                         hotkey       = hotkey,
                         canDisable   = canDisable,
                         propertyGate = propertyGate,
                         disabledIcon = disabledIcon,
                         menuItems    = ','.join(menuItems))
                         
registerElement(MultiActionButton)

#
# EOF
#
