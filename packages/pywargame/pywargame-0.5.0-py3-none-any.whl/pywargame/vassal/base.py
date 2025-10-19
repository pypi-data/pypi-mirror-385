# ====================================================================
# Key encoding
SHIFT      = 65
CTRL       = 130
ALT        = 520
CTRL_SHIFT = CTRL+SHIFT
ALT_SHIFT  = ALT+SHIFT
NONE       = '\ue004'
NONE_MOD   = 0
RIGHT      = "'" # 39
LEFT       = "%" # 37
DOWN       = "(" # 40
UP         = "&" # 38
PAGE_DOWN  = ''
PAGE_UP    = ''

# --------------------------------------------------------------------
def key(let,mod=CTRL):

    '''Encode a key sequence

    down  = 40,0
    up    = 38,0
    left  = 37,0
    right = 39,0

    Parameters
    ----------
    let : str
        Key code (Letter)
    mod : int
        Modifier mask
    '''
    if let is None:
        return f'{ord(NONE)},{NONE_MOD}'
    return f'{ord(let)},{mod}'

# --------------------------------------------------------------------
def named(name):
    '''Encode a named command
    '''
    return key(NONE)+','+name

# --------------------------------------------------------------------
#
def hexcolor(s):
    '''Encode a hex-color as triplet'''
    a = None
    if isinstance(s,str):
        s = s.replace('0x','').replace('#','')
        if len(s) == 3:
            r, g, b = [int(si,16)/16 for si in s]
        if len(s) == 4:
            r, g, b, a = [int(si,16)/16 for si in s]
        elif len(s) == 6:
            r = int(s[0:2],16) / 256
            g = int(s[2:4],16) / 256
            b = int(s[4:6],16) / 256
        elif len(s) == 8:
            r = int(s[0:2],16) / 256
            g = int(s[2:4],16) / 256
            b = int(s[4:6],16) / 256
            a = int(s[6:8],16) / 256
        else:
            raise RuntimeError('3,4,6, or 8 hexadecimal digits '
                               'for color string')
    elif isinstance(s,int):
        r = ((s >> 16) & 0xFF) / 256
        g = ((s >>  8) & 0xFF) / 256
        b = ((s >>  0) & 0xFF) / 256
    else:
        raise RuntimeError('Hex colour must be string or integer')

    if a is not None:
        rgba(int(r*256),int(g*256),int(b*256),int(a*256))
    return rgb(int(r*256),int(g*256),int(b*256))
    
# --------------------------------------------------------------------
# Colour encoding 
def rgb(r,g,b):
    '''Encode RGB colour

    Parameters
    ----------
    r : int
        Red channel
    g : int
        Green channel
    b : int
        Blue channel

    Returns
    -------
    colour : str
        RGB colour as a string
    '''
    return ','.join([str(r),str(g),str(b)])

# --------------------------------------------------------------------
def rgba(r,g,b,a):
    '''Encode RGBA colour

    Parameters
    ----------
    r : int
        Red channel
    g : int
        Green channel
    b : int
        Blue channel
    a : int
        Alpha channel
    
    Returns
    -------
    colour : str
        RGBA colour as a string
    '''
    return ','.join([str(r),str(g),str(b),str(a)])

# --------------------------------------------------------------------
def dumpTree(node,ind=''):
    '''Dump the tree of nodes

    Parameters
    ----------
    node : xml.dom.Node
        Node to dump
    ind : str
        Current indent 
    '''
    print(f'{ind}{node}')
    for c in node.childNodes:
        dumpTree(c,ind+' ')

# --------------------------------------------------------------------
def registerElement(cls,uniqueAttr=[],tag=None):
    '''Register a TAG to element class, as well as unique attributes
    to compare when comparing objects of that element class.

    '''
## BEGIN_IMPORT
    from . element import Element
## END_IMPORT

    # Get class-level definitions of UNIQUE
    uniqueCls = getattr(cls,'UNIQUE',None)
    if uniqueCls:
        try:
            iter(uniqueCls)
        except:
            uniqueCls = list(uniqueCls)
    else:
        uniqueCls = []    
        
    tagName                       = cls.TAG if tag is None else tag 
    Element.known_tags  [tagName] = cls
    Element.unique_attrs[tagName] = uniqueAttr+uniqueCls
    
        
#
# EOF
#
