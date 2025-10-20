## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . command import *
from . trait import Trait
from . traits import *
## END_IMPORT

# --------------------------------------------------------------------
#
# Traits of this kind of object are
#
# - Evaluated from the start of the list to the end of the list,
#   skipping over report and trigger traits
# - Then evaluated from the end of the list to the start, only
#   evaluating report and trigger traits
# - The list _must_ end in a BasicTrait
#
# Traits are copied when making a copy of objects of this class, and
# are done so using a full decoding and encoding.  This means that
# copying is a bit susceptible to expansions of the strings of the traits,
# in particular if they contain special characters such as ',' or '/'.
#
class WithTraits(Element):
    UNIQUE = ['entryName']
    def __init__(self,parent,tag,node=None,traits=[],**kwargs):
        '''Base class for things that have traits

        Parameters
        ----------
        parent : Element
            Parent to add this to
        node : xml.minidom.Element
            If not None, XML element to read definition from.
            Rest of the arguments are ignored if not None.
        traits : list of Trait objects
            The traits to set on this object
        kwargs : dict
            More attributes to set on element
        '''
        super(WithTraits,self).__init__(parent,tag,node=node,**kwargs)
        if node is None: self.setTraits(*traits)
        
    def addTrait(self,trait):
        '''Add a `Trait` element to this.  Note that this re-encodes
        all traits.

        Parameters
        ----------
        trait : Trait
            The trait to add 
        '''
        traits = self.getTraits()
        traits.append(trait)
        self.setTraits(*traits)


    def getTraits(self):
        '''Get all element traits as objects.  This decodes the trait
        definitions.  This is useful if we have read the element from
        the XML file, or similar.

        Note that the list of traits returned are _not_ tied to the
        XML nodes content.  Therefore, if one makes changes to the list,
        or to elements of the list, and these changes should be
        reflected in this object, then we _must_ call

            setTraits(traits)

        with the changed list of traits. 

        Returns
        -------
        traits : list of Trait objects
            The decoded traits

        '''
        code = self._node.childNodes[0].nodeValue
        return self.decodeAdd(code)

    def encodedStates(self):
        from re import split

        code = self._node.childNodes[0].nodeValue
        cmd, iden, typ, sta = split(fr'(?<!\\)/',code) #code.split('/')

        return sta

    def decodeStates(self,code,verbose=False):
        from re import split
        
        newstates, oldstates = split(fr'(?<!\\)/',code)#code.split('/')
        
        splitit = lambda l : \
            [s.strip('\\').split(';') for s in l.split(r'	')]

        newstates = splitit(newstates)
        oldstates = splitit(oldstates)
        
        traits = self.getTraits()

        if len(traits) != len(newstates):
            print(f'Piece has {len(traits)} traits but got '
                  f'{len(newstates)} states')
        
        for trait, state in zip(traits,newstates):
            trait._state = state;
            # print(trait.ID)
            # for n,s in zip(trait._snames,trait._state):
            #     print(f'  {n:30s}: {s}')

        self.setTraits(*traits)
            
    def copyStates(self,other,verbose=False):
        straits = other.getTraits()
        dtraits = self.getTraits()

        matches = 0
        for strait in straits:
            if len(strait._state) < 1:
                continue

            cand = []
            ttrait = None
            for dtrait in dtraits:
                if dtrait.ID == strait.ID:
                    cand.append(dtrait)

            if verbose and len(cand) < 1:
                print(f'Could not find candidate for {strait.ID}')
                continue

            if len(cand) == 1:
                ttrait = cand[0]

            else:
                # print(f'Got {len(cand)} candidiate targets {strait.ID}')

                best  = None
                count = 0
                types = strait._type
                for c in cand:
                    cnt = sum([ct == t for ct,t in zip(c._type, types)])
                    if cnt > count:
                        best = c
                        count = cnt
                        
                if verbose and best is None:
                    print(f'No candidate for {strait.ID} {len(again)}')

                if verbose and count+2 < len(types):
                    print(f'Ambigious candidate for {strait.ID} '
                          f'({count} match out of {len(types)})')
                    #print(best._type)
                    #print(types)
                       
                ttrait = best

            if ttrait is None:
                continue

            ttrait._state = strait._state
            matches += 1
            # print(ttrait.ID)
            # for n,s in zip(ttrait._snames,ttrait._state):
            #     print(f'  {n:30s}: {s}')

        if verbose:
            print(f'Got {matches} matches out of {len(dtraits)}')

        self.setTraits(*dtraits)
            
            
    def decodeAdd(self,code,verbose=False):
        '''Try to decode make a piece from a piece of state code'''
        from re import split
        
        cmd, iden, typ, sta = split(fr'(?<!\\)/',code) #code.split('/')
        # print(cmd,iden,typ,sta)
        
        types               = typ.split(r'	')
        states              = sta.split(r'	')
        types               = [t.strip('\\').split(';') for t in types]
        states              = [s.strip('\\').split(';') for s in states]
        traits              = []
        
        for t, s in zip(types,states):
            tid   = t[0]
            trem  = t[1:]
            known = False
            
            for c in Trait.known_traits:
                t = c.take(tid,trem,s) # See if we have it
                if t is not None:
                    traits.append(t)  # Got it
                    known = True
                    break
                
            if not known:
                print(f'Warning: Unknown trait {tid}')

        return traits

    def encodeAdd(self,*traits,iden='null',verbose=False):
        '''Encodes type and states'''
        if len(traits) < 1: return ''
        
        last = traits[-1]
        # A little hackish to use the name of the class, but needed
        # because of imports into patch scripts.
        lastBasic = isinstance(last,BasicTrait) or \
            last.__class__.__name__.endswith('BasicTrait')
        lastStack = isinstance(last,StackTrait) or \
            last.__class__.__name__.endswith('StackTrait')
        if not lastBasic and not lastStack:
            from sys import stderr
            print(f'Warning - last trait NOT a Basic(Stack)Trait, '
                  f'but a {type(last)}',
                  file=stderr)
            
        types = []
        states = []
        for trait in traits:
            if trait is None:
                print(f'Trait is None (traits: {traits})')
                continue
            tpe, state = trait.encode()
            types.append(tpe)
            states.append(state)

        tpe   = WithTraits.encodeParts(*types)
        state = WithTraits.encodeParts(*states)
        add   = AddCommand(str(iden),tpe,state)
        return add.cmd
        
    
    def setTraits(self,*traits,iden='null'):
        '''Set traits on this element.  This encodes the traits into
        this object.
        
        Parameters
        ----------
        traits : tuple of Trait objects
            The traits to set on this object.
        iden : str
            Identifier

        '''
        add = self.encodeAdd(*traits,iden=iden)
        if self._node is None:
            # from xml.dom.minidom import Element, Text
            self._node = xmlns.Element(self.TAG)
            self._node.appendChild(xmlns.Text())
            
        if len(self._node.childNodes) < 1:
            self.addText('')
        self._node.childNodes[0].nodeValue = add

    def removeTrait(self,ID,key=None,value=None,verbose=False):
        '''Remove a trait from this object.

        Parameters
        ----------
        ID : str
            The type of trait to remove.  Must be a valid
            ID of a class derived from Trait.
        key : str
            Optional key to inspect to select trait that has 
            this key and the traits key value is the argument value,
        value :
            If specified, then only traits which key has this value
            are removed
        verbose : bool
            Be verbose if True

        Returns
        -------
        trait : Trait
            The removed trait or None
        '''
        traits = self.getTraits()
        trait  = Trait.findTrait(traits,ID,key,value,verbose)
        if trait is not None:
            traits.remove(trait)
            self.setTraits(traits)
        return trait

    def addTraits(self,*toadd):
        '''Add traits to this.  Note that this will
        decode and reencode the traits.  Only use this when
        adding traits on-mass.  Repeated use of this is inefficient.

        This member function takes care to push any basic trait to
        the end of the list.

        The added traits will not override existing triats. 

        Paramters
        ---------
        toAdd : tuple of Trait objects
            The traits to add 

        '''
        traits = self.getTraits()
        basic  = Trait.findTrait(traits,BasicTrait.ID)
        if basic:
            traits.remove(basic)
        traits.extend(toAdd)
        if basic:
            traits.append(basic)
        self.setTraits(traits)
        
        
    @classmethod
    def encodeParts(cls,*parts):
        '''Encode parts of a full piece definition

        Each trait (VASSAL.counter.Decorator,
        VASSAL.counter.BasicPiece) definition or state is separated by
        a litteral TAB character.  Beyond the first TAB separator,
        additional escape characters (BACKSLAH) are added in front of
        the separator.  This is to that VASSAL.utils.SequenceDecoder
        does not see consequitive TABs as a single TAB.
        '''
        ret = ''
        sep = r'	'
        for i, p in enumerate(parts):
            if i != 0:
                ret += '\\'*(i-1) + sep
            ret += str(p)

        return ret
        
        
    def cloneNode(self,parent):
        '''This clones the underlying XML node.

        Parameters
        ----------
        parent : Element
            The element to clone this element into

        Returns
        -------
        copy : xml.minidom.Element
            The newly created clone of this object's node
        '''
        copy = self._node.cloneNode(deep=True)
        if parent is not None:
            parent._node.appendChild(copy)
        else:
            print('WARNING: No parent to add copy to')
        return copy

    def print(self,file=None,recursive=1024,indent=''):
        if file is None:
            from sys import stdout
            file = stdout
            
        from textwrap import indent as i
        
        if recursive <= 1:
            n = len(self.getTraits())
            if n > 1:
                print(i(f'  {n} traits',indent),file=file)
            return
        
            
        from io import StringIO


        stream = StringIO()
        traits = self.getTraits()
        for trait in traits:
            trait.print(stream)

        s = i(stream.getvalue().rstrip(), '  ')
        print(i(s,indent), file=file)
        
    
