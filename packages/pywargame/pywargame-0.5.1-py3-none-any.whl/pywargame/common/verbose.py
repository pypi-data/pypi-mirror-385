# --------------------------------------------------------------------
## BEGIN_IMPORT
from . singleton import Singleton
## END_IMPORT

class Verbose(metaclass=Singleton):
    def __init__(self,verbose=False):
        '''Singleton for writing message to screen, contigent on setting

        Parameters
        ----------
        verbose : bool
             Whether to show messages or not
        '''
        self._indent  = ''
        self._verbose = verbose

    def setVerbose(self,verbose):
        '''Set whether to print or not

        Parameters
        ----------
        verbose : bool
             Whether to show messages or not
        '''
        self._verbose = verbose

    @property
    def verbose(self):
        '''Test if this is verbose'''
        return self._verbose

    def message(self,*args,**kwargs):
        '''Write messsage if verbose

        Parameters
        ----------
        args : tuple
            Arguments
        kwargs : dict
            Keyword arguments
        '''        
        if not self._verbose: return
        if not kwargs.pop('noindent', False):
            print(self._indent,end='')
        print(*args,**kwargs)

    def incr(self):
        '''Increment indention'''
        self._indent += ' '

    def decr(self):
        '''Decrement indention'''
        if len(self._indent) > 0:
            self._indent = self._indent[:-1]

#
# EOF
#
