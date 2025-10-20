class Geometry:
    RECTANGLE        = 0
    HORIZONTAL_BRICK = 1
    VERTICAL_BRICK   = 2
    HEXAGON          = 3
    SIDEWAYS_HEXAGON = 4
    STAGGER_OUT      = 0
    STAGGER_IN       = 1
    TYPES = {
        RECTANGLE       : 'rectangle',
        HORIZONTAL_BRICK: 'horizontal brick',
        VERTICAL_BRICK  : 'vertical brick',
        HEXAGON         : 'hexagon',
        SIDEWAYS_HEXAGON: 'sideways hexagon'
    }
    STAGGERS = {
        STAGGER_OUT: 'out',
        STAGGER_IN:  'in'
    }
    SKETCHES = {
        RECTANGLE       : r'''
|---|---|
|---|---|''',
        HORIZONTAL_BRICK: r'''
|---|---|
  |---|''',
        VERTICAL_BRICK  : r'''
|--|  |
|  |--|
|--|  |''',
        HEXAGON         : r''' _
/ \
\_/'''        ,
        SIDEWAYS_HEXAGON: r'''/\
||
\/'''
    }

    def __init__(self,nrows,ncols,tpe,stagger,w,h):
        self._nrows   = nrows
        self._ncols   = ncols
        self._type    = tpe
        self._stagger = stagger
        self._width   = w
        self._height  = h
        self._dx      = w
        self._dy      = h

        if self._type == self.HEXAGON:
            self._dx = int(0.75 * self._dx)
        elif self._type == self.SIDEWAYS_HEXAGON:
            self._dy = int(0.75 * self._dy)

    def toPixel(self,row,col):
        x = col * self._dx
        y = row * self._dy
        if self._type == self.RECTANGLE: # No offset for rectangles
            return x,y
        elif self._type in [self.HORIZONTAL_BRICK,self.SIDEWAYS_HEXAGON]:
            x += self._dx//2 if (row % 2) != self._stagger else 0
        elif self._type in [self.VERTICAL_BRICK,self.HEXAGON]:
            y += self._dy//2 if (col % 2) != self._stagger else 0
        return x,y

    def toGrid(self,x,y):
        col = x / self._dx
        row = y / self._dy
        if self._type in [self.HORIZONTAL_BRICK,self.SIDEWAYS_HEXAGON]:
            col -= .5 if (int(row) % 2) != self._stagger else 0
        if self._type in [self.VERTICAL_BRICK,self.HEXAGON]:
            row -= .5  if (int(col) % 2) != self._stagger else 0
        
        return int(row), int(col)

    def boardSize(self,nrows,ncols):
        w = ncols * self._dx
        h = nrows * self._dy

        if self._type in [2,3]:
            h += self._dy // 2
        if self._type in [1,4]:
            w += self._dx // 2
        if self._type == 3:
            w += self._dx // 3
        if self._type == 4:
            h += self._dy // 3

        return w+1,h+1

    def test(self,stepX=None,stepY=None):
        from numpy import linspace
        
        width, height = self.boardSize(self._nrows,self._ncols)
        print(f'Test: {self._type},{self._stagger}')
        print(f'{self._width}x{self._height} ({self._dx},{self._dy})')
        print(f'      {self.TYPES[self._type]} {self.STAGGERS[self._stagger]}')
        print(self.SKETCHES[self._type])

        for row in range(self._nrows):
            for col in range(self._ncols):
                x, y   = self.toPixel(row,col)
                cx, cy = x + self._width // 2, y + self._height // 2
                r, c   = self.toGrid(cx,cy)
                print(f'== {row:3d},{col:3d} -> {cx:6d},{cy:6d} -> {r:3d},{c:3d}')
                assert r == row, f'Rows (from {row} to {r}) inconsistent'
                assert c == col, f'Columns (from {col} to {c}) inconsistent'

                if row >= 3 or col >= 3:
                    continue 
                for dx in linspace(-self._width/4,self._width/4,5):
                    idx = int(dx)
                    for dy in linspace(-self._height/4,self._height/4,5):
                        idy = int(dy)
                        xx = cx + idx
                        yy = cy + idy
                        r, c = self.toGrid(xx,yy)
                        if r != row or c != col:
                            print(f'{row:3d},{col:3d} -> {cx:6d}+{idx:3d}={xx:6d},{cy:6d}+{idy:3d}={yy:6d} -> {r:3d},{c:3d}')
            
                    


def testit(tpe,stagger):
    w = 100
    h = 100
    if tpe == 3:
        w = 80
        h = 68
    elif tpe == 4:
        w = 68
        h = 80

    geo = Geometry(5,5,tpe,stagger,w,h)
    geo.test()


def testall():
    for t in [Geometry.RECTANGLE,
              Geometry.HORIZONTAL_BRICK,
              Geometry.VERTICAL_BRICK,
              Geometry.HEXAGON,
              Geometry.SIDEWAYS_HEXAGON]:
        for s in [Geometry.STAGGER_IN,
                  Geometry.STAGGER_OUT]:
            testit(t,s)



if __name__ == '__main__':
    testall()
    
    
                
    
        
        
        
