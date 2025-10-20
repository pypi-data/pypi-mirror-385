## BEGIN_IMPORT
from .. common import VerboseGuard
from .. common import Verbose
from . features import Features
## END_IMPORT



class BaseArchive:
    WORD_SIZE = 2
    
    def __init__(self,filename,mode='rb'):
        '''Read data from a MFT CArchive stored on disk

        Works as a context manager 
        '''
        with VerboseGuard(f'Opening archive {filename}'):
            self._filename = filename
            self._file = open(filename,mode)
            self._i    = 0
            self.vmsg  = lambda *args : Verbose().message(*args)
            #self.vmsg  = lambda *args : None
        
    def __enter__(self):
        '''Enter context'''
        return self

    def __exit__(self,*args,**kwargs):
        '''Exit context'''
        self._file.close()

    def tell(self):
        pass

    def read(self,n):
        '''Read n bytes from archive'''
        pass

    def chr(self,n):
        '''Read n characters from archive'''
        b = self.read(n)
        try:
            c = b.decode()
            self.vmsg(f'char->{c}')
            return c
        except:
            print(f'Failed at {b} ({self._file.tell()})')
            raise

    def int(self,n):
        '''Read an (unsigned) integer from archive'''
        b = self.read(n)
        i = int.from_bytes(b,'little' if Features().little_endian else 'big')
        self.vmsg(f'int->{i}')
        return i     

    def byte(self):
        '''Read a byte from archive'''
        return self.int(1)

    def word(self):
        '''Read a word (16bit integer) from archive'''
        w = self.int(BaseArchive.WORD_SIZE)
        self.vmsg(f'word->{w}')
        return w;


    def dword(self):
        '''Read a double word (32bit integer) from archive'''
        d = self.int(2*BaseArchive.WORD_SIZE)
        self.vmsg(f'dword->{d}')
        return d

    def size(self):
        '''Read a size'''
        s = self.int(Features().size_size)
        self.vmsg(f'size->{s}')
        return s

    def sub_size(self):
        '''Read a size'''
        s = self.int(Features().sub_size)
        self.vmsg(f'sub->{s}')
        return s
    
    def count(self):
        '''Read a count'''
        if Features().size_size == 4:
            return self.word()

        c = self.word()
        if c != 0xFFFF:
            return c

        c = self.dword()
        if c != 0xFFFFFFFF:
            return c

        return int(8)
        
    def iden(self):
        '''Read an identifier'''
        i = self.int(Features().id_size)
        self.vmsg(f'id->{i}')
        return i
        
    def _strlen(self):
        '''Read length of following string from archive'''
        # See https://github.com/pixelspark/corespark/blob/master/Libraries/atlmfc/src/mfc/arccore.cpp

        s = 1
        l = self.byte()
        
        if l < 0xFF: # Small ASCII string
            self.vmsg(f'slen->{l},{s}')
            return l, s
        
        l = self.word()
        if l == 0xFFFE: # Unicode  - try again
            s = 2
            l = self.byte()

            if l < 0xFF: # Small unicode
                self.vmsg(f'slen->{l},{s}')
                return l, s
            

            l = self.word() # Large unicode string

        if l < 0xFFFF: # Not super long
            self.vmsg(f'slen->{l},{s}')
            return l, s

        l = self.dword()

        if l < 0xFFFFFFFF: # Not hyper long
            self.vmsg(f'slen->{l},{s}')
            return l, s

        
        self.vmsg(f'slen->{8},fixed')
        return self.int(8)
        
    def str(self):
        '''Read a string from the archive'''
        # See https://github.com/pixelspark/corespark/blob/master/Libraries/atlmfc/src/mfc/arccore.cpp
        l, s = self._strlen()
        # print(f'Read string of length {l}*{s} at {self.tell()}')
        ret  = [self.read(s) for i in range(l)]
        try:
            ret = [c.decode() for c in ret]
        except:
            ret = ['']
        self.vmsg(f'str->"{"".join(ret)}"')
        return ''.join(ret)

    @property
    def filename(self):
        return self._filename

    @property
    def path(self):
        from pathlib import Path
        return Path(self._filename)
    
# ====================================================================
class UnbufferedArchive(BaseArchive):
    def __init__(self,filename,mode='rb'):
        '''Read data from a MFT CArchive stored on dist

        Works as a context manager 
        '''
        super(UnbufferedArchive,self).__init__(filename,mode='rb')

    def read(self,n):
        '''Read n bytes from archive - directly from file'''
        b = self._file.read(n)
        self.vmsg(f'read->{list(b)}')
        # print(f'{self._i:6d} -> {b}')
        self._i += n
        return b

    def tell(self):
        return self._file.tell()

# ====================================================================
class BufferedArchive(BaseArchive):
    def __init__(self,filename,mode='rb'):
        '''Read data from a MFT CArchive stored on dist

        Works as a context manager 
        '''
        super(BufferedArchive,self).__init__(filename,mode='rb')
        self._size    = 4096
        self._max     = self._size
        self._current = self._max
        self._buffer  = []

    def read(self,n):
        with VerboseGuard(f'Read {n} bytes') as g:
            '''Read n bytes from archive - buffered
            
            This emulates the behaviour of MFC CArchive::Read 
            '''
            
            nmax          = n
            ntmp          =  min(nmax, self._max - self._current)
            b             =  self._buffer[self._current:self._current+ntmp]
            g(f'Take {ntmp} bytes from buffer -> {b}')
            self._current += ntmp
            nmax          -= ntmp
            
            if nmax != 0:
                g(f'Need to read at least {nmax} from file')
                assert self._current == self._max,\
                    f'Something is wrong! {self._current} != ' \
                    f'{self._max} (1)'

                g(f'Missing {nmax} bytes -> ({nmax % self._size})')
                ntmp         = nmax - (nmax % self._size)
                nread        = 0
                nleft        = ntmp
                nbytes       = 0
                while True:
                    tmpbuf =  self._file.read(nleft)
                    nbytes =  len(tmpbuf)
                    nread  += nbytes
                    nleft  -= nbytes
                    b      += tmpbuf
                    g(f'Read {nleft} -> {tmpbuf}')
                    
                    if nbytes <= 0 or nleft <= 0:
                        break
            
                nmax -= nread
            
                if nmax > 0 and nread  == ntmp:
                    # Last read chunk into buffer and copy
                    assert self._current == self._max,\
                        f'Something is wrong! {self._current} != ' \
                        f'{self._max} (2)'
                    
                    assert nmax < self._size, \
                        f'Something is wrong {nmax} >= {self._size}'
                    
                    nlastleft    = max(nmax,self._size)
                    nlastbytes   = 0
                    nread        = 0
                    self._buffer = []
                    while True:
                        tmpbuf       =  self._file.read(nlastleft)
                        nlastbytes   =  len(tmpbuf)
                        nread        += nlastbytes
                        nlastleft    -= nlastbytes
                        self._buffer += tmpbuf
            
                        if (nlastbytes <= 0) or \
                           (nlastleft <= 0) or \
                           nread >= ntmp:
                            break
            
                    self._current = 0
                    self._max     = nread
            
                    ntmp          =  min(nmax, self._max - self._current)
                    b             += self._buffer[self._current:
                                                  self._current+ntmp]
                    self._current += ntmp
                    nmax          -= ntmp
            
            g(b)
            return b''.join(b)

    def tell(self):
        return self._file.tell()
    

Archive = UnbufferedArchive
# Archive = BufferedArchive

#
# EOF
#
