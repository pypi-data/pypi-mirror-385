## BEGIN_IMPORTS
from . base import DomInspect, ZTImage
from pywargame.common import VerboseGuard
## END_IMPORTS

# --------------------------------------------------------------------
class ZTMap(DomInspect):
    def __init__(self,elem):
        with VerboseGuard(f'Got a map'):
            self._name  = self._get_attr(elem,'name')
            self._image = ZTImage(elem)

    def read_image(self,zf):
        with VerboseGuard(f'Reading map ({self._name}) image') as v:
            self._image.read_image(zf)
            sc = ZTImage.target_dpi / self._image._reso
            v(f'Scale by {sc}={ZTImage.target_dpi}/{self._image._reso} '
              f'from {self._image._image.width}x{self._image._image.height}')
            self._image._image.resize(int(sc*self._image._image.width),
                                      int(sc*self._image._image.height))
            v(f'Scaled by {sc} to {self._image._image.width}x'
              f'{self._image._image.height}')
        
    @property
    def filename(self):
        return f'{self._name.replace(" ","_")}.{self._image._image.format.lower()}'

    @property
    def size(self):
        return self._image._image.width,self._image._image.height

    def __str__(self):
        return f' Map: name={self._name}'+'\n'+str(self._image)
#
# EOF
#
