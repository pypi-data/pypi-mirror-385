## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . xmlns import xmlns
## END_IMPORT

# --------------------------------------------------------------------
class Data(Element):
    TAG = 'data'
    def __init__(self,doc,node=None,version='1'):
        super(Data,self).__init__(doc,self.TAG,node=node,version=version)
        
    def addVersion(self,**kwargs):
        '''Add a `Version` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Version
            The added element
        '''
        return self.add(Version,**kwargs)
    def addVASSALVersion(self,**kwargs):
        '''Add a `VASSALVersion` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : VASSALVersion
            The added element
        '''
        return self.add(VASSALVersion,**kwargs)
    def addName(self,**kwargs):
        '''Add a `Name` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Name
            The added element
        '''
        return self.add(Name,**kwargs)
    def addDescription(self,**kwargs):
        '''Add a `Description` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Description
            The added element
        '''
        return self.add(Description,**kwargs)
    def addDateSaved(self,**kwargs):
        '''Add a `DateSaved` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : DateSaved
            The added element
        '''
        return self.add(DateSaved,**kwargs)
    def getVersion(self,single=True):
        '''Get all or a sole `Version` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Version` child, otherwise fail.
            If `False` return all `Version` children in this element
        
        Returns
        -------
        children : list
            List of `Version` children (even if `single=True`)
        '''
        return self.getAllElements(Version,single=single)
    def getVASSALVersion(self,single=True):
        '''Get all or a sole `VASSALVersion` element(s) from this

        Parameters
        ----------
        single : bool        
            If `True`, there can be only one `VASSALVersion` child,
            otherwise fail.  If `False` return all `VASSALVersion`
            children in this element
        
        Returns
        -------
        children : list
            List of `VASSALVersion` children (even if `single=True`)

        '''
        return self.getAllElements(VASSALVersion,single=single)
    def getName(self,single=True):
        return self.getAllElements(Name,single=single)
    def getDescription(self,single=True):
        '''Get all or a sole `Description` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `Description` child,
            otherwise fail.  If `False` return all `De` children in
            this element
        
        Returns
        -------
        children : list
            List of `De` children (even if `single=True`)

        '''
        return self.getAllElements(Description,single=single)
    def getDateSaved(self,single=True):
        '''Get all or a sole `DateSaved` element(s) from this

        Parameters
        ----------
        single : bool
            If `True`, there can be only one `DateSaved` child, otherwise fail.
            If `False` return all `DateSaved` children in this element
        
        Returns
        -------
        children : list
            List of `DateSaved` children (even if `single=True`)
        '''
        return self.getAllElements(DateSaved,single=single)
    
registerElement(Data)

# --------------------------------------------------------------------
class DataElement(Element):
    def __init__(self,data,tag,node=None,**kwargs):
        super(DataElement,self).__init__(data,tag,node=node,**kwargs)

    def getData(self):
        return self.getParent(Data)

# --------------------------------------------------------------------
class Version(DataElement):
    TAG = 'version'
    def __init__(self,data,node=None,version=''):
        super(Version,self).__init__(data,self.TAG,node=node)
        if node is None:
            self.addText(version)

registerElement(Version)

# --------------------------------------------------------------------
class Extra1(DataElement):
    TAG = 'extra1'
    def __init__(self,data,node=None,extra=''):
        super(Extra1,self).__init__(data,self.TAG,node=node)
        if node is None:
            self.addText(extra)

registerElement(Extra1)

# --------------------------------------------------------------------
class Extra2(DataElement):
    TAG = 'extra2'
    def __init__(self,data,node=None,extra=''):
        super(Extra2,self).__init__(data,self.TAG,node=node)
        if node is None:
            self.addText(extra)

registerElement(Extra2)

# --------------------------------------------------------------------
class VASSALVersion(DataElement):
    TAG = 'VassalVersion'
    def __init__(self,data,node=None,version='3.6.7'):
        super(VASSALVersion,self).__init__(data,self.TAG,node=node)
        if node is None:
            self.addText(version)

registerElement(VASSALVersion)

# --------------------------------------------------------------------
class Name(DataElement):
    TAG = 'name'
    def __init__(self,data,node=None,name=''):
        super(Name,self).__init__(data,self.TAG,node=node)
        if node is None:
            self.addText(name)
            
registerElement(Name)

# --------------------------------------------------------------------
class Description(DataElement):
    TAG = 'description'
    def __init__(self,data,node=None,description=''):
        super(Description,self).__init__(data,self.TAG,node=node)
        if node is None:
            self.addText(description)

registerElement(Description)

# --------------------------------------------------------------------
class DateSaved(DataElement):
    TAG = 'dateSaved'
    def __init__(self,data,node=None,milisecondsSinceEpoch=-1):
        super(DateSaved,self).__init__(data,self.TAG,node=node)
        if node is None:
            from time import time
            s = f'{int(time()*1000)}' if milisecondsSinceEpoch < 0 else \
                str(milisecondsSinceEpoch)
            self.addText(s)
            
registerElement(DateSaved)

# --------------------------------------------------------------------
class ModuleData(Element):

    def __init__(self,root=None):
        '''Construct from a DOM object, if given, otherwise make new'''
        #from xml.dom.minidom import Document
        super(ModuleData,self).__init__(None,'',None)
        
        self._root = root
        self._tag  = 'moduledata'
        if self._root is None:
            self._root = xmlns.Document()

        self._node = self._root

    def addData(self,**kwargs):
        '''Add a `Data` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Data
            The added element
        '''
        return Data(self,**kwargs)

    def getData(self):
        return Data(self,
                    node=self._root.getElementsByTagName(Data.TAG)[0])

    def encode(self):
        return self._root.toprettyxml(indent=' ',
                                      encoding="UTF-8",
                                      standalone=False)


#
# EOF
#
