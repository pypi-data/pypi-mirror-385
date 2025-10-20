# --------------------------------------------------------------------
class DiceContext:
    def __init__(self,draw,darker=None):
        self._draw = draw
        self._darker = darker
        
        

    def __enter__(self):
        from wand.color import Color
        self._draw._draw.push()

        if self._darker:
            r, g, b = (self._draw._draw.fill_color.red_int8,
                       self._draw._draw.fill_color.green_int8,
                       self._draw._draw.fill_color.blue_int8)
            r *= self._darker
            g *= self._darker
            b *= self._darker
            #print(r,g,b)        
            self._draw._draw.fill_color = \
                Color(f'srgb({int(r)},{int(g)},{int(b)})')
        
        return self._draw

    def __exit__(self,*e):
        self._draw._draw.pop()

# --------------------------------------------------------------------
class DicePath:
    def __init__(self,draw):
        self._draw = draw

    def __enter__(self):
        self._draw._draw.path_start()
        return self

    def __exit__(self,*e):
        self._draw._draw.path_finish()

    def move(self,to):
        self._draw._draw.path_move(to=(self._draw.x(to[0]),
                                       self._draw.y(to[1])))
        
    def line(self,to):
        self._draw._draw.path_line(to=(self._draw.x(to[0]),
                                       self._draw.y(to[1])))

    def arc(self,to,r,cw=True):
        self._draw._draw.path_elliptic_arc(to=(self._draw.x(to[0]),
                                               self._draw.y(to[1])),
                                           radius=(self._draw.x(r),
                                                   self._draw.y(r)),
                                           clockwise=cw)
        
