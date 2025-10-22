## BEGIN_IMPORT
from .. common import VerboseGuard
## END_IMPORT

# ====================================================================
class GBXImage:
    def __init__(self,ar,transparent=None,save=None):
        '''A DIB image stored in GameBox'''
        with VerboseGuard('Reading an image') as g:
            size = ar.dword()
                
            if size & 0x80000000: # Compressed
                from zlib import decompress
                g(f'Read compressed image')
                
                size       &= 0x80000000  # Remove flag
                compSize   =  ar.dword() # Compressed size
                compressed =  ar.read(compSize) # Compressed
                buffer     = decompress(compressed,bufsize=size)
                #assert len(buffer) == size, \
                #    f'Failed to decompress to expected {size}, ' \
                #    f'got {len(buffer)}'
                    
            else:
                buffer  = ar.read(size)
            
            from PIL import Image as PILImage
            from io import BytesIO
            from numpy import asarray, where, uint8
            
            img = PILImage.open(BytesIO(buffer)).convert('RGBA')
            
            # If transparancy is defined, clean up the image 
            if transparent is None:
                self._img = img
            else:
                g(f'Making #{transparent:06x} transparent')
                dat         = asarray(img)
                tr          = (transparent >> 16) & 0xFF
                tg          = (transparent >> 8)  & 0xFF
                tb          = (transparent >> 0)  & 0xFF
                dat2        = dat.copy()
                dat2[:,:,3] = (255*(dat[:,:,:3]!=[tb,tg,tr]).any(axis=2))\
                    .astype(uint8)

                #if (dat[:,:,3] == dat2[:,:,3]).all():
                #    print(f'Transparency operation seemed to have no effect '
                #          f'for image')
                
                self._img  = PILImage.fromarray(dat2)
            
            if save is None:
                return
            
            self._img.save(save)

    @classmethod
    def b64encode(cls,img):
        '''Encode image as a base64 data URL'''
        from io import BytesIO
        from base64 import b64encode

        if img is None:
            return None
        
        buffered = BytesIO()
        img.save(buffered,format='PNG')
        data = b64encode(buffered.getvalue())
        if not isinstance(data,str):
            data = data.decode()

        return 'data:image/png;base64,'+data

#
# EOF
#
