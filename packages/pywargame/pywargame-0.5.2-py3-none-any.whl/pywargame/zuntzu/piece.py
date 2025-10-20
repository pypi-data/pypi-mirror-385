# --------------------------------------------------------------------
class ZTPiece:
    def __init__(self,front_image,back_image,x,y,terrain,card):
        self._front   = front_image
        self._back    = back_image
        self._terrain = terrain
        self._card    = card
        self._x       = x
        self._y       = y

    @property
    def two_sides(self):
        return (self._front        is not None and
                self._back         is not None)

    @property
    def size(self):
        return self.width,self.height

    @property
    def width(self):
        return self._front.width

    @property
    def height(self):
        return self._front.height

    
    def __str__(self):
        return (f'  Piece: '+
                f'{"card" if self._card else "piece"} '+
                f'{"terrain" if self._terrain else "piece"} '+
                f'front={self._front} back={self._back}')

#
# EOF
#
