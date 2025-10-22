## BEGIN_IMPORTS
from . base import DomInspect, ZTImage
from . piece import ZTPiece
from pywargame.common import VerboseGuard
## END_IMPORTS

# --------------------------------------------------------------------
class ZTCounterImage(ZTImage):
    def __init__(self,elem,prefix):
        super().__init__(elem,prefix)
        self._mask_file = self._get_attr(elem,prefix+'mask-file')

    def read_image(self,zf):
        from wand.image import Image
        
        super().read_image(zf)
        
        self._mask = self._read_image(zf,self._mask_file,self._reso)
        if not self._mask:
            return

        
        # Get blue channel and make alpha mash from that 
        blue               = self._mask.channel_images['blue']
        blue.alpha_channel = 'copy'

        # Make copy of input image, and turn on alpha channel for that
        cp                 = Image(image=self._image)
        cp.alpha_channel   = 'set'

        # Compose with alpha of blue mask
        cp.composite(blue,operator='dst_in')

        # Set new image (now with alpha channel)
        self._orig  = self._image
        self._image = cp
        self._blue  = blue
 
# --------------------------------------------------------------------
class Face(DomInspect):
    def __init__(self,elem,prefix=''):
        with VerboseGuard(f'Got a face'):
            self._left    = int(self._get_attr(elem,prefix+'left',  -1))
            self._top     = int(self._get_attr(elem,prefix+'top',   -1))
            self._right   = int(self._get_attr(elem,prefix+'right', -1))
            self._bottom  = int(self._get_attr(elem,prefix+'bottom',-1))

    @property
    def width(self):
        return self._right - self._left

    @property
    def height(self):
        return self._bottom - self._top

    def get_tiles(self,image,dx,dy,reverse):
        with VerboseGuard(f'Get tiles from image {dx},{dy},{reverse}') as v:
            # Check ordering - ZunTzu goes row-wise first
            xl = self._left  if not reverse else self._right-dx
            xh = self._right if not reverse else self._left -dx
            x1 = self._left
            x2 = self._right
            yl = self._top
            yh = self._bottom
            sx = dx          if not reverse else -dx
            
            def crop(image,x,y):
                xx  = max(x,   x1)
                xxx = min(x+dx,x2)
                yy  = max(y,   yl)
                yyy = min(y+dy,yh)
                if xxx-xx < 0 or yyy-yy < 0:
                    return
                return image[xx:xxx,yy:yyy],x+dx//2,y+dy//2
            
            v(f'{x1} <= x+dx <= {x2} {yl} <= y+dy <= {yh}')
            return [crop(image,x,y)
                    for y in range(yl, yh-dy//2, dy)
                    for x in range(xl, xh-sx//2, sx)
                    ]

    def __str__(self):
        return f'Face: {self._left},{self._top},{self._right},{self._bottom}'
        
        
# --------------------------------------------------------------------
class Section(DomInspect):
    def __init__(self,elem,terrain):
        with VerboseGuard(f'Got an image section') as v:
            self._terrain = terrain
            self._card    = elem.tagName == 'card-section'
            self._type    = self._get_attr(elem,'type',0)
            self._rows    = int(self._get_attr(elem,'rows',1))
            self._cols    = int(self._get_attr(elem,'columns',1))
            self._shadow  = float(self._get_attr(elem,'shadow',
                                                 0 if terrain else 20))
            self._supply  = int(self._get_attr(elem,'supply',1))
            self._front   = Face(elem,'face-' if self._card else 'front-')
            self._back    = Face(elem,'back-')
            if self._terrain:
                self._shadow = 0;
                
            v(f'{"Terrain" if self._terrain else "Piece"} '
              f'{"Card" if self._card else "Piece"} '
              f'{self._type} {self._rows}x{self._cols} {self._supply}')

    @property
    def expected(self):
        return self._rows * self._cols * self._supply
    
    def get_tiles(self,image,face,reverse):
        with VerboseGuard(f'Get tiles from face {face}') as v:
            dx = int(face.width / self._cols+.5)
            dy = int(face.height / self._rows+.5)
            #v(f'Offsets are {dx},{dy}')
            if dx <= 0 or dy <= 0:
                return [(None,None,None)]*(self._cols*self._rows)

        return face.get_tiles(image,dx,dy,reverse)

    def make_pieces(self,
                    front_image,
                    back_image,
                    front_reso,
                    back_reso):
        with VerboseGuard(f'Make pieces from images {self._supply}. '
                          f'Expecting {self.expected}') as v:
            fronts = self.get_tiles(front_image, self._front, False)
            backs  = self.get_tiles(back_image,  self._back,  True)

            fs = ZTImage.target_dpi / front_reso
            bs = ZTImage.target_dpi / back_reso
            #v(f'Scales are {fs} and {bs} '
            #  f'({ZTImage.target_dpi} {front_reso},{back_reso})')
            
            def fixup(i,f,s):
                if not i:
                    return

                i.resize(int(f * i.width),int(f * i.height))
                c = i.clone()
                o = min(min(i.width,i.height) * s / 100 / 5,8)
                c.shadow(50,o,0,0)
                c.negate(channel='rgb')
                c.composite(i,int(o/4),int(o/4))
                return c
            
            def make(f,b):
                fi, fx, fy = f
                bi, bx, by = b
                #v(f' fx={fx} fy={fy} bx={bx} by={by}')
                x          = fs * fx if f else bs * bx
                y          = fs * fy if f else bs * by
                fi         = fixup(fi,fs,self._shadow)
                bi         = fixup(bi,bs,self._shadow)
                #v(f' x={x} y={y} w={fi.width} h={fi.height}')
                return [ZTPiece(fi,bi,int(x),int(y),self._terrain,self._card)
                        for _ in range(self._supply)]
        
            return sum([make(f,b) for f,b in zip(fronts,backs)],[])
            
    def __str__(self):
        return (f'  Section: {"terrain" if self._terrain else "piece"} '+
                f'{"card" if self._card else "piece"} '+
                f'{self._rows}x{self._cols} (x{self._supply}) '+
                f'type={self._type} shadow={self._shadow}%'+'\n'
                f'   Front: '+str(self._front)+'\n'
                f'   Back:  '+str(self._back))
        
# --------------------------------------------------------------------
class ZTCounterSheet(DomInspect):
    def __init__(self,elem):
        self._name    = self._get_attr(elem,'name')
        with VerboseGuard(f'Got a counter sheet "{self._name}"'):
            self._terrain = elem.tagName == 'terrain-sheet'
            self._name    = self._get_attr(elem,'name')
            self._front   = ZTCounterImage(elem,'front-')
            self._back    = ZTCounterImage(elem,'back-')

            self._sections = [self.parse_section(sc)
                              for sc in self._find_children(elem,
                                                            'counter-section',
                                                            'terrain-section')]
            self._cards    = [self.parse_card(cd)
                              for cd in self._find_children(elem,
                                                            'card-section')]
        
    def parse_section(self,section):
        return Section(section,self._terrain)


    def parse_card(self,card):
        return Section(card,self._terrain)
    
    def read_image(self,zf):
        self._front.read_image(zf)
        self._back .read_image(zf)

    def make_pieces(self):
        with VerboseGuard(f'Making pieces from counter sheet {self._name}') \
             as v:
            self._piece = sum([s.make_pieces(self._front._image,
                                             self._back._image,
                                             self._front._reso,
                                             self._back._reso)
                               for s in self._sections],[])
            self._card  = sum([c.make_pieces(self._front._image,
                                             self._back._image,
                                             self._front._reso,
                                             self._back._reso)
                               for c in self._cards],[])
            exp_piece = sum([s.expected for s in self._sections])
            exp_card  = sum([s.expected for s in self._cards])
            v(f'{len(self._piece)} pieces and {len(self._card)} cards, '
              f'expected {exp_piece} pieces and {exp_card} cards')

            for img, res in zip([self._front._image,self._back._image],
                                [self._front._reso, self._back._reso]):
                if not img:
                    continue

                s = ZTImage.target_dpi / res
                #v(f'scale image from {img.width}x{img.height} by {s}')
                img.resize(int(s*img.width+.5),
                           int(s*img.height+.5))

    @property
    def filename(self):
        return f'{self._name.replace(" ","_")}.{self._front._image.format.lower()}'

    @property
    def size(self):
        return self._front._image.width,self._front._image.height
        
    def __str__(self):
        return (f' Sheet: {self._name} '+
                f'{"terrain" if self._terrain else "pieces"} '+'\n'+
                f'  Front: '+str(self._front)+'\n'+
                f'  Back:  '+str(self._back)+
                ('\n' if len(self._sections)>0 else '')+
                '\n'.join([str(s) for s in self._sections])+
                ('\n' if len(self._cards)>0 else '')+
                '\n'.join([str(s) for s in self._cards])+
                ('\n' if len(self._piece)>0 else '')+
                '\n'.join([str(p) for p in self._piece])+
                ('\n' if len(self._card)>0 else '')+
                '\n'.join([str(c) for c in self._card]))
#
# EOF
#
