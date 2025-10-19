## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . gameelements import GameElement
from . widget import WidgetElement
## END_IMPORT

# --------------------------------------------------------------------
class ChartWindow(GameElement,WidgetElement):
    TAG=Element.MODULE+'ChartWindow'
    UNIQUE = ['name']
    def __init__(self,elem,node=None,
                 name        = '',
                 hotkey      = key('A',ALT),
                 description = '',
                 text        = '',
                 tooltip     = 'Show/hide Charts',
                 icon        = '/images/chart.gif'):
        super(ChartWindow,self).__init__(elem,self.TAG,node=node,
                                         name        = name,
                                         hotkey      = hotkey,
                                         description = description,
                                         text        = text,
                                         tooltip     = tooltip,
                                         icon        = icon)

    def addChart(self,**kwargs):
        '''Add a `Chart` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Chart
            The added element
        '''
        return self.add(Chart,**kwargs)
    def getCharts(self,asdict=True):
        '''Get all Chart element(s) from this

        Parameters
        ----------
        asdict : bool        
            If `True`, return a dictonary that maps key to `Chart`
            elements.  If `False`, return a list of all Chart`
            children.
        
        Returns
        -------
        children : dict or list
            Dictionary or list of `Chart` children

        '''
        return self.getElementsById(Chart,'chartName',asdict=asdict)
    
registerElement(ChartWindow)    

# --------------------------------------------------------------------
class Chart(Element):
    TAG=Element.WIDGET+'Chart'
    UNIQUE = ['chartName','fileName']
    def __init__(self,elem,node=None,
                 chartName   = '',
                 fileName    = '',
                 description = ''):
        super(Chart,self).__init__(elem,self.TAG,node=node,
                                   chartName   = chartName,
                                   description = description,
                                   fileName    = fileName)

registerElement(Chart)

#
# EOF
#
