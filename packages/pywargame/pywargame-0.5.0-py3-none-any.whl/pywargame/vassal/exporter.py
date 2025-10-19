## BEGIN_IMPORT
from . vmod import VMod
from .. common import VerboseGuard, Verbose 
## END_IMPORT

class Exporter:
    def __init__(self):
        '''Base class for exporters'''
        pass


    def setup(self):
        '''Should be defined to set-up for processing, for example
        generating images and such.  This is executed in a context
        where the VMod file has been opened for writing via
        `self._vmod`. Thus, files can be added to the module at this
        stage.
        '''         
        pass

    def createBuildFile(self,ignores='(.*markers?|all|commons|[ ]+)'):
        '''Should be defined to make the `buildFile.xml` document

        Parameters
        ----------
        ignores : str
            Regular expression to match ignored categories for factions
            determination. Python's re.fullmatch is applied to this
            regular exression against chit categories.  If the pattern
            is matched, then the chit is not considered to belong to a
            faction.

        '''
        pass

    def createModuleData(self):
        '''Should be defined to make the `moduledata` document'''
        pass
    
    def run(self,vmodname,patch=None):
        '''Run the exporter to generate the module
        '''
        with VMod(vmodname,'w') as vmod:
            self._vmod = vmod
            self.setup()
            self.createBuildFile() 
            self.createModuleData()
            self.runPatch(patch)
            self._vmod.addFiles(**{VMod.BUILD_FILE  :
                                   self._build.encode(),
                                   VMod.MODULE_DATA :
                                   self._moduleData.encode()})
        Verbose().message('Created VMOD')
        

    def runPatch(self,patch):
        '''Run user specified patch script.  The script should define

            ```
            def patch(buildFile,moduleData,vmod,verbose):
            ```

        where `buildFile` is the `buildFile.xml` and `moduleData` are
        the XML documents as `xml.dom.Document` objects, `vmod` is a
        `VMod` instance, and `verbose` is a `bool` selecting verbose
        mode or not.
        '''
        if patch is None or patch == '':
            return
        
        from importlib.util import spec_from_file_location, module_from_spec
        from pathlib import Path
        from sys import modules

        p = Path(patch)
        with VerboseGuard(f'Will patch module with {p.stem}.patch function') \
             as v:

            spec   = spec_from_file_location(p.stem, p.absolute())
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            modules[p.stem] = module
            
            # Patch must accept xml.dom.document,xml.dom.document,ZipFile
            module.patch(self._build,
                         self._moduleData,
                         self._vmod,
                         Verbose().verbose)
    
