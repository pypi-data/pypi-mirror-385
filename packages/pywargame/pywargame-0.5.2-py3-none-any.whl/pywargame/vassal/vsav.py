## BEGIN_IMPORT
from . save import SaveData, SaveFile, SaveIO
from . moduledata import ModuleData
from . vmod import VMod
## END_IMPORT

# --------------------------------------------------------------------
class VSav:
    SAVE_DATA = 'savedata'
    
    def __init__(self,build,vmod):
        '''Create a VASSAL save file programmatically

        Parameters
        ----------
        build : xml.dom.Document
            `buildFile.xml` as XML
        vmod : VMod
            Module file
        '''
        from time import time 
        self._vmod  = vmod
        self._game  = build.getGame()
        self._start = int(time()*1000)
        

    def createSaveData(self,description=None):
        '''Create `savedgame`'''
        desc           = (self._game['description']
                          if description is None else description)
        self._saveData = SaveData(root=None)
        data           = self._saveData.addData()
        data.addVersion      (version    =self._game['version'])
        data.addVASSALVersion(version    =self._game['VassalVersion'])
        data.addDescription  (description=desc)
        data.addDateSaved    (milisecondsSinceEpoch=self._start)
        return self._saveData

    def createModuleData(self):
        '''Create `moduleData`'''
        self._moduleData = ModuleData()
        data = self._moduleData.addData()
        data.addVersion      (version    =self._game['version'])
        data.addVASSALVersion(version    =self._game['VassalVersion'])
        data.addName         (name       =self._game['name'])
        data.addDescription  (description=self._game['description'])
        data.addDateSaved    (milisecondsSinceEpoch=self._start)
        return self._moduleData
        
    def addSaveFile(self):
        '''Add a save file to the module

        Returns
        -------
        vsav : SaveFile
            Save file to add content to        
        '''
        self._saveFile = SaveFile(game=self._game,firstid=self._start)
        return self._saveFile

    def run(self,
            savename    = 'Save.vsav',
            description = None,
            update      = None):
        '''Run this to generate the save file

        Parameters
        ----------
        savename : str
            Name of save file to write
        description : str
            Short description of the save file
        update : callable or None
            A callable that can update trait states after the piece
            traits have been fully flattened.  The callable should
            adhere to the interface

                update(name,traits)

            where `name` is the name of the piece (entryName) and
            `traits` is a list of unrolled traits.

        '''
        from zipfile import ZipFile, ZIP_DEFLATED
        
        self.createSaveData(description=description)
        self.createModuleData()
        
        with self._vmod.getInternalFile(savename,'w') as vsav:
            with ZipFile(vsav,'w',ZIP_DEFLATED) as zvsav:
                # The key is set to 0xAA (alternating ones and zeros)
                SaveIO.writeInZip(zvsav,0xAA,
                                  self._saveFile.getLines(update=update))
            
                zvsav.writestr(VMod.MODULE_DATA, self._moduleData.encode())
                zvsav.writestr(VSav.SAVE_DATA,   self._saveData.encode())
            
#
# EOF
#
