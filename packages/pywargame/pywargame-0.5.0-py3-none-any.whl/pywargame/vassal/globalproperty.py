## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
## END_IMPORT

# --------------------------------------------------------------------
class GlobalProperties(Element):
    TAG = Element.MODULE+'properties.GlobalProperties'
    def __init__(self,elem,node=None,**named):
        super(GlobalProperties,self).__init__(elem,self.TAG,node=node)
        
        for n, p in named:
            self.addProperty(n, **p)

    def getGame(self):
        return self.getParent(Game)
    def addProperty(self,**kwargs):
        '''Add a `Property` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Property
            The added element
        '''
        return GlobalProperty(self,node=None,**kwargs)
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
        return self.add(GlobalPropertyFolder,**kwargs)
    
    def getProperties(self):
        return getElementsByKey(GlobalProperty,'name')

    def addScenarioTab(self,**kwargs):
        '''Add a scenario property tab

        Parameters
        -----------
        kwargs : dict
            Key-value pairs to send to ScenarioOptionsTab

        Returns
        -------
        element : ScenarioOptionsTab
            Added element
        '''
        return ScenarioOptionsTab(self,node=None,**kwargs)

    def getScenarioTabs(self):
        return getElementsByKey(ScenarioOptionsTab,'name')
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
        return self.getElementsByKey(GlobalPropertyFolder,'name',asdict)
    
registerElement(GlobalProperties)

# --------------------------------------------------------------------
class GlobalProperty(Element):
    TAG = Element.MODULE+'properties.GlobalProperty'
    UNIQUE = ['name']
    def __init__(self,
                 elem,
                 node         = None,
                 name         = '',
                 initialValue = '',
                 isNumeric    = False,
                 min          = "null",
                 max          = "null",
                 wrap         = False,
                 description  = ""):
        super(GlobalProperty,self).__init__(elem,self.TAG,
                                            node         = node,
                                            name         = name,
                                            initialValue = initialValue,
                                            isNumeric    = isNumeric,
                                            min          = min,
                                            max          = max,
                                            wrap         = wrap,
                                            description  = description)

    def getGlobalProperties(self):
        return self.getParent(GlobalProperties)

    def addChange(self,**kwargs):
        '''Add a global button, or key or named key command to change
        the property.

        Parameters
        ----------
        kwargs : dict
            Keywords to pass to `ChangeProperty` CTOR

        Returns:
        --------
        elem : ChangeProperty
            The added element
        '''
        self.add(ChangeProperty,**kwargs)
        
    def getChange(self,single=True):
        '''Get all or a sole `ChangeProperty` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `ChangeProperty` child,
            otherwise fail.

            If `False` return all `ChangeProperty` children in this
            element
        
        Returns
        -------
        children : list
            List of `ChangeProperty` children (even if `single=True`)

        '''
        return self.getAllElements(ChangeProperty,single)
        

registerElement(GlobalProperty)

# --------------------------------------------------------------------
class ChangeProperty(Element):
    TAG = Element.MODULE+'properties.ChangePropertyButton'
    DIRECT    = 'P'
    INCREMENT = 'I'
    PROMPT    = 'R'
    LIST      = 'E'
    def __init__(self,
                 elem,
                 node             = None,
                 text             = '', # Button text
                 tooltip          = '', # Button tooltop
                 icon             = '', # Button icon
                 hotkey           = '', # Hotkey or named command
                 desc             = 'Change parent property', # Description
                 canDisable       = False,
                 propertyGate     = '',
                 disabledIcon     = '',
                 hideWhenDisabled = False,
                 mode             = DIRECT, # How to change
                 expression       = '',     # For direct, increment - BS
                 prompt           = 'Enter value',
                 values           = [],     # From list'
                 
                 reportFormat     = '', # Report on change - BS
                 oldValue         = '', # Old value format - Deprecated
                 newValue         = '', # New value format - Deprecated
                 description      = ''): # Description format
        propChanger = (mode + ',' +
                       (expression if mode in [self.DIRECT,self.INCREMENT]
                        else prompt) +
                       (r'\,'.join(values) if mode == self.LIST else ''))
        
        super(ChangeProperty,self).__init__(elem,self.TAG,
                                            node         = node,
                                            text             = text,
                                            tooltip          = tooltip,
                                            icon             = icon,
                                            hotkey           = hotkey,
                                            desc             = desc,
                                            canDisable       = canDisable,
                                            propertyGate     = propertyGate,
                                            disabledIcon     = disabledIcon,
                                            hideWhenDisabled = hideWhenDisabled,
                                            propChanger      = propChanger,
                                            reportFormat     = reportFormat,
                                            oldValue         = oldValue,
                                            newValue         = newValue,
                                            description      = description)

    def getGlobalProperties(self):
        return self.getParent(GlobalProperties)

