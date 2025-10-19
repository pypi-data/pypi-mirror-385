# ====================================================================
class Singleton(type):
    '''Meta base class for singletons'''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        '''Create the singleton object or returned existing

        Parameters
        ----------
        args : tuple
            Arguments
        kwargs : dict
            Keyword arguments
        '''
        if cls not in cls._instances:
            cls._instances[cls] = \
                super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

#
# EOF
#