# --------------------------------------------------------------------
class DummyWithTraits(WithTraits):
    TAG = 'dummy'
    def __init__(self,parent,node=None,traits=[]):
        '''An empty element.  Used when making searching'''
        super(DummyWithTraits,self).__init__(tag       = self.TAG,
                                             parent    = parent,
                                             node      = node,
                                             traits    = traits)
        if parent is not None:
            parent.remove(self)


registerElement(DummyWithTraits)

# --------------------------------------------------------------------
class WithTraitsSlot(WithTraits):
    def __init__(self,
                 parent,
                 tag,
                 node           = None,
                 entryName      = '',
                 traits         = [],
                 gpid           = 0,
                 height         = 72,
                 width          = 72,
                 icon           = ''):
        '''A piece slot.  Used all the time.

        Parameters
        ----------
        parent : Element
            Parent to add this to
        node : xml.minidom.Element
            If not None, XML element to read definition from.
            Rest of the arguments are ignored if not None.
        entryName : str
            Name of this
        traits : list of Trait objects
            The traits to set on this object
        gpid : int
            Global Piece identifier. If 0, will be set by Game
        height : int
            Height size of the piece (in pixels)
        width : int
            Width size of the piece (in pixels)
        icon : str
            Piece image file name within 'image' sub-dir of archive
        '''
        super().\
            __init__(parent,
                     tag,
                     node      = node,
                     traits    = traits,
                     entryName = entryName,
                     gpid      = gpid,
                     height    = height,
                     width     = width,
                     icon      = icon)

    
    def _clone(self,cls,parent):
        '''Adds copy of self to parent, possibly with new GPID'''
        ## BEGIN_IMPORT
        from . game import Game
        ## END_IMPORT
        game  = self.getParentOfClass([Game])
        gpid  = game.nextPieceSlotId()
        #opid  = int(self.getAttribute('gpid'))
        #print(f'Using GPID={gpid} for clone {opid}')
        
        node  = self.cloneNode(parent)
        piece = cls(parent,node=node)
        piece.setAttribute('gpid',gpid)
        
        traits = piece.getTraits()
        for trait in traits:
            if isinstance(trait,BasicTrait):
                trait['gpid'] = gpid

        piece.setTraits(*traits)
        return piece

    def print(self,file=None,recursive=1024,indent=''):
        if file is None:
            from sys import stdout
            file = stdout
        from textwrap import indent as i

        print(i(f'{type(self).__name__} {self["entryName"]}'+'\n'
                f' gpid  : {self["gpid"]}'+'\n'
                f' height: {self["height"]}'+'\n'
                f' width : {self["width"]}'+'\n'
                f' icon  : {self["icon"]}',indent),
              file = file)

        super().print(file=file,
                      recursive=recursive-1,
                      indent=indent)