registerElement(ChangeProperty)

# ====================================================================
class ScenarioOptionsTab(Element):
    TAG = Element.MODULE+'properties.ScenarioPropertiesOptionTab'
    LEFT = 'left'
    RIGHT = 'right'
    UNIQUE = ['name']
    
    def __init__(self,elem,node=None,
                 name         = 'Options',
                 description  = 'Scenario options',
                 heading      = '',
                 leftAlign    = 'left',
                 reportFormat = ('!$PlayerId$ changed Scenario Option '
                                 '[$tabName$] $propertyPrompt$ from '
                                '$oldValue$ to $newValue$')):
        super(ScenarioOptionsTab,self).__init__(elem,
                                                self.TAG,
                                                node         = node,
                                                name         = name,
                                                description  = description,
                                                heading      = heading,
                                                leftAlign    = leftAlign,
                                                reportFormat = reportFormat)

    def addList(self,**kwargs):

        '''Add a list property option

        Parameters
        ----------
        kwargs : dict
            Key, value pairs to initalise ScenarioOptionList

        Returns
        -------
        element : ScenarioOption
            The added element
        '''
        return ScenarioOptionList(self,node=None,**kwargs)

    def addBoolean(self,**kwargs):
        '''Add a list property option

        Parameters
        ----------
        kwargs : dict
            Key, value pairs to initalise ScenarioOptionBool

        Returns
        -------
        element : ScenarioOption
            The added element
        '''
        return ScenarioOptionBool(self,node=None,**kwargs)

    def addString(self,**kwargs):
        '''Add a list property option

        Parameters
        ----------
        kwargs : dict
            Key, value pairs to initalise ScenarioOptionString

        Returns
        -------
        element : ScenarioOption
            The added element
        '''
        return ScenarioOptionString(self,node=None,**kwargs)

    def addNumber(self,**kwargs):
        '''Add a list property option

        Parameters
        ----------
        kwargs : dict
            Key, value pairs to initalise ScenarioOptionNumber

        Returns
        -------
        element : ScenarioOption
            The added element
        '''
        return ScenarioOptionString(self,node=None,**kwargs)

    def getOptions(self):
        return self.getElementsByKey(ScenarioOption,'name')

    def getListOptions(self):
        return self.getElementsByKey(ScenarioOptionList,'name')

    def getBoolOptions(self):
        return self.getElementsByKey(ScenarioOptionBool,'name')

    def getStringOptions(self):
        return self.getElementsByKey(ScenarioOptionString,'name')
    
    def getNumberOptions(self):
        return self.getElementsByKey(ScenarioOptionNumber,'name')
    
    def getGlobalProperties(self):
        return self.getParent(GlobalProperties)

registerElement(ScenarioOptionsTab)
    
# --------------------------------------------------------------------
class ScenarioOption(Element):
    UNIQUE = ['name']

    def __init__(self,
                 tab, 
                 tag,
                 node         = None,
                 name         = '',
                 hotkey       = '',
                 description  = 'Set option value',
                 switch       = False,
                 initialValue = '',
                 **kwargs):
        '''
        Parameters
        ----------
        tab : ScenarioOptionsTab
            Tab to add to 
        tag : str
            Tag value (full)
        name : str
            Name of global property 
        hotkey : named-key
            Key stroke to send (global key)
        description : str
            Text to show user
        switch : bool
            If true, then prompt is put to the right
        initialValue : str
            Initial value
        kwargs : dict
            Other arguments
        '''
        super(ScenarioOption,self).__init__(tab,
                                            tag,
                                            node         = node,
                                            name         = name,
                                            hotkey       = hotkey,
                                            description  = description,
                                            switch       = switch,
                                            initialValue = initialValue,
                                            **kwargs)

    def getTab(self):
        return self.getParent(ScenarioOptionsTab)

