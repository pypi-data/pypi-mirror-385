# --------------------------------------------------------------------
## BEGIN_IMPORT
from . verbose import Verbose
## END_IMPORT

class VerboseGuard:
    def __init__(self,*args,**kwargs):
        '''A guard pattern that increases verbose indention

        This is a context manager.  The arguments passed are used for
        an initial message, before increasinig indention.

        Parameters
        ----------
        args : tuple
            Arguments
        kwargs : dict
            Keyword arguments
        '''                
        Verbose().message(*args,**kwargs)

    def __bool_(self):
        '''Test if verbose'''
        return Verbose().verbose
    
    def __enter__(self):
        '''Enter context'''
        Verbose().incr()
        return self

    def __exit__(self,*args):
        '''Exit context'''        
        Verbose().decr()

    @property
    def i(self):
        return Verbose()._indent
    
    def __call__(self,*args,**kwargs):
        '''Write a message at current indention level
        
        Parameters
        ----------
        args : tuple
            Arguments
        kwargs : dict
            Keyword arguments
        '''                
        Verbose().message(*args,**kwargs)

#
# EOF
#
