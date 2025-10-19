# ====================================================================
#
# Wrapper around a module 
#
## BEGIN_IMPORT
from . xmlns import xmlns
## END_IMPORT

class VMod:
    BUILD_FILE = 'buildFile.xml'
    BUILD_FILE_SANS = 'buildFile'
    MODULE_DATA = 'moduledata'
    EXTENSION_DATA = 'extensiondata'
    
    def __init__(self,filename,mode):
        '''Interface to VASSAL Module (a Zip file)'''
        self._mode = mode
        self._vmod = self._open(filename,mode)

    def __enter__(self):
        '''Enter context'''
        return self

    def __exit__(self,*e):
        '''Exit context'''
        self._vmod.close()
        return None

    def _open(self,filename,mode):
        '''Open a file in VMod'''
        from zipfile import ZipFile, ZIP_DEFLATED

        return ZipFile(filename,mode,compression=ZIP_DEFLATED)
        
    def removeFiles(self,*filenames):
        '''Open a temporary zip file, and copy content from there to
        that file, excluding filenames mentioned in the arguments.
        Then close current file, rename the temporary file to this,
        and reopen in 'append' mode.  The deleted files are returned
        as a dictionary.

        Parameters
        ----------
        filenames : tuple
            List of files to remove from the VMOD

        Returns
        -------
        files : dict
            Dictionary from filename to content of the removed files.

        Note, the VMOD is re-opened in append mode after this
        '''
        from tempfile import mkdtemp
        from zipfile import ZipFile
        from shutil import move, rmtree 
        from os import path

        tempdir = mkdtemp()
        ret     = {}

        try:
            tempname = path.join(tempdir, 'new.zip')
            with self._open(tempname, 'w') as tmp:

                for item in self._vmod.infolist():
                    data = self._vmod.read(item.filename)

                    if item.filename not in filenames:
                        tmp.writestr(item, data)
                    else:
                        ret[item.filename] = data

            name = self._vmod.filename
            self._vmod.close()
            move(tempname, name)

            self._mode = 'a'
            self._vmod = self._open(name,'a')
        finally:
            rmtree(tempdir)

        # Return the removed files 
        return ret

    def clone(self,newname,mode='a',filter=lambda f:False):
        '''Clones the VMod and returns new object.

        This is done by first opening a temporary ZIP file, and then
        copy all files of this module to that tempoary.  Then the
        temporary ZIP is closed and moved to its `newname`.  After
        that, we open it up as a VMod (write-enabled).

        '''
        from tempfile import mkdtemp
        from zipfile import ZipFile
        from shutil import move, rmtree 
        from os import path

        tempdir = mkdtemp()
        ret     = None

        try:
            tempname = path.join(tempdir, 'new.zip')
            with self._open(tempname, 'w') as tmp:

                for item in self._vmod.infolist():
                    # Ignore some files, a given by filter functoin 
                    if filter(item.filename):
                        continue
                    
                    data = self._vmod.read(item.filename)

                    tmp.writestr(item, data)

            move(tempname, newname)

            ret =  VMod(newname,mode)
        finally:
            rmtree(tempdir)

        return ret
        

    def fileName(self):
        '''Get name of VMod file'''
        return self._vmod.filename

    def replaceFiles(self,**files):
        '''Replace existing files with new files

        Parameters
        ----------
        files : dict
            Dictionary that maps file name to content
        '''
        self.removeFiles(*list(files.keys()))

        self.addFiles(**files);
    
    def addFiles(self,**files):
        '''Add a set of files  to this

        Parameters
        ----------
        files : dict
            Dictionary that maps file name to content.
        '''
        for filename,data in files.items():
            self.addFile(filename,data)

    def addFile(self,filename,content):
        '''Add a file to this

        Parameters
        ----------
        filename : str
            File name in module
        content : str
            File content
        
        Returns
        -------
        element : File
            The added element
        '''
        self._vmod.writestr(filename,content)

    def addExternalFile(self,filename,target=None):
        '''Add an external file element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : ExternalFile
            The added element
        '''
        if target is None: target = filename
        self._vmod.write(filename,target)
        
    def getFileNames(self):
        '''Get all filenames in module'''
        return self._vmod.namelist()

    def getFileMapping(self):
        '''Get mapping from short name to full archive name'''
        from pathlib import Path
        
        names = self.getFileNames()

        return {Path(p).stem: str(p) for p in names}
    
    def getFiles(self,*filenames):
        '''Return named files as a dictionary.

        Parameters
        ----------
        filenames : tuple
            The files to get 
        
        Returns
        -------
        files : dict
            Mapping of file name to file content
        '''
        fn  = self.getFileNames()
        ret = {}
        for f in filenames:
            if f not in fn:
                continue

            ret[f] = self._vmod.read(f)

        return ret

    def getDOM(self,filename):
        '''Get content of a file decoded as XML DOM

        Parameters
        ----------
        filename : str
            Name of file in module 
        '''
        #from xmlns import parseString

        r = self.getFiles(filename)
        if filename not in r:
            raise RuntimeError(f'No {filename} found!')

        return xmlns.parseString(r[filename])
        
    def getBuildFile(self):
        '''Get the buildFile.xml decoded as a DOM tree'''
        try:
            return self.getDOM(VMod.BUILD_FILE)
        except Exception as e:
            print(e)
        try:
            return self.getDOM(VMod.BUILD_FILE_SANS)
        except:
            raise

    def getModuleData(self):
        '''Get the moduledata decoded as a DOM tree'''
        return self.getDOM(VMod.MODULE_DATA)

    def getExtensionData(self):
        '''Get the moduledata decoded as a DOM tree'''
        return self.getDOM(VMod.EXTENSION_DATA)

    def isExtension(self):
        return VMod.EXTENSION_DATA in self.getFileNames()
    
    def getInternalFile(self,filename,mode):
        return self._vmod.open(filename,mode)

    def addVSav(self,build):
        '''Add a `VSav` element to this

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : VSav
            The added element
        '''
        return VSav(build=build,vmod=self)

    @classmethod
    def patch(cls,vmod_filename,patch_name,verbose):
        '''Patch a module with a Python script

        Parameters
        ----------
        vmod_filename : str
            File name of module to patch.  Will be overwritten
        patch_name : str
            File name of Python script to patch with
        verbose : bool
            Whether to be verbose or not
        '''
