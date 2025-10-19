## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
## END_IMPORT

# --------------------------------------------------------------------
class TurnLevel(Element):
    UNIQUE = ['property']
    def __init__(self,elem,tag,node=None,**kwargs):
        super(TurnLevel,self).__init__(elem,tag,node=node,**kwargs)

    def addLevel(self,counter=None,phases=None):
        '''Add a `Level` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Level
            The added element
        '''
        if counter is None and phases is None:
            return self
        
        t = TurnCounter if counter is not None else TurnList
        o = counter     if counter is not None else phases

        subcounter = o.pop('counter',None)
        subphases  = o.pop('phases',None)

        s = t(self,node=None,**o)

        return s.addLevel(subcounter, subphases)

    def getUp(self):
        return self.getParent(TurnLevel)
    def addCounter(self,**kwargs):
        '''Add a `Counter` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Counter
            The added element
        '''
        return self.add(self,TurnCounter,**kwargs)
    def addList(self,**kwargs):
        '''Add a `List` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : List
            The added element
        '''
        return self.add(self,TurnList,**kwargs)
    def getCounter(self):
        return self.getAllElements(TurnCounter)
    def getList(self):
        return self.getAllElements(TurnList)

# --------------------------------------------------------------------
class TurnTrack(TurnLevel):
    TAG = Element.MODULE+'turn.TurnTracker'
    UNIQUE   = ['name']
    MAXIMUM  = 'Maximum'
    FIXED    = 'Fixed'
    VARIABLE = 'Variable'
    def __init__(self,elem,node=None,
                 name             = '',
                 buttonText       = 'Turn',
                 hotkey           = '',
                 icon             = '',
                 length           = -1,
                 lengthStyle      = MAXIMUM,
                 nexthotkey       = key('T',ALT),
                 plusButtonSize   = 22,
                 prevhotkey       = key('T',ALT_SHIFT),
                 reportFormat     = 'Turn updated from $oldTurn$ to $newTurn$',
                 turnButtonHeight = 22,
                 fwdOnly          = True,
                 turnFormat       = None,
                 counter          = None,
                 phases           = None):
        levels = (counter if counter is not None else
                  phases if phases is not None else None)
        if levels is not None:
            lvl = 1
            lvls = [f'$level{lvl}$']
            sub  = levels
            while True:
                sub = sub.get('counter',sub.get('phases',None))
                if sub is None:
                    break
                lvl += 1
                lvls.append(f'$level{lvl}$')
            
            turnFormat = ' '.join(lvls)
        
        if turnFormat is None:
            turnFormat = '$level1$ $level2$ $level3$ $level4$'        
        
        super(TurnTrack,self).__init__(elem, self.TAG,
                                       node             = node,
                                       name             = name,
                                       buttonText       = buttonText,
                                       hotkey           = hotkey,
                                       icon             = icon,
                                       length           = length,
                                       lengthStyle      = lengthStyle,
                                       nexthotkey       = nexthotkey,
                                       plusButtonSize   = plusButtonSize,
                                       prevhotkey       = prevhotkey,
                                       reportFormat     = reportFormat,
                                       turnButtonHeight = turnButtonHeight,
                                       turnFormat       = turnFormat)

        self.addLevel(counter=counter, phases=phases)

    def getGame(self):
        return self.getParent(Game)
    def getLists(self,asdict=True):
        '''Get all List element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `List`
            elements.  If `False`, return a list of all List`
            children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `List` children

        '''
        return self.getElementsByKey(TurnList,'property',asdict=asdict)
    def getCounters(self,asdict=True):
        '''Get all Counter element(s) from this

        Parameters
        ----------
        asdict : bool
            If `True`, return a dictonary that maps key to `Counter`
            elements.  If `False`, return a list of all Counter`
            children.

        Returns
        -------
        children : dict or list
            Dictionary or list of `Counter` children

        '''
        return self.getElementsByKey(TurnCounter,'property',asdict=asdict)
    def addHotkey(self,**kwargs):
        '''Add a `Hotkey` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Hotkey
            The added element
        '''
        return self.add(TurnGlobalHotkey,**kwargs)
    def getHotkeys(self,asdict=True):
        return self.getElementsByKey(TurnGlobalHotkey,'name',asdict=asdict)
    def encode(self):
        ret = f'TURN{self["name"]}\t'
        
        return []

registerElement(TurnTrack)

# --------------------------------------------------------------------
class TurnCounter(TurnLevel):
    TAG = Element.MODULE+"turn.CounterTurnLevel"
    def __init__(self,elem,node=None,
                 property      = '',
                 start         = 1,
                 incr          = 1,
                 loop          = False,
                 loopLimit     = -1,
                 turnFormat    = "$value$"):
        super(TurnCounter,self).__init__(elem,self.TAG,node=node,
                                         property       = property,
                                         start          = start,
                                         incr           = incr,
                                         loop           = loop,
                                         loopLimit      = loopLimit,
                                         turnFormat     = turnFormat)
                    
registerElement(TurnCounter)

# --------------------------------------------------------------------
class TurnList(TurnLevel):
    TAG = Element.MODULE+"turn.ListTurnLevel"
    def __init__(self,elem,node=None,
                 property      = '',
                 names         = [],
                 configFirst   = False,
                 configList    = False,
                 turnFormat    = '$value$'):
        super(TurnList,self).\
            __init__(elem,self.TAG,node=node,
                     property       = property,
                     list           = ','.join([str(p) for p in names]),
                     configFirst    = configFirst,
                     configList     = configList,
                     turnFormat     = turnFormat)
                  
registerElement(TurnList)

# --------------------------------------------------------------------
class TurnGlobalHotkey(Element):
    TAG = Element.MODULE+'turn.TurnGlobalHotkey'
    UNIQUE = ['name']
    def __init__(self,elem,
                 node         = None,
                 hotkey       = '',
                 match        = '{true}',
                 reportFormat = '',
                 name         = ''):
        '''Global key activated by turn change

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        hotkey : str
            What to send (global command)
        match : str
            When to send
        reportFormat : str
            What to what
        name : str
            A free form name
        '''
        super(TurnGlobalHotkey,self).__init__(elem,self.TAG,
                                              node         = node,
                                              hotkey       = hotkey,
                                              match        = match,
                                              reportFormat = reportFormat,
                                              name         = name)

    def getTurnTrack(self):
        '''Get the turn track'''
        return self.getParent(TurnTrack)

registerElement(TurnGlobalHotkey)

#
# EOF
#
