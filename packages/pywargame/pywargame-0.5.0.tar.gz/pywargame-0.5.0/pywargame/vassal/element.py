## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . xmlns import xmlns
## END_IMPORT

# ====================================================================
class Element:
    BUILD  = 'VASSAL.build.'
    MODULE = BUILD  + 'module.'
    WIDGET = BUILD  + 'widget.'
    FOLDER = MODULE + 'folder.'
    MAP    = MODULE + 'map.'    
    PICKER = MAP    + 'boardPicker.'
    BOARD  = PICKER + 'board.'
    known_tags   = {}
    unique_attrs = {}
    
    def __init__(self,parent,tag,node=None,**kwargs):
        '''Create a new element

        Parameters
        ----------
        parent : Element
            Parent element to add this element to
        tag : str
            Element tag
        node : xml.dom.Node
            If not None, then read attributes from that. Otherwise
            set elements according to kwargs
        kwargs : dict
            Attribute keys and values.  Only used if node is None
        '''
        #from xml.dom.minidom import Document
        
        if parent is not None:
            self._tag  = tag                
            self._root = (parent if isinstance(parent,xmlns.Document) else
                          parent._root)
            self._node = (node if node is not None else
                          parent.addNode(tag,**kwargs))
        else:
            self._root = None
            self._node = None
            self._tag  = None

    # ----------------------------------------------------------------
    @classmethod
    def _make_unique(cls,tag,*values):
        return tag + ('_'+'_'.join(values) if len(values)>0 else '')
    
    def _unique(self):
        uattr = Element.unique_attrs.get(self._tag,[])
        return self._make_unique(self._tag,
                                 *[self.getAttribute(a) for a in uattr])
    
    def __hash__(self):
        return hash(self._unique())
    
    def __eq__(self,other):
        '''Equality comparison - check if to elements are the same.

        This is based on the tag of the elements first, then on the
        attributes.  However, not all attributes should be compared
        for equality - only thise that are meant to be unique.

        '''
        #print(f'Compare {self} to {other} ({self._tag},{other._tag})')
        if not isinstance(other,Element):
            return False
        return self.__hash__() == other.__hash__()
        #if self._tag != other._tag:
        #    return False

        # to be done
        #
        # uattr = Element.unique_attrs[self._tag]
        # attr  = self .getAttributes()
        # oattr = other.getAttributes()
        
        return True

        
    # ----------------------------------------------------------------
    # Attributes
    def __contains__(self,key):
        '''Check if element has attribute key'''        
        return self.hasAttribute(key)
    
    def __getitem__(self,key):
        '''Get attribute key value'''
        return self.getAttribute(key)

    def __setitem__(self,key,value):
        '''Set attribute key value'''
        self.setAttribute(key,value)

    def hasAttribute(self,k):
        '''Check if element has attribute '''
        return self._node.hasAttribute(k)

    def getAttribute(self,k):
        '''Get attribute key value'''
        return self._node.getAttribute(k)
        
    def setAttribute(self,k,v):
        '''Set attribute key value'''
        self._node.setAttribute(k,str(v).lower()
                                if isinstance(v,bool) else str(v))
        
    def setAttributes(self,**kwargs):
        '''Set attributes to dictionary key and value'''
        for k,v in kwargs.items():
            self.setAttribute(k,v)

    def getAttributes(self):
        '''Get attributes as dict'''
        return self._node.attributes

    # ----------------------------------------------------------------
    # Plain nodes
    def getChildren(self):
        '''Get child nodes (xml.dom.Node)'''
        return self._node.childNodes

    # ----------------------------------------------------------------
    # Getters
    #
    # First generics 
    def getAsDict(self,tag='',key=None,enable=True):
        '''Get elements with a specific tag as a dictionary
        where the key is given by attribute key'''
        cont = self._node.getElementsByTagName(tag)
        if not enable or key is None:
            return cont

        return {e.getAttribute(key): e for e in cont}

    def getAsOne(self,tag='',single=True):
        '''Get elements with a specific tag, as a list.
        If single is true, then assume we only have one such
        child element, or fail.'''
        cont = self._node.getElementsByTagName(tag)
        if single and len(cont) != 1:
            return None
        return cont
    
    def getElementsByKey(self,cls,key='',asdict=True):
        '''Get elments of a specific class as a dictionary,
        where the key is set by the key attribute.'''
        cont = self.getAsDict(cls.TAG,key,asdict)
        if cont is None: return None
        
        if not asdict: return [cls(self,node=n) for n in cont]

        return {k : cls(self,node=n) for k, n in cont.items()}

    def getAllElements(self,cls,single=True):
        '''Get elements with a specific tag, as a list.  If single is
        true, then assume we only have one such child element, or
        fail.

        If `cls` is None, then return _all_ child elements. 

        '''
        #from xml.dom.minidom import Text, Element as XMLElement
        if cls is None:
            ret = []
            for node in self.getChildren():
                if isinstance(node,xmlns.Text):
                    continue
                
                if not hasattr(node,'tagName'):
                    print(f'Do not know how to deal with {type(node)}')
                    continue

                tag = node.tagName
                cls = Element.getTagClass(tag)
                if cls is None:
                    raise RuntimeError(f'No class reflection of tag {tag}')
                
                ret.append(cls(self,node=node))

            return ret
                           
        cont = self.getAsOne(cls.TAG,single=single)
        if cont is None: return None
        return [cls(self,node=n) for n in cont]

    def getSpecificElements(self,cls,key,*names,asdict=True):
        '''Get all elements of specific class and that has the
        attribute key, and the attribute value is in names

        '''
        cont = self.getAsOne(cls.TAG,single=False)
        cand = [cls(self,node=n) for n in cont
                if n.getAttribute(key) in names]
        if asdict:
            return {c[key] : c for c in cand}
        return cand
    
    def getParent(self,cls=None,checkTag=True):
        if self._node.parentNode is None:
            return None
        if cls is None:
            cls = self.getTagClass(self._node.parentNode.tagName)
            checkTag = False
        if cls is None:
            return None
        if checkTag and self._node.parentNode.tagName != cls.TAG:
            return None
        return cls(self,node=self._node.parentNode)

    def getParentOfClass(self,cls):
        '''Searches back until we find the parent with the right
        class, or none
        '''
        try:
            iter(cls)
        except:
            cls = [cls]
        t = {c.TAG: c for c in cls}
        p = self._node.parentNode
        while p is not None:
            c = t.get(p.tagName,None)
            if c is not None: return c(self,node=p)
            p = p.parentNode
        return None

    @classmethod
    def getTagClass(cls,tag):
        '''Get class corresponding to the tag'''
        # if tag not in cls.known_tags: return None;
        # Older VASSAL may have funny tag-names
        return cls.known_tags.get(tag,None)
        
    # ----------------------------------------------------------------
    # Adders
    def addNode(self,tag,**attr):
        '''Add a note to this element

        Parameters
        ----------
        tag : str
            Node tag name
        attr : dict
            Attributes to set
        '''
        e = self._root.createElement(tag)
        if self._node: self._node.appendChild(e)

        for k, v in attr.items():
            e.setAttribute(k,str(v).lower() if isinstance(v,bool) else str(v))

        return e

    def addText(self,text):
        '''Add a text child node to an element'''
        t = self._root.createTextNode(text)
        self._node.appendChild(t)
        return t

    def hasText(self):
        return self._node.firstChild is not None and \
            self._node.firstChild.nodeType == self._node.firstChild.TEXT_NODE
        
    def getText(self):
        '''Get contained text node content'''
        if self._node.firstChild is None or \
           self._node.firstChild.nodeType != self._node.firstChild.TEXT_NODE:
            return ''
        return self._node.firstChild.nodeValue

    def setText(self,txt):
        '''Set contained text node content'''
        if self._node.firstChild is None or \
           self._node.firstChild.nodeType != self._node.firstChild.TEXT_NODE:
            return 
        self._node.firstChild.nodeValue = txt
    

    def add(self,cls,**kwargs):
        '''Add an element and return wrapped in cls object'''
        return cls(self,node=None,**kwargs)

    def append(self,elem):
        '''Append and element'''
        if self._node.appendChild(elem._node):
            return elem
        return False

    # ----------------------------------------------------------------
    def remove(self,elem):
        '''Remove an element'''
        try:
            self._node.removeChild(elem._node)
        except:
            return None
        return elem
    # ----------------------------------------------------------------
    def insertBefore(self,toadd,ref):
        '''Insert an element before another element'''
        try:
            self._node.insertBefore(toadd._node,ref._node)
        except:
            return None
        return toadd

    # ----------------------------------------------------------------
    def print(self,file=None,recursive=False,indent=''):
        '''Print this element, and possibly its child elements.

        If `file` is None, then print to stdout.  If `recursive` is
        `True`, then also print child elements.  If `recursive` is an
        integer, then print this many deep levels of child elements.

        '''
        if file is None:
            from sys import stdout
            file = stdout

        from io import StringIO
        from textwrap import indent as i

        stream = StringIO()
        
        print(f'Element TAG={self.TAG} CLS={self.__class__.__name__}',
              file=stream)
        attrs = self.getAttributes()
        #print(type(attrs))
        ln    = max([len(n) for n in attrs.keys()]+[0])
        for name,value in attrs.items():
            print(f' {name:{ln}s}: {value}',file=stream)

        if isinstance(recursive,bool):
            recursive = 1024 if recursive else 0# Large number
            
        if recursive > 1:
            for child in self.getAllElements(cls=None):
                child.print(file=stream,
                            recursive=recursive-1,
                            indent='  ')
        else:
            n = len(self.getChildren())
            if n > 0:
                print(f'  {n} child elements',file=stream)

        print(i(stream.getvalue(),indent).rstrip(),file=file)
            
            
        
