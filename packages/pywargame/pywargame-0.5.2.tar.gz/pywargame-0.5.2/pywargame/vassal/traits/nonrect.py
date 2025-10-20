## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class NonRectangleTrait(Trait):
    ID      = 'nonRect2'
    CLOSE   = 'c'
    MOVETO  = 'm'
    LINETO  = 'l'
    CUBICTO = 'l'
    QUADTO  = 'l'
    def __init__(self,
                 scale    = 1.,
                 filename = '',
                 path     = [],
                 image    = None):
        '''Create a NonRectangle trait (static property)'''
        super(NonRectangleTrait,self).__init__()
        l = []
        if len(filename) > 0:
            l.append(f'n{filename}')

        if len(path) <= 0:
            path = self.getShape(image)

        if len(path) > 0:
            # print(path)
            l += [f'{p[0]},{int(p[1])},{int(p[2])}' if len(p) > 2 else p
                  for p in path]
    
        self.setType(scale = scale,
                     code  = ','.join(l))
        self.setState()

    @classmethod
    def getShape(cls,buffer):
        if buffer is None:
            return []

        from io import BytesIO

        image = buffer
        if image[:5] == b'<?xml':
            from cairosvg import svg2png
            image = svg2png(image)

        from PIL import Image

        code = []
        with Image.open(BytesIO(image)) as img:
            alp = img.getchannel('A') # Alpha channel
            # Find least and largest non-transparent pixel in each row
            rows  = []
            w     = alp.width
            h     = alp.height
            bb    = alp.getbbox()
            for r in range(bb[1],bb[3]):
                ll, rr = bb[2], bb[0]
                for c in range(bb[0],bb[2]):
                    if alp.getpixel((c,r)) != 0:
                        ll = min(c,ll)
                        rr = max(c,rr)
                rows += [[r-h//2,ll-w//2,rr-w//2]]
                    
            # Now produce the code - we start with the top line
            code = [(cls.MOVETO,rows[0][1],rows[0][0]-1),
                    (cls.LINETO,rows[0][2],rows[0][0]-1)]
            
            # Now loop  down right side of image
            for c in rows:
                last = code[-1]
                if last[1] != c[2]:
                    code += [(cls.LINETO, c[2], last[2])]
                code += [(cls.LINETO, c[2], c[0])]
                
            # Now loop up left side of image
            for c in rows[::-1]:
                last = code[-1]
                if last[1] != c[1]:
                    code += [(cls.LINETO,c[1],last[2])]
                code += [(cls.LINETO,c[1],c[0])]

            # Terminate with close
            code += [(cls.CLOSE)]

        return code


Trait.known_traits.append(NonRectangleTrait)

#
# EOF
#
