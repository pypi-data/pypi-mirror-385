## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class StackTrait(Trait):
    ID = 'stack'
    def __init__(self,
                 board     = '',
                 x         = '',  
                 y         = '',  
                 pieceIds  = [],
                 layer     = -1): 
        '''Create a stack trait in a save file'''
        self.setType()       # NAME
        # print('Piece IDs:',pieceIds)
        self.setState(board      = board,
                      x          = x,
                      y          = y,
                      pieceIds   = ';'.join([str(p) for p in pieceIds]),
                      layer      = f'@@{layer}')
        
Trait.known_traits.append(StackTrait)

#
# EOF
#
