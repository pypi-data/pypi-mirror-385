## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class LayerTrait(Trait):
    ID = 'emb2'
    def __init__(self,
                 images       = [''],
                 newNames     = None,
                 activateName = 'Activate',
                 activateMask = CTRL,
                 activateChar = 'A',
                 increaseName = 'Increase',
                 increaseMask = CTRL,
                 increaseChar = '[',
                 decreaseName = '',
                 decreaseMask = CTRL,
                 decreaseChar  = ']',
                 resetName    = '',
                 resetKey     = '',
                 resetLevel   = 1,
                 under        = False,
                 underXoff    = 0,
                 underYoff    = 0,
                 loop         = True,
                 name         = '',
                 description  = '',
                 randomKey    = '',
                 randomName   = '',
                 follow       = False,
                 expression   = '',
                 first        = 1,
                 version      = 1, # 1:new, 0:old
                 always       = True,
                 activateKey  = key('A'),
                 increaseKey  = key('['),
                 decreaseKey  = key(']'),
                 scale        = 1.):
        '''Create a layer trait (VASSAL.counter.Embellishment)'''
        super(LayerTrait,self).__init__()
        if newNames is None and images is not None:
            newNames = ['']*len(images)
        self.setType(
            activateName        = activateName,
            activateMask        = activateMask,
            activateChar        = activateChar,
            increaseName        = increaseName,
            increaseMask        = increaseMask,
            increaseChar        = increaseChar,
            decreaseName        = decreaseName,
            decreaseMask        = decreaseMask,
            decreaseChar        = decreaseChar,
            resetName           = resetName,
            resetKey            = resetKey,
            resetLevel          = resetLevel,
            under               = under,
            underXoff           = underXoff,
            underYoff           = underYoff,
            images              = ','.join(images),
            newNames            = ','.join(newNames),
            loop                = loop,
            name                = name,
            randomKey           = randomKey,
            randomName          = randomName,
            follow              = follow,
            expression          = expression,
            first               = first,
            version             = version,
            always              = always,
            activateKey         = activateKey,
            increaseKey         = increaseKey,
            decreaseKey         = decreaseKey,
            description         = description,
            scale               = scale)
        self.setState(level=1)

    def getImages(self):
        return self['images'].split(',')

    def setImages(self,*images):
        self['images'] = ','.join(images)
        
    def getNames(self):
        return self['newNames'].split(',')

    def setNames(self,*names):
        images   = self.getImages()
        newNames = ','.join(names+['']*(len(images)-len(names)))
        self['newNames'] = newNames

    def getLevel(self):
        return self['level']

    def setLevel(self,level):
        self['level'] = level
                            

Trait.known_traits.append(LayerTrait)

#
# EOF
#
