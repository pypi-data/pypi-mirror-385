TARGET_DPI = 300

# --------------------------------------------------------------------
class DomInspect:
    '''Utilities'''
    @classmethod
    def _get_attr(cls,node,name,default=None):
        '''Get attribute from node, or default value'''
        val = node.attributes.get(name,None)
        if val is None:
            return default
        return val.nodeValue

    @classmethod
    def _find_children(cls,node,*tags):
        '''Find all children of a node with specific tags'''
        if len(tags) == 1:
            return node.getElementsByTagName(tags[0])
        return [child  for child in node.childNodes
                if child.nodeType != child.TEXT_NODE and
                child.nodeType != child.COMMENT_NODE and 
                child.tagName in tags]

    @classmethod
    def _parse_hex(cls,txt):
        '''Parse a hex number'''
        if isinstance(txt,int):
            return txt

        if not (txt.startswith('0x') and txt.startswith('0X')) and \
           any([c in txt for c in 'ABCFEFabcdef']):
            txt = '0x'+txt

        return int(txt,0)

    @classmethod
    def _parse_resolution(cls,txt):
        '''Parse resolution specifier'''
        if isinstance(txt,int):
            return txt

        return int(txt.lower().replace('dpi',''))

    @classmethod
    def _read_image(cls,zf,filename,resolution=None):
        '''Read in an image from Zip file.  Note the image is
        explicitly converted to PNG

        '''        
        if not filename:
            return None
        
        from wand.image import Image

        with VerboseGuard(f'Reading in image from {filename}'):
            with zf.open(filename,'r') as inp:
                img = Image(file=inp,
                            #resolution=(resolution,resolution)
                            )
                img.format        = 'png'
                return img

# --------------------------------------------------------------------
class ZTImage(DomInspect):
    target_dpi = 300
    
    def __init__(self,elem,prefix=''):
        '''A stored image in the game box'''
        self._image_file = self._get_attr(elem,prefix+'image-file')
        self._reso       = self._parse_resolution(
            self._get_attr(elem,prefix+'resolution',150))


    def read_image(self,zf):
        self._image = self._read_image(zf,self._image_file,self._reso)

    def __str__(self):
        return f'  Image: file={self._image_file}, resolution={self._reso}'
        
#
# EOF
#