# --------------------------------------------------------------------
class PieceSlot(WithTraitsSlot):
    TAG = Element.WIDGET+'PieceSlot'
    def __init__(self,
                 parent,
                 node           = None,
                 entryName      = '',
                 traits         = [],
                 gpid           = 0,
                 height         = 72,
                 width          = 72,
                 icon           = ''):
        '''A piece slot.  Used all the time.

        Parameters
        ----------
        parent : Element
            Parent to add this to
        node : xml.minidom.Element
            If not None, XML element to read definition from.
            Rest of the arguments are ignored if not None.
        entryName : str
            Name of this
        traits : list of Trait objects
            The traits to set on this object
        gpid : int
            Global Piece identifier. If 0, will be set by Game
        height : int
            Height size of the piece (in pixels)
        width : int
            Width size of the piece (in pixels)
        icon : str
            Piece image file name within 'image' sub-dir of archive
        '''
        super().\
            __init__(parent,
                     self.TAG,
                     node      = node,
                     traits    = traits,
                     entryName = entryName,
                     gpid      = gpid,
                     height    = height,
                     width     = width,
                     icon      = icon)

    
    def clone(self,parent):
        return self._clone(PieceSlot,parent)
        
        
registerElement(PieceSlot)

# --------------------------------------------------------------------
class CardSlot(WithTraitsSlot):
    TAG = Element.WIDGET+'CardSlot'
    def __init__(self,
                 parent,
                 node           = None,
                 entryName      = '',
                 traits         = [],
                 gpid           = 0,
                 height         = 72,
                 width          = 72,
                 icon           = ''):        
        '''A card slot.  Used all the time.  It is essentially the
        same as a PieceSlot, though a `MaskTrait` is added (with
        default settings), if no such trait is present (to-be-done)

        Parameters
        ----------
        parent : Element
            Parent to add this to
        node : xml.minidom.Element
            If not None, XML element to read definition from.
            Rest of the arguments are ignored if not None.
        entryName : str
            Name of this
        traits : list of Trait objects
            The traits to set on this object
        gpid : int
            Global Piece identifier. If 0, will be set by Game
        height : int
            Height size of the card (in pixels)
        width : int
            Width size of the card (in pixels)
        icon : str
            Card image file name within 'image' sub-dir of archive

        '''
        super().\
            __init__(parent,
                     self.TAG,
                     node      = node,
                     traits    = traits,
                     entryName = entryName,
                     gpid      = gpid,
                     height    = height,
                     width     = width,
                     icon      = icon)

    def clone(self,parent):
        return self._clone(CardSlot,parent)
        
registerElement(CardSlot)
        
# --------------------------------------------------------------------
class Prototype(WithTraits):
    TAG = Element.MODULE+'PrototypeDefinition'
    UNIQUE = ['name']
    def __init__(self,cont,node=None,
                 name          = '',
                 traits        = [],
                 description   = ''):
        '''A prototype.  Used all the time.

        Parameters
        ----------
        cont : Element
            Parent to add this to
        node : xml.minidom.Element
            If not None, XML element to read definition from.
            Rest of the arguments are ignored if not None.
        name : str
            Name of this
        traits : list of Trait objects
            The traits to set on this object
        description : str
            A free-form description of this prototype
        '''
        super(Prototype,self).__init__(cont,self.TAG,node=node,
                                       traits      = traits,
                                       name        = name,
                                       description = description)
    
    def print(self,file=None,recursive=1024,indent=''):
        if file is None:
            from sys import stdout
            file = stdout
        from textwrap import indent as i

        print(i(f'Prototype {self["name"]}'+'\n'
                f' description: {self["description"]}',indent),
              file = file)
        
        super(Prototype,self).print(file=file,
                                    indent=indent,
                                    recursive=recursive-1)
        
registerElement(Prototype)

#
# EOF
#
