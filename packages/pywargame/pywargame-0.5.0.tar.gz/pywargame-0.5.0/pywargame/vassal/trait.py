# ====================================================================
class Trait:
    known_traits = []
    def __init__(self):
        '''Base class for trait capture.
        
        Unlike the Element classes, this actually holds state that
        isn't reflected elsewhere in the DOM.  This means that the
        data here is local to the object.  So when we do::

        
            piece  = foo.getPieceSlots()[0]
            traits = p.getTraits()
            for trait in traits:
                if trait.ID == 'piece': 
                    trait["gpid"] = newPid
                    trait["lpid"] = newPid
                
        we do not actually change anything in the DOM.  To do that, we
        must add back _all_ the traits as::

            piece.setTraits(traits)
        
        We can add traits to a piece, like::

            piece.addTrait(MarkTrait('Hello','World'))
                
        But it is not particularly efficient.  Better to do
        (continuing from above)::

       
            traits.append(MarkTrait('Hello','World;)
            piece.setTraits(traits)
       
        
        .. include:: traits/README.md
           :parser: myst_parser.sphinx_
        
        '''
        self._type  = None
        self._state = None

    def setType(self,**kwargs):
        '''Set types.  Dictionary of names and values.  Dictonary keys
        defines how we access the fields, which is internal here.
        What matters is the order of the values.

        '''
        self._type   = list(kwargs.values())
        self._tnames = list(kwargs.keys())

    def setState(self,**kwargs):
        '''Set states.  Dictionary of names and values.  Dictonary keys
        defines how we access the fields, which is internal here.
        What matters is the order of the values.
        '''
        self._state  = list(kwargs.values())
        self._snames = list(kwargs.keys())

    def __getitem__(self,key):
        '''Look up item in either type or state'''
        try:
            return self._type[self._tnames.index(key)]
        except:
            pass
        return self._state[self._snames.index(key)]

    def __setitem__(self,key,value):
        '''Set item in either type or state'''
        try:
            self._type[self._tnames.index(key)] = value
            return
        except:
            pass
        self._state[self._snames.index(key)] = value

    def encode(self,term=False):
        '''
        returns type and state encoded'''
        t = self.encodeFields(self.ID,*self._type,term=term)
        s = self.encodeFields(*self._state,term=term)
        return t,s

    @classmethod
    def findTrait(cls,traits,ID,key=None,value=None,verbose=False):
        for trait in traits:
            if trait.ID != ID:
                continue
            if verbose:
                print(f' {trait.ID}')
            if key is None or value is None:
                if verbose:
                    print(f' Return {trait.ID}')
                return trait
            if verbose:
                print(f' Check {key}={value}: {trait[key]}')
            if trait[key] == value:
                return trait
        if verbose:
            print(f' Trait of type {ID} with {key}={value} not found')
        return None
        
    @classmethod
    def take(cls,iden,t,s):
        '''If the first part of the string t matches the ID, then take it.

        t and s are lists of strings.
        ''' 
        if iden != cls.ID: return None

        ret = cls()
        ret._type = t
        ret._state = s
        ret.check() # Check if we're reasonable, or raise
        #print(f'Took {iden} {cls}\n'
        #      f'  {ret._tnames}\n'
        #      f'  {ret._snames}')
        return ret

    def check(self):
        '''Implement if trait should check that all is OK when cloning'''
        pass

    @classmethod
    def encodeFields(cls,*args,term=False):
        return ';'.join([str(e).lower() if isinstance(e,bool) else str(e)
                         for e in args])+(';' if term else '')

    @classmethod
    def decodeFields(cls,s):
        from re import split
        return split(r'(?<!\\);',s)
        # return s.split(';') # Probably too simple-minded 

    @classmethod
    def encodeKeys(cls,keys,sep=','):
        return sep.join([k.replace(',','\\'+f'{sep}') for k in keys])
        
    @classmethod
    def decodeKeys(cls,keys,sep=','):
        from re import split
        ks = split(r'(?<!\\)'+f'{sep}',keys)
        return [k.replace('\\'+f'{sep}',f'{sep}') for k in ks]

    @classmethod
    def flatten(cls,traits,game=None,prototypes=None,verbose=False):
## BEGIN_IMPORT        
        from . traits import BasicTrait
## END_IMPORT        
        if prototypes is None:
            if game is None:
                print(f'Warning: Game or prototypes not passed')
                return None
            prototypes = game.getPrototypes()[0].getPrototypes()

        if len(traits) < 1: return None

        basic = None
        if traits[-1].ID == 'piece': # BasicTrait.ID:
            basic = traits.pop()

        if verbose:
            print(f'Piece {basic["name"]}')
            
        ret = cls._flatten(traits,prototypes,' ',verbose)
        ret.append(basic)

        return ret
    
    @classmethod
    def _flatten(cls,traits,prototypes,ind,verbose):
## BEGIN_IMPORT        
        from . traits import BasicTrait
        from . traits import PrototypeTrait
## END_IMPORT        
        '''Expand all prototype traits in traits'''
        ret = []
        for trait in traits:
            # Ignore recursive basic traits
            if trait.ID == BasicTrait.ID:
                continue
            # Add normal traits
            if trait.ID != PrototypeTrait.ID:
                if verbose:
                    print(f'{ind}Adding trait "{trait.ID}"')
                    
                ret.append(trait)
                continue

            # Find prototype
            name  = trait['name']
            proto = prototypes.get(name,None)
            if proto is None:
                if name != ' prototype':
                    print(f'{ind}Warning, prototype {name} not found')
                continue

            if verbose:
                print(f'{ind}Expanding prototype "{name}"')
                
            # Recursive call to add prototype traits (and possibly
            # more recursive calls 
            ret.extend(cls._flatten(proto.getTraits(), prototypes,
                                    ind+' ',verbose))

        return ret

    def print(self,file=None):
        if file is None:
            from sys import stdout
            file = stdout

        nt = max([len(i) for i in self._tnames]) if self._tnames else 0
        ns = max([len(i) for i in self._snames]) if self._snames else 0
        nw = max(nt,ns)

        print(f'Trait ID={self.ID}',file=file)
        print(f' Type:',            file=file)
        for n,v in zip(self._tnames,self._type):
            print(f'  {n:<{nw}s}: {v}',file=file)
        print(f' State:',           file=file)
        for n,v in zip(self._snames,self._state):
            print(f'  {n:<{nw}s}: {v}',file=file)
            
#
# EOF
#