# --------------------------------------------------------------------
class DiceDraw:
    def __init__(self,width=100,height=100,fg='black',bg='white'):
        from wand.drawing import Drawing
        from wand.color import Color
        
        self._width  = width
        self._height = height
        self._fg     = fg if isinstance(fg,Color) else Color(fg)
        self._bg     = bg if isinstance(bg,Color) else Color(bg)
        self._draw   = Drawing()
        self._size   = min(self._width,self._height)

    @property
    def size(self):
        return self._size
    
    def x(self,xx):
        return int((xx  + 0.5) * self.size)

    def y(self,yy):
        return  int((0.5 -  yy) * self.size)

    def __enter__(self):
        self._draw.stroke_width = max(1,self.size//75)
        self._draw.stroke_color = self._fg
        self._draw.fill_color   = self._bg
        return self

    def number(self,num,yoff=0,scale=1):
        if num is None or num == '':
            return
        
        with DiceContext(self):
            self._draw.stroke_width   = 1
            self._draw.stroke_color   = self._fg
            self._draw.fill_color     = self._fg
            self._draw.text_alignment = 'center'
            self._draw.font_size      = scale * self.size / 2
            self._draw.text(self.x(0),
                            int(self.y(yoff)+self._draw.font_size//2),
                            f'{num}')
            
    def image(self):
        from wand.image import Image as WImage
        
        image = WImage(width=self._width,height=self._height,format='png')
        image.alpha_channel = True
        self._draw(image)
        
        off   = min(self._width,self._height) // 30
        copy  = image.clone()
        copy.shadow(50,off,0,0)
        copy.negate(channel='rgb')
        copy.composite(image,int(off/4),int(off/4))
        
        #copy.save(filename='d4.png')
        return copy

    def __exit__(self,*e):
        pass 

# --------------------------------------------------------------------
class DiceDrawer:
    def __init__(self,nsides,width,height,fg='red',bg='white'):
        from wand.color import Color
        self._nsides = nsides
        self._width  = width
        self._height = height
        self._fg     = Color(fg if isinstance(fg,str) else f'#{fg:06x}')
        self._bg     = Color(bg if isinstance(bg,str) else f'#{bg:06x}')
        if self._nsides not in [4,6,8,10,12,20]:
            raise RuntimeError(f'Unknown number of sides: {self._nsides}')
            

    def draw(self,num):
        if self._nsides ==  4:  return self.draw_d4 (num)
        if self._nsides ==  6:  return self.draw_d6 (num)
        if self._nsides ==  8:  return self.draw_d8 (num)
        if self._nsides == 10:  return self.draw_d10(num)
        if self._nsides == 12:  return self.draw_d12(num)
        if self._nsides == 20:  return self.draw_d20(num)
        return None
        
    def draw_d4(self,num):
        with DiceDraw(self._width,self._height,
                      fg=self._fg,bg=self._bg) as draw:
            with DicePath(draw) as path:
                path.move(to=( 0.000, 0.40))
                path.line(to=( 0.433,-0.35))
                path.line(to=(-0.433,-0.35))
                path.line(to=( 0.000, 0.40))

            draw.number(num)
            return draw.image()

    def draw_d6(self,num):
        with DiceDraw(self._width,self._height,
                      fg=self._fg,bg=self._bg) as draw:
            with DicePath(draw) as path:
                r = 0.05
                w = .4 - r
                path.move(to=(    w, 0.40))
                path.arc (to=( 0.40,    w), r=r)
                path.line(to=( 0.40,-   w))
                path.arc (to=(    w,-0.40), r=r)
                path.line(to=(-   w,-0.40))
                path.arc (to=(-0.40,-   w), r=r)
                path.line(to=(-0.40,    w))
                path.arc (to=(-   w, 0.40), r=r)
                path.line(to=(    w, 0.40))

            draw.number(num,yoff=.1)
            return draw.image()

    def draw_d8(self,num):
        with DiceDraw(self._width,self._height,
                      fg=self._fg,bg=self._bg) as draw:
            with DiceContext(draw,darker=.9):
                with DicePath(draw) as path:
                    path.move(to=(0.0000,0.5000))
                    path.line(to=(0.4330,0.2500))
                    path.line(to=(0.4330,-0.2500))
                    path.line(to=(0.0000,-0.5000))
                    path.line(to=(-0.4330,-0.2500))
                    path.line(to=(-0.4330,0.2500))
                    path.line(to=(0.0000,0.5000))
                        
            with DicePath(draw) as path:
                path.move(to=(0.0000,0.5000))
                path.line(to=(0.4330,-0.2500))
                path.line(to=(-0.4330,-0.2500))
                path.line(to=(0.0000,0.5000))

            draw.number(num,yoff=.1)
            return draw.image()

    def draw_d10(self,num):
        with DiceDraw(self._width,self._height,
                      fg=self._fg,bg=self._bg) as draw:
            with DiceContext(draw,darker=.9):
                with DicePath(draw) as path:
                    path.move(to=(0.0000,0.5000))            
                    path.line(to=(0.4750,0.1000))
                    path.line(to=(0.4750,-0.1000))
                    path.line(to=(0.0000,-0.5000))
                    path.line(to=(-0.4750,-0.1000))
                    path.line(to=(-0.4750,0.1000))
                    path.line(to=(0.0000,0.5000))
                    path.move(to=(0.2940,-0.1540))
                    path.line(to=(0.4750,-0.1000))
                    path.move(to=(-0.4750,-0.1000))
                    path.line(to=(-0.2940,-0.1540))
                    path.move(to=(0.0000,-0.5000))
                    path.line(to=(0.0000,-0.3000))
            with DicePath(draw) as path:
                path.move(to=(0.0000,0.5000))
                path.line(to=(0.2940,-0.1540))
                path.line(to=(0.0000,-0.3000))
                path.line(to=(-0.2940,-0.1540))
                path.line(to=(0.0000,0.5000))

            draw.number(num,yoff=.1)
            return draw.image()

    def draw_d12(self,num):
        with DiceDraw(self._width,self._height,
                      fg=self._fg,bg=self._bg) as draw:
            with DiceContext(draw,darker=.9):
                with DicePath(draw) as path:
                    path.move(to=( 0.0000, 0.5000))
                    path.line(to=( 0.2940, 0.4050))
                    path.line(to=( 0.4750, 0.1730))
                    path.line(to=( 0.4750,-0.1730))
                    path.line(to=( 0.2940,-0.4050))
                    path.line(to=( 0.0000,-0.5000))
                    path.line(to=(-0.2940,-0.4050))
                    path.line(to=(-0.4750,-0.1730))
                    path.line(to=(-0.4750, 0.1730))
                    path.line(to=(-0.2940, 0.4050))
                    path.line(to=( 0.0000, 0.5000))
                    path.line(to=( 0.0000, 0.3490))
                    path.move(to=( 0.4750, 0.1730))
                    path.line(to=( 0.3320, 0.1080))
                    path.move(to=( 0.2940,-0.4050))
                    path.line(to=( 0.2050,-0.2820))
                    path.move(to=(-0.2940,-0.4050))
                    path.line(to=(-0.2050,-0.2820))
                    path.move(to=(-0.4750, 0.1730))
                    path.line(to=(-0.3320, 0.1080))
            with DicePath(draw) as path:
                path.move(to=(0.0000,0.3490))
                path.line(to=(0.3320,0.1080))
                path.line(to=(0.2050,-0.2820))
                path.line(to=(-0.2050,-0.2820))
                path.line(to=(-0.3320,0.1080))
                path.line(to=(0.0000,0.3490))
                    

            draw.number(num,yoff=.1)
            return draw.image()
            
    def draw_d20(self,num):
        with DiceDraw(self._width,self._height,
                      fg=self._fg,bg=self._bg) as draw:
            with DiceContext(draw,darker=.85):
                with DicePath(draw) as path:
                    path.move(to=(0.0000,0.5000))
                    path.line(to=(0.4540,0.2620))
                    path.line(to=(0.4540,-0.2620))
                    path.line(to=(0.0000,-0.5000))
                    path.line(to=(-0.4540,-0.2620))
                    path.line(to=(-0.4540,0.2620))
                    path.line(to=(0.0000,0.5000))            
                    path.line(to=(0.0000,0.2920))
            with DiceContext(draw,darker=.95):
                with DicePath(draw) as path:
                    path.move(to=(0.0000,0.2920))
                    path.line(to=(0.4540,0.2620))
                    path.line(to=(0.2530,-0.1460))
                    path.line(to=(0.0000,-0.5000))
                    path.line(to=(-0.2530,-0.1460))
                    path.line(to=(-0.4540,0.2620))
                    path.line(to=(0.0000,0.2920))
                    path.move(to=(0.4540,-0.2620))
                    path.line(to=(0.2530,-0.1460))
                    path.move(to=(-0.4540,-0.2620))
                    path.line(to=(-0.2530,-0.1460))
            with DicePath(draw) as path:
                path.move(to=(0.0000,0.2920))
                path.line(to=(0.2530,-0.1460))
                path.line(to=(-0.2530,-0.1460))
                path.line(to=(0.0000,0.2920))
            

            scale = .7
            yoff  = .07
            if num > 9:
                scale *= .8
                yoff  =  .015
            draw.number(num,yoff=yoff,scale=scale)
            return draw.image()


# --------------------------------------------------------------------
class DiceAnimator:
    def __init__(self,nsides,width,height,fg='red',bg='white'):
        drawer = DiceDrawer(nsides = nsides,
                            width  = width,
                            height = height,
                            fg     = fg,
                            bg     = bg)
        self._pool = [drawer.draw(v) for v in range(1,nsides+1)]
            
    def draw(self,num,n,dt=10):
        
        '''
        delay : int
            1 / 100 of a second as base delay
        '''
        from random     import sample
        from wand.image import Image

        if num > len(self._pool):
            raise RuntimeError(f'Final value {num} not possible for '
                               f'd{len(self._pool)}')

        if n >= len(self._pool) - 1:
            raise RuntimeError(f'Pre-steps {n} not possible for '
                               f'd{len(self._pool)}')
            
        end   = self._pool[num-1]

        # Round-about, but for debug 
        nums  = list(range(1,len(self._pool)+1))
        nums.remove(num)
        pool  = sample(nums, k=n)
        other = [self._pool[i-1] for i in pool]
        print(num,pool)
        
        # More direct
        # pool  = self._pool[:num] + self._pool[num+1:]
        # other = sample(pool, k=n)
        
        faces = other + [end]
        dang  = 360 / (len(faces))
        img   = Image(format='gif')
        ang   = 360
        wait  = dt
        for i, face in enumerate(faces):
            ang  -= dang
            wait += dt

            with face.clone() as rotated:
                w, h = rotated.size
                rotated.rotate(ang, reset_coords=False)
                rotated.crop(0,0,w,h)
                rotated.dispose = 'previous'
                rotated.delay   = wait # dt * (i + 1)
                rotated.loop    = 1
                img.sequence.append(rotated)

        # Make sure we dispose of the previous image altogether
        #img.dispose = 'previous'
        img.coalesce()
        #img.deconstruct()
        

        return img

#
# EOF
#
