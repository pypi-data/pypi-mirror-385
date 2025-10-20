## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . gameelements import GameElement
## END_IMPORT

# ====================================================================
def createKeyHelp(*args,**kwargs):
    '''Creates a help file with key-bindings

    See Documentation.createKeyHelp
    '''
    return Documentation.createKeyHelp(*args,**kwargs)

# --------------------------------------------------------------------
class Documentation(GameElement):
    TAG=Element.MODULE+'Documentation'
    def __init__(self,doc,node=None,**kwargs):
        '''Documentation (or help menu)

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        kwargs : dict
            Attributes
        '''
        super(Documentation,self).__init__(doc,self.TAG,node=node,**kwargs)

    def addAboutScreen(self,**kwargs):
        '''Add a `AboutScreen` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : AboutScreen
            The added element
        '''
        return self.add(AboutScreen,**kwargs)
    def addHelpFile(self,**kwargs):
        '''Add a `HelpFile` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : HelpFile
            The added element
        '''
        return self.add(HelpFile,**kwargs)
    def addBrowserHelpFile(self,**kwargs):
        '''Add a `BrowserHelpFile` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : BrowserHelpFile
            The added element
        '''
        return self.add(BrowserHelpFile,**kwargs)
    def addBrowserPDFFile(self,**kwargs):
        '''Add a `BrowserPDFFile` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : BrowserPDFFile
            The added element
        '''
        return self.add(BrowserPDFFile,**kwargs)
    def addTutorial(self,**kwargs):
        '''Add a `Tutorial` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Tutorial
            The added element
        '''
        return self.add(Tutorial,**kwargs)
    def getAboutScreens(self):
        return self.getElementsByKey(AboutScreen,'title')
    def getHelpFiles(self):
        return self.getElementsByKey(HelpFile,'title')
    def getBrowserHelpFiles(self):
        return self.getElementsByKey(BrowserHelpFile,'title')
    def getBrowserPDFFiles(self):
        return self.getElementsByKey(BrowserPDFFile,'title')
    def getTutorials(self):
        return self.getElementsByKey(Tutorial,'name')

    @classmethod
    def createKeyHelp(cls,keys,title='',version=''):
        '''Creates a help file with key-bindings
        
        Parameters
        ----------
        keys : list of list of str
             List of key-binding documentation
        title : str
             Title of help file
        version : str
             Version number
        
        Returns
        -------
        txt : str
            File content
        '''
        txt = f'''
        <html>
         <body>
          <h1>{title} (Version {version}) Key bindings</h1>
          <table>
          <tr><th>Key</th><th>Where</th><th>Effect</th></tr>'''
        
        for key, where, description in keys:
            txt += (f'<tr><td>{key}</td>'
                    f'<td>{where}</td>'
                    f'<td>{description}</td></tr>')
        
        txt += '''
          </table>
         </body>
        </html>'''
        
        return txt 

registerElement(Documentation)

# --------------------------------------------------------------------
class AboutScreen(Element):
    TAG = Element.MODULE+'documentation.AboutScreen'
    UNIQUE = ['title']
    def __init__(self,doc,node=None,title='',fileName=""):
        '''Create an about screen element that shows image

        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        title : str
            Entry title
        fileName : str
            Internal file name        
        '''
        super(AboutScreen,self).__init__(doc,
                                         self.TAG,
                                         node     = node,
                                         fileName = fileName,
                                         title    = title)
    def getDocumentation(self):
        '''Get Parent element'''
        return self.getParent(Documentation)

registerElement(AboutScreen)

# --------------------------------------------------------------------
class BrowserPDFFile(Element):
    TAG = Element.MODULE+'documentation.BrowserPDFFile'
    UNIQUE = ['title','pdfFile']
    def __init__(self,doc,node=None,title='',pdfFile=''):
        '''Create help menu item that opens an embedded PDF
        
        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        title : str
            Entry title
        pdfFile : str
            Internal file name
        '''
        super(BrowserPDFFile,self).__init__(doc,self.TAG,
                                            node    = node,
                                            pdfFile = pdfFile,
                                            title   = title)
    def getDocumentation(self):
        '''Get Parent element'''
        return self.getParent(Documentation)

registerElement(BrowserPDFFile)
    
# --------------------------------------------------------------------
class HelpFile(Element):
    TAG = Element.MODULE+'documentation.HelpFile'
    ARCHIVE = 'archive'
    UNIQUE = ['title','fileName']
    def __init__(self,doc,node=None,
                 title='',
                 fileName='',
                 fileType=ARCHIVE):
        '''Create a help menu entry that opens an embeddded file
        
        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        title : str
            Entry title
        fileName : str
            Internal file name
        fileType : str
            How to find the file 
        '''
        super(HelpFile,self).__init__(doc,self.TAG,node=node,
                                      fileName = fileName,
                                      fileType = fileType,
                                      title    = title)

    def getDocumentation(self):
        '''Get Parent element'''
        return self.getParent(Documentation)

registerElement(HelpFile)
    
# --------------------------------------------------------------------
class BrowserHelpFile(Element):
    TAG = Element.MODULE+'documentation.BrowserHelpFile'
    UNIQUE = ['title','startingPage']
    def __init__(self,doc,node=None,
                 title='',
                 startingPage='index.html'):
        '''Create a help menu entry that opens an embeddded HTML
        page (with possible sub-pages) file
        
        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        title : str
            Entry title
        startingPage : str
            which file to start at
        '''
        super(BrowserHelpFile,self).__init__(doc,self.TAG,node=node,
                                             startingPage=startingPage,
                                             title=title)

    def getDocumentation(self):
        '''Get Parent element'''
        return self.getParent(Documentation)

registerElement(BrowserHelpFile)
    
# --------------------------------------------------------------------
class Tutorial(Element):
    TAG = Element.MODULE+'documentation.Tutorial'
    UNIQUE = ['name','logfile']
    def __init__(self,doc,node=None,
                 name            = 'Tutorial',
                 logfile         = 'tutorial.vlog',
                 promptMessage   = 'Load the tutorial?',
                 welcomeMessage  = 'Press "Step forward" (PnDn) to step through the tutorial',
                 launchOnStartup = True):
        '''Add a help menu item that loads the tutorial

        Also adds the start-up option to run the tutorial


        Parameters
        ----------
        doc : Element
            Parent
        node : xml.dom.Element
            Node to read state from
        name : str
            Name of entry
        logfile : str
            Internal file name
        promptMessage : str
            What to show
        launchOnStartup : bool
            By default, launch tutorial first time running module
        '''
        super(Tutorial,self).__init__(doc,self.TAG,node=node,
                                      name            = name,
                                      logfile         = logfile,
                                      promptMessage   = promptMessage,
                                      welcomeMessage  = welcomeMessage,
                                      launchOnStartup = launchOnStartup)

    def getDocumentation(self):
        '''Get Parent element'''
        return self.getParent(Documentation)

registerElement(Tutorial)
    

#
# EOF
#
