# --------------------------------------------------------------------
## BEGIN_IMPORT
from .. common.singleton import Singleton
## END_IMPORT

class Features(metaclass=Singleton):
    def __init__(self):
        self.bmp_zlib      = False # wxBMPHandler + Zlib
        self.id_size       = 2     # Size of IDs in bytes (1, 2 or 4)
        self.size_size     = 4     # Size of sizes in bytes (4 or 8)
        self.sub_size      = 2     # Size of sub-sizes in bytes (4 or 8)
        self.square_cells  = False # Geomorphic boards, square cells
        self.rotate_unit   = False # Geomorphic boards, rotated unit board
        self.piece_100     = False # Pieces w/<= 100 sides
        self.private_board = False #
        self.roll_state    = False # serialize roll state
        self.little_endian = True
