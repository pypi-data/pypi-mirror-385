## BEGIN_IMPORT
from .. common import VerboseGuard
from . base import *
from . element import Element
from . extension import *
from . vmod import *
from . buildfile import *
from . moduledata import *
## END_IMPORT

class Merger:
    def __init__(self,outname,*inputs):
        self._outName = outname  # Output name 
        self._inputs  = list(inputs)   # File-like objects 
        self._names   = [i.name for i in self._inputs]

        # Pop the first input, and open it as a module, and clone it 
        first     = self._inputs.pop(0)
        firstname = first.name
        first.close()
        with VMod(firstname, 'r') as vfirst:
            self._dest = vfirst.clone(outname,
                                      mode   = 'a',
                                      filter = self.filterCruft)

        self._mergedData = {}
        self._buildFile  = BuildFile(self._dest.getBuildFile())
        self._moduleData = ModuleData(self._dest.getModuleData())
        self._extensions = None
        self._mergedData[firstname] = self._moduleData._root
        self._buildFileDest = (VMod.BUILD_FILE if
                               VMod.BUILD_FILE in self._dest._vmod.namelist()
                               else VMod.BUILD_FILE_SANS)
        
    # ----------------------------------------------------------------
    def filterCruft(self,f):
        '''Filter special.  Return true for files that should be
        filtered out.

        Some cruft left behind by MacOSX is explicitly
        removed, and wrongly embedded module files are also
        filtered out.

        '''                
        if f.startswith('__MACOSX'):
            return True
        if f.endswith('.vmod'):
            return True
        if f.endswith('.DS_Store'):
            return True
        return False
        
    # ----------------------------------------------------------------
    def run(self,overwrite=True,assume_same=False,patch=None):
        with VerboseGuard(f'Merging inputs into {self._outName}') as v:
            try:
                while self._inputs:
                    input             = self._inputs.pop(0)
                    self._currentName = input.name
                    input.close()

                    self.mergeOne(overwrite=True,assume_same=assume_same)
            except:
                raise

            #v(f'{"\n".join(self._dest.getFileNames())}')
            self.documentMerge()
            self.patch(patch)
            
            v(f'Overrding updated files {self._buildFileDest}')
            self._dest.replaceFiles(**{self._buildFileDest:
                                       self._buildFile.encode(),
                                       VMod.MODULE_DATA:
                                       self._moduleData.encode()})

            self.summary()
            
        self._dest._vmod.close()

    # ----------------------------------------------------------------
    def documentMerge(self):
        with VerboseGuard(f'Writing summary of merge') as v:
            doc = self._buildFile.getGame().getDocumentation(single=True)
            if not doc:
                doc = self._buildFile.getGame().addDocumentation()
            else:
                doc = doc[0]
            
            def li(n,d):
                return f'<li><code>{n}</code></li>'

            desc = f'''<html><body>
            <h1>Merged modules and extensions</h1>
            <p>
            This module was created from other modules or extensions by
            the Python script <code>vslmerge.py</code> available from
            </p>
            <pre>
            htps://gitlab.com/wargames_tex/pywargame
            </pre>
            <h1>Merged files</h1>
            <ul>
            {"\n".join([li(n,d) for n,d in self._mergedData.items()])}
            </ul>
            <p>
            See also the XML file <code>merged</code>, in the module
            archive, for more information of the merged modules or
            extensions
            </p>
            </body></html>;'''
            self._dest.addFile('help/merged.html',desc)
            doc.addHelpFile(title='Merged',fileName='help/merged.html')
            v(f'Wrote merge information to help menu')
        
    # ----------------------------------------------------------------
    def summary(self):
        with VerboseGuard(f'Writing summary XML to output') as v:
            from pprint import pprint
            #from xml.dom.minidom import Document
            from pathlib import Path
            
            doc = xmlns.Document()
            lst = doc.createElement('MergeSummary')
            doc.appendChild(lst)
            for n,d in self._mergedData.items():
                p = Path(n).name
                v(f'{p}')
                
                m = doc.createElement('Merged')
                m.setAttribute('filename',p)
                lst.appendChild(m)
                m.appendChild(d.firstChild)

            self._dest.addFile('merged',doc.toprettyxml())


        
            
            
        
    # ----------------------------------------------------------------
    def patch(self,patch):
        if not patch:
            return

        with VerboseGuard(f'Patching merged module w/file {patch.name}') as v:
            from importlib.util import spec_from_file_location, \
                module_from_spec
            from pathlib import Path
            from sys import modules
        
            p = Path(patch.name)
        

            spec   = spec_from_file_location(p.stem, p.absolute())
            module = module_from_spec(spec)
            spec.loader.exec_module(module)
            
            modules[p.stem] = module
            
            module.patch(self._buildFile,
                         self._moduleData,
                         self._dest,
                         Verbose())


    # ----------------------------------------------------------------
    def mergeOne(self,overwrite=True,assume_same=False):
        with VerboseGuard(f'Merging from {self._currentName}') as v:
            with VMod(self._currentName,'r') as self._current:

                if self._current.isExtension():
                    self._mergedData[self._currentName] = \
                        self._current.getExtensionData()
                else:
                    self._mergedData[self._currentName] = \
                        self._current.getModuleData()

                v(f'About to merge files')
                self.mergeFiles(overwrite=overwrite)

                if self._current.isExtension():
                    v(f'About to merge extension data')
                    self.mergeExtension(overwrite=overwrite)
                else:
                    v(f'About to merge module data')
                    self.mergeModuleData(overwrite=overwrite)

                    v(f'About to merge build files')
                    self.mergeBuildFile(overwrite=overwrite,
                                        assume_same=assume_same)
                
    # ----------------------------------------------------------------
    def mergeFiles(self,overwrite=True):
        specials     = [VMod.BUILD_FILE,
                        VMod.BUILD_FILE_SANS,
                        VMod.MODULE_DATA,
                        VMod.EXTENSION_DATA]

        def filter(f):
            return self.filterCruft(f) or f in specials
        
        with VerboseGuard(f'Merging files from {self._currentName}') as v:
            
                
            currentFiles = {f for f in self._current.getFileNames()
                            if not filter(f)}
            destFiles    = {f for f in self._dest.getFileNames()
                            if not filter(f)}
            unique       = currentFiles - destFiles

            v(f'Will add {len(unique)} unique files from '
              f'{self._currentName} to destination')
            uniqueContent = self._current.getFiles(*unique)

            # Do not break line
            v(f'{f"\n{v.i}".join([f"{f}: {len(c)}" for f,c in uniqueContent.items()])}')
            self._dest.addFiles(**uniqueContent)

            if not overwrite:
                return 

            overlap = currentFiles.intersection(destFiles)
            v(f'Will overwrite {len(overlap)} files in destination '
              f'with files from {self._currentName}')

            
            overlapContent = self._current.getFiles(*overlap)
            # Do not break line 
            v(f'{f"\n{v.i}".join([f"{f}: {c[:20]}..." for f,c in overlapContent.items()])}')
            self._dest.replaceFiles(**overlapContent)
            
    # ----------------------------------------------------------------
    def mergeModuleData(self,overwrite=True):
        ''' Merge module data XML''';
        with VerboseGuard(f'Merging module data from '
                          f'{self._currentName}') as v:
            currentModuleDoc  = self._current.getModuleData()
            currentModuleData = ModuleData(currentModuleDoc)

            # v(f'{currentModuleDoc.toprettyxml()}')
            self.mergeElement(self._moduleData,
                              currentModuleData,
                              overwrite=overwrite)

    # ----------------------------------------------------------------
    def mergeBuildFile(self,
                       overwrite   = True,
                       assume_same = False):
        ''' Merge module data XML''';
        with VerboseGuard(f'Merging build file from '
                          f'{self._currentName}') as v:
            currentModuleDoc  = self._current.getBuildFile()
            currentBuildFile  = BuildFile(currentModuleDoc)

            if assume_same:
                with VerboseGuard(f'Assuming same game') as v:
                    # We assume that the modules are modules of the
                    # same game. Thus, we want to change the name of
                    # the top-level element of subsequent modules to
                    # be the same as the destination name.
                    destGame = self._buildFile .getGame()
                    srcGame  = currentBuildFile.getGame()
                    v(f'Destination game is {destGame["name"]}')
                    v(f'Current source game is {srcGame["name"]}')
                    if v: destGame.print()
                    if v: srcGame .print()
                    srcGame['name'] = destGame['name']
                
            # v(f'{currentModuleDoc.toprettyxml()}')
            self.mergeElement(self._buildFile,
                              currentBuildFile,
                              depth       = 0,
                              overwrite   = overwrite)

    # ----------------------------------------------------------------
    def mergeExtension(self,overwrite=True):
        ''' Merge module data XML''';
        with VerboseGuard(f'Merging extension from '
                          f'{self._currentName}') as v:
            currentModuleDoc  = self._current.getBuildFile()
            currentBuildFile  = Extension(parent=currentModuleDoc,
                                          node=currentModuleDoc.firstChild)

            if not self._extensions:
                self._extensions = self._buildFile.getGame().addFolder(
                    name = 'MergedExtensions',
                    description = 'Extensions merged in')

            # Mark extension as loaded
            #
            # Doesn't work because VASSAL.build.module.ModuleExtension
            # does not have a default CTOR - sigh!  Probably done on
            # purpose, bit still annoying.
            #
            # oext = self._extensions.add(Extension)
            # oext.setAttributes(
            #     anyModule         = currentBuildFile['anyModule'],
            #     version           = currentBuildFile['version'],
            #     description       = currentBuildFile['description'],
            #     module            = currentBuildFile['module'],
            #     moduleVersion     = currentBuildFile['moduleVersion'],
            #     vassalVersion     = currentBuildFile['vassalVersion'],
            #     nextPieceSlotId   = currentBuildFile['nextPieceSlotId'],
            #     extensionId       = currentBuildFile['extensionId'])
                

            # Get all the extension elements specified 
            for k,ext in currentBuildFile.getExtensionElements().items():
                v(f'Extension element: {k}/{ext}')
                cur  = self._buildFile
                if ext.target == '':
                    print(f'Warning, no target specified for extension '
                          f'element, will assume top')
                    spec = [[cur._node.firstChild.tagName]]
                else:
                    spec = ext.getSelect()

                # From the unpacked target path, find the target
                # element in destination.
                for tn,*en in spec:
                    v(f' Looking for element w/tag={tn} and attributes={en}')
                    
                    cs = Element.getTagClass(tn)
                    if not cs:
                        raise RuntimeError(f'Got no class for tag={tn}')

                    es = cur.getAllElements(cs,single=len(en)<1)
                    if not es:
                        raise RuntimeError(f'Got no elements w/tag={tn}')

                    if en:
                        tgt = None
                        unt = Element._make_unique(tn,*en)
                        for e in es:
                            #v(f'  candidate: {e._unique()} ?= {unt}')
                            if e._unique() == unt:
                                tgt = e
                                break
                    else:
                        tgt = es[0]
                            

                    if not tgt:
                        raise RuntimeError(f'Failed to find element w/tag='
                                           f'{tn} and "name"={en}')
                        
                    cur = tgt

                if not cur:
                    raise RuntimeError(f'Failed to find element w/tag='
                                       f'{tn} and "name"={en}')

                # We have our target element.  As we cannot specify
                # changed attributes in extension elements, all we
                # need to do is to merge in the child elements 
                v(f'Target element is {cur}')

                self.mergeElement(cur,
                                  ext,
                                  depth          = 0,
                                  overwrite      = overwrite,
                                  skipAttributes = True)

                
            
            
    # ----------------------------------------------------------------
    def mergeElement(self,
                     dest,
                     src,
                     depth          = 0,
                     overwrite      = True,
                     skipAttributes = False):
        '''Merge element src into dest under the policy 'overwrite'

        This is a multi-stage process.

        First, we check if there are attributes to merge, and then do that.
        Second, we check if there are child nodes to merge, and then do that. 
        '''
        with VerboseGuard(f'Merging element '
                          f'{src._unique()}') as v:
            if not skipAttributes:
                self.mergeAttributes(dest,src,overwrite)
            self.mergeChildren (dest,src,
                                depth       = depth,
                                overwrite   = overwrite)

            if overwrite and dest.hasText() and src.hasText():
                # Perhaps append?
                dest.setText(src.getText())
                #dest.setText(dest.getText()+' '+src.getText())


    # ----------------------------------------------------------------
    def mergeAttributes(self,dest,src,overwrite=True):
        with VerboseGuard(f'Merging attributes of elements '
                          f'{src._unique()}') as v:
            srcAttributes  = src.getAttributes()
            destAttributes = dest.getAttributes()
            srcNames       = set(srcAttributes .keys()
                                 if srcAttributes  else [])
            
            if srcAttributes is None:
                return
            
            destNames      = set(destAttributes .keys()
                                 if destAttributes  else [])
            unique         = srcNames - destNames

            v(f'Adding attributes {unique}')
            dest.setAttributes(**{k:v for k,v in srcAttributes.items()
                                  if k in unique})

            if not overwrite:
                return

            overlap        = srcNames.intersection(destNames)
            v(f'Overwriting attributes {overlap}')
            dest.setAttributes(**{k:v for k,v in srcAttributes.items()
                                  if k in overlap})
        
    # ----------------------------------------------------------------
    def mergeChildren(self,dest,src,
                      overwrite   = True,
                      depth       = 0):
        if depth > 20:
            print(f'Maximum depth {depth} reached')
            return
        
        with VerboseGuard(f'Merging children of element '
                          f'{src._unique()}') as v:
            srcChildren  = set(src. getAllElements(cls=None))
            destChildren = set(dest.getAllElements(cls=None))
            unique       = srcChildren - destChildren
            overlap      = destChildren.intersection(srcChildren)

            with VerboseGuard(f'Adding {len(unique)} unique elements from '
                              f'{self._currentName} to destination {dest}') as vv:
                for e in unique:
                    vv(f'Adding unique element {e._unique()}')
                    dest.append(e)
                    # print(dest._node.toprettyxml())

            with VerboseGuard(f'Merging {len(overlap)} children from '
                              f'{self._currentName} into destination') as vv:
                for e in overlap:
                    ds = [ee for ee in destChildren if ee == e]
                    if len(ds) != 1:
                        raise RuntimeError('Should not happen')
                    d = ds[0]
                    # Only apply `assume_same` on top-level
                    self.mergeElement(d,e,
                                      depth       = depth+1,
                                      overwrite   = overwrite)

#
# EOF
#
