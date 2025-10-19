## BEGIN_IMPORTS
from pywargame.common import VerboseGuard
from . base import DomInspect
## END_IMPORTS

# --------------------------------------------------------------------        
class ZTStack:
    def __init__(self,x,y,ids,flp,rot):
        self._x    = x
        self._y    = y
        self._ids  = ids
        self._flip = flp
        self._rot  = rot

    def translate(self,dx,dy):
        self._x += dx
        self._y += dy

    def scale(self,f):
        self._x *= f
        self._y *= f
    
        
# --------------------------------------------------------------------        
class ZTLayout(DomInspect):
    def __init__(self,elem):
        self._name    = self._get_attr(elem,'board')
        self._left    = float(self._get_attr(elem,'left',  -1))
        self._top     = float(self._get_attr(elem,'top',   -1))
        self._right   = float(self._get_attr(elem,'right', -1))
        self._bottom  = float(self._get_attr(elem,'bottom',-1))
        self._visible = self._get_attr(elem,'visible','true')=='true'

        self._stacks  = [self.parse_stack(s)
                         for s in self._find_children(elem,'counter','stack')]

    @property
    def ulx(self):
        return self._left
    
    @property
    def lrx(self):
        return self._right
    
    @property
    def uly(self):
        return self._top
    
    @property
    def lry(self):
        return self._bottom

    @property
    def left(self):
        return int(self._left)

    @property
    def top(self):
        return int(self._top)
    
    @property
    def width(self):
        return int(self._right - self._left+.5)

    @property
    def height(self):
        return int(self._bottom - self._top+.5)
    
    def parse_stack(self,elem):
        x   = float(self._get_attr(elem,'x',0))
        y   = float(self._get_attr(elem,'y',0))
        # We ignore the `rot` and `Side` attributes for now
        # More difficult to propagate to the states, which are handled
        # in VSav.  Could perhaps add a mapping from traits to states
        # when the traits are flattened there. 
        ids = []
        flp = []
        rot = [] 
        if elem.tagName == 'counter':
            ids.append(int(self._get_attr(elem,'id',-1)))
            flp.append(self._get_attr(elem,'side','')=='Back')
            rot.append(int(self._get_attr(elem,'rot',0)))
        else:
            ids.extend([int(self._get_attr(c,'id',-1))
                        for c in self._find_children(elem,'counter')])
            flp.extend([self._get_attr(c,'side','')=='Back'
                        for c in self._find_children(elem,'counter')])
            rot.extend([int(self._get_attr(c,'rot',0))
                        for c in self._find_children(elem,'counter')])

        return ZTStack(x,y,ids,flp,rot)
            
    def translate(self,dx,dy):
        self._left   += dx
        self._right  += dx
        self._top    += dy
        self._bottom += dy
        for s in self._stacks:
            s.translate(dx,dy)

    def scale(self,f):
        self._left   *= f
        self._right  *= f
        self._top    *= f
        self._bottom *= f
        for s in self._stacks:
            s.scale(f)

    def __str__(self):
        return f'Layout "{self._name}" ({len(self._stacks)}: {self.ulx},{self.uly},{self.lrx},{self.lry}'
            
# --------------------------------------------------------------------        
class ZTScenario(DomInspect):
    def __init__(self,file):        
        from xml.dom.minidom import parse
        from pathlib import Path
        
        with VerboseGuard(f'Got a scenario {file}') as v:
            self._dom = parse(file)

            p = Path(file if isinstance(file,str) else file.name)

            self._file = p.stem
            self._root = self._dom.firstChild
            self._game = self._get_attr(self._root,'game-box')
            self._name = self._get_attr(self._root,'scenario-name')
            self._desc = self._get_attr(self._root,'scenario-description','')
            self._copy = self._get_attr(self._root,'scenario-copyright','')

            self._layouts = [self.parse_layout(elem)
                             for elem in
                             self._root.getElementsByTagName('layout')]

            self.ulx = None
            self.uly = None
            self.lrx = None
            self.lry = None
            
            v(f'Bounding box: {self.bounding_box}')

    def parse_layout(self,elem):
        return ZTLayout(elem)

    def translate(self,dx,dy):
        with VerboseGuard(f'Translating scenario by {dx},{dy}'):
            self.ulx = None
            self.uly = None
            self.lrx = None
            self.lry = None
            
            for l in self._layouts:
                l.translate(dx,dy)

    def scale(self,f):
        with VerboseGuard(f'Scaling scenario by {f}'):
            self.ulx = None
            self.uly = None
            self.lrx = None
            self.lry = None
            
            for l in self._layouts:
                l.scale(f)
                
    def on_map(self,name):
        return any([l._name == name for l in self._layouts])

    def map_layout(self,name):
        return [l for l in self._layouts if l._name == name]

    def calc_bounding_box(self,name=None):
        layouts = self._layouts if name is None else self.map_layout(name)
        ulx     = int(min([l.ulx for l in layouts])-.5)
        uly     = int(min([l.uly for l in layouts])-.5)
        lrx     = int(max([l.lrx for l in layouts])+.5)
        lry     = int(max([l.lry for l in layouts])+.5)
        return ulx,uly,lrx,lry
        
    @property 
    def bounding_box(self):
        '''Cache calculations'''
        if self.ulx is None or \
           self.uly is None or \
           self.lrx is None or \
           self.lry is None:
            self.ulx = int(min([l.ulx for l in self._layouts])-.5)
            self.uly = int(min([l.uly for l in self._layouts])-.5)
            self.lrx = int(max([l.lrx for l in self._layouts])+.5)
            self.lry = int(max([l.lry for l in self._layouts])+.5)

        return self.ulx,self.uly,self.lrx,self.lry

    def __str__(self):
        return f'Scenario "{self._name}": {self._desc}'+'\n'+\
            '\n'.join([str(l) for l in self._layouts])
        
    @property
    def width(self):
        x1,_,x2,_ = self.bounding_box
        return x2-x1 
    @property
    def height(self):
        _,y1,_,y2 = self.bounding_box
        return y2-y1
   
    
#
# EOF
#