## BEGIN_IMPORT
        from .. common import VerboseGuard, Verbose 
## END_IMPORT
    
        with cls(vmod_filename,'r') as vmod:
            buildFile  = BuildFile(vmod.getBuildFile())
            moduleData = ModuleData(vmod.getModuleData())

        from importlib.util import spec_from_file_location, module_from_spec
        from pathlib import Path
        from sys import modules

        p = Path(patch_name)

        spec   = spec_from_file_location(p.stem, p.absolute())
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
    
        modules[p.stem] = module

        with cls(vmod_filename,'a') as vmod:
            module.patch(buildFile,
                         moduleData,
                         vmod,
                         verbose)
    
            vmod.replaceFiles(**{VMod.BUILD_FILE :
                                 buildFile.encode(),
                                 VMod.MODULE_DATA :
                                 moduleData.encode()})


    @classmethod
    def patchFunction(cls,vmod_filename,patch,verbose):
        '''Patch a module with a Python script

        Parameters
        ----------
        vmod_filename : str
            File name of module to patch.  Will be overwritten
        patch : callable
            A callable to patch the VMod.  It must have signature
        
                patch(buildFile  : pywargames.vassal.BuildFile,
                      moduleData : pywargames.vassal.ModuleData,
                      vmod       : pywargames.vassal.VMod
                      verbose    : boolean)

        verbose : bool
            Whether to be verbose or not
        '''
## BEGIN_IMPORT
        from .. common import VerboseGuard, Verbose
        from . buildfile import BuildFile
        from . moduledata import ModuleData
## END_IMPORT
    
        with cls(vmod_filename,'r') as vmod:
            buildFile  = BuildFile(vmod.getBuildFile())
            moduleData = ModuleData(vmod.getModuleData())

        with cls(vmod_filename,'a') as vmod:
            try:
                patch(buildFile,
                      moduleData,
                      vmod,
                      verbose)
    
                vmod.replaceFiles(**{VMod.BUILD_FILE :
                                     buildFile.encode(),
                                     VMod.MODULE_DATA :
                                     moduleData.encode()})
            except Exception as e:
                raise
            

#
# EOF
#