# --------------------------------------------------------------------
class DummyElement(Element):
    def __init__(self,parent,node=None,**kwargs):
        '''A dummy element we can use to select elements of different
        classes

        '''  
        super(DummyElement,self).__init__(parent,'Dummy',node=node)

# --------------------------------------------------------------------
class ToolbarElement(Element):
    def __init__(self,
                 parent,
                 tag,
                 node         = None,
                 name         = '', # Toolbar element name
                 tooltip      = '', # Tool tip
                 text         = '', # Button text
                 icon         = '', # Button icon,
                 hotkey       = '', # Named key or key stroke
                 canDisable   = False,
                 propertyGate = '',
                 disabledIcon = '',
                 **kwargs):
        '''Base class for toolbar elements.

        Parameters
        ----------
        parent : Element
            Parent element if any
        tag : str
            Element tag
        node : XMLNode
            Possible node - when reading back
        name : str
            Name of element (user reminder).  If not set, and tooltip is set,
            set to tooltip
        toolttip : str        
            Tool tip when hovering. If not set, and name is set, then
            use name as tooltip.
        text : str
            Text of button
        icon : str
            Image path for button image
        hotkey : str
            Named key or key-sequence
        canDisable : bool
            If true, then the element can be disabled
        propertyGate : str        
            Name of a global property.  When this property is `true`,
            then this element is _disabled_.  Note that this _must_ be
            the name of a property - it cannot be a BeanShell
            expression.
        disabledIcon : str
            Path to image to use when the element is disabled.
        kwargs : dict
            Other attributes to set on the element
        '''
        if name == '' and tooltip != '': name    = tooltip
        if name != '' and tooltip == '': tooltip = name

        # Build arguments for super class 
        args = {
            'node':         node,
            'name':         name,
            'icon':         icon,
            'tooltip':      tooltip,
            'hotkey':       hotkey,
            'canDisable':   canDisable,
            'propertyGate': propertyGate,
            'disabledIcon': disabledIcon }
        bt = kwargs.pop('buttonText',None)
        # If the element expects buttonText attribute, then do not set
        # the text attribute - some elements interpret that as a
        # legacy name attribute,
        if bt is not None:
            args['buttonText'] = bt
        else:
            args['text']       = text
        args.update(kwargs)

        super(ToolbarElement,self).__init__(parent,
                                            tag,
                                            **args)
        # print('Attributes\n','\n'.join([f'- {k}="{v}"' for k,v in self._node.attributes.items()]))
        
#
# EOF
#
