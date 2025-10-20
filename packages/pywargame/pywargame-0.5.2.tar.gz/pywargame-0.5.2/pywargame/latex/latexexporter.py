## BEGIN_IMPORTS
from .. common import VerboseGuard, Verbose
from .. vassal.buildfile import BuildFile
from .. vassal.documentation import Documentation
from .. vassal.traits import *
from .. vassal.base import *
from .. vassal.moduledata import ModuleData
from .. vassal.exporter import Exporter
from pprint import pprint

## END_IMPORTS

# ====================================================================
#
# Exporter class 
#
class LaTeXExporter(Exporter):
    class Specials: 
        BATTLE_MARK       = 'wgBattleMarker'
        BATTLE_CTRL       = 'wgBattleCtrl'
        BATTLE_CALC       = 'wgBattleCalc'
        BATTLE_UNIT       = 'wgBattleUnit'
        ODDS_MARK         = 'wgOddsMarker'
        DRM_MARK          = 'wgDRMMarker'
        HIDDEN_NAME       = 'wg hidden unit'

    class Keys:
        MARK_BATTLE       = key(NONE,0)+',wgMarkBattle'
        CLEAR_BATTLE      = key(NONE,0)+',wgClearBattle'
        CLEAR_ALL_BATTLE  = key(NONE,0)+',wgClearAllBattle'
        ZERO_BATTLE       = key(NONE,0)+',wgZeroBattle'
        INCR_BATTLE       = key(NONE,0)+',wgIncrBattle'
        SET_BATTLE        = key(NONE,0)+',wgSetBattle'
        GET_BATTLE        = key(NONE,0)+',wgGetBattle'
        MARK_ODDS         = key(NONE,0)+',wgMarkOdds'
        MARK_RESULT       = key(NONE,0)+',wgMarkResult'
        CLEAR_MOVED       = key(NONE,0)+',wgClearMoved'
        ZERO_BATTLE_AF    = key(NONE,0)+',wgZeroBattleAF'
        ZERO_BATTLE_DF    = key(NONE,0)+',wgZeroBattleDF'
        ZERO_BATTLE_FRAC  = key(NONE,0)+',wgZeroBattleFrac'
        ZERO_BATTLE_ODDS  = key(NONE,0)+',wgZeroBattleOdds'
        ZERO_BATTLE_SHFT  = key(NONE,0)+',wgZeroBattleShift'
        ZERO_BATTLE_DRM   = key(NONE,0)+',wgZeroBattleDRM'
        ZERO_BATTLE_IDX   = key(NONE,0)+',wgZeroBattleIdx'
        CALC_BATTLE_AF    = key(NONE,0)+',wgCalcBattleAF'
        CALC_BATTLE_DF    = key(NONE,0)+',wgCalcBattleDF'
        CALC_BATTLE_FRAC  = key(NONE,0)+',wgCalcBattleFrac'
        CALC_BATTLE_ODDS  = key(NONE,0)+',wgCalcBattleOdds'
        CALC_BATTLE_SHFT  = key(NONE,0)+',wgCalcBattleShift'
        CALC_BATTLE_DRM   = key(NONE,0)+',wgCalcBattleDRM'
        CALC_BATTLE_IDX   = key(NONE,0)+',wgCalcBattleIdx'
        CALC_BATTLE_RES   = key(NONE,0)+',wgCalcBattleResult'
        CLEAR_BATTLE_PHS  = key(NONE,0)+',wgClearBattlePhs'
        RESOLVE_BATTLE    = key(NONE,0)+',wgResolveBattle'
        ROLL_DICE         = key(NONE,0)+',wgRollDice'
        DICE_INIT_KEY     = key(NONE,0)+',wgInitDice'
        TRAIL_TOGGLE_KEY  = key(NONE,0)+',wgTrailToggle'
        CLEAR_KEY         = key('C')
        CLEAR_ALL_KEY     = key('C',CTRL_SHIFT)
        DELETE_KEY        = key('D')
        ELIMINATE_KEY     = key('E')
        FLIP_KEY          = key('F')
        TRAIL_KEY         = key('T')
        RESTORE_KEY       = key('R') 
        MARK_KEY          = key('X')
        RESOLVE_KEY       = key('Y')
        ROTATE_CCWKey     = key('[')
        ROTATE_CWKey      = key(']')
        CHARTS_KEY        = key('A',ALT)
        OOB_KEY           = key('B',ALT)
        COUNTERS_KEY      = key('C',ALT)
        DEAD_KEY          = key('E',ALT)
        DICE_KEY          = key('6',ALT)
        RECALC_ODDS       = key('X',CTRL_SHIFT)
        UNDO_KEY          = key('Z')
        PRINT_CMD         = key(NONE,0)+'+wgPrint'

    class Globals:
        BATTLE_COUNTER    = 'wgBattleCounter'
        CURRENT_BATTLE    = 'wgCurrentBattle'
        PLACED_GLOBAL     = 'wgOddsPlaced'
        MARK_START        = 'wgPlaceMarks'
        CURRENT_ATTACKER  = 'wgCurrentAttacker'
        BATTLE_NO         = 'wgBattleNo'
        BATTLE_AF         = 'wgBattleAF'
        BATTLE_DF         = 'wgBattleDF'
        BATTLE_FRAC       = 'wgBattleFrac'
        BATTLE_IDX        = 'wgBattleIdx'
        BATTLE_ODDS       = 'wgBattleOdds'
        BATTLE_DRM        = 'wgBattleDRM'
        BATTLE_ODDSM      = 'wgBattleOddsMarker'
        BATTLE_SHIFT      = 'wgBattleShift'
        BATTLE_RESULT     = 'wgBattleResult'
        AUTO_ODDS         = 'wgAutoOdds'
        AUTO_RESULTS      = 'wgAutoResults'
        NO_CLEAR_MOVES    = 'wgNoClearMoves'
        NO_CLEAR_BATTLES  = 'wgNoClearBattles'
        DEBUG             = 'wgDebug'
        VERBOSE           = 'wgVerbose'
        TRAILS_FLAG       = 'wgTrailsFlag'
        NO_MOVEMENT_FLAG  = 'wgNoMovement'
        NO_COMBAT_FLAG    = 'wgNoCombat'
    
    def __init__(self,
                 vmodname      = 'Draft.vmod',
                 pdfname       = 'export.pdf',
                 infoname      = 'export.json',
                 title         = 'Draft',
                 version       = 'draft',
                 imageFormat   = 'png',
                 description   = '',     
                 rules         = None,
                 tutorial      = None,
                 patch         = None,
                 visible       = True,
                 vassalVersion = '3.6.7',
                 nonato        = False,
                 nochit        = False,
                 counterScale  = 1,
                 resolution    = 150):
        '''Exports a PDF and associated JSON files to a VASSAL module.

        Parameters
        ----------
        vmodname : str
            Name of module file to write
        pdfname : str
            Name of PDF file to read images from
        infoname : str
            Name of JSON file to read meta data from
        title : str
            Name of module
        version : str
            Version of midule
        description : str
            Short description of the module
        rules : str
            Optional name PDF file to attach as rules
        tutorial : str
            Optional name of a VASSAL log file to use as tutorial
        patch : str
            Optional name of Python script to post process the module
        visible : bool
            Make grids visible
        vassalVersion : str
            VASSAL version to encode this module for
        resolution : int
            Resolution for images (default 150)
        '''
        self._vmodname        = vmodname
        self._pdfname         = pdfname
        self._infoname        = infoname
        self._title           = title
        self._version         = version
        self._description     = description
        self._rules           = rules
        self._tutorial        = tutorial
        self._patch           = patch
        self._visible         = visible or version.lower() == 'draft'
        self._vassalVersion   = vassalVersion
        self._nonato          = nonato
        self._nochit          = nochit
        self._resolution      = resolution
        self._counterScale    = counterScale
        self._img_format      = imageFormat.lower()
        
        self._battleMark      = LaTeXExporter.Specials.BATTLE_MARK
        self._oddsMark        = LaTeXExporter.Specials.ODDS_MARK
        self._drmMark         = LaTeXExporter.Specials.DRM_MARK
        self._battleCtrl      = LaTeXExporter.Specials.BATTLE_CTRL
        self._battleCalc      = LaTeXExporter.Specials.BATTLE_CALC
        self._battleUnit      = LaTeXExporter.Specials.BATTLE_UNIT
        self._hiddenName      = LaTeXExporter.Specials.HIDDEN_NAME
        self._markBattle      = LaTeXExporter.Keys.MARK_BATTLE
        self._clearBattle     = LaTeXExporter.Keys.CLEAR_BATTLE
        self._clearAllBattle  = LaTeXExporter.Keys.CLEAR_ALL_BATTLE
        self._zeroBattle      = LaTeXExporter.Keys.ZERO_BATTLE
        self._incrBattle      = LaTeXExporter.Keys.INCR_BATTLE
        self._setBattle       = LaTeXExporter.Keys.SET_BATTLE
        self._getBattle       = LaTeXExporter.Keys.GET_BATTLE
        self._markOdds        = LaTeXExporter.Keys.MARK_ODDS
        self._markResult      = LaTeXExporter.Keys.MARK_RESULT
        self._clearMoved      = LaTeXExporter.Keys.CLEAR_MOVED
        self._zeroBattleAF    = LaTeXExporter.Keys.ZERO_BATTLE_AF
        self._zeroBattleDF    = LaTeXExporter.Keys.ZERO_BATTLE_DF
        self._zeroBattleFrac  = LaTeXExporter.Keys.ZERO_BATTLE_FRAC
        self._zeroBattleOdds  = LaTeXExporter.Keys.ZERO_BATTLE_ODDS
        self._zeroBattleShft  = LaTeXExporter.Keys.ZERO_BATTLE_SHFT
        self._zeroBattleDRM   = LaTeXExporter.Keys.ZERO_BATTLE_DRM
        self._zeroBattleIdx   = LaTeXExporter.Keys.ZERO_BATTLE_IDX
        self._calcBattleAF    = LaTeXExporter.Keys.CALC_BATTLE_AF
        self._calcBattleDF    = LaTeXExporter.Keys.CALC_BATTLE_DF
        self._calcBattleFrac  = LaTeXExporter.Keys.CALC_BATTLE_FRAC
        self._calcBattleOdds  = LaTeXExporter.Keys.CALC_BATTLE_ODDS
        self._calcBattleShft  = LaTeXExporter.Keys.CALC_BATTLE_SHFT
        self._calcBattleIdx   = LaTeXExporter.Keys.CALC_BATTLE_IDX
        self._calcBattleDRM   = LaTeXExporter.Keys.CALC_BATTLE_DRM
        self._calcBattleRes   = LaTeXExporter.Keys.CALC_BATTLE_RES
        self._clearBattlePhs  = LaTeXExporter.Keys.CLEAR_BATTLE_PHS
        self._resolveBattle   = LaTeXExporter.Keys.RESOLVE_BATTLE
        self._rollDice        = LaTeXExporter.Keys.ROLL_DICE
        self._diceInitKey     = LaTeXExporter.Keys.DICE_INIT_KEY
        self._clearKey        = LaTeXExporter.Keys.CLEAR_KEY
        self._clearAllKey     = LaTeXExporter.Keys.CLEAR_ALL_KEY
        self._deleteKey       = LaTeXExporter.Keys.DELETE_KEY
        self._eliminateKey    = LaTeXExporter.Keys.ELIMINATE_KEY
        self._flipKey         = LaTeXExporter.Keys.FLIP_KEY
        self._trailKey        = LaTeXExporter.Keys.TRAIL_KEY
        self._trailToggleKey  = LaTeXExporter.Keys.TRAIL_TOGGLE_KEY
        self._restoreKey      = LaTeXExporter.Keys.RESTORE_KEY
        self._markKey         = LaTeXExporter.Keys.MARK_KEY
        self._resolveKey      = LaTeXExporter.Keys.RESOLVE_KEY
        self._rotateCCWKey    = LaTeXExporter.Keys.ROTATE_CCWKey
        self._rotateCWKey     = LaTeXExporter.Keys.ROTATE_CWKey
        self._chartsKey       = LaTeXExporter.Keys.CHARTS_KEY
        self._oobKey          = LaTeXExporter.Keys.OOB_KEY
        self._countersKey     = LaTeXExporter.Keys.COUNTERS_KEY
        self._deadKey         = LaTeXExporter.Keys.DEAD_KEY
        self._diceKey         = LaTeXExporter.Keys.DICE_KEY
        self._recalcOdds      = LaTeXExporter.Keys.RECALC_ODDS        
        self._battleCounter   = LaTeXExporter.Globals.BATTLE_COUNTER
        self._currentBattle   = LaTeXExporter.Globals.CURRENT_BATTLE
        self._placedGlobal    = LaTeXExporter.Globals.PLACED_GLOBAL
        self._markStart       = LaTeXExporter.Globals.MARK_START
        self._currentAttacker = LaTeXExporter.Globals.CURRENT_ATTACKER
        self._battleNo        = LaTeXExporter.Globals.BATTLE_NO
        self._battleAF        = LaTeXExporter.Globals.BATTLE_AF
        self._battleDF        = LaTeXExporter.Globals.BATTLE_DF
        self._battleFrac      = LaTeXExporter.Globals.BATTLE_FRAC
        self._battleIdx       = LaTeXExporter.Globals.BATTLE_IDX
        self._battleOdds      = LaTeXExporter.Globals.BATTLE_ODDS
        self._battleOddsM     = LaTeXExporter.Globals.BATTLE_ODDSM
        self._battleShift     = LaTeXExporter.Globals.BATTLE_SHIFT
        self._battleDRM       = LaTeXExporter.Globals.BATTLE_DRM
        self._battleResult    = LaTeXExporter.Globals.BATTLE_RESULT
        self._autoOdds        = LaTeXExporter.Globals.AUTO_ODDS
        self._autoResults     = LaTeXExporter.Globals.AUTO_RESULTS
        self._noClearMoves    = LaTeXExporter.Globals.NO_CLEAR_MOVES
        self._noClearBattles  = LaTeXExporter.Globals.NO_CLEAR_BATTLES
        self._debug           = LaTeXExporter.Globals.DEBUG
        self._verbose         = LaTeXExporter.Globals.VERBOSE
        self._trailsFlag      = LaTeXExporter.Globals.TRAILS_FLAG
        self._noMoveFlag      = LaTeXExporter.Globals.NO_MOVEMENT_FLAG
        self._noCombatFlag    = LaTeXExporter.Globals.NO_COMBAT_FLAG
        self._battleMarks     = []
        self._oddsMarks       = []
        self._resultMarks     = []
        self._hidden          = None
        self._dice            = {}
        self._diceInit        = None
        self._printCmd        = LaTeXExporter.Keys.PRINT_CMD
        self._undoKey         = LaTeXExporter.Keys.UNDO_KEY
        
        with VerboseGuard('Overall settings') as v:
            v(f'Module file name:  {self._vmodname}')
            v(f'PDF file name:     {self._pdfname}')
            v(f'JSON file name:    {self._infoname}')
            v(f'Game title:        {self._title}')
            v(f'Game version:      {self._version}')
            v(f'Description:       {self._description}')
            v(f'Rules PDF file:    {self._rules}')
            v(f'Tutorial log:      {self._tutorial}')
            v(f'Patch scripts:     {self._patch}')
            v(f'Visible grids:     {self._visible}')
            v(f'Resolution:        {self._resolution}')
            v(f'Scale of counters: {self._counterScale}')
            v(f'Image format:      {self._img_format}')
              
        
    def setup(self):
        # Start the processing 
        self._info       = self.convertPages()
        self._categories, \
            self._mains, \
            self._echelons, \
            self._commands = self.writeImages(self._counterScale)


    def run(self):
        super(LaTeXExporter,self).run(self._vmodname,self._patch)
        
            

    # ================================================================
    def createProcess(self,args):
        '''Spawn a process and pipe output here

        Parameters
        ----------
        args : list
            List of process command line elements
        
        Returns
        -------
        pipe : subprocess.Pipe
            Pipe to read from 
        '''
        from os import environ
        from subprocess import Popen, PIPE

        return Popen(args,env=environ.copy(),stdout=PIPE,stderr=PIPE)

    # ----------------------------------------------------------------
    def addPws(self,opw=None,upw=None):
        '''Add a `Pws` element to arguments

        Add password options
        
        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        
        Returns
        -------
        element : Pws
            The added element
        '''
        args = []
        if upw is not None:  args.extend(['-upw',upw])
        if opw is not None:  args.extend(['-opw',opw])
        return args
            
    # ----------------------------------------------------------------
    def getPdfInfo(self,upw=None,opw=None,timeout=None):
        '''Get information about the PDF

        Parameters
        ----------
        opw : str
            Owner password (optional)
        upw : str
            User password (optional)
        timeout : int
            Time out in miliseconds for subprocesses

        Returns
        -------
        info : dict
             Image information 
        '''
        args = ['pdfinfo', self._pdfname ]
        args.extend(self.addPws(opw=opw,upw=upw))

        with VerboseGuard(f'Getting information from PDF {self._pdfname}'):
            proc = self.createProcess(args)
            try:
                out, err = proc.communicate(timeout=timeout)
            except:
                proc.kill()
                proc.communicate()
                raise RuntimeError(f'Failed to get PDF info: {e}')
            
            d = {}
            for field in out.decode('utf8','ignore').split('\n'):
                if field == '':
                    continue
                subfields  = field.split(':')
                key, value = subfields[0], ':'.join(subfields[1:])
                if key != '':
                    d[key] = (int(value.strip()) if key == 'Pages'
                              else value.strip())
            
            if 'Pages' not in d:
                raise ValueError(f'Page count not found from {self._pdfname}')

        return d

    # ----------------------------------------------------------------
    def getImagesInfo(self):
        '''Read in JSON information, and return as dictionary'''
        from json import load

        with VerboseGuard(f'Getting information from JSON {self._infoname}'):
            with open(self._infoname) as file:
                info = load(file)

        return info

    # ================================================================
    @classmethod
    def parseLength(cls,value,def_unit='px'):
        from re import match
        
        scales = {
            'px': 1,
            'pt': 1.25,
            'pc': 15,
            'in': 90,
            'mm': 3.543307,
            'cm': 35.43307,
            '%':  -1/100
        }

        if not value:
            return 0

        parts = match(r'^\s*(-?\d+(?:\.\d+)?)\s*(px|in|cm|mm|pt|pc|%)?', value)
        if not parts:
            raise RuntimeError(f'Unknown length format: "{value}"')

        number = float(parts.group(1))
        unit   = parts.group(2) or def_unit
        factor = scales.get(unit,None)

        if not factor:
            raise RuntimeError(f'Unknown unit: "{unit}"')
        
        return factor * number

    # ----------------------------------------------------------------
    @classmethod
    def scaleSVG(cls,buffer,factor):
        '''Buffer is bytes'''
        #from xml.dom.minidom import parse
        from re import split
        from io import StringIO, BytesIO
        
        if not LaTeXExporter.isSVG(buffer):
            return buffer

        with BytesIO(buffer) as stream:
            doc = xmlns.parse(stream)

        if not doc:
            raise RuntimeError('Failed to parse buffer as XML')

        root = doc.childNodes[0]
        getA = lambda e,n,d=None : \
            e.getAttribute(n) if e.hasAttribute(n) else d
        setA = lambda e,n,v : e.setAttribute(n,v)
        leng = LaTeXExporter.parseLength

        width  = leng(getA(root,'width', '0'))
        height = leng(getA(root,'height','0'))
        vport  = getA(root,'viewBox','0 0 0 0').strip()
        vp     = [leng(v) for v in split('[ \t,]',vport)]
        # print(f'Input WxH: {width}x{height} ({vp})')

        width  *= factor
        height *= factor
        vp     =  [factor * v for v in vp]
    
        # print(f'Scaled WxH: {width}x{height} ({vp})')

        if width <= 0 and vp:
            width  = vp[2] - vp[0]

        if height <= 0 and vp:
            height = vp[3] - vp[1]

        if not vp:
            vp = [0, 0, width, height]
            
        setA(root,'transform',f'scale({factor})')
        setA(root,'width', f'{width}')
        setA(root,'height',f'{height}')
        setA(root,'viewBox',' '.join([f'{v}' for v in vp]))


        with StringIO() as out:
            doc.writexml(out)
            return out.getvalue().encode()
 
    
    # ================================================================
    def convertPage(self,page,opw=None,upw=None,timeout=None):
        '''Convert a page from PDF into an image (bytes)

        Parameters
        ----------
        page : int
            Page number in the PDF to convert 
        opw : str
            Owner password (optional)
        upw : str
            User password (optional)
        timeout : int
            Time out in miliseconds for subprocesses

        Returns
        -------
        info : dict
             Image information 
        '''
        args = ['pdftocairo']
        if self._img_format != 'svg':
            args.extend([
                '-transp',
                '-singlefile'])

        args.extend([
                '-r', str(self._resolution),
                '-f', str(page),
                '-l', str(page),
                f'-{self._img_format}' ])
        args.extend(self.addPws(opw=opw,upw=upw))
        args.append(self._pdfname)
        args.append('-')
        
        # print(f'Conversion command',' '.join(args))
        proc = self.createProcess(args)

        try:
            out, err = proc.communicate(timeout=timeout)
        except Exception as e:
            proc.kill()
            proc.communicate()
            raise RuntimeError(f'Failed to convert page {page} of '
                               f'{self._pdfname}: {e}')

        if len(out) <= 0:
            raise RuntimeError(f'Failed to convert page {page} of '
                               f'{self._pdfname}: {err}')

        # This does not seem to work - VASSAL (and Inkscape) does not
        # apply the 'scale' transformation to the image!
        #
        # if self._img_format == 'svg':
        #     out = LaTeXExporter.scaleSVG(out,2)
            
        return out
        
        
    # ----------------------------------------------------------------
    def ignoreEntry(self,info,ignores=['<<dummy>>','<<eol>>']):
        '''Check if we should ignore an entry in the JSON file'''
        return info['category'] in ignores

    # ----------------------------------------------------------------
    def scaleImage(self,buffer,factor):
        from PIL import Image
        from io import BytesIO
        from math import isclose

        if isclose(factor,1): return buffer

        # print(f'Scaling image by factor {factor}')
        with Image.open(BytesIO(buffer)) as img:
            w, h = img.width, img.height
            cpy  = img.resize((int(factor*w),int(factor*h)))

            with BytesIO() as out:
                cpy.save(out,format='PNG')
                return out.getvalue()

        
    # ----------------------------------------------------------------
    def convertPages(self,opw=None,upw=None,timeout=None):
        '''Reads in JSON and pages from PDF and stores information
        dictionary, which is returned

        Parameters
        ----------
        opw : str
            Owner password (optional)
        upw : str
            User password (optional)
        timeout : int
            Time out in miliseconds for subprocesses

        Returns
        -------
        info : dict
             Image information 
        '''
        oargs    = {'opw':opw,'upw':upw }
        docinfo  = self.getPdfInfo()
        imgsinfo = self.getImagesInfo()

        if len(imgsinfo) - 1 != docinfo['Pages']:
            raise RuntimeError(f'Number of pages in {self._pdfname} '
                               f'{docinfo["Pages"]} not matched in JSON '
                               f'{self._infoname} -> {len(imgsinfo)}')

        with VerboseGuard(f'Converting {docinfo["Pages"]} '
                          f'pages in {self._pdfname}') as v:
            for i,info in enumerate(imgsinfo):
                if self.ignoreEntry(info): continue

                if i == 0: v(end='')
                v(f'[{info["number"]}]',end=' ',flush=True)
                info['img'] = self.convertPage(info['number'],**oargs)

            v('done')

        return imgsinfo

    # ----------------------------------------------------------------
    @classmethod
    def isSVG(cls,buffer):
        return buffer[:5] == b'<?xml'
    
    # ----------------------------------------------------------------
    def getBB(self,buffer):
        '''Get bounding box of image
    
        Parameters
        ----------
        buffer : bytes
             The image bytes
    
        Returns
        -------
        ulx, uly, lrx, lry : tuple
             The coordinates of the bounding box 
        '''
        from io import BytesIO
        
        with BytesIO(buffer) as inp:
            if LaTeXExporter.isSVG(buffer):
                from svgelements import SVG
            
                svg = SVG.parse(inp)
                # bb  = svg.bbox()
                # if bb is None:
                #     print(f'No bounding box!')
                #     bb = [0, 0, 1, 1]
                # else:
                #     bb  = [int(b) for b in bb]
                x, y, w, h = svg.x, svg.y, svg.width, svg.height
                bb = (x,y,x+w,y+h)
            else:
                from PIL import Image
    
                with Image.open(inp) as img:
                    bb  = img.getbbox()
    
        return bb

    # ----------------------------------------------------------------
    def getWH(self,buffer):
        '''Get bounding box of image
    
        Parameters
        ----------
        buffer : bytes
             The image bytes
    
        Returns
        -------
        ulx, uly, lrx, lry : tuple
             The coordinates of the bounding box 
        '''
        from io import BytesIO
        
        with BytesIO(buffer) as inp:
            if LaTeXExporter.isSVG(buffer):
                from svgelements import SVG

                svg = SVG.parse(inp)
                w, h = svg.x, svg.y, svg.width, svg.height
                # bb  = svg.bbox()
                # w, h = int(bb[2]-bb[0]),int(bb[3]-bb[1])
            else:
                from PIL import Image

                with Image.open(inp) as img:
                    w, h  = img.width, img.height
    
        return w,h
    
    # ----------------------------------------------------------------
    def getOutline(self,buffer):
        '''Get bounding box of image
    
        Parameters
        ----------
        buffer : bytes
             The image bytes
    
        Returns
        -------
        ulx, uly, lrx, lry : tuple
             The coordinates of the bounding box 
        '''
        from PIL import Image
        from io import BytesIO

        # print(buffer)
        with Image.open(BytesIO(buffer)) as img:
            bb  = img.getbbox()

            for r in range(bb[0],bb[2]):
                for c in range(bb[1],bb[3]):
                    pass #print(img.getpixel((c,r)))
    
        return None
    
            
    # ================================================================
    def writeImages(self,counterScale=1):
        '''From the information gathered about the images (including
        their bitmap representation, generate image files in the
        module

        '''
        categories = {}
        unittypes  = []
        echelons   = []
        commands   = []
        
        with VerboseGuard(f'Writing images in VMod '
                          f'{self._vmod.fileName()}',end=' ') as v:
            for info in self._info:
                if self.ignoreEntry(info): continue
            
                typ = info.get('category','counter')
                sub = info.get('subcategory','all')
                nam = info['name']
                num = info['number']
                
                info['filename'] = f'{nam.replace(" ","_")}.{self._img_format}'
                imgfn            = 'images/'+info['filename']
                if imgfn not in self._vmod.getFileNames():
                    if typ == 'counter' and self._img_format != 'svg':
                        # print(f'Possibly scale file {imgfn}')
                        info['img'] = self.scaleImage(info['img'],
                                                      counterScale)
                    # self.message(f'Writing image {imgfn}')
                    self._vmod.addFile(imgfn,info['img'])
            
                if sub == '':
                    info['subcategory'] = 'all'
                    sub                 = 'all'
            
                # Add into catalogue 
                if typ not in categories:
                    v('')
                    v(f'Adding category "{typ}"')
                    v('',end=' ')
                    categories[typ] = {}
                cat = categories[typ]
            
                if sub not in cat:
                    v('')
                    v(f'Adding sub-category "{sub}"')
                    v('',end=' ')
                    cat[sub] = {}
                tgt = cat[sub]

                v(f'[{nam}]',end=' ',flush=True,noindent=True)
                #self.message(f'Adding "{info["name"]}" to catalogue')
                #
                # Here we could handle multiple info's with the same
                # name by adding a unique postfix - e.g., for dices
                # what have non-uniform PMFs.
                #
                # if info['name'] in tgt:
                #     n = len([i for k,i in tgt.items() if k.startswith(info['name'])])
                #     info['name'] += '_' + str(n)
                #     info['filename'] =  info['name'].replace(' ','_') + '.png'
                unam = f'{nam}'
                tgt[unam] = info

                if self._nonato: continue
                
                # Get NATO App6c information, if any
                natoapp6c = info.get('natoapp6c',None)
                if natoapp6c is not None:
                    from re import sub
                    def clean(s):
                        return sub('.*=','',
                                   (sub(r'\[[^]]+\]','',s.strip())
                                    .replace('{','')
                                    .replace('}','')
                                    .replace('/',' '))).strip()
                    mains   = clean(natoapp6c.get('main',   ''))
                    lower   = clean(natoapp6c.get('lower',  ''))
                    upper   = clean(natoapp6c.get('upper',  ''))
                    echelon = clean(natoapp6c.get('echelon',''))
                    command = clean(natoapp6c.get('command',''))

                    
                    if mains is not None:
                        if len(lower) > 0: mains += ' '+lower
                        if len(upper) > 0: mains += ' '+upper
                        mains = sub(r'\[[^]]+\]','',mains)\
                            .replace('{','').replace('}','')#.split(',')
                        unittypes.append(mains.replace(',',' '))
                        unittypes.extend([s.strip().replace(',',' ')
                                          for s in mains.split(',')])
                        #if len(mains) > 1:
                        #    unittypes.append('+'.join(mains))
                        info['mains'] = mains
                        
                    if len(echelon) > 0:
                        echelons.append(echelon)
                        info['echelon'] = echelon
            
                    if len(command) > 0:
                        commands.append(command)
                        info['command'] = command
            
            
            # Finished loop over infos. Make unit types, echelons,
            # commands unique  
            v('done')

        return categories, set(unittypes), set(echelons), set(commands)

    # ================================================================
    def createModuleData(self):
        '''Create the `moduleData` file in the module
        '''
        with VerboseGuard(f'Creating module data'):
            self._moduleData = ModuleData()
            data = self._moduleData.addData()
            data.addVersion      (version=self._version)
            data.addVASSALVersion(version=self._vassalVersion)
            data.addName         (name=self._title)
            data.addDescription  (description=self._description)
            data.addDateSaved    ()
        
    # ================================================================
    def createBuildFile(self,
                        ignores = '(.*markers?|all|commons|.*hidden|[ ]+)'):
        '''Create the `buildFile.xml` file in the module.

        Parameters
        ----------
        ignores : str
            Regular expression to match ignored categories for factions
            determination. Python's re.fullmatch is applied to this
            regular exression against chit categories.  If the pattern
            is matched, then the chit is not considered to belong to a
            faction.

        '''
        from re import fullmatch, IGNORECASE
        with VerboseGuard(f'Creating build file') as v:
            self._build = BuildFile() # 'buildFile.xml')
            self._game  = self._build.addGame(name        = self._title,
                                              version     = self._version,
                                              description = self._description)
            doc = self.addDocumentation()
            self._game.addBasicCommandEncoder()
            
            # Extract the sides
            self._sides = [ k
                            for k in self._categories.get('counter',{}).keys()
                            if fullmatch(ignores, k, IGNORECASE) is None]
            v(f'Got sides: {", ".join(self._sides)}')
            
            v(f'Adding Global options')
            go = self._game.addGlobalOptions(
                autoReport         = GlobalOptions.PROMPT,
                centerOnMove       = GlobalOptions.PROMPT,
                nonOwnerUnmaskable = GlobalOptions.PROMPT,
                playerIdFormat     = '$playerName$')
            go.addOption(name='undoHotKey',value=self._undoKey)
            go.addOption(name='undoIcon',  value='/images/Undo16.gif')
            # go.addOptoin(name='stepHotKey',value='')
            go.addBoolPreference(name    = self._verbose,
                                 default = True,
                                 desc    = 'Be verbose',
                                 tab     = self._title)
            go.addBoolPreference(name    = self._debug,
                                 default = False,
                                 desc    = 'Show debug chat messages',
                                 tab     = self._title)
            go.addBoolPreference(name    = self._autoOdds,
                                 default = False,
                                 desc    = 'Calculate Odds on battle declaration',
                                 tab     = self._title)
            go.addBoolPreference(name    = self._autoResults,
                                 default = False,
                                 desc    = 'Resolve battle results automatically',
                                 tab     = self._title)
            go.addBoolPreference(name    = self._noClearMoves,
                                 default = False,
                                 desc    = ('Do not remove moved markers '
                                            'on phase change'),
                                 tab     = self._title)
            go.addBoolPreference(name    = self._noClearBattles,
                                 default = False,
                                 desc    = ('Do not remove battle markers '
                                            'on phase change'),
                                 tab     = self._title)
                                            
            v(f'Adding player roster')
            roster = self._game.addPlayerRoster()
            for side in self._sides:
                roster.addSide(side)
            
            v(f'Adding global properties')
            glob = self._game.addGlobalProperties()
            glob.addProperty(name='TurnTracker.defaultDocked',
                             initialValue=True)
            glob.addProperty(name         = self._trailsFlag,
                             initialValue = False,
                             isNumeric    = True,
                             description  = 'Global trails on/off')
            noMove = glob.addProperty(name         = self._noMoveFlag,
                                      initialValue = False,
                                      isNumeric    = True,
                                      description  = 'True when no movement')
            noMove.addChange(desc       = 'Set no movement',
                             mode       = ChangeProperty.DIRECT,
                             expression = '{true}',
                             hotkey     = named(self._noMoveFlag+'Set'),
                             reportFormat = ''
                             #(f'{{"~{self._noMoveFlag}="'
                             # f'+{self._noMoveFlag}'
                             # f'+" set"}}')
                             )
            noMove.addChange(desc       = 'Reset no movement',
                             mode       = ChangeProperty.DIRECT,
                             expression = '{false}',
                             hotkey     = named(self._noMoveFlag+'Clear'),
                             reportFormat = ''
                             #(f'{{"~{self._noMoveFlag}="'
                             #f'+{self._noMoveFlag}'
                             #f'+" cleared"}}')
                             )

            self._battleMarks   = self._categories\
                                      .get('counter',{})\
                                      .get('BattleMarkers',[])
            if len(self._battleMarks) > 0:
                v(f'We have battle markers')

                glob.addProperty(name         = self._battleCounter,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 min          = 0,
                                 max          = len(self._battleMarks),
                                 wrap         = True,
                                 description  = 'Counter of battles')
                glob.addProperty(name         = self._currentBattle,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 min          = 0,
                                 max          = len(self._battleMarks),
                                 wrap         = True,
                                 description  = 'Current battle number')
                glob.addProperty(name         = self._placedGlobal,
                                 initialValue = False,
                                 isNumeric    = True,
                                 wrap         = True,
                                 description  = 'Odds have been placed')
                glob.addProperty(name         = self._markStart,
                                 initialValue = False,
                                 isNumeric    = True,
                                 wrap         = True,
                                 description  = 'Mark battle in progress')
                glob.addProperty(name         = self._currentAttacker,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 min          = 0,
                                 max          = 1,
                                 wrap         = True,
                                 description  = 'Current unit is attacker')
                glob.addProperty(name         = self._battleAF,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 description  = 'Current battle AF')
                glob.addProperty(name         = self._battleDF,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 description  = 'Current battle DF')
                glob.addProperty(name         = self._battleFrac,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 description  = 'Current battle fraction')
                glob.addProperty(name         = self._battleShift,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 description  = 'Current battle odds shift')
                glob.addProperty(name         = self._battleDRM,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 description  = 'Current battle die roll mod')
                glob.addProperty(name         = self._battleOdds,
                                 initialValue = '',
                                 isNumeric    = False,
                                 description  = 'Current battle odds')
                glob.addProperty(name         = self._battleResult,
                                 initialValue = '',
                                 isNumeric    = False,
                                 description  = 'Current battle results')
                glob.addProperty(name         = self._battleIdx,
                                 initialValue = 0,
                                 isNumeric    = True,
                                 description  = 'Current battle odds index')
            
                noCombat = glob.addProperty(name         = self._noCombatFlag,
                                          initialValue = False,
                                          isNumeric    = True,
                                          description  = 'True when no movement')
                noCombat.addChange(desc       = 'Set no combat',
                                   mode       = ChangeProperty.DIRECT,
                                   expression = '{true}',
                                   hotkey     = named(self._noCombatFlag+'Set'),
                                   reportFormat = ''
                                   #(f'{{"~{self._noCombatFlag}="'
                                   #f'+{self._noCombatFlag}'
                                   #f'+" set"}}')
                                   )
                noCombat.addChange(desc       = 'Reset no combat',
                                   mode       = ChangeProperty.DIRECT,
                                   expression = '{false}',
                                   hotkey     = named(self._noCombatFlag+'Clear'),
                                   reportFormat = ''
                                   #(f'{{"~{self._noCombatFlag}="'
                                   #f'+{self._noCombatFlag}'
                                   #f'+" cleared"}}')
                                   )

            self._oddsMarks   = self._categories\
                                      .get('counter',{})\
                                      .get('OddsMarkers',[])
            if len(self._oddsMarks) > 0:
                v(f'We have odds markers')
                
            self._resultMarks   = self._categories\
                                      .get('counter',{})\
                                      .get('ResultMarkers',[])
            if len(self._resultMarks) > 0:
                v(f'We have result markers')
              
            self.addNotes()
            v(f'Adding turn track')
            turns = self._game.addTurnTrack(name='Turn',
                                            counter={
                                                'property': 'Turn',
                                                'phases': {
                                                    'property': 'Phase',
                                                    'names': self._sides } })
            turns.addHotkey(hotkey = self._clearMoved+'Phase',
                            name   = 'Clear moved markers',
                            reportFormat = (f'{{{self._debug}?('
                                            f'"`Clear all moved markers, "+'
                                            f'""):""}}'))
            if len(self._battleMarks) > 0:
                turns.addHotkey(
                    hotkey = self._clearBattlePhs,
                    name   = 'Clear battle markers',
                    reportFormat = (f'{{{self._debug}?('
                                    f'"`Clear all battle markers, "+'
                                    f'""):""}}'))

            self._dice   = self._categories\
                               .get('die-roll',{})
            if len(self._dice) > 0:
                v(f'We have symbolic dice')
                self._diceInit = []
                # from pprint import pprint 
                # pprint(self._dice,depth=2)
                for die, faces in self._dice.items():
                    ico  = self.getIcon(die+'-die-icon','')
                    # print(f'Die {die} icon="{ico}"')
                               
                    dmin = +100000
                    dmax = -100000
                    symb = self._game.addSymbolicDice(
                        name         = die+'Dice',
                        text         = die if ico == '' else '',
                        icon         = ico,
                        tooltip      = f'{die} die roll',
                        format       = (f'{{"<b>"+PlayerSide+"</b> "+'
                                        f'"(<i>"+PlayerName+"</i>): "+'+
                                        f'"{die} die roll: "+result1'
                                        # f'+" <img src=\'{die}-"+result1'
                                        # f'+".png\' width=24 height=24>"'
                                        f'}}'),
                        resultWindow = True,
                        windowX      = str(int(67 * self._resolution/150)),
                        windowY      = str(int(65 * self._resolution/150)));
                    sdie = symb.addDie(name = die);
                    w    = 0
                    h    = 0
                    for face, fdata in faces.items():
                        fn   = fdata['filename']
                        img  = fdata['img']
                        iw,ih = self.getWH(img)
                        w    = max(w,iw)
                        h    = max(h,ih)
                        val  = sum([int(s) for s in
                                    fn.replace(f'.{self._img_format}','')
                                    .replace(die+'-','').split('-')])
                        dmin = min(dmin,val)
                        dmax = max(dmax,val)
                        sdie.addFace(icon  = fn,
                                     text  = str(val),
                                     value = val);
                    symb['windowX'] = w # self._resolution/150
                    symb['windowY'] = h # self._resolution/150

                    self._diceInit.extend([
                        GlobalPropertyTrait(
                            ['',self._diceInitKey,
                             GlobalPropertyTrait.DIRECT,
                             f'{{{dmin}}}'],
                            name        = die+'Dice_result',
                            numeric     = True,
                            min         = dmin,
                            max         = dmax,
                            description = f'Initialize {die}Dice'),
                        ReportTrait(
                            self._diceInitKey,
                            report=(f'{{{self._debug}?("~Initialize '
                                    f'{die}Dice_result to {dmin}"):""}}'))
                    ])
                    

                # Add start-up key
                self._game.addStartupMassKey(
                    name        = 'Initialise dice results',
                    hotkey      = self._diceInitKey,
                    target      = '',
                    filter      = f'{{BasicName=="{self._hiddenName}"}}',
                    whenToApply = StartupMassKey.EVERY_LAUNCH,
                    reportFormat=f'{{{self._debug}?("`Init Dice"):""}}')
                
                                
                                

                
            
            self.addKeybindings(doc)
            self.addCounters()
            self.addInventory()
            self.addBoards()
            self.addDeadMap()
            self.addOOBs()
            self.addCharts()
            self.addDie()

    # ----------------------------------------------------------------
    def addDocumentation(self):
        '''Add documentation to the module.  This includes rules,
        key-bindings, and about elements.
        '''
        with VerboseGuard('Adding documentation') as v:
            doc = self._game.addDocumentation()
            if self._rules is not None:
                self._vmod.addExternalFile(self._rules,'rules.pdf')
                doc.addBrowserPDFFile(title   = 'Show rules',
                                      pdfFile = 'rules.pdf')
            
            if self._tutorial is not None:
                self._vmod.addExternalFile(self._tutorial,'tutorial.vlog')
                doc.addTutorial(name            = 'Tutorial',
                                logfile         = 'tutorial.vlog',
                                launchOnStartup = True)
            
            
            fronts    = self._categories.get('front',{}).get('all',[])
            front     = list(fronts.values())[0] if len(fronts) > 0 else None
            if front is not None:
                v(f'Adding about page')
                doc.addAboutScreen(title=f'About {self._title}',
                                   fileName = front['filename'])

            return doc

    # ----------------------------------------------------------------
    def addKeybindings(self,doc):
        keys = [
            ['Alt-A',	    '-',	    'Show the charts panel'],
            ['Alt-B',	    '-',	    'Show the OOBs'],
            ['Alt-C',	    '-',	    'Show the counters panel'],
            ['Alt-E',	    '-',	    'Show the eliminated units'],
            ['Alt-I',	    '-',	    'Show/refresh inventory window'],
            ['Alt-M',	    '-',	    'Show map'],
            ['Alt-T',	    '-',	    'Increase turn track'],
            ['Alt-S',       '-',            'Toggle movement trails'],
            ['Alt-Shift-T', '-',	    'Decrease turn track'],
            ['Alt-6',	    '-',	    'Roll the dice'],
            ['Alt-&rarr;',  'Board',
             'Centre on nearest un-moved piece'],
            ['Ctrl-D',	    'Board,Counter','Delete counters'],
            ['Ctrl-E',	    'Board,Counter','Eliminate counters'],
            ['Ctrl-F',	    'Board,Counter','Flip counters'],
            ['Ctrl-M',	    'Board,Counter','Toggle "moved" markers'],
            ['Ctrl-O',	    'Board',	    'Hide/show counters'],
            ['Ctrl-R',	    'Board,Counter','Restore unit'],
            ['Ctrl-T',	    'Board,Counter','Toggle move trail'],
            ['Ctrl-Z',	    'Board',        'Undo last move'],
            ['Ctrl-+',	    'Board',	    'Zoom in'],
            ['Ctrl--',	    'Board',	    'Zoom out'],
            ['Ctrl-=',	    'Board',	    'Select zoom'],
            ['Ctrl-Shift-O','Board',        'Show overview map'],
            ['&larr;,&rarr;,&uarr;&darr;','Board',
             'Scroll board left, right, up, down (slowly)'],
            ['PnUp,PnDn',                 'Board',
	     'Scroll board up/down (fast)'],
            ['Ctrl-PnUp,Ctrl-PnDn',       'Board',
             'Scroll board left/right (fast)'],
            ['Mouse-scroll up/down',	  'Board',
             'Scroll board up//down'],
            ['Shift-Mouse-scroll up/down','Board',
             'Scroll board right/left'],
            ['Ctrl-Mouse-scroll up/down', 'Board','Zoom board out/in'],
            ['Mouse-2',	'Board',	  'Centre on mouse']]
        if self._battleMarks:
            for a,l in zip(
                    ['Ctrl-D',
                     'Ctrl-Shift-O',
                     'Ctrl-+',
                     'Ctrl-+',
                     'Ctrl-D'],
                    [['Ctrl-C',      'Counter',      'Clear battle'],
                     ['Ctrl-Shift-C','Board',        'Clear all battle'],
                     ['Ctrl-X',      'Board,Counter','Mark battle'],
                     ['Ctrl-Shift-X','Board,Counter','Recalculate Odds'],
                     ['Ctrl-Y',      'Board,Counter','Resolve battle'],
                     ['Alt-&darr;',  'Board',
                      'Centre on nearest un-resolved combat'],
                     ]):
                ks   = [k[0] for k in keys]
                didx = ks.index(a)
                keys.insert(didx,l)
            
        self._vmod.addFile('help/keys.html',
                           Documentation.createKeyHelp(
                               keys,
                               title=self._title,
                               version=self._version))
        doc.addHelpFile(title='Key bindings',fileName='help/keys.html')
        
    # ----------------------------------------------------------------
    def addNatoPrototypes(self,prototypes):
        # Add unit categories as prototypes 
        for n,c in zip(['Type','Echelon','Command'],
                       [self._mains, self._echelons, self._commands]):
            sc = set([cc.strip() for cc in c])
            with VerboseGuard(f'Adding prototypes for "{n}"') as vv:
                for i,cc in enumerate(sc):
                    cc = cc.strip()
                    if len(cc) <= 0: continue
                    vv(f'[{cc}] ',end='',flush=True,noindent=True)
                    p = prototypes.addPrototype(name        = f'{cc} prototype',
                                                description = '',
                                                traits      = [MarkTrait(n,cc),
                                                               BasicTrait()])
                vv('')
        
    # ----------------------------------------------------------------
    def addBattleControlPrototype(self,prototypes):
        # Control of battles.
        #
        # This has traits to
        #
        # - Zero battle counter
        # - Increment battle counter
        # - Set current battle number
        # - Mark battle
        # - Calculate odds
        #
        # When wgMarkBattle is issued to this piece, then
        #
        # - Increment battle counter
        # - Set global current battle
        # - Trampoline to GCK markBattle
        #   - For all selected pieces, issue markBattle
        #     - All wgBattleUnit pieces then
        #       - Get current battle # and store
        #       - Add marker on top of it self
        # - Issue calculateOddsAuto
        #   - If auto odds on, go to calcOddsStart,
        #     - Trampoline to GCK calcOddsAuto
        #       - Which sends calcOddsStart to all markers
        #         - For each mark
        #           - Set current battle to current global
        #           - Trampoline calcOdds via GKC
        #             - Send calcBattleOdds to wgBattleCalc
        #               - Zero odds
        #               - Calculate fraction
        #                 - Zero fraction
        #                 - Calculate total AF
        #                   - Zero AF
        #                   - via trampoline to GKC
        #                 - Calculate total DF
        #                   - Zero DF
        #                   - via trampoline to GKC
        #                 - Real fraction calculation
        #                   - From calculate fraction 
        #                   - Access via calculate trait
        #               - Calculate shift
        #                 - Zero shift
        #                 - Trampoline to GKC
        #                 - Access via calculate trait
        #               - Calculate index
        #                 - Via calculated OddsIndex
        #               - Calculate odds real
        #                 - Via calculated Index to odds 
        #               - Calculate DRM
        #                 - Zero DRM
        #                 - Trampoline to GKC
        #                 - Access via calculate trait
        #           - Do markOddsAuto which selects between odds
        #             - Do markOddsReal+OddsIndex
        #               - Set global battle #
        #               - Place marker
        #                 - Take global battle #
        #            - De-select all other marks to prevent
        #              further propagation
        #              
        if len(self._battleMarks) <= 0:
            return False

        n = len(self._battleMarks)
        # --- Battle counter control - reset and increment -----------
        traits = [
            GlobalPropertyTrait(
                ['',self._zeroBattle,GlobalPropertyTrait.DIRECT,'{0}'],
                ['',self._incrBattle,GlobalPropertyTrait.DIRECT,
                 f'{{({self._battleCounter}%{n})+1}}'],
                name        = self._battleCounter,
                numeric     = True,
                min         = 0,
                max         = n,
                wrap        = True,
                description = 'Zero battle counter',
            ),
            # Set global property combat # from this 
            GlobalPropertyTrait(
                ['',self._setBattle,GlobalPropertyTrait.DIRECT,
                 f'{{{self._battleCounter}}}'],
                name        = self._currentBattle,
                numeric     = True,
                min         = 0,
                max         = n,
                wrap        = True,
                description = 'Zero battle counter',
            ),
            ReportTrait(self._zeroBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": zero battle counter: "'
                                f'+{self._battleCounter}):""}}')),
            ReportTrait(self._incrBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": '
                                f'increment battle counter: "'
                                f'+{self._battleCounter}):""}}')),
            ReportTrait(self._setBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": set current battle: "+'
                                f'{self._battleCounter}+" -> "+'
                                f'{self._currentBattle}):""}}')),
            # Set global property combat # from this 
            GlobalPropertyTrait(
                ['',self._markBattle+'ResetPlaced',GlobalPropertyTrait.DIRECT,
                 f'{{false}}'],
                name        = self._placedGlobal,
                numeric     = True,
                description = 'Reset the placed marker flag',
            ),
            GlobalPropertyTrait(
                ['',self._markBattle+'ResetPlaced',GlobalPropertyTrait.DIRECT,
                 f'{{true}}'],
                ['',self._calcBattleOdds+'Start',GlobalPropertyTrait.DIRECT,
                 f'{{false}}'],
                name        = self._markStart,
                numeric     = True,
                description = 'Reset the placed marker flag',
            ),
            ReportTrait(self._markBattle+'ResetPlaced',
                        report = (f'{{{self._debug}?("~"+BasicName+'
                                  f'" reset placed "+'
                                  f'{self._placedGlobal}+" markStart="+'
                                  f'{self._markStart}):""}}')),
            GlobalHotkeyTrait(name         = '',
                              key          = self._markBattle+'Trampoline',
                              globalHotkey = self._markBattle,
                              description  = 'Mark selected for battle'),
            ReportTrait(self._markBattle+'Trampoline',
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": forward mark battle: "+'
                                f'{self._battleCounter}):""}}')),
            GlobalHotkeyTrait(name         = '',
                              key          = self._calcBattleOdds+'Start',
                              globalHotkey = self._calcBattleOdds+'Auto',
                              description  = 'Trampoline to global'),
            ReportTrait(self._calcBattleOdds+'Start',
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": start forward odds: "+'
                                f'{self._battleCounter}+" markStart="+'
                                f'{self._markStart}):""}}')),
            DeselectTrait(command    = '',
                          key        = self._calcBattleOdds+'Deselect',
                          deselect   = DeselectTrait.ALL),
            ReportTrait(self._calcBattleOdds+'Deselect',
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": select only this: "+'
                                f'{self._battleCounter}):""}}')),
            TriggerTrait(command    = '',
                         key        = self._calcBattleOdds+'Auto',
                         actionKeys = [self._calcBattleOdds+'Start'],
                         property   = f'{{{self._autoOdds}==true}}'),
            ReportTrait(self._calcBattleOdds+'Auto',
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": auto forward odds: "+'
                                f'{self._battleCounter}):""}}')),
            TriggerTrait(command    = '',
                         key        = self._markBattle,
                         actionKeys = [self._incrBattle,
                                       self._setBattle,
                                       self._markBattle+'ResetPlaced',
                                       self._markBattle+'Trampoline',
                                       self._calcBattleOdds+'Auto']),
            ReportTrait(self._markBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": mark battle: "+'
                                f'{self._battleCounter}):""}}')),
            GlobalHotkeyTrait(name         = '',
                              key          = self._clearAllBattle+'Trampoline',
                              globalHotkey = self._clearAllBattle,
                              description  = 'Clear all battles'),
            TriggerTrait(command    = '',
                         key        = self._clearAllBattle,
                         actionKeys = [self._clearAllBattle+'Trampoline',
                                       self._zeroBattle]),
            ReportTrait(self._clearBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+": clear battle: "+'
                                f'{self._battleCounter}):""}}')),
            GlobalHotkeyTrait(name         = '',
                              key          = self._clearMoved+'Trampoline',
                              globalHotkey = self._clearMoved,
                              description  = 'Clear moved markers'),
            MarkTrait(name=self._battleCtrl,value=True),            
            BasicTrait()]
        prototypes.addPrototype(name        = self._battleCtrl,
                                description = '',
                                traits      = traits)
        return True

    # ----------------------------------------------------------------
    def addBattleCalculatePrototype(self,prototypes):
        # --- Batttle AF, DF, Odds -----------------------------------
        # This calculate odds derivation from stated odds.
        with VerboseGuard(f'Making battle calculation prototype') as v:
            calcIdx   = 0
            maxIdx    = len(self._oddsMarks)+1
            minIdx    = 0
            idx2Odds  = '""'
            calcFrac  = 1
            if len(self._oddsMarks) > 0:
                odds = [o.replace('odds marker','').strip() for
                        o in self._oddsMarks]
                ratios = all([o == '0' or ':' in o for o in odds])

                if ratios: # All is ratios!
                    def calc(s):
                        if s == '0': return 0
                        num, den = [float(x.strip()) for x in s.split(':')]
                        return num/den
                    ratios = [[calc(s),s] for s in odds]
                    ind    = [i[0] for i in sorted(enumerate(ratios),
                                                   key=lambda x:x[1][0])]
                    #print(f'=== Rations: {ratios}, Index: {ind[::-1]}')
                    calcIdx  = ':'.join([f'{self._battleFrac}>={ratios[i][0]}?'
                                         f'({i+1})'
                                         for i in ind[::-1]]) + ':0'
                    idx2Odds = ':'.join([f'OddsIndex=={i+1}?'
                                       f'"{ratios[i][1]}"'
                                       for i in ind[::-1]]) + ':""'
                    calcFrac = (f'{{{self._battleDF}==0?0:'
                                f'(((double)({self._battleAF}))'
                                fr'\/{self._battleDF})}}')
                    v(f'Calculate index: {calcIdx}')
                    v(f'Index to odds: {idx2Odds}')
                else:
                    try:
                        nums     = [[int(o),o] for o in odds]
                        calcFrac = f'{{{self._battleAF}-{self._battleDF}}}'
                        ind      = [i[0] for i in sorted(enumerate(nums),
                                                         key=lambda x:x[1])]
                        calcIdx  = ':'.join([f'{self._battleFrac}>={nums[i][0]}?'
                                             f'({i+1})'
                                             for i in ind[::-1]])+':0'
                        idx2Odds = ':'.join([f'OddsIndex=={i+1}?"{nums[i][1]}"'
                                             for i in ind[::-1]]) + ':""'
                        vidx2Odds = '\t'+idx2Odds.replace(':',':\n\t')
                        #print(f'Index to odds: {vidx2Odds}')
                    except:
                        pass 
                    
            traits = [
                CalculatedTrait(# This should be changed to game rules
                    name        = 'OddsShift',
                    expression  = f'{{{self._battleShift}}}',
                    description = 'Calculated internal oddsshift'),
                CalculatedTrait(# This should be changed to game rules
                    name        = 'DRM',
                    expression  = f'{{{self._battleDRM}}}',
                    description = 'Calculated internal oddsshift'),
                CalculatedTrait(# This should be changed to game rules
                    name        = 'OddsIndexRaw',
                    expression  = f'{{{calcIdx}}}',
                    description = 'Calculated internal odds index'),
                CalculatedTrait(# This should be changed to game rules
                    name        = 'OddsIndexLimited',
                    expression  = (f'{{OddsIndexRaw>{maxIdx}?{maxIdx}:'
                                   f'OddsIndexRaw<{minIdx}?{minIdx}:'
                                   f'OddsIndexRaw}}'),
                    description = 'Calculated internal limited odds index'),
                CalculatedTrait(# This should be changed to game rules
                    name        = 'OddsIndex',
                    expression  = (f'{{OddsIndexLimited+OddsShift}}'),
                    description = 'Calculated internal odds index (with shift)'),
                CalculatedTrait(# This should be changed to game rules
                    name        = 'BattleFraction',
                    expression  = calcFrac,
                    description = 'Calculated fraction off battle'),
                GlobalPropertyTrait(
                    ['',self._zeroBattleShft,GlobalPropertyTrait.DIRECT,'{0}'],
                    name        = self._battleShift,
                    numeric     = True,
                    description = 'Zero battle odds shift',
                ),
                GlobalPropertyTrait(
                    ['',self._zeroBattleDRM,GlobalPropertyTrait.DIRECT,'{0}'],
                    name        = self._battleDRM,
                    numeric     = True,
                    description = 'Zero battle die roll modifier',
                ),
                GlobalPropertyTrait(
                    ['',self._zeroBattleAF,GlobalPropertyTrait.DIRECT,'{0}'],
                    name        = self._battleAF,
                    numeric     = True,
                    description = 'Zero battle AF',
                ),
                GlobalPropertyTrait(
                    ['',self._zeroBattleDF,GlobalPropertyTrait.DIRECT,'{0}'],
                    name        = self._battleDF,
                    numeric     = True,
                    description = 'Zero battle AF',
                ),
                # {wgBattleDF==0?0:(double(wgBattleAF)/wgBattleDF)}
                GlobalPropertyTrait(
                    ['',self._zeroBattleFrac,GlobalPropertyTrait.DIRECT,'{0}'],
                    ['',self._calcBattleFrac+'Real',GlobalPropertyTrait.DIRECT,
                     '{BattleFraction}'],
                    name        = self._battleFrac,
                    description = 'Calculate battle fraction',
                ),
                GlobalPropertyTrait(
                    ['',self._zeroBattleIdx,GlobalPropertyTrait.DIRECT,'{0}'],
                    ['',self._calcBattleIdx,GlobalPropertyTrait.DIRECT,
                     '{OddsIndex}'],
                    name        = self._battleIdx,
                    description = 'Calculate battle odds index',
                ),
                GlobalPropertyTrait(
                    ['',self._zeroBattleOdds,GlobalPropertyTrait.DIRECT,'{""}'],
                    ['',self._calcBattleOdds+'Real',GlobalPropertyTrait.DIRECT,
                     f'{{{idx2Odds}}}'],
                    name        = self._battleOdds,
                    description = 'Calculate battle odds',
                ),
                GlobalHotkeyTrait(
                    name         = '',# Forward to units
                    key          = self._calcBattleAF+'Trampoline',
                    globalHotkey = self._calcBattleAF,
                    description  = 'Calculate total AF'),
                GlobalHotkeyTrait(
                    name         = '',# Forward to units
                    key          = self._calcBattleDF+'Trampoline',
                    globalHotkey = self._calcBattleDF,
                    description  = 'Calculate total DF'),
                GlobalHotkeyTrait(
                    name         = '',# Forward to units
                    key          = self._calcBattleShft+'Trampoline',
                    globalHotkey = self._calcBattleShft,
                    description  = 'Calculate total shift'),
                GlobalHotkeyTrait(
                    name         = '',# Forward to units
                    key          = self._calcBattleDRM+'Trampoline',
                    globalHotkey = self._calcBattleDRM,
                    description  = 'Calculate total DRM'),
                TriggerTrait(
                    command        = '',
                    key            = self._calcBattleAF,
                    actionKeys     = [self._zeroBattleAF,
                                      self._calcBattleAF+'Trampoline']),
                TriggerTrait(
                    command        = '',
                    key            = self._calcBattleDF,
                    actionKeys     = [self._zeroBattleDF,
                                      self._calcBattleDF+'Trampoline']),
                TriggerTrait(
                    command        = '',
                    key            = self._calcBattleShft,
                    actionKeys     = [self._zeroBattleShft,
                                      self._calcBattleShft+'Trampoline']),
                TriggerTrait(
                    command        = '',
                    key            = self._calcBattleDRM,
                    actionKeys     = [self._calcBattleDRM+'Trampoline']),
                TriggerTrait(
                    command        = '',
                    key            = self._calcBattleFrac,
                    actionKeys     = [self._zeroBattleFrac,
                                      self._zeroBattleDRM,
                                      self._calcBattleAF,
                                      self._calcBattleDF,
                                      self._calcBattleFrac+'Real']),
                # Entry point for calculations 
                TriggerTrait(
                    command        = '',
                    key            = self._calcBattleOdds,
                    actionKeys     = [self._zeroBattleOdds,
                                      self._calcBattleFrac,
                                      self._calcBattleShft,
                                      self._calcBattleIdx,
                                      self._calcBattleDRM,
                                      self._calcBattleOdds+'Real']),
                ReportTrait(
                    self._zeroBattleAF,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Reset AF: "+'
                            f'{self._battleAF}):""}}')),
                ReportTrait(
                    self._zeroBattleDF,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Reset DF: "+'
                            f'{self._battleDF}):""}}')),
                ReportTrait(
                    self._zeroBattleFrac,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Reset fraction: "+'
                            f'{self._battleFrac}):""}}')),
                ReportTrait(
                    self._zeroBattleOdds,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Reset odds: "+'
                            f'{self._battleOdds}):""}}')),
                ReportTrait(
                    self._zeroBattleShft,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Reset Shift: "+'
                            f'{self._battleShift}):""}}')),
                ReportTrait(
                    self._zeroBattleDRM,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Reset DRM: "+'
                            f'{self._battleDRM}):""}}')),
                ReportTrait(
                    self._calcBattleAF,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Total AF: "+'
                            f'{self._battleAF}):""}}')),
                ReportTrait(
                    self._calcBattleDF,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Total DF: "+'
                            f'{self._battleDF}):""}}')),
                ReportTrait(
                    self._calcBattleShft,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Battle odds shift: "+'
                            f'{self._battleShift}):""}}')),
                ReportTrait(
                    self._calcBattleDRM,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Battle DRM: "+'
                            f'{self._battleDRM}):""}}')),
                ReportTrait(
                    self._calcBattleFrac,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Battle fraction: "+'
                            f'{self._battleFrac}):""}}')),
                ReportTrait(
                    self._calcBattleOdds,
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Battle odds: "+'
                            f'{self._battleOdds}+" ("+'
                            f'{self._battleIdx}+")"):""}}')),
                ReportTrait(
                    self._calcBattleFrac+'Real',
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Battle fraction: "+'
                            f'{self._battleFrac}+'
                            f'" AF="+{self._battleAF}+'
                            f'" DF="+{self._battleDF}'
                            f'):""}}')),
                ReportTrait(
                    self._calcBattleOdds+'Real',
                    report=(f'{{{self._debug}?'
                            f'("~"+BasicName+" @ "+LocationName+'
                            f'": Battle odds: "+'
                            f'{self._battleOdds}+'
                            f'" ("+{self._battleIdx}+","+OddsShift+","+'
                            f'" raw="+OddsIndexRaw+","+'
                            f'" limited="+OddsIndexLimited+","+'
                            f'" -> "+OddsIndex+","+'
                            f'{self._battleShift}+")"+'
                            f'" DRM="+{self._battleDRM}+'
                            f'" Fraction="+{self._battleFrac}+'
                            f'" AF="+{self._battleAF}+'
                            f'" DF="+{self._battleDF}'
                            f'):""}}')),
                ReportTrait(
                    self._calcBattleOdds+'Real',
                    report=(f'{{{self._verbose}?'
                            f'("! Battle # "'
                            f'+{self._battleNo}'
                            f'+{self._currentBattle}'
                            f'+" AF="+{self._battleAF}'
                            f'+" DF="+{self._battleDF}'
                            f'+" => "+{self._battleOdds}'
                            f'+" DRM="+{self._battleDRM}'
                            # f'+" <img src=\'odds_marker_"'
                            # f'+{self._battleOdds}+".png\' "'
                            # f'+" width=24 height=24>"'
                            f'):""}}')),
                MarkTrait(name=self._battleCalc,value=True),            
                BasicTrait()]
            prototypes.addPrototype(name        = self._battleCalc,
                                    description = '',
                                    traits      = traits)
        
    # ----------------------------------------------------------------
    def addBattleUnitPrototype(self,prototypes):
        # --- Battle units that set battle markers -------------------
        # 
        # - Trait to add battle number 1 to max
        #
        # - Trigger trait for each of these using the global property
        #   for the current battle
        #
        traits = [
            # getBattle retrieves the battle number from the global property.
            # clearBattle sets piece battle to -1
            DynamicPropertyTrait(['',self._getBattle,
                                  DynamicPropertyTrait.DIRECT,
                                  f'{{{self._currentBattle}}}'],
                                 ['',self._clearBattle,
                                  DynamicPropertyTrait.DIRECT,
                                  f'{{-1}}'],
                                 name        = self._battleNo,
                                 numeric     = True,
                                 value       = f'{{-1}}',
                                 description = 'Set battle number'),
            # This setBattle sets current attacker in global property
            GlobalPropertyTrait(['',self._setBattle,
                                 GlobalPropertyTrait.DIRECT,
                                 '{IsAttacker}'],
                                name        = self._currentAttacker,
                                numeric     = True,
                                description = 'Set attacker'),
            ReportTrait(self._getBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" current battle # "+'
                                f'{self._currentBattle}+" -> "+'
                                f'{self._battleNo}):""}}')),
            ReportTrait(self._clearBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" Clear this global="+'
                                f'{self._currentBattle}+" this="+'
                                f'{self._battleNo}):""}}')),
        ]
        place  = []
        trig   = []
        rept   = []
        for i, bm in enumerate(self._battleMarks):
            kn   = self._markBattle+str(i+1)
            skel = PlaceTrait.SKEL_PATH()
            path = skel.format('BattleMarkers',bm)

            place.append(
                PlaceTrait(command       = '',#f'Add battle marker {i}',
                           key           = kn,
                           markerSpec    = path,
                           markerText    = 'null',
                           xOffset       = -8,
                           yOffset       = -16,
                           matchRotation = False,
                           afterKey      = self._getBattle,
                           gpid          = self._game.nextPieceSlotId(),
                           description   = f'Add battle marker {i+1}',
                           placement     = PlaceTrait.ABOVE,
                           above         = False))
            # Get current global battle number
            # Set current battle
            # Filtered on current global battle # is equal to 
            trig.append(
                TriggerTrait(command     = '',#Mark battle',
                             key         = self._markBattle,
                             actionKeys  = [self._getBattle,
                                            self._setBattle,
                                            kn],
                             property    = f'{{{self._currentBattle}=={i+1}}}'))
            rept.append(
                ReportTrait(kn,
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+" placing marker ({i+1})'
                                    f' ="+ {self._currentBattle}+"'
                                    f'={kn}"):""}}')))

        oth = [
            TriggerTrait(name       = 'Declare combat',
                         command    = 'Declare battle',
                         key        = self._markKey,
                         actionKeys = [self._markBattle+'Unit'],
                         property   = f'{{{self._battleNo}<=0}}'
                         ),
            GlobalHotkeyTrait(name         = '',#'Declare battle',
                              key          = self._markBattle+'Unit',
                              globalHotkey = self._markBattle+'Unit',
                              description  = 'Mark for combat'),
            GlobalPropertyTrait(
                ['',self._calcBattleAF,GlobalPropertyTrait.DIRECT,
                f'{{EffectiveAF+{self._battleAF}}}'],
                name        = self._battleAF,
                numeric     = True,
                description = 'Update battle AF'),
            GlobalPropertyTrait(
                ['',self._calcBattleDF,GlobalPropertyTrait.DIRECT,
                 f'{{EffectiveDF+{self._battleDF}}}'],
                 name        = self._battleDF,
                numeric     = True,
                description = 'Update battle DF'),
            GlobalPropertyTrait(
                ['',self._calcBattleShft,GlobalPropertyTrait.DIRECT,
                 f'{{OddsShift}}'],
                name        = self._battleShift,
                numeric     = True,
                description = 'Update battle shift',
            ),
            GlobalPropertyTrait(
                ['',self._calcBattleDRM,GlobalPropertyTrait.DIRECT,
                 f'{{DRM+{self._battleDRM}}}'],
                name        = self._battleDRM,
                numeric     = True,
                description = 'Update battle die roll modifier',
            ),
            CalculatedTrait(#This could be redefined in module 
                name        = 'EffectiveAF',
                expression  = '{CF}',
                description = 'Current attack factor'),
            CalculatedTrait(#This could be redefined in module 
                name        = 'EffectiveDF',
                expression  = '{DF}',
                description = 'Current defence factor'),
            CalculatedTrait(#This could be redefined in module 
                name        = 'IsAttacker',
                expression  = '{Phase.contains(Faction)}',
                description = 'Check if current phase belongs to faction'),
            CalculatedTrait(#This could be redefined in module 
                name        = 'OddsShift',
                expression  = f'{{{self._battleShift}}}',
                description = 'Add to odds shift'),
            # CalculatedTrait(#This could be redefined in module 
            #     name        = 'DRM',
            #     expression  = f'{{{self._battleDRM}}}',
            #     description = 'Add die-roll modifer'),
            ReportTrait(
                self._markKey,
                report = (f'{{{self._debug}?("~"+BasicName'
                          f'+" Mark battle trampoline global "'
                          f'+" "+{self._markStart}):""}}')),
            ReportTrait(
                self._calcBattleAF,
                report=(f'{{{self._verbose}?'
                        f'("! "+BasicName+'
                        f'" add "+EffectiveAF+'
                        f'" to total attack factor -> "+'
                        f'{self._battleAF}'
                        f'):""}}')),
            ReportTrait(
                self._calcBattleDF,
                report=(f'{{{self._verbose}?'
                        f'("! "+BasicName+'
                        f'" add "+EffectiveDF+'
                        f'" to total defence factor -> "+'
                        f'{self._battleDF}'
                        f'):""}}')),
            ReportTrait(
                self._calcBattleShft,
                report=(f'{{{self._debug}?'
                        f'("~ "+BasicName+'
                        f'" Updating odds shift with "+OddsShift+'
                        f'" -> "+{self._battleShift}):""}}')),
            ReportTrait(
                self._calcBattleDRM,
                report=(f'{{{self._debug}?'
                        f'("~ "+BasicName+'
                        f'" Updating DRM with "+DRM+'
                        f'" -> "+{self._battleDRM}):""}}')),
        ]
        traits.extend(
            place+
            trig+
            oth+
            [MarkTrait(name=self._battleUnit,value=True),
             BasicTrait()])
        prototypes.addPrototype(name        = self._battleUnit,
                                description = '',
                                traits      = traits)
    # ----------------------------------------------------------------
    def addBattleCorePrototype(self,prototypes):
        # --- Core traits for battle markers (number, odds, results)
        # - Set the global current battle number
        # - Get the current global battle number
        # - Clear this counter
        # - Trampoline to global command to clear all marks for this battle
        traits = [
            # NoStackTrait(select     = NoStackTrait.NORMAL_SELECT,
            #              move       = NoStackTrait.NORMAL_MOVE,
            #              canStack   = False,
            #              ignoreGrid = False),
            GlobalPropertyTrait(['',self._setBattle,GlobalPropertyTrait.DIRECT,
                                 f'{{{self._battleNo}}}'],
                                name        = self._currentBattle,
                                numeric     = True,
                                description = 'Set current battle'),
            GlobalPropertyTrait(['',self._setBattle,
                                 GlobalPropertyTrait.DIRECT, '{IsAttacker}'],
                                name        = self._currentAttacker,
                                numeric     = True,
                                description = 'Set attacker'),
            GlobalPropertyTrait(['',self._markBattle+'ResetPlaced',
                                 GlobalPropertyTrait.DIRECT, '{false}'],
                                name = self._placedGlobal,
                                numeric = True,
                                description = 'Clear Odds placed flag'),
            ReportTrait(self._markBattle+'ResetPlaced',
                        report = (f'{{{self._debug}?("`"+BasicName+":"+'
                                  f'"Clear placed odds flags "+'
                                  f'{self._placedGlobal}):""}}')),
            DynamicPropertyTrait(['',self._getBattle,
                                  DynamicPropertyTrait.DIRECT,
                                  f'{{{self._currentBattle}}}'],
                                 name        = self._battleNo,
                                 numeric     = True,
                                 value       = f'{{{self._battleNo}}}',
                                 description = 'Set battle number'),
            DynamicPropertyTrait(['',self._getBattle,
                                  DynamicPropertyTrait.DIRECT,
                                  f'{{{self._currentAttacker}}}'],
                                 name        = 'IsAttacker',
                                 numeric     = True,
                                 value       = 'false',
                                 description = 'Set attacker'),
            DeleteTrait('',self._clearBattle),
            GlobalHotkeyTrait(name         = '',
                              key          = self._clearBattle+'Trampo',
                              globalHotkey = self._clearBattle,
                              description  = 'Clear selected battle'),
            TriggerTrait(command    = 'Clear',
                         key        = self._clearKey,
                         actionKeys = [self._setBattle,
                                       self._clearBattle+'Trampo']),
            ReportTrait(self._setBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" @ "+LocationName+'
                                f'": Set global current battle # "+'
                                f'{self._battleNo}+" -> "+'
                                f'{self._currentBattle}+" IsAttacker("+'
                                f'IsAttacker+")="+{self._currentAttacker}+'
                                f'" Marker="+{self._battleMark}+'
                                f'" Odds="+{self._oddsMark}+'
                                f'" Placed="+{self._placedGlobal}+'
                                f'""):""}}')),
            ReportTrait(self._getBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" @ "+LocationName+'
                                f'": Get global current battle # "+'
                                f'{self._currentBattle}+" -> "+'
                                f'{self._battleNo}+'
                                f'" IsAttacker="+IsAttacker+'
                                f'" Marker="+{self._battleMark}+'
                                f'" Odds="+{self._oddsMark}+'
                                f'""):""}}')),
            ReportTrait(self._clearBattle,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" @ "+LocationName+'
                                f'": Clear this global="+'
                                f'{self._currentBattle}+" this="+'
                                f'{self._battleNo}):""}}')),
            ReportTrait(self._clearKey,
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" @ "+LocationName+'
                                f'": To clear battle # global="+'
                                f'{self._currentBattle}+" this="+'
                                f'{self._battleNo}):""}}')),
            ReportTrait(self._clearBattle+'Trampo',
                        report=(f'{{{self._debug}?'
                                f'("~ "+BasicName+" @ "+LocationName+'
                                f'": Forward clear battle # global="+'
                                f'{self._currentBattle}+" this="+'
                                f'{self._battleNo}):""}}')),
            MarkTrait(name=self._battleMark,value=True),
            # TriggerTrait(name       = '',
            #              command    = 'Print',
            #              key        = self._printKey,
            #              actionKeys = []),
            # ReportTrait(self._printKey,
            #             report = (f'{{{self._debug}?("`"+BasicName+":"+'
            #                       f'" Battle no "+{self._battleNo}+'
            #                       f'" Current no "+{self._currentBattle}):""}}'
            #                       )),
            BasicTrait()
        ]
        prototypes.addPrototype(name        = self._currentBattle,
                                description = '',
                                traits      = traits)
        
    # ----------------------------------------------------------------
    def addBattlePrototypes(self,prototypes):
        if not self.addBattleControlPrototype(prototypes):
            return
        
        self.addBattleCalculatePrototype(prototypes)
        self.addBattleUnitPrototype(prototypes)
        self.addBattleCorePrototype(prototypes)

    # ----------------------------------------------------------------
    def markerTraits(self):
        return [DeleteTrait(),
                SubMenuTrait(
                    subMenu='Rotate',
                    keys=['Clock-wise',
                          'Counter clock-wise']),
                RotateTrait(
                    rotateCW         = 'Clock-wise',
                    rotateCCW        = 'Counter clock-wise',
                )]

    # ----------------------------------------------------------------
    def battleMarkerTraits(self,c):
        '''Derives from the CurrentBattle prototype and adds a submenu
        to place odds counter on the battle marker'''
        traits = [PrototypeTrait(name=self._currentBattle),
                  NonRectangleTrait(filename = c['filename'],
                                    image    = c['img'])]
        
        subs  = []
        ukeys = []
        place = []
        trig  = []
        rept  = []
        repp  = []
        for i, odds in enumerate(self._oddsMarks):
            on   = odds.replace('odds marker','').strip()
            om   = odds.replace(':',r'\:')
            kn   = self._markOdds+str(i+1)
            gpid = self._game.nextPieceSlotId()
            skel = PlaceTrait.SKEL_PATH()
            path = skel.format('OddsMarkers',om)
            subs.append(on)

            place.append(
                PlaceTrait(command       = '',
                           key           = kn,
                           markerSpec    = path,
                           markerText    = 'null',
                           xOffset       = -6,
                           yOffset       = -8,
                           matchRotation = False,
                           afterKey      = self._getBattle+'Details',
                           gpid          = gpid,
                           placement     = PlaceTrait.ABOVE,
                           description   = f'Add odds marker {on}'))
            trig.append(
                TriggerTrait(name        = '',
                             command     = on,
                             key         = kn+'real',
                             actionKeys  = [
                                 self._setBattle,
                                 kn]))
            rept.append(
                ReportTrait(kn+'real',
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+": Set odds '
                                    f'{on} ({kn})"):""}}')))
            repp.append(
                ReportTrait(kn,
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+": Place odds '
                                    f'{on} ({kn})"):""}}')))
            ukeys.append(kn+'real')

        auto = []
        auton = []
        if len(self._oddsMarks) > 0:
            auton = ['Auto']
            for i, odds in enumerate(self._oddsMarks):
                trig.append(
                    TriggerTrait(name        = '',
                                 command     = '',
                                 key         = self._markOdds+'Auto',
                                 property    = f'{{{self._battleIdx}=={i+1}}}',
                                 actionKeys  = [self._markOdds+str(i+1)]))

            auto = [
                GlobalHotkeyTrait(name = '',
                                  key          = self._calcBattleOdds,
                                  globalHotkey = self._calcBattleOdds,
                                  description  = 'Calculate fraction'),
                DeselectTrait(command    = '',
                              key        = self._calcBattleOdds+'Deselect',
                              deselect   = DeselectTrait.ONLY),
                ReportTrait(self._calcBattleOdds+'Deselect',
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+": Select only this "'
                                    f'+" Attacker="+IsAttacker'
                                    f'):""}}')),
                GlobalPropertyTrait(
                    ['',self._calcBattleOdds+'Placed',
                     GlobalPropertyTrait.DIRECT, '{true}'],
                    name = self._placedGlobal),
                GlobalPropertyTrait(
                    ['',self._calcBattleOdds+'Placed',
                     GlobalPropertyTrait.DIRECT, '{false}'],
                    name = self._markStart),
                TriggerTrait(name        = '',
                             command     = '',
                             key         = self._markOdds+'Trampoline',
                             actionKeys  = [
                                 self._calcBattleOdds+'Placed',
                                 self._calcBattleOdds,
                                 self._markOdds+'Auto',
                                 self._calcBattleOdds+'Deselect'],
                             property    = (f'{{IsAttacker!=true&&'
                                            f'{self._placedGlobal}!=true}}'
                                            )
                             ),
                TriggerTrait(name        = '',
                             command     = 'Auto',
                             key         = self._calcBattleOdds+'Start',
                             actionKeys  = [
                                 self._setBattle,
                                 self._markOdds+'Trampoline',
                             ]),
                ReportTrait(self._markOdds+'Trampoline',
                            report = (f'{{{self._debug}?("~"+BasicName+'
                                      f'" @ "+LocationName+'
                                      f'" Trampoline to mark odds"+'
                                      f'" IsAttacker="+IsAttacker)'
                                      f':""}}')),
                ReportTrait(self._calcBattleOdds+'Placed',
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+" @ "+LocationName+'
                                    f'": placed for odds "+'
                                    f'{self._placedGlobal}+" "+'
                                    f'{self._markStart}):""}}')),
                ReportTrait(self._calcBattleOdds,
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+'
                                    f'": to global Battle odds "):""}}')),
                ReportTrait(self._calcBattleOdds+'Start',
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+" @ "+LocationName+'
                                    f'": Battle calculate odds start ."+'
                                    f'{self._battleOdds}+"."):""}}')),
                ReportTrait(self._markOdds+'Auto',
                            report=(f'{{{self._debug}?'
                                    f'("~"+BasicName+" : "+LocationName+'
                                    f'": Auto battle odds ."+'
                                    f'{self._battleOdds}+"."):""}}'))
            ]
            
        traits.extend([
            RestrictCommandsTrait(
                name='Hide when auto-odds are enabled',
                hideOrDisable = RestrictCommandsTrait.HIDE,
                expression    = f'{{{self._autoOdds}==true}}',
                keys          = ukeys)]+
                      place
                      +trig
                      +auto
                      +rept
                      +repp)
        if len(subs) > 0:
            traits.extend([
                SubMenuTrait(subMenu = 'Odds',
                             keys    = auton+subs),
            ])

        return traits

    # ----------------------------------------------------------------
    def oddsMarkerTraits(self,c=None):
        '''Derives from the CurrentBattle prototype and adds a submenu
        to replace odds counter with result marker'''
        gpid   = self._game.nextPieceSlotId()
        traits = [
            PrototypeTrait(name=self._currentBattle),
            MarkTrait(self._oddsMark,'true'),
            NonRectangleTrait(filename = c['filename'],
                              image    = c['img']),
            DynamicPropertyTrait(
                ['',self._getBattle+'More',DynamicPropertyTrait.DIRECT,
                 (f'{{{self._battleAF}+" vs "+{self._battleDF}+'
                  f'" (odds "+{self._battleOdds}+" shift "+'
                  f'{self._battleShift}+" DRM "+{self._battleDRM}+'
                  f'")"}}')],
                name = 'BattleDetails',
                value = '',
                numeric = False,
                description = 'Stored battle details'),
            DynamicPropertyTrait(
                ['',self._getBattle+'More',DynamicPropertyTrait.DIRECT,
                 f'{{{self._battleDRM}}}'],
                name = 'BattleDRM',
                value = 0,
                numeric = True,
                description = 'Stored DRM'),
            TriggerTrait(command    = '',
                         key        = self._getBattle+'Details',
                         actionKeys = [self._getBattle,
                                       self._getBattle+'More']),
            # DeleteTrait('',self._recalcOdds+'Delete'),
            # ReplaceTrait(command    = '',
            #              key        = self._recalcOdds+'Replace',
            #              markerSpec = '',
            #              markerText = 'null',
            #              xOffset    = 0,
            #              yOffset    = 0,
            #              matchRotation = False,
            #              afterKey      = '',
            #              gpid          = gpid,
            #              description   = f'Replace with nothing'),
            GlobalHotkeyTrait(
                name        = '',
                key         =self._calcBattleOdds+'Start',
                globalHotkey=self._calcBattleOdds+'ReAuto',
                description ='Trampoline to global'),
            # Recalculate odds
            # First setBatle to make battle No global
            # Then send global key command 
            # Then delete this
            TriggerTrait(
                command    = 'Recalculate',
                key        = self._recalcOdds,
                actionKeys = [self._setBattle,
                              self._markBattle+'ResetPlaced',
                              self._calcBattleOdds+'Start',
                              self._clearBattle,
                              ]),
            ReportTrait(
                self._recalcOdds+'Delete',
                report=(f'{{{self._debug}?'
                        f'("~"+BasicName+'
                        f'": Deleting self"):""}}')),
            ReportTrait(
                self._clearBattle,
                report=(f'{{{self._debug}?'
                        f'("~"+BasicName+'
                        f'": Remove"):""}}')),
            ReportTrait(
                self._recalcOdds,
                report=(f'{{{self._debug}?'
                        f'("! Recalculate Odds"):""}}')),
            ReportTrait(
                self._calcBattleOdds+'Start',
                report=(f'{{{self._debug}?'
                        f'("~Start auto recalculate Odds"):""}}')),
            ReportTrait(
                self._getBattle+'More',
                report = (f'{{{self._debug}?('
                          f'"~Getting more battle info: "+'
                          f'BattleDetails+" "+BattleDRM'
                          f'):""}}'))
        ]

        subs  = []
        place = []
        trig  = []
        rept  = []
        ukeys = [self._recalcOdds]
        first = ''
        for i, result in enumerate(self._resultMarks):
            r    = result.replace('result marker','').strip()
            kn   = self._markResult+str(i+1)
            gpid = self._game.nextPieceSlotId()
            ukeys.append(kn+'real')
            subs.append(r)
            if first == '': first = r
            
            skel = PlaceTrait.SKEL_PATH()
            path = skel.format('ResultMarkers',result)

            place.append(
                ReplaceTrait(command    = '',
                             key        = kn,
                             markerSpec = path,
                             markerText = 'null',
                             xOffset    = -6,
                             yOffset    = -8,
                             matchRotation = False,
                             afterKey      = self._getBattle,
                             gpid          = gpid,
                             description   = f'Add result marker {r}'))
            trig.append(
                TriggerTrait(name        = '',
                             command     = r,
                             key         = kn+'real',
                             actionKeys  = [
                                 self._setBattle,
                                 kn]))
            rept.append(
                ReportTrait(kn+'real',
                            report=(f'{{{self._debug}?'
                                    f'("~ "+BasicName+" setting result '
                                    f'{r}"):""}}')))

        auto = []
        auton = []
        if len(self._resultMarks) > 0:
            auton = ['Auto']
            for i, res in enumerate(self._resultMarks):
                r = res.replace('result marker','').strip()
                trig.append(
                    TriggerTrait(
                        name        = '',
                        command     = '',
                        key         = self._markResult+'Auto',
                        property    = f'{{{self._battleResult}=="{r}"}}',
                        actionKeys  = [self._markResult+str(i+1)]))

            auto = [ # Override in the module
                CalculatedTrait(
                    name = 'Die',
                    expression = '{GetProperty("1d6_result")}',
                    description = 'Die roll'),
                GlobalHotkeyTrait(
                    name         = '',
                    key          = self._rollDice,
                    globalHotkey = self._diceKey,
                    description  = 'Roll dice'),        
                CalculatedTrait(
                    name       = 'BattleResult',
                    expression = f'{{"{first}"}}',
                ),
                GlobalPropertyTrait(
                    ['',self._calcBattleRes+'real',GlobalPropertyTrait.DIRECT,
                     '{BattleResult}'],
                    name = self._battleResult,
                    numeric = False,
                    description = 'Set combat result'),
                TriggerTrait(
                    name        = '',
                    command     = 'Resolve',
                    key         = self._resolveKey,
                    property    = f'{{{self._autoResults}==true}}',
                    actionKeys  = [
                        self._setBattle,
                        self._rollDice,
                        self._calcBattleRes+'real',
                        self._markResult+'Auto',
                             ]),
                ReportTrait(
                    self._rollDice,
                    report = (f'{{{self._debug}?("~"+BasicName+": "'
                              f'+"Rolling the dice with DRM "'
                              f'+BattleDRM):""}}')),
                ReportTrait(
                    self._calcBattleRes,
                    report=(f'{{{self._debug}?'
                            f'("~ "+BasicName+" @ "+LocationName+'
                            f'": Battle result "+'
                            f'{self._battleOdds}):""}}')),
                ReportTrait(
                    self._markResult+'Auto',
                    report=(f'{{{self._debug}?'
                            f'("~ "+BasicName+" @ "+LocationName+'
                            f'": Auto battle result "+'
                            f'{self._battleResult}):""}}')),
                ReportTrait(
                    self._markResult+'Auto',
                    report=(f'{{"` Battle # "+{self._battleNo}+": "+'
                            f'BattleDetails+" with die roll "+Die+": "+'
                            f'{self._battleResult}'
                            # f'+ "<img src=\'result_marker_"'
                            # f'+{self._battleResult}+".png\'"'
                            # f'+" width=24 height=24>"'
                            f'}}')),
                MarkTrait(name=self._battleOddsM,value='true')
            ]

        traits.extend(
            [RestrictCommandsTrait(
                name='Hide when auto-results are enabled',
                hideOrDisable = RestrictCommandsTrait.HIDE,
                expression    = f'{{{self._autoResults}==true}}',
                keys          = ukeys)]+
            place
            +trig
            +auto)
        
        if len(subs) > 0:
            traits.append(SubMenuTrait(subMenu = 'Result',
                                       keys    = subs))

        return traits

    # ----------------------------------------------------------------
    def resultMarkerTraits(self,c=None):
        traits = [PrototypeTrait(name=self._currentBattle),
                  NonRectangleTrait(filename = c['filename'],
                                    image    = c['img'])]

        return traits

    # ----------------------------------------------------------------
    def factionTraits(self,faction):
        offX =  36 * self._counterScale * self._resolution/150
        offY = -38 * self._counterScale * self._resolution/150
        traits = [
            SubMenuTrait(subMenu = 'Movement',
                         keys = ['Trail',
                                 'Toggle mark']),
            TrailTrait(name      = 'Trail',
                       lineWidth = 5,
                       radius    = 10,
                       key       = self._trailKey,
                       turnOn    = self._trailToggleKey+'On',
                       turnOff   = self._trailToggleKey+'Off'),
            MovedTrait(name      = 'Toggle mark',
                       xoff      = int(offX),
                       yoff      = int(offY)),
            RotateTrait(
                rotateCW         = 'Clock-wise',
                rotateCCW        = 'Counter clock-wise',
            ),
            SubMenuTrait(
                subMenu='Rotate',
                keys=['Clock-wise',
                      'Counter clock-wise']),
            SendtoTrait(mapName     = 'DeadMap',
                        boardName   = f'{faction} pool',
                        name        = 'Eliminate',
                        key         = self._eliminateKey,
                        restoreName = '', # 'Restore',
                        restoreKey  = '', # self._restoreKey,
                        description = 'Eliminate unit'),
            PrototypeTrait(name=self._battleUnit),                 
            MarkTrait(name='Faction',value=faction),
            ReportTrait(
                self._trailToggleKey+'On',
                report = (f'{{{self._debug}?("~"+BasicName+'
                          f'" turning ON movement trail"):""}}')),
            ReportTrait(
                self._trailToggleKey+'Off',
                report = (f'{{{self._debug}?("~"+BasicName+'
                          f'" turning OFF movement trail"):""}}'))
        ]

        return traits

    # ----------------------------------------------------------------
    def getFactors(self,val):
        from re import sub

        with VerboseGuard(f'Parsing factors: {val}') as v:
            cf = None
            mf = None
            df = None
            ra = None
            try:
                for rem in ['protect',
                            'leavevmode@ifvmode',
                            'kern',
                            '[-0-9.]+em',
                            'relax',
                            'TU']:
                    val = sub(rem,'',val)
            
                paren = False
                while True:
                    tt = sub(r'\(([^()]*)\)',r'\1',val)
                    if tt == val:
                        break
                    val = tt
                    paren = True

                if val.startswith('['):
                    eb = val.rindex(']')
                    val = val[eb+1:]
                    
                v(f'Value to parse {val}')
                if 'chit/1 factor' in val:
                    vv = val.replace('chit/1 factor=','')
                    v(f'1 factor: {vv}')
                    cf = float(vv)
                elif 'chit/2 factors artillery' in val:
                    vv       = val.replace('chit/2 factors artillery=','')
                    vv       = vv.replace('*','0')
                    v(f'2 factors artillery: {vv}')
                    cf,mf,ra = [float(v) for v in vv.strip('=').split()]
                elif 'chit/3 factors artillery' in val:
                    vv          = val.replace('chit/3 factors artillery=','')
                    vv          = vv.replace('*','0')
                    v(f'3 factors artillery: {vv}')
                    cf,df,mf,ra = [int(v) for v in vv.strip('=').split()]
                elif 'chit/2 factors defence' in val:
                    vv    = val.replace('chit/2 factors defence=','')
                    cf    = 0
                    v(f'2 factors defence: {vv}')
                    df,mf = [float(v) for v in vv.split()]
                elif 'chit/2 factors' in val:
                    vv    = val.replace('chit/2 factors=','')
                    v(f'2 factors: {vv}')
                    cf,mf = [float(v) for v in vv.split()]
                    if paren:
                        df = cf
                        cf = 0
                elif 'chit/3 factors' in val:
                    vv       = val.replace('chit/3 factors=','')
                    vv       = vv.replace('*','0')
                    v(f'3 factors: {vv}')
                    cf,df,mf = [float(v) for v in vv.split()]
                else:
                    v(f'Unknown factors: {val}')
            
                # Set defensive factor to combat factor if not defined. 
                if df is None and cf is not None:
                    df = cf
                    
                    
                
            except Exception as e:
                print(f'\nWarning when extracting factors: {e} '
                      f'in "{val}" -> "{vv}"')
                return None,None,None,None
                pass

            v(f'-> CF={cf} DF={df} MF={mf} RA={ra}')
            return cf,df,mf,ra
        
    # ----------------------------------------------------------------
    def pieceTraits(self,subn,subc,cn,c):
        from re import sub

        bb     = self.getBB(c['img'])
        height = bb[3]-bb[1] if bb is not None else 1
        width  = bb[2]-bb[0] if bb is not None else 1
            
        cf     = subc.get(cn + ' flipped', None)
        traits = [PrototypeTrait(name=f'{subn} prototype')]

        def clean(s):
            return s.strip().replace(',',' ').replace('/',' ').strip()
        
        if not self._nonato:
            mains = c.get('mains','')
            mm    = clean(mains).strip()
            traits.append(PrototypeTrait(name=f'{mm} prototype'))
            # Commented code adds all 'main' types as prototypes, which
            # doesn't make so much sense
            #
            # m   = set([clean(m) for m in mains.split(',')])
            # traits.extend([PrototypeTrait(name=f'{m.strip()} prototype')
            #                for m in set(m)])
            for p in ['echelon','command']:
                val = c.get(p,None)
                if val is not None:
                    pv = f'{val.strip()} prototype'
                    traits.append(PrototypeTrait(name=pv))
                    
        if cf is not None:
            traits.extend([
                LayerTrait(images = [c['filename'],
                                     cf['filename']],
                           newNames = ['','Reduced +'],
                           activateName = '',
                           decreaseName = '',
                           increaseName = 'Flip',
                           increaseKey  = self._flipKey,
                           decreaseKey  = '',
                           name         = 'Step'),
                ReportTrait(self._flipKey)])

        if not self._nochit:
            def clean(value):
                return sub(r'\[[^=]+\]=','',value)\
                    .replace('{','')\
                    .replace('}','')\
                    .replace('/',' ')\
                    .replace(',',' ')\
                    .replace('\\',' ')

            def factor_clean(value):
                tmp = sub(r'\[[^=]+\]=','',value)\
                    .replace('{','')\
                    .replace('}','')\
                    .replace('/TU','')\
                    .replace('\\',' ')
                return sub(r'\textonehalf','0.5',
                           sub(r'([0-9])\textonehalf',r'\1.5',tmp))\
                    .replace(',',' ')
            
            # Add extra marks.  This may be useful later on. 
            for field in ['upper left', 'upper right', 
                          'lower left', 'lower right',
                          'left',       'right',
                          'factors']:
                value = c.get('chit',{}).get(field,None)
                if value is None:
                    continue

                if field != 'factors':
                    val = clean(value)
                    val = val\
                        .replace('chit identifier=','')\
                        .replace('chit small identifier=','')
                
                    traits.append(MarkTrait(name = field, value = val))
                    continue


                #print('\n'+f'Got factors "{value}" -> "{val}"')
                val = factor_clean(value)
                
                af, df, mf, ra = self.getFactors(val)
                saf, sdf, smf, sra = None,None,None,None
                if cf is not None:
                    value = cf.get('chit',{}).get(field,None)
                    if value is not None:
                        val = factor_clean(value)
                        val = val\
                            .replace('chit/identifier=','')\
                            .replace('chit/small identifier=','')
                        #print('\n'+f'Got s-factors "{value}" -> "{val}"')
                        saf, sdf, smf, sra = self.getFactors(val)

                rf  = []
                srf = []
                for f,sf,n in [[af,saf,'CF'],
                               [df,sdf,'DF'],
                               [mf,smf,'MF'],
                               [ra,sra,'Range']]:
                    if f is None: continue
                    try:
                        # Try to make the factor an integer
                        f = int(str(f))                        
                    except:
                        pass 
                    
                    if sf is None:
                        rf.append(MarkTrait(name=n,value=f))
                    else:
                        try:
                            # Try to make the factor an integer
                            sf = int(str(sf))                        
                        except:
                            pass
                        
                        rf .append(MarkTrait(name='Full'+n,   value=f))
                        srf.append(MarkTrait(name='Reduced'+n,value=sf))
                        traits.append(CalculatedTrait(
                            name = n,
                            expression = (f'{{(Step_Level==2)?'
                                          f'Reduced{n}:Full{n}}}')))

                # Perhaps modify in module
                srf.append(MarkTrait(name='DRM',value=0))
                traits.extend(rf+srf)
                        

                

                
                        
        return height, width, traits
        
    # ----------------------------------------------------------------
    def addCounters(self):
        '''Add all counters (pieces) element to the module.
        Prototypes are also created as part of this.
        '''
        from re import sub

        with VerboseGuard('Adding counters') as v:
            protos       =  self._game.addPrototypes()
            
            self.addNatoPrototypes(protos)
            self.addBattlePrototypes(protos)
            
            pieces = self._game.addPieceWindow(
                name   = 'Counters',
                icon   = self.getIcon('unit-icon',
                                      '/images/counter.gif'),
                hotkey = self._countersKey)
            tabs   = pieces.addTabs(entryName='Counters')
            
            for subn, subc in self._categories.get('counter',{}).items():
            
                subn  = subn.strip()
                panel = tabs.addPanel(entryName = subn, fixed = False)
                plist = panel.addList(entryName = f'{subn} counters')

                traits = []
                if   subn in ['BattleMarkers']:
                    traits = self.battleMarkerTraits(list(subc.values())[0])
                elif subn in ['OddsMarkers']:
                    traits = self.oddsMarkerTraits(list(subc.values())[0])
                elif subn in ['ResultMarkers']:
                    traits = self.resultMarkerTraits(list(subc.values())[0])
                elif subn.lower() in ['marker', 'markers']:
                    traits = self.markerTraits()
                else:
                    traits = self.factionTraits(subn)

                traits.append(BasicTrait())
                
                p = protos.addPrototype(name        = f'{subn} prototype',
                                        description = f'Prototype for {subn}',
                                        traits      = traits)
                v('')
             
                with VerboseGuard(f'Adding pieces for "{subn}"') as vv:
                    for i, (cn, c) in enumerate(subc.items()):
                        if cn.endswith('flipped'): continue

                        if i == 0: v('',end='')
                        vv(f'[{cn}',end='',flush=True,noindent=True)
                    
                        height, width, traits = self.pieceTraits(subn,subc,cn,c)
                        if cn == self._hiddenName:
                            traits = [
                                PrototypeTrait(name=self._battleCtrl),
                                PrototypeTrait(name=self._battleCalc),
                                TriggerTrait(
                                    name       = 'Toggle trails',
                                    command    = '',
                                    key        = self._trailKey,
                                    actionKeys = [
                                        self._trailToggleKey+'Value',
                                        self._trailToggleKey+'Cmd'],
                                ),
                                GlobalPropertyTrait(
                                    ['',self._trailToggleKey+'Value',
                                     GlobalPropertyTrait.DIRECT,
                                     f'{{!{self._trailsFlag}}}'],
                                    name        = self._trailsFlag,
                                    description = 'State of global trails'),
                                TriggerTrait(
                                    name       = 'Turn on trails',
                                    command    = '',
                                    key        = self._trailToggleKey+'Cmd',
                                    actionKeys = [self._trailToggleKey+'On'],
                                    property   = f'{{{self._trailsFlag}==true}}'),
                                TriggerTrait(
                                    name       = 'Turn off trails',
                                    command    = '',
                                    key        = self._trailToggleKey+'Cmd',
                                    actionKeys = [self._trailToggleKey+'Off'],
                                    property   = f'{{{self._trailsFlag}!=true}}'),
                                # ReportTrait(
                                #     self._trailToggleKey+'Cmd',
                                #     report = (f'{{{self._verbose}?('
                                #               f'BasicName+" toggle trails "'
                                #               f'+{self._trailsFlag}):""}}')),
                                #GlobalCommandTrait
                                GlobalHotkeyTrait
                                (
                                    name        = '',
                                    #commandName = '',
                                    key         = self._trailToggleKey+'On',
                                    globalHotkey= self._trailToggleKey+'On',
                                    #properties  = '{Moved!=""}',
                                    #ranged      = False
                                ),
                                #GlobalCommandTrait
                                GlobalHotkeyTrait
                                (
                                    name        = '',
                                    #commandName = '',
                                    key         = self._trailToggleKey+'Off',
                                    globalHotkey= self._trailToggleKey+'Off',
                                    #properties  = '{Moved!=""}',
                                    #ranged      = False
                                ),
                                ReportTrait(
                                    self._trailKey,
                                    report = (f'{{{self._debug}?("~"+'
                                              f'BasicName+" toggle trails"'
                                              f'):""}}')),
                                ReportTrait(
                                    self._trailToggleKey+'Value',
                                    report = (f'{{{self._debug}?("~"+'
                                              f'BasicName+" trail state: "+'
                                              f'TrailsFlag):""}}')),
                                ReportTrait(
                                    self._trailToggleKey+'Cmd',
                                    report = (f'{{{self._debug}?("~"+'
                                              f'BasicName+" send cmd: "+'
                                              f'TrailsFlag):""}}')),
                                ReportTrait(
                                    self._trailToggleKey+'On',
                                    report = (f'{{{self._debug}?("~"+'
                                              f'BasicName+" turn on: "+'
                                              f'TrailsFlag):""}}')),
                                ReportTrait(
                                    self._trailToggleKey+'Off',
                                    report = (f'{{{self._debug}?("~"+'
                                              f'BasicName+" turn off: "+'
                                              f'TrailsFlag):""}}')),
                            ]
                            if self._diceInit is not None:
                                traits.extend(self._diceInit)
                            traits.append(
                                RestrictAccessTrait(sides=[],
                                                    description='Fixed'))

                            
                        #if cn.startswith('odds marker'):
                        #    cn  = cn.replace(':','_')
                            
                        gpid = self._game.nextPieceSlotId()
                        traits.extend([BasicTrait(name     = c['name'],
                                                  filename = c['filename'],
                                                  gpid     = gpid)])
                        
                        ps = plist.addPieceSlot(entryName = cn,
                                                gpid      = gpid,
                                                height    = height, 
                                                width     = width,
                                                traits    = traits)
                        if cn == self._hiddenName:
                            self._hidden = ps
                        vv('] ',end='',flush=True,noindent=True)
                    
                    vv('')
            

    # ----------------------------------------------------------------
    def addNotes(self,**kwargs):
        '''Add a `Notes` element to the module

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        '''
        self._game.addNotes(**kwargs)
        
    # ----------------------------------------------------------------
    def addInventory(self,**kwargs):
        '''Add a `Inventory` element to module

        Parameters
        ----------
        kwargs : dict
            Dictionary of attribute key-value pairs
        '''
        filt = '{' + '||'.join([f'Faction=="{s}"' for s in self._sides])+'}'
        grp  = 'Faction,Command,Echelon,Type'
        self._game.addInventory(include = filt,
                                groupBy = grp,
                                sortFormat  = '$PieceName$',
                                tooltip     ='Show inventory of all pieces',
                                zoomOn      = True,
                                **kwargs)

    # ----------------------------------------------------------------
    def addBoard(self,name,info,hasFlipped=False):
        '''Add a `Board` element to module

        Parameters
        ----------
        name : str
            Name of board
        info : dict
            Information on board image
        hasFlipped : bool
            True if any piece can be flipped 
        '''
        with VerboseGuard(f'Adding board {name}') as v:
            # from pprint import pprint 
            # pprint(info)
            map    = self._game.addMap(mapName=name,
                                       markUnmovedHotkey=self._clearMoved)
            map.addCounterDetailViewer(
                description         = 'Investigate stack of pieces',
                propertyFilter      = f'{{{self._battleMark}!=true}}',
                fontSize            = 14,
                summaryReportFormat = '<b>$LocationName$</b>',
                hotkey              = key('\n'),
                stopAfterShowing    = True)
            map.addHidePiecesButton()
            map.addGlobalMap()
            # Basics
            map.addStackMetrics()
            map.addImageSaver()
            map.addTextSaver()
            map.addForwardToChatter()     
            map.addMenuDisplayer()        
            map.addMapCenterer()          
            map.addStackExpander()        
            map.addPieceMover()           
            map.addKeyBufferer()          
            map.addForwardKeys()# Be careful - does duplicate!
            map.addSelectionHighlighters()
            map.addHighlightLastMoved()   
            map.addZoomer()               

            # Forward
            # map.addMassKey(
            #     name         = 'Movement trails',
            #     buttonHotkey = '',
            #     hotkey       = self._trailKey,
            #     icon         = self.getIcon('trail-icon',
            #                                 '/images/recenter.gif'),
            #     tooltip      = 'Toggle movement trails',
            #     #filter       = '{Moved!=""}', # Filter on MarkMoved
            #     filter       = f'{{BasicName=="{self._hiddenName}"}}',
            #     target       = '',
            #     reportFormat = (f'{{{self._debug}?'
            #                     f'("`Movement trails toggled"):""}}'))
            map.addMassKey(
                name         = '',
                buttonHotkey = self._trailToggleKey+'On',
                hotkey       = self._trailToggleKey+'On',
                icon         = '',
                tooltip      = '',
                filter       = '{Moved!=""}', # Filter on MarkMoved
                target       = '',
                reportFormat = (f'{{{self._verbose}?'
                                f'("`Movement trails toggled on"):""}}'))
            map.addMassKey(
                name         = '',
                buttonHotkey = self._trailToggleKey+'Off',
                hotkey       = self._trailToggleKey+'Off',
                icon         = '',
                tooltip      = '',
                filter       = '{Moved!=""}', # Filter on MarkMoved
                target       = '',
                reportFormat = (f'{{{self._verbose}?'
                                f'("`Movement trails toggled off"):""}}'))
            map.addMassKey(
                name         = 'Eliminate',
                buttonHotkey = self._eliminateKey,
                hotkey       = self._eliminateKey,
                icon         = self.getIcon('eliminate-icon',
                                            '/icons/16x16/edit-undo.png'),
                tooltip      = 'Eliminate selected units')
            map.addMassKey(
                name         = 'Delete',
                buttonHotkey = self._deleteKey,
                hotkey       = self._deleteKey,
                icon         = self.getIcon('delete-icon',
                                            '/icons/16x16/no.png'),
                tooltip      = 'Delete selected units')
            map.addMassKey(
                name         = 'Trail',
                buttonHotkey = self._trailKey,
                hotkey       = self._trailKey,
                icon         = '',
                tooltip      = '')
            # Forward
            # map.addMassKey(
            #     name='Rotate CW',
            #     buttonHotkey = self._rotateCWKey,
            #     hotkey       = self._rotateCWKey,
            #     icon         = '', #/icons/16x16/no.png',
            #     tooltip      = 'Rotate selected units')
            # map.addMassKey(
            #     name='Rotate CCW',
            #     buttonHotkey = self._rotateCCWKey,
            #     hotkey       = self._rotateCCWKey,
            #     icon         = '', #/icons/16x16/no.png',
            #     tooltip      = 'Rotate selected units')
            map.addMassKey(
                name='Phase clear moved markers',
                buttonHotkey = self._clearMoved+'Phase',
                hotkey       = self._clearMoved+'Trampoline',
                canDisable   = True,
                target       = '',
                filter       = f'{{{self._battleCtrl}==true}}',
                propertyGate = f'{self._noClearMoves}',
                icon         = '', #/icons/16x16/no.png',
                tooltip      = 'Phase clear moved markers',
                reportFormat = (f'{{{self._debug}?'
                                f'("~ {name}: '
                                f'Phase Clear moved markers "+'
                                f'{self._noClearMoves})'
                                f':""}}'))
            map.addMoveCamera(
                name           = 'Move camera to next un-moved',
                tooltip        = 'Move to nearest un-moved piece',
                hotkey         = key(RIGHT,ALT),
                text           = '',
                icon           = self.getIcon('next-move-icon',''),
                canDisable     = True,
                propertyGate   = self._noMoveFlag,
                zoom           = 0,
                moveCameraMode = MoveCamera.NEAREST,
                boardName      = name,
                propertyFilter = '{Phase.contains(Faction)&&Moved==false}',
                xOffset        = 0,
                yOffset        = 0)
                
            if hasFlipped:
                map.addMassKey(
                    name         = 'Flip',
                    buttonHotkey = self._flipKey,
                    hotkey       = self._flipKey,
                    icon         = self.getIcon('flip-icon',
                                                '/images/Undo16.gif'),
                    tooltip      = 'Flip selected units')

            if len(self._battleMarks) > 0:
                v(f'Adding battle mark interface')
                ctrlSel = f'{{{self._battleCtrl}==true}}'
                ctrlSl2 = (f'{{{self._battleCtrl}==true&&'
                           f'{self._markStart}!=true}}')
                oddsSel = f'{{{self._battleMark}==true}}'
                calcSel = f'{{{self._battleCalc}==true}}'
                curSel  = (f'{{{self._battleNo}=={self._currentBattle}}}')
                curAtt  = (f'{{{self._battleNo}=={self._currentBattle}&&'
                           f'{self._battleUnit}==true&&'
                           f'IsAttacker==true}}')
                curDef  = (f'{{{self._battleNo}=={self._currentBattle}&&'
                           f'{self._battleUnit}==true&&'
                           f'IsAttacker==false}}')
                curUnt  = (f'{{{self._battleNo}=={self._currentBattle}&&'
                           f'{self._battleUnit}==true}}')
                markSel = (f'{{{self._battleNo}=={self._currentBattle}&&'
                           f'{self._battleMark}==true&&'
                           f'{self._oddsMark}!=true}}')
                markSel = (f'{{{self._battleNo}=={self._currentBattle}&&'
                           f'{self._placedGlobal}!=true&&'
                           f'{self._battleMark}==true&&'
                           f'{self._oddsMark}!=true}}')

                # ctrlSel = '{BasicName=="wg hidden unit"}'
                map.addMassKey(
                    # This can come from a unit
                    name         = 'User mark battle',
                    buttonHotkey = self._markBattle+'Unit',
                    buttonText   = '',
                    hotkey       = self._markBattle,
                    icon         = self.getIcon('battle-marker-icon',''),
                    tooltip      = 'Mark battle (Ctrl-X)',
                    target       = '',
                    singleMap    = True, # Was False,
                    filter       = ctrlSel,
                    reportFormat = (f'{{{self._verbose}?'
                                    f'("~{name}: '
                                    f'User marks battle # "+'
                                    f'{self._currentBattle})'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Selected mark battle',
                    buttonHotkey = self._markBattle,
                    hotkey       = self._markBattle,
                    icon         = '',
                    tooltip      = '',
                    singleMap    = True, # Was False,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~{name}: '
                                    f'Mark battle # "+'
                                    f'{self._currentBattle})'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Clear current battle',
                    buttonText   = '',
                    buttonHotkey = self._clearBattle,
                    hotkey       = self._clearBattle,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # Was False,
                    filter       = curSel,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~{name}: '
                                    f'Clear battle # "+'
                                    f'{self._currentBattle})'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Clear selected battle',
                    buttonText   = '',
                    buttonHotkey = '',#self._clearKey,
                    hotkey       = self._clearKey,
                    icon         = '',
                    tooltip      = '',
                    singleMap    = False,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Clear battle # "+'
                                    f'{self._currentBattle})'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Clear all battles',
                    buttonText   = '',
                    buttonHotkey = self._clearAllBattle,
                    hotkey       = self._clearBattle,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # Was False,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Clear all battle markers")'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'User clear all battles',
                    buttonText   = '',
                    buttonHotkey = self._clearAllKey,
                    hotkey       = self._clearAllBattle,
                    icon         = self.getIcon('clear-battles-icon',''),
                    tooltip      = 'Clear all battles',
                    target       = '',
                    singleMap    = True, # False,
                    filter       = ctrlSel,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'User clears battle markers")'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Phase clear all battles',
                    buttonText   = '',
                    buttonHotkey = self._clearBattlePhs,
                    hotkey       = self._clearAllBattle,
                    icon         = '',
                    tooltip      = 'Clear all battles',
                    canDisable   = True,
                    propertyGate = f'{self._noClearBattles}',
                    target       = '',
                    singleMap    = True, # Was False,
                    filter       = ctrlSel,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Phase clears battle markers "+'
                                    f'{self._noClearBattles})'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Selected resolve battle',
                    buttonHotkey = '',#self._resolveKey,
                    hotkey       = self._resolveKey,
                    icon         = self.getIcon('resolve-battles-icon',''),
                    tooltip      = 'Resolve battle',
                    singleMap    = True, # False,
                    filter       = oddsSel,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Resolve battle # "+'
                                    f'{self._currentBattle})'
                                    f':""}}'))
                map.addMassKey(
                    name         = 'Sum AFs',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleAF,
                    hotkey       = self._calcBattleAF,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # False,
                    filter       = curAtt,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Calculate total AF"):""}}'))
                map.addMassKey(
                    name         = 'Sum DFs',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleDF,
                    hotkey       = self._calcBattleDF,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # Was False,
                    filter       = curDef,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Calculate total DF"):""}}'))
                map.addMassKey(
                    name         = 'Sum odds shifts',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleShft,
                    hotkey       = self._calcBattleShft,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # False,
                    filter       = curUnt,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Calculate odds shift"):""}}'))
                map.addMassKey(
                    name         = 'Sum die roll modifiers',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleDRM,
                    hotkey       = self._calcBattleDRM,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # False,
                    filter       = curUnt,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Calculate DRM"):""}}'))
                map.addMassKey(
                    name         = 'Calc battle odds',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleOdds,
                    hotkey       = self._calcBattleOdds,
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = True, # Was False,
                    filter       = calcSel,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Calculate odds"):""}}'))
                # If `target` is set to the nothing, then the command
                # is sent to all - which means that will get duplicate
                # odd markers.  If set to selected, then we have
                # deselected all but one, and so we will not get
                # duplicate odds markers. However, we may get into the
                # situation where a battle marker isn't selected (for
                # example becuase the unit is in a different layer),
                # which means we will not get the right calculations.
                #
                # IF I can find a way to not get double ciate markers,
                # then it would be preferable to set "target" to the
                # empty string.
                #
                # Found that way - keep track ourselves of whether
                # this has been called, and only dispatch if it
                # hasn't.  Requires a reset to be done before hand,
                # and a set of flag in battle marker.  That is, we do
                # not rely on the VASSAL selection mechanism, which
                # has it's own quirks.
                map.addMassKey(
                    name         = 'Auto calc battle odds',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleOdds+'Auto',
                    hotkey       = self._calcBattleOdds+'Start',
                    icon         = '',
                    tooltip      = '',
                    target       = '', # Was commented ?
                    singleMap    = True, # Was False,
                    filter       = markSel,
                    reportFormat = (
                        f'{{{self._debug}?'
                        f'("~{name}: Auto calculate odds # "+'
                        f'{self._currentBattle}+" "+'
                        f'{self._placedGlobal}+" "+'
                        f'"{markSel}"):""}}')) 
                map.addMassKey(
                    name         = 'User recalc',
                    buttonHotkey = self._recalcOdds,
                    buttonText   = '',
                    hotkey       = self._recalcOdds,
                    icon         = '',
                    tooltip      = 'Recalculate odds',
                    singleMap    = False,
                    filter       = '',
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Recalculate odds"):""}}'))
                map.addMassKey(
                    name         = 'Auto recalc battle odds',
                    buttonText   = '',
                    buttonHotkey = self._calcBattleOdds+'ReAuto',
                    hotkey       = self._calcBattleOdds+'Start',
                    icon         = '',
                    tooltip      = '',
                    target       = '',
                    singleMap    = False,
                    filter       = markSel,
                    reportFormat = (f'{{{self._debug}?'
                                    f'("~ {name}: '
                                    f'Auto re-calculate odds of "+'
                                    f'{self._currentBattle}):'
                                    f'""}}')) 
                map.addMoveCamera(
                    name           = 'Move to nearest unresolved combat',
                    tooltip        = 'Move to nearest unresolved combat',
                    text           = '',
                    hotkey         = key(DOWN,ALT),
                    icon           = self.getIcon('next-battle-icon',''),
                    canDisable     = True,
                    propertyGate   = self._noCombatFlag,
                    zoom           = 0,
                    moveCameraMode = MoveCamera.NEAREST,
                    boardName      = name,
                    propertyFilter = f'{{{self._battleNo}!=-1}}',
                    xOffset        = 0,
                    yOffset        = 0)
               
            
            v(f'Getting the board dimensions')
            ulx,uly,lrx,lry = self.getBB(info['img'])
            width           = int(abs(ulx - lrx))
            height          = int(abs(uly - lry))
            # Why is it we take the width and height like this?
            # Do they every differ from the above?
            # This is the only place that we actually use this
            #
            # width, height   = self.getWH(info['img'])
            height          += 20
            width           += 5
            # v(f'{ulx},{uly},{lrx},{lry}')

            v(f'Board BB=({lrx},{lry})x({ulx},{uly}) {width}x{height}')
            picker = map.addBoardPicker()
            board  = picker.addBoard(name   = name,
                                     image  = info['filename'],
                                     width  = width,
                                     height = height)
            zoned  = board.addZonedGrid()
            zoned.addHighlighter()
            
            if not 'zones' in info:
                color = rgb(255,0,0)
                full = zoned.addZone(name = 'full',
                                     useParentGrid = False,
                                     path=(f'{ulx},{uly};' +
                                           f'{lrx},{uly};' +
                                           f'{lrx},{lry};' +
                                           f'{ulx},{lry}'))
                grid = full.addHexGrid(color   = color,
                                       dx      = HEX_WIDTH,
                                       dy      = HEX_HEIGHT,
                                       visible = self._visible)
                grid.addNumbering(color   = color,
                                  hType   = 'A',
                                  hOff    = -1,
                                  vType   = 'N',
                                  vOff    = -1,
                                  visible = self._visible)
                return
            
            w = abs(ulx-lrx)
            h = abs(uly-lry)
            self.addZones(zoned,name,info['zones'],w,h)

            if self._hidden is not None:
                v(f'Adding hidden unit to map {name}')
                at = map.addAtStart(name            = self._hiddenName,
                                    location        = '',
                                    useGridLocation = False,
                                    owningBoard     = name,
                                    x               = 0,
                                    y               = 0)
                at.addPieces(self._hidden)
            

    # ----------------------------------------------------------------
    def addDeadMap(self):
        '''Add a "Dead Map" element to the module 
        '''
        name = 'DeadMap'
        with VerboseGuard(f'Adding deadmap {name}') as v:
            map    = self._game.addMap(
                mapName       = name,
                buttonName    = '',
                markMoved     = 'Never',
                launch        = True,
                icon          = self.getIcon('pool-icon',
                                             '/images/playerAway.gif'),
                allowMultiple = True,
                hotkey        = self._deadKey)
            # Basics
            map.addStackMetrics()
            map.addImageSaver()
            map.addTextSaver()
            map.addForwardToChatter()     
            map.addMenuDisplayer()        
            map.addMapCenterer()          
            map.addStackExpander()        
            map.addPieceMover()           
            map.addKeyBufferer()          
            map.addSelectionHighlighters()
            map.addHighlightLastMoved()   
            map.addZoomer()               
            
            map.addMassKey(
                name='Restore',
                buttonHotkey = self._restoreKey,
                hotkey       = self._restoreKey,
                icon         = self.getIcon('restore-icon',
                                            '/images/Undo16.gif'),
                tooltip      = 'Restore selected units')
            
            picker = map.addBoardPicker()
            picker.addSetup(maxColumns=len(self._sides),mapName=name,
                            boardNames=[s+' pool' for s in self._sides])
            
            for i, s in enumerate(self._sides):
                v(f'Adding {s} pool')
                color        = [0,0,0,64]
                color[i % 3] = 255
                w            = 400
                h            = 400
                c            = rgba(*color)
                img          = ''
                dimg         = self._categories.get('pool',{}).get('all',{})\
                                                              .get(s,None)
            
                if dimg:
                    bb  = self.getBB(dimg['img'])
                    w   = bb[2] - bb[0]
                    h   = bb[3] - bb[1]
                    c   = ''
                    img = dimg['filename']
                    v(f'Using image provided by user {img}')
            
                board  = picker.addBoard(name   = f'{s} pool',
                                         image  = img,
                                         width  = w,
                                         height = h,
                                         color  = c)
            
                if dimg is None or not 'zones' in dimg:
                    continue
            
                zoned  = board.addZonedGrid()
                zoned.addHighlighter()
                w = abs(w)
                h = abs(h)
                self.addZones(zoned,board['name'],dimg['zones'],w,h)
                
        
    # --------------------------------------------------------------------
    def getPictureInfo(self,picture,name,width,height):
        '''
        Returns
        -------
        hex_width, hex_height : float, float
            Scale hex width
        scx, scy : float, float, float, float
            Scale to image and picture (x,y)
        rot90 : bool
            True if rotated +/-90 degrees
        tran : callable
            Translation function
        '''
        if picture is None:
            print(f'WARNING: No Tikz picture information.'
                  f"Are you sure you used the `[zoned]' option for the "
                  f"tikzpicture environment of {name}?")
            f = lambda x,y: (x,y)
            return HEX_WIDTH,HEX_HEIGHT,1,1,False,f
        
        # Get picture bounding box
        tll = picture['lower left']
        tur = picture['upper right']
        # Get picture transformation
        pa  = picture['xx']
        pb  = picture['xy']
        pc  = picture['yx']
        pd  = picture['yy']
        # Get picture offset (always 0,0?)
        pdx = picture['dx']
        pdy = picture['dy']
        # Define picture global transformation
        pr  = lambda x,y: (pa * x + pc * y, pb * x + pd * y)
        # Globally transform (rotate) picture bounding box 
        pll  = pr(*tll)
        pur  = pr(*tur)
        # Calculate widht, height, and scaling factors 
        pw   = pur[0] - pll[0]
        ph   = pur[1] - pll[1]
        scw  = width / pw
        sch  = height / ph
        # Extract picture scales and rotation
        # Courtesy of
        # https://math.stackexchange.com/questions/13150/extracting-rotation-scale-values-from-2d-transformation-matrix
        from math import sqrt, atan2, degrees, isclose
        psx   = sqrt(pa**2 + pb**2) # * (-1 if pa < 0 else 1)
        psy   = sqrt(pc**2 + pd**2) # * (-1 if pd < 0 else 1)
        prt   = degrees(atan2(pc,pd))
        if not any([isclose(abs(prt),a) for a in [0,90,180,270]]):
            raise RuntimeException('Rotations of Tikz pictures other than '
                                   '0 or +/-90,+/- 180, or +/-270 not supported. '
                                   'found {prt}')
        rot90      = int(prt // 90)
        if rot90 == 2: rot90 = -2
        # Now supported 
        # if any([isclose(prt,a) for a in [90,270,180,-180]]):
        #     print(f'WARNING: rotations by {prt} not fully supported')

        from math import sqrt
        hex_width  = psx * scw * 2  # HEX_WIDTH
        hex_height = psy * sch * sqrt(3) # HEX_HEIGHT
        with VerboseGuard('Picture') as v:
            v(f'Transformations:        {pa},{pb},{pc},{pd}')
            v(f'Scale (x,y):            {psx},{psy}')
            v(f'Rotation (degrees):     {prt} ({rot90})')
            v(f'Scale to pixels (x,y):  {scw},{sch}')
    
        # When translating the Tikz coordinates, it is important to note
        # that the Tikz y-axis point upwards, while the picture y-axis
        # point downwards.  This means that the upper right corner is at
        # (width,0) and the lower left corner is at (0,height).
        def tranx(x,off=-pll[0]):
            # print(f'x: {x} + {off} -> {x+off} -> {int(scw*(x+off))}')
            return int(scw * (x + off)+.5)
        def trany(y,off=-pur[1]):
            # print(f'y: {y} + {off} -> {y+off} -> {-int(sch*(y+off))}')
            return -int(sch * (y + off)+.5)
        tran  = lambda x,y : (tranx(x), trany(y))

        return hex_width, hex_height, scw * psx, sch * psy, rot90, tran
        
    # --------------------------------------------------------------------
    def getHexParams(self,
                     llx,
                     lly,
                     urx,
                     ury,
                     mx,
                     my,
                     hex_width,
                     hex_height,
                     rot90,
                     labels,
                     coords,
                     targs,
                     nargs):
        '''rot90 =  0  No rotation
                 =  1  Rotated -90 (clock-wise)
                 = -1  Rotated  90 (counter clock-wise)
                 = -2  Rotated 180
        '''
        with VerboseGuard('Hex parameters') as v:
            from math import sqrt
            isodd   = lambda x : (x % 2 == 1)
            iseven  = lambda x : (x % 2 == 0)
            isfalse = lambda x : False
            shorts  = {'isodd': isodd, 'iseven': iseven, 'isfalse': isfalse }
            
            # Funny scaling needed by VASSAL.  Seems like they only
            # really about the absolute value of 'dy' and then the
            # aspect ratio between dx and dy.
            pxfac               = sqrt(3)/2
            hex_pw              = hex_height * pxfac
            hex_ph              = hex_width  * pxfac
            stagger             = False
            #
            # Get parameters from coordinates. These should always be set  
            #
            rows                = coords  .get('row',   {})
            columns             = coords  .get('column',{})
            top_short           = columns .get('top short',   'isfalse')
            bot_short           = columns .get('bottom short','isfalse')
            inv_col             = columns .get('factor',1)
            inv_row             = rows    .get('factor',1)
            voff                = -rows   .get('offset',0) # 0:  from 0 -> -1
            hoff                = -columns.get('offset',0) # -1: from 1 -> -2
            vdesc               = inv_row == 1
            hdesc               = inv_col == -1
            #
            # Calculate total dimensions, and number of columns and rows
            #
            w                   =  abs((urx-llx) - 2 * mx)
            h                   =  abs((ury-lly) - 2 * my)
            if abs(rot90) == 1: h, w  = w, h
            nc                  = int(w // (hex_width  * 3 / 4))
            nr                  = int(h // (hex_height))
            namrot              = {0:   'none - 0',
                                   -1: '-90 - CCW',
                                   1:  '90 CW',
                                   -2: '180 - half-turn'}
            
            v(f'Width:    {w}')
            v(f'Height:   {h}')
            v(f'Margins:  x={mx} y={my}')
            v(f'Rotation: {rot90} ({namrot[rot90]})')
            v(f'Labels:   {labels}')
            v(f'Columns:')
            v(f' size:          {nc}')
            v(f' start:         {hoff}')
            v(f' direction:     {inv_col}')
            v(f' top short:     {top_short}')
            v(f' bottom short:  {bot_short}')
            v(f'Rows:')
            v(f' size:          {nr}')
            v(f' start:         {voff}')
            v(f' direction:     {inv_row}')
            v(f'Image:')
            v(f' BB: ({llx},{lly}) x ({urx},{ury})')
            #
            # X0 and Y0 are in the local (rotated) frame of the hex grid.
            # Thus X is always along hex breadth, and Y along the
            # height. Thus the base offset (rotated into the hex frame) differs.
            x0 =  ury if abs(rot90) == 1 else llx
            y0 =  llx if abs(rot90) == 1 else ury
            # Calculate column,row of corners
            llc     = hoff
            ulc     = hoff
            lrc     = hoff+nc-1
            urc     = hoff+nc-1
            #
            # Swap in directions
            if hdesc: llc, lrc, ulc, urc = lrc, llc, urc, ulc
            #
            is_short_top  = shorts[columns.get('top short',   'isfalse')]
            is_short_bot  = shorts[columns.get('bottom short','isfalse')]
            if is_short_top is isfalse:
                # Assume fully populated columns 
                is_short_top = isodd if iseven(hoff) else iseven
            if is_short_bot is isfalse:
                is_short_bot = isodd if isodd(hoff)  else iseven
            
            #
            # Now we have the hex coordinates of the corners.  We can
            # now check how things are offset.  Before rotation, we
            # will have that the first column is offset by hex_pw / 2.
            x0 += hex_width / 2
            #
            # If the first column is _not_ short on top, then off set
            # is simply hex_ph / 2. Otherwise, the offset is hex_ph
            y0   +=  hex_ph / 2
            voff -= 1
            voff -= inv_row
            v(f' Initial offset of image {x0},{y0}')
            
            # Treat each kind of rotation separately.  Note that -90 and
            # 180 uses the `is_short_bot' while 0 and 90 uses
            # `is_short_top'.  There might be a way to unify these, if
            # offsets and so on may warrent it, but it may be complete
            # overkill.
            is_off  = False
            col_map = {0  : (ulc, is_short_top, is_short_bot),
                       -1 : (urc, is_short_top, is_short_bot),
                       1  : (ulc, is_short_bot, is_short_top),
                       -2 : (urc, is_short_bot, is_short_top) }
            col_chk, is_s1, is_s2 = col_map[rot90]
            
            is_off = is_s1(col_chk)
            if is_off:
                y0     += hex_ph /2
            
            v(f'Is first column off: {is_off}')
            
            # For full columns, noting more is needed
            #
            # Below is if some columns are short both top and bottom.
            # VASSAL seems to start numbering from a given place, and
            # then use that for the rest numbering, and forgets to
            # take into account various offsets and the like.  hence,
            # we need to hack it hard.
            if iseven(nc):
                v(f'Even number of columns, perhaps hacks')
                if rot90 == 0:
                    # Hacks
                    #
                    # If the last column is short in both top and bottom,
                    # and we have inverse columns, but not inverse rows,
                    # then add to offset 
                    if inv_col == -1 and inv_row == 1 and \
                       is_s1(urc) and is_s2(urc):
                        voff += 1
                    # If the column we check for short is short both top
                    # and bottom, and we have inverse rows, but not
                    # inverse columns, then add offset
                    if inv_row == -1 and inv_col == 1 and \
                       is_s2(col_chk) and is_off:
                        voff += 1
                        
                if rot90 == -1:
                    # If the last column is short in both top and bottom,
                    # and we have inverse columns, then add to offset
                    if is_s1(urc) and inv_col == -1 and is_s2(urc):
                        voff -= inv_row
                        
                if rot90 == 1:
                    voff  += inv_row + (inv_row == 1)
                    # If the first column is short in both top and bottom,
                    # and we have inverse columns, then add to offset
                    if is_s1(ulc) and is_s2(ulc) and inv_col == -1:
                            voff += inv_row
                            
                if rot90 == -2:
                    voff    += inv_row * 2
                    # Hacks If the column we check for short is short both
                    # top and bottom, and we have either inverse rows and
                    # inverse columns, or rows and columns are normal,
                    # then add offset
                    if inv_col == inv_row and is_s1(col_chk) and is_s2(col_chk):
                        voff += 1
                    # If the first column is short in both top and bottom,
                    # and we have inverse columns and rows, then add to
                    # offset
                    if inv_col == inv_row and inv_col == -1 and \
                       is_s1(ulc) and is_s2(ulc):
                        voff += 1
            else:
                v(f'Odd number of columns')
                voff -= inv_row
                if rot90 == 1:
                    # If we offset in the column direction, add the
                    # inverse row direction, and if we have inverse rows,
                    # substract one, otherwise add 2.
                    voff  += (inv_row * hoff + (-1 if inv_row == -1 else 2))
                    # If we have a short column, and that column is even,
                    # then add, otherwise subtract, the inverse row
                    # direction, if the checked column is even.
                    voff  += ((1 if is_off else -1) *
                              inv_row if is_short_bot(2) else 0)
                if rot90 == 2:
                    voff    += inv_row * (2 + is_off) # OK for odd
                    
                    
            if rot90 == 0:
                if inv_col == -1 and iseven(nc): # OK
                    stagger =  not stagger
                hoff    -= (inv_col == -1) # OK
            
            if rot90 == -1: # CCW
                if inv_col == 1 and iseven(nc): # OK
                    stagger =  not stagger
                vdesc, hdesc =  hdesc, vdesc
                vdesc        =  not vdesc
                voff         += (inv_row == 1)
                hoff         -= (inv_col == 1) # OK
            
            if rot90 == 1: # CW
                if (inv_col == 1 and iseven(nc)) or isodd(nc): # OK
                    stagger =  not stagger
                vdesc, hdesc =  hdesc, vdesc
                hdesc        =  not hdesc
                hoff         -= (inv_col == -1) # OK
            
            if rot90 == -2:
                if (inv_col == -1 and iseven(nc)) or isodd(nc): # OK
                    stagger =  not stagger                
                vdesc, hdesc = not vdesc, not hdesc
                hoff    -= (inv_col == 1) # OK
                
            # Labels 
            if labels is not None:
                labmap = {
                    'auto': {
                        'hLeading': 1,'vLeading': 1,'hType': 'N','vType': 'N' },
                    'auto=numbers' : {
                        'hLeading': 1,'vLeading': 1,'hType': 'N','vType': 'N' },
                    'auto=alpha column': {
                        'hLeading': 0,'vLeading': 0,'hType': 'A','vType': 'N' },
                    'auto=alpha 2 column': {# Not supported
                        'hLeading': 1,'vLeading': 1,'hType': 'A','vType': 'N' },
                    'auto=inv y x plus 1': {
                        'hLeading': 1,'vLeading': 1,'hType': 'N','vType': 'N' },
                    'auto=x and y plus 1': {
                        'hLeading': 1,'vLeading': 1,'hType': 'N','vType': 'N' }
                }
                for l in labels.split(','): 
                    nargs.update(labmap.get(l,{}))
                    if 'alpha column' in l or 'alpha 2 column' in l:
                        hoff -= 1 # VASSAL 0->A, wargame 1->A
                    if l == 'auto=inv y x plus 1':
                        hoff += 1
                        #inv_row  =  not inv_row
                    if l == 'auto=x and y plus 1':
                        hoff -= 1
                        voff -= 1
            
            # Add margins 
            x0 += int(mx)
            y0 += int(my)
            
            targs['dx']         = hex_pw
            targs['dy']         = hex_ph
            nargs['vOff']       = voff 
            nargs['hOff']       = hoff 
            nargs['vDescend']   = vdesc
            nargs['hDescend']   = hdesc
            targs['edgesLegal'] = True
            targs['sideways']   = abs(rot90) == 1
            nargs['stagger']    = stagger
            targs['x0']         = int(x0+.5)
            targs['y0']         = int(y0+.5)
        
    # --------------------------------------------------------------------
    def getRectParams(self,i,llx,ury,width,height,targs,nargs):
        targs['dx']       = width
        targs['dy']       = height
        targs['x0']       = int(llx - width/2)
        targs['y0']       = int(ury + height/2)
        targs['color']    = rgb(0,255,0)
        nargs['color']    = rgb(0,255,0)
        nargs['vDescend'] = True
        nargs['vOff']     = -3
        nargs.update({'sep':',','vLeading':0,'hLeading':0})
        
    # ----------------------------------------------------------------
    def addZones(self,
                 zoned,
                 name,
                 info,
                 width,
                 height,
                 labels=None,
                 coords=None,
                 picinfo=None):
        '''Add zones to the Zoned element.

        Parameters
        ----------
        zoned : Zoned
            Parent element
        name : str
            Name of Zoned
        info : dict
            Dictionary of zones informatio
        width : int
            Width of parent
        height : int
            Height of parent
        labels : list
            On recursive call, list of labels
        coords : list
            On recursive call, coordinates
        picinfo : dict
            On recursive call, picture information
        '''
        grids = []
        picture = None

        with VerboseGuard(f'Adding zones to {name}') as v:
            for k, val in info.items():
                if k == 'labels': labels  = val;
                if k == 'coords': coords  = val
                if k == 'zoned':  picture = val
                if 'zone' not in k or k == 'zoned':
                    continue
            
                grids = [[k,val]] + grids  # Reverse order!
                # grids.append([k,v])
            
            if len(grids) < 1:
                return
            
            if picinfo is None:
                picinfo = self.getPictureInfo(picture,name,width,height)
                
            hex_width, hex_height, scx, scy, rot90, tran = picinfo 
                
            for g in grids:
                n, i = g
                v(f'Adding zone {n}')
            
                if 'scope' in n:
                    llx,lly = tran(*i['global lower left'])
                    urx,ury = tran(*i['global upper right'])
                    path    = [[llx,ury],[urx,ury],[urx,lly],[llx,lly]]
                    nm      = n.replace('zone scope ','')
                elif 'path' in n:
                    path    = [tran(*p) for p in i['path']]
                    llx     = min([px for px,py in path])
                    ury     = max([py for px,py in path])
                    nm      = n.replace('zone path ','')
            
                # Checkf if we have "point" type elements in this object and
                # add them to dict.
                points = [ val for k,val in i.items()
                           if (k.startswith('point') and
                               isinstance(val,dict) and \
                               val.get('type','') == 'point')]
            
                pathstr = ';'.join([f'{s[0]},{s[1]}' for s in path])
                v(f'Zone path ({llx},{ury}): {pathstr} ({len(points)})')
            
                ispool = 'pool' in n.lower() and len(points) <= 0
                zone = zoned.addZone(name           = nm,
                                     locationFormat = ("$name$"
                                                       if ispool else
                                                       "$gridLocation$"),
                                     useParentGrid  = False,
                                     path           = pathstr)
            
                # Do not add grids to pools 
                if ispool:
                    v(f'Board {n} is pool with no points')
                    continue
            
                targs  = {'color':rgb(255,0,0),'visible':self._visible}
                nargs  = {'color':rgb(255,0,0),'visible':self._visible}
                # print(targs,nargs)
                if 'turn' in n.lower(): nargs['sep'] = 'T'
                if 'oob' in n.lower():  nargs['sep'] = 'O'
            
                if len(points) > 0:
                    with VerboseGuard('Using region grid') as vv:
                        grid = zone.addRegionGrid(snapto  = True,
                                                  visible = self._visible)
                        for j,p in enumerate(points):
                            pn = p["name"].strip()
                            pp = p.get('parent','').strip()
                            pc = p["coords"]
                            if j == 0: vv(f'',end='')
                            vv(f'[{pn}] ',end='',flush=True,noindent=True)

                            if pn.endswith(' flipped'):
                                pn = pn[:-len(' flipped')]
                                
                            x, y = tran(*pc)
                            r = grid.addRegion(name      = pn,
                                               originx   = x,
                                               originy   = y,
                                               alsoPiece = True,
                                               prefix    = pp)
                        v('')
                    
                elif 'hex' in n.lower():
                    margin = i.get('board frame',{}).get('margin',0)
                    mx     = scx * margin
                    my     = scy * margin
                    # self.message(f'{margin} -> {scx},{scy} -> {mx},{my}')
                    w      = abs(urx - llx)-2*mx
                    h      = abs(ury - lly)-2*my
                    self.getHexParams(llx         = llx,         
                                      lly         = lly,         
                                      urx         = urx,         
                                      ury         = ury,         
                                      mx          = mx,          
                                      my          = my,          
                                      hex_width   = hex_width,   
                                      hex_height  = hex_height,  
                                      rot90       = rot90,       
                                      labels      = labels,      
                                      coords      = coords,      
                                      targs       = targs,       
                                      nargs       = nargs)       
            
                    v(f'Adding hex grid')
                    
                    grid = zone.addHexGrid(**targs)
                    grid.addNumbering(**nargs)
                    
                else:
                    width  = hex_width / HEX_WIDTH * RECT_WIDTH
                    height = hex_height / HEX_HEIGHT * RECT_HEIGHT
                    self.getRectParams(i,llx,ury,width,height,targs,nargs)
            
                    v(f'Adding rectangular grid')
                    
                    grid = zone.addSquareGrid(**targs)
                    grid.addNumbering(**nargs)
                
            
                # Once we've dealt with this grid, we should see if we have
                # any embedded zones we should deal with.
                self.addZones(zoned,name,i,width,height,
                              labels=labels,
                              coords=coords,
                              picinfo=picinfo)
            
    
    # ----------------------------------------------------------------
    def addBoards(self):
        '''Add Boards to the module
        '''
        with VerboseGuard('Adding boards') as v:
            hasFlipped = False
            for cn,cd in self._categories.get('counter',{}).items():
                for sn in cd:
                    if ' flipped' in sn:
                        hasFlipped = True
                        break
            
            v(f'Has flipped? {hasFlipped}')
            for bn, b in self._categories.get('board',{}).get('all',{}).items():
                self.addBoard(bn, b,hasFlipped=hasFlipped)


    # ----------------------------------------------------------------
    def getIcon(self,name,otherwise):
        with VerboseGuard(f'Get Icon {name}') as v:
            icon   = self._categories\
                         .get('icon',{})\
                         .get('all',{})\
                         .get(name,{
                             'filename':otherwise})['filename']
            v(f'Using "{icon}"')
            return icon
        
    # ----------------------------------------------------------------
    def addOOBs(self):
        '''Add OOBs  to the game'''
        oobc = self._categories.get('oob',{}).get('all',{}).items()
        if len(oobc) < 1:
            return

        with VerboseGuard(f'Adding OOBs') as v:
            icon   = self.getIcon('oob-icon','/images/inventory.gif')
            v(f'Using icon "{icon}" for OOB')
            charts = \
                self._game.addChartWindow(name='OOBs',
                                          hotkey      = self._oobKey,
                                          description = 'OOBs',
                                          text        = '',
                                          icon       = icon,
                                          tooltip     = 'Show/hide OOBs')
            tabs = charts.addTabs(entryName='OOBs')
            
            for on, o in oobc:
                widget = tabs.addMapWidget(entryName=on)
                self.addOOB(widget, on, o)


    # ----------------------------------------------------------------
    def addOOB(self,widget,name,info):
        '''Add a OOB elements to the game

        Parameters
        ----------
        widget : Widget
            Widget to add to
        name : str
            Name
        info : dict
            Information on the OOB image 
        '''
        map = widget.addWidgetMap(mapName   = name,
                                  markMoved = 'Never',
                                  hotkey    = '')
        map.addCounterDetailViewer()
        map.addStackMetrics()
        map.addImageSaver()
        map.addTextSaver()
        map.addForwardToChatter()     
        map.addMenuDisplayer()        
        map.addMapCenterer()          
        map.addStackExpander()        
        map.addPieceMover()           
        map.addKeyBufferer()          
        map.addSelectionHighlighters()
        map.addHighlightLastMoved()   
        map.addZoomer()
        
        picker          = map.addPicker()
        ulx,uly,lrx,lry = self.getBB(info['img'])
        board           = picker.addBoard(name  = name,
                                          image = info['filename'])
        zoned           = board.addZonedGrid()
        zoned.addHighlighter()
        
        if not 'zones' in info:
            zone = zoned.addZone(name = 'full',
                                 useParentGrid = False,
                                 path=(f'{ulx},{uly};' +
                                       f'{lrx},{uly};' +
                                       f'{lrx},{lry};' +
                                       f'{ulx},{lry}'))
            grid = zone.addSquareGrid()
            grid.addNumbering()

            return

        # If we get here, we have board info!
        w = abs(ulx-lrx)
        h = abs(uly-lry)
        self.addZones(zoned,name,info['zones'],w,h)

    # ----------------------------------------------------------------
    def addCharts(self):
        '''Add Charts elements to game
        '''
        chartc = self._categories.get('chart',{}).get('all',{}).items()
        if len(chartc) < 1:
            return

        with VerboseGuard('Adding charts') as v:
            charts = self._game.addChartWindow(name = 'Charts',
                                               hotkey = self._chartsKey,
                                               description = '',
                                               text = '',
                                               tooltip = 'Show/hide charts',
                                               icon    = self.getIcon('chart-icon',
                                                                      '/images/chart.gif'))
            tabs = charts.addTabs(entryName='Charts')
            for i, (cn, c) in enumerate(chartc):
                if i == 0: v('',end='')
                v(f'[{cn}] ',end='',flush=True,noindent=True)
            
                tabs.addChart(chartName   = cn,
                              description = cn,
                              fileName    = c['filename'])
            
            v('')

    # ----------------------------------------------------------------
    def addDie(self):
        '''Add a `Die` element to the module
        '''
        if self._dice is not None and len(self._dice) > 0:
            return
        self._game.addDiceButton(name       = '1d6',
                                 hotkey     = self._diceKey)



#
# EOF
#
