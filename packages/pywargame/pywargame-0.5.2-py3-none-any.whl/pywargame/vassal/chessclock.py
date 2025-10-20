## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . gameelements import GameElement
## END_IMPORT

# ====================================================================
class ChessClock(Element):
    TAG=Element.MODULE+'chessclockcontrol.ChessClock'
    UNIQUE = ['side']
    def __init__(self,
                 doc,
                 node                   = None,
                 icon                   = '',
                 description            = '',
                 side                   = '',
                 tooltip                = 'Individual clock control',
                 buttonText             = '',
                 startHotkey            = '',
                 stopHotkey             = '',
                 tickingBackgroundColor = rgb(255,255,0),
                 tickingFontColor       = rgb(0,0,0),
                 tockingFontColor       = rgb(51,51,51)):
        '''Individual clock for a side

        When the clock is running, the background colour may be
        changed, and the colour of the numbers alternate between
        `tickingFontColor` and `tockingFontColor`.
        
        Parameters
        ----------
        doc : Element
            Parent element 
        node : xml.dom.Element 
            Read from this node
        icon : str
            File name of button icon
        description : str
            Note on this clock
        side : str
            Name of side this clock belongs to
        tooltop : str
            Hover help text
        buttonText : str
            Text on button
        startHotkey : str (key code)
            Key or command to start timer
        stopHotkey : str (key code)
            Key or command to stop timer
        tickingBackgroundColor : str (color)
            Background color of time display when clock is running
        tickingFontColor : str (color)
            First color of numbers in display when clock is running.
        tockingFontColor : str (color)
            Second color of numbers in display when clock is running.
        '''
        super(ChessClock,self).__init__(#ChessClock
                 doc,
                 self.TAG,
                 node                   = node,
                 icon                   = icon,
                 description            = description,
                 side                   = side,
                 tooltip                = tooltip,
                 buttonText             = buttonText,
                 startHotkey            = startHotkey,
                 stopHotkey             = stopHotkey,
                 tickingBackgroundColor = tickingBackgroundColor,
                 tickingFontColor       = tickingFontColor,
                 tockingFontColor       = tockingFontColor)
            
    def getControl(self):
        '''Get Parent element'''
        return self.getParent(ChessClockControl)

registerElement(ChessClock)

# ====================================================================
class ChessClockControl(GameElement):
    TAG=Element.MODULE+'ChessClockControl'
    ALWAYS = 'Always'
    AUTO   = 'Auto'
    NEVER  = 'Never'
    UNIQUE = ['name']
    def __init__(self,
                 doc,
                 node              = None,
                 name              = 'Chess clock',
                 description       = '',
                 buttonIcon        = 'chess_clock.png',
                 buttonText        = '',
                 buttonTooltip     = 'Show/stop/hide chess clocks',
                 showHotkey        = key('U',ALT),
                 pauseHotkey       = key('U',CTRL_SHIFT),
                 nextHotkey        = key('U'),
                 startOpponentKey  = '',
                 showTenths        = AUTO,
                 showSeconds       = AUTO,
                 showHours         = AUTO,
                 showDays          = AUTO,
                 allowReset        = False,
                 addClocks         = True):
        '''A set of chess clocs

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        name : str
            Name of clock control
        description : str
            Note on the chess clocks control
        buttonIcon : str
            Icon file name for button (chess_clock.png)
        buttonText : str
            Text on button 
        buttonTooltip : str
            Hower help
        showHotkey : str (key code)
            Show or hide interface hot key
        nextHotkey : str (key code)
            Start the next clock hot key
        pauseHotkey : str (key code)
            Pause all clocks hot key 
        startOpponentKey : str (key code)
            Start opponens clock 
        showTenths : one of AUTO, ALWAYS, NEVER
            Whether to show tenths of seconds
        showSeconds : one of AUTO, ALWAYS, NEVER
            Whether to show seconds in clock 
        showHours : one of AUTO, ALWAYS, NEVER
            Whether to show hours in clock
        showDays : one of AUTO, ALWAYS, NEVER
            Whether to show days in clock
        allowReset : boolean
            If true, allow manual reset of all clocks
        '''
        super(ChessClockControl,self).__init__(# ChessclockControl
            doc,
            self.TAG,
            node              = node,
            name              = name,
            description       = description,
            buttonIcon        = buttonIcon,
            buttonText        = buttonText,
            buttonTooltip     = buttonTooltip,
            showHotkey        = showHotkey,
            pauseHotkey       = pauseHotkey,
            nextHotkey        = nextHotkey,
            startOpponentKey  = startOpponentKey,
            showTenths        = showTenths,
            showSeconds       = showSeconds,
            showHours         = showHours,
            showDays          = showDays,
            allowReset        = allowReset)
        print(node,addClocks)
        if node is not None or not addClocks:
            return
        
        print('--- Will add clocks')
        game   = self.getGame()
        roster = game.getPlayerRoster()[0]
        sides  = roster.getSides()
        for side in sides:
            name = side.getText()
            self.addClock(side        = name,
                          tooltip     = f'Clock for {name}',
                          buttonText  = name,
                          startHotkey = key('U'),
                          stopHotkey  = key('U'))
    
    def addClock(self,**kwargs):
        '''Add a clock element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : AboutScreen
            The added element
        '''
        return self.add(ChessClock,**kwargs)
    def getClocks(self,asdict=True):
        '''Return dictionary of clocs'''
        return self.getElementsByKey(ChessClock,'side',asdict)

registerElement(ChessClockControl)

#
# EOF
#