# --------------------------------------------------------------------
class ScenarioOptionList(ScenarioOption):
    TAG = Element.MODULE+'properties.ListScenarioProperty'

    def __init__(self,
                 tab,
                 node         = None,
                 name         = '',
                 hotkey       = '',
                 description  = 'Set option value',
                 switch       = False,
                 initialValue = None,
                 options      = []):
        '''
        Parameters
        ----------
        tag : str
            Tag value (full)
        name : str
            Name of global property 
        hotkey : named-key
            Key stroke to send (global key)
        description : str
            Text to show user
        switch : bool
            If true, then prompt is put to the right
        initialValue : str
            Initial value.  If None, set to first option
        options : list 
            Possible values
        '''
        opts = ','.join([str(s) for s in options])
        if initialValue is None:
            initialValue = opts[0]
            
        super(ScenarioOptionList,self).__init__(tab,
                                                self.TAG,
                                                node         = node,
                                                name         = name,
                                                hotkey       = hotkey,
                                                description  = description,
                                                switch       = switch,
                                                initialValue = initialValue,
                                                options      = opts)

registerElement(ScenarioOptionList)

# --------------------------------------------------------------------
class ScenarioOptionBool(ScenarioOption):
    TAG = Element.MODULE+'properties.BooleanScenarioProperty'

    def __init__(self,
                 tab,
                 node         = None,
                 name         = '',
                 hotkey       = '',
                 description  = 'Set option value',
                 switch       = False,
                 initialValue = False):
        '''
        Parameters
        ----------
        tag : str
            Tag value (full)
        name : str
            Name of global property 
        hotkey : named-key
            Key stroke to send (global key)
        description : str
            Text to show user
        switch : bool
            If true, then prompt is put to the right
        initialValue : bool
            Initial value
        '''
        super(ScenarioOptionBool,self).__init__(tab,
                                                self.TAG,
                                                node         = node,
                                                name         = name,
                                                hotkey       = hotkey,
                                                description  = description,
                                                switch       = switch,
                                                initialValue = initialValue)
        
registerElement(ScenarioOptionBool)

# --------------------------------------------------------------------
class ScenarioOptionString(ScenarioOption):
    TAG = Element.MODULE+'properties.StringScenarioProperty'

    def __init__(self,
                 tab,
                 node         = None,
                 name         = '',
                 hotkey       = '',
                 description  = 'Set option value',
                 switch       = False,
                 initialValue = False):
        '''
        Parameters
        ----------
        tag : str
            Tag value (full)
        name : str
            Name of global property 
        hotkey : named-key
            Key stroke to send (global key)
        description : str
            Text to show user
        switch : bool
            If true, then prompt is put to the right
        initialValue : str
            Initial value
        '''
        super(ScenarioOptionString,self).__init__(tab,
                                                  self.TAG,
                                                  node         = node,
                                                  name         = name,
                                                  hotkey       = hotkey,
                                                  description  = description,
                                                  switch       = switch,
                                                  initialValue = initialValue)
        
registerElement(ScenarioOptionString)

# --------------------------------------------------------------------
class ScenarioOptionNumber(ScenarioOption):
    TAG = Element.MODULE+'properties.NumberScenarioProperty'

    def __init__(self,
                 tab,
                 node         = None,
                 name         = '',
                 hotkey       = '',
                 description  = 'Set option value',
                 switch       = False,
                 initialValue = False):
        '''
        Parameters
        ----------
        tag : str
            Tag value (full)
        name : str
            Name of global property 
        hotkey : named-key
            Key stroke to send (global key)
        description : str
            Text to show user
        switch : bool
            If true, then prompt is put to the right
        initialValue : str
            Initial value
        '''
        super(ScenarioOptionNumber,self).__init__(tab,
                                                  self.TAG,
                                                  node         = node,
                                                  name         = name,
                                                  hotkey       = hotkey,
                                                  description  = description,
                                                  switch       = switch,
                                                  initialValue = initialValue)

registerElement(ScenarioOptionNumber)

#
# EOF
#
