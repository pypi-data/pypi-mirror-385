## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
## END_IMPORT

# --------------------------------------------------------------------
class Command:
    def __init__(self,what,iden,tpe,state):
        self.cmd = '/'.join([what,iden,tpe,state])
    
# --------------------------------------------------------------------
class AddCommand(Command):
    ID = '+'
    def __init__(self,iden,tpe,state):
        super(AddCommand,self).__init__(self.ID,iden,tpe,state)
        

#
# EOF
#
