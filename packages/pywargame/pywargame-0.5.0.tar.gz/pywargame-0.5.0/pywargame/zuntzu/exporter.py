## BEGIN_IMPORTS
from pywargame.common import VerboseGuard, Verbose
from pywargame.vassal.buildfile import BuildFile
from pywargame.vassal.documentation import Documentation
from pywargame.vassal.traits import *
from pywargame.vassal.base import *
from pywargame.vassal.moduledata import ModuleData
from pywargame.vassal.exporter import Exporter
from pywargame.vassal.mapelements import LayerControl
from pywargame.vassal.vsav import VSav
from . base import ZTImage
## END_IMPORTS


class ZTExporter(Exporter):
    def __init__(self,
                 gamebox,
                 version       = None,
                 vassalVersion = '3.6',
                 allmaps       = False,
                 mainMap       = None,
                 nrotations    = 6,
                 symbolic_dice = True):
        self._gamebox       = gamebox
        self._version       = '0.0.1' if version is None else version
        self._vassalVersion = vassalVersion
        self._allmaps       = allmaps
        self._main_map      = mainMap
        self._n_rotations   = nrotations
        self._symbolic_dice = symbolic_dice

    # ----------------------------------------------------------------
    def setup(self):
        with VerboseGuard('Saving images'):
            from pathlib import Path


    # ----------------------------------------------------------------
    def createModuleData(self):
        with VerboseGuard('Creating module data'):
            self._moduleData = ModuleData()
            data             = self._moduleData.addData()
            data.addVersion      (version='0.0.1')
            data.addVASSALVersion(version=self._vassalVersion)
            data.addName         (name   =self._gamebox._name)
            data.addDescription  (description=self._gamebox._desc)
            data.addDateSaved    ()

    # ----------------------------------------------------------------
    def createBuildFile(self,
                        ignores = ['all',
                                   'common',
                                   'marker',
                                   'markers',
                                   ' ']):
        with VerboseGuard(f'Creating build file') as v:
            self._build = BuildFile() # 'buildFile.xml')
            self._game  = self._build.addGame(
                name        = self._gamebox._name,
                version     = self._version,
                description = self._gamebox._desc)
            
            v(f'Adding description')
            self.addDocumentation()
            
            v(f'Adding command encoder')
            self._game.addBasicCommandEncoder()

            v(f'Adding Global options')
            go = self._game.addGlobalOptions(
                autoReport         = 'Use Preferences Setting',
                centerOnMove       = 'Use Preferences Setting',
                nonOwnerUnmaskable = 'Use Preferences Setting',
                playerIdFormat     = '$playerName$')
            go.addOption(name='undoHotKey',value=key('Z'))

            v(f'Adding dice hands')
            self.addDiceHands()
            
            v(f'Adding prototypes')
            self.addPrototypes()

            v(f'Adding pieces')
            self.addPieces()

            v(f'Fixing up map locations')
            self.fixMaps()
            
            v(f'Adding maps')
            self.addMaps()

            v(f'Adding counter sheets')
            self.addCounterSheets()

            v(f'Adding scenarios')
            self.addScenarios()

    def fixMaps(self):
        # Scale all scenarios to target resolution before anything else
        for sc in self._gamebox._scenarios:
            sc.scale(ZTImage.target_dpi / 600)

        for m in self._gamebox._maps:
            self.fixMap(m)

    def fixMap(self,map):
        from wand.image import Image, Color
        from wand.drawing import Drawing
        
        with VerboseGuard(f'Fixing up map {map._name}') as v:
            tgt = [s for s in self._gamebox._scenarios if s.on_map(map._name)]
            if not tgt:
                v(f'No target scenario found for map')
                return

            # if len(tgt) > 1:
            #     v(f'More than 1 target scenario found for map')
            #     return
            dxs = []
            dys = []
            ws  = []
            hs  = []
            for sc in tgt:
                v(f'Target scenario for map "{map._name}" is "{sc._name}"')
                v(f'Map "{map._name}" image is '
                  f'{map._image._image.width}x{map._image._image.height}')
            
                ly = sc.map_layout(map._name)[0]
                v(f'Layout at {ly.left},{ly.top} {ly.lrx},{ly.lry}')

                bb  = sc.calc_bounding_box(map._name if self._allmaps
                                           else None)
                v(f'Bounding box for map: {bb}')
                
                ulx = min([s._x - self._gamebox._piece_map[p]._front.width/2
                           for s in ly._stacks for p in s._ids]+[0])
                lrx = max([s._x + self._gamebox._piece_map[p]._front.width/2
                           for s in ly._stacks for p in s._ids]+
                          [map._image._image.width])
                uly = min([s._y - self._gamebox._piece_map[p]._front.height/2
                           for s in ly._stacks for p in s._ids]+[0])
                lry = max([s._y + self._gamebox._piece_map[p]._front.height/2
                           for s in ly._stacks for p in s._ids]+
                          [map._image._image.height])
                v(f'Bounding box for map: {bb} {ulx},{uly},{lrx},{lry}')

                # Translate the layout
                mar = 10
                sdx = -int(ulx-.5)+mar
                sdy = -int(uly-.5)+mar
                sw  = int(lrx+sdx+.5)+2*mar
                sh  = int(lry+sdy+.5)+2*mar
                dxs.append(sdx)
                dys.append(sdy)
                ws .append(sw)
                hs .append(sh)
                v(f'{sc._name}: dx={sdx} dy={sdy} w={sw} h={sh}')
                
            # Find the smallest translation, and largest size
            dx = max(dxs)
            dy = max(dys)
            w  = max(ws)
            h  = max(hs)
            v(f'All scenarios translated by {dx},{dy}')
            for sc in tgt:
                sc.translate(dx,dy)
                # v(f'{sc}')
            
            v(f'Background image {w}x{h}')
            bg = Image(width=w,height=h,
                       colorspace='truecolor',
                       background=Color('#404040'))
            bg.format = 'png'
            #map._image._image.save(filename=map.filename)
            
            v(f'Compose over at {dx},{dy}')
            bg.composite(map._image._image,left=dx,top=dy)

            # Replace with new image
            #bg.save(filename='bg_'+map.filename)
            map._image._image = bg #.save(filename=map.filename)
            
    # ----------------------------------------------------------------
    def saveImages(self,vmod):
        pass

    # ----------------------------------------------------------------
    def savePNG(self,vmod,filename,img):
        #with VerboseGuard(f'Saving PNG {filename}'):
        from io import BytesIO

        stream = BytesIO()
        img.save(stream)
        vmod.addFile('images/'+filename,stream.getvalue())

    # ----------------------------------------------------------------
    def addDocumentation(self):
        '''Add documentation to the module.  This includes rules,
        key-bindings, and about elements.
        '''
        with VerboseGuard('Adding documentation') as v:
            doc = self._game.addDocumentation()

            desc = f'''<html><body>
            <h1>Module</h1>
            <p>
            This module was created from a ZunTzu gamebox
            {self._gamebox._name} by the Python script
            <code>ztexport.py</code> available from
            </p>
            <p>
            Ctrl-click to select terrain pieces.
            </p>
            <pre>
            https://gitlab.com/wargames_tex/pywargames
            </pre>
            <h1>Game</h1>
            <p>{self._gamebox._desc}</p>
            <h1>Scenarios</h1>
            <ul>
            {'\n'.join(['<li>'+s._name+': '+s._desc+'</li>'
                        for s in self._gamebox._scenarios])}            
            </ul>
            <h1>Copyright</h1>
            <p>&copy; {self._gamebox._copy}</p>
            </body></html>;'''

            self._vmod.addFile('help/description.html',desc)
            doc.addHelpFile(title='Description',
                            fileName='help/description.html')

            if self._gamebox._splash:
                v(f'Adding splash screen') 
                fname = 'splash.'+self._gamebox._splash.format.lower()
                self.savePNG(self._vmod,fname,self._gamebox._splash)
                self._gamebox._splash = None
                doc.addAboutScreen(title=self._gamebox._name,
                                   fileName=fname)
                
                
            
    # ----------------------------------------------------------------
    def addDiceHands(self):
        with VerboseGuard(f'Adding dice hands: '
                          f'{self._gamebox._dice_hands}') as v:
            seen = set()
            for no,hand in enumerate(self._gamebox._dice_hands):
                name = f'{len(hand._dice)}d{hand._type}'
                if name in seen:
                    name += f'_{no}'
                    
                seen.add(name)
                # v(f'Prepare to add dice {name}')
                self.addDiceHand(name,hand)

    # ----------------------------------------------------------------
    def addDiceHand(self,name,hand):
        with VerboseGuard(f'Adding dice hand {name} '
                          f'{len(hand._dice)}d{hand._type}') as v:

            cnt  = len(hand._dice)
            sid  = hand._type

            rep = '$name$ = '
            if cnt > 1:
                rep += ' + '.join([f'$result{i+1}$' for i in range(cnt)])+' = '
            rep += '$result$'
            ky  =  {4:  '4',
                    6:  '6',
                    8:  '8',
                    10: '0',
                    12: '2',
                    20: '3'}[hand._type]
            #v(f'Dice defined: {hand._dice}')
            if not self._symbolic_dice:
                self._game.addDiceButton(name         = name,
                                         hotkey       = key(ky,ALT),
                                         tooltip      = f'Roll {cnt}d{sid}',
                                         text         = name,
                                         nDice        = cnt,
                                         nSides       = sid,
                                         reportFormat = rep,
                                         reportTotal  = True)
                return


            # Could be used instead if we knew we had images
            #
            v(f'Adding symbolic dice')

            # Make icon.  A nicer way would be to combine the images
            # created below and then scale to the appropriate height.
            #
            # For another time.
            # drawer = DiceDrawer(hand._type,20,20,
            #                     fg='white',
            #                     bg='black')
            # image = drawer.draw(hand._type//2)
            # image.format = 'png'
            # fn    = f'{name}-logo.png'
            # self.savePNG(self._vmod,fn,image)

            rep = '{name+": "+'
            def img(i,d):
                return (f'"<img src=\'{name}{i}_"+result{i}+".png\' '
                        f'width=\'24\' height=\'24\'>"')
            def txt(i,d):
                bg = d['pips']
                fg = d['color']
                bg = 0xFFFFFF
                if fg == 0xFFFFFF:
                    fg = 0

                return (f'"<span style=\'color:#{fg:06x}; '
                        f'background-color:#{bg:06x}; '
                        f'font-weight:bold; '
                        f'padding: 5px;\'>"+'
                        f'result{i}+"</span>"')
                
            rep += '+'.join([img(i+1,d)
                                 for i,d in enumerate(hand._dice)])+\
                                         '+" = "+'
            rep += '+" + "+'.join([txt(i+1,d)
                                   for i,d in enumerate(hand._dice)])
            if cnt > 1:
                rep += '+" = <b>"+numericalTotal+"</b>"}'
            else:
                rep += '}'
                

            diceW  = 80
            diceH  = 80
            iconfn = f'{name}-icon.png'
            but    = self._game.addSymbolicDice(
                name         = name,
                icon         = iconfn,
                hotkey       = key(str(hand._type),ALT),
                tooltip      = f'Roll {cnt}d{sid}',
                text         = name,
                doReport     = True,
                resultWindow = True,
                format       = rep,
                windowX      = (diceW+10)*len(hand._dice),
                windowY      = diceH+10)
            v(f'Report format: {rep}')

            from wand.image import Image as WImage
            from wand.color import Color
            from random import randint
            
            icon = WImage(format='png',width=diceW,height=diceH)
            icon.alpha_channel = True
            icon.background_color = Color('transparent')
            
            for i, dice in enumerate(hand._dice):
                # v(f'- {dice}')
                dien = f'{name}{i+1}'
                die  = but.addDie(name=dien)
                drawer = DiceDrawer(hand._type,80,80,
                                    fg=dice['pips'],
                                    bg=dice['color'])

                imgs = []
                for num in range(1,hand._type+1):
                    if hand._type == 10 and num == 10:
                        num = 0
                    image = drawer.draw(num)
                    image.format = 'png'
                    imgs.append(image)
                    fn    = f'{dien}_{num}.png'
                    self.savePNG(self._vmod,fn,image)
                    
                    die.addFace(icon = fn,
                                text = f'{num}',
                                value = num)

                icon.sequence.append(imgs[randint(0,hand._type-1)])

            icon.smush(stacked=False,offset=0)
            sc = 20 / diceH
            icon.resize(int(sc * icon.width),int(sc * icon.height))
            icon.format = 'png'
            self.savePNG(self._vmod,iconfn,icon)
            
            
            
    # ----------------------------------------------------------------
    def addPrototypes(self):
        with VerboseGuard(f'Creating prototypes'):
            protos = self._game.addPrototypes()

            traits = [TrailTrait(),
                      RotateTrait(nangles = self._n_rotations),
                      DeleteTrait(),
                      BasicTrait()]
            protos.addPrototype(name        = 'Basic prototype',
                                description = 'Prototype for most',
                                traits      = traits)


            traits = [PrototypeTrait(name      = 'Basic prototype'),
                      NoStackTrait(
                          select      = NoStackTrait.CTRL_SELECT,
                          bandSelect  = NoStackTrait.NEVER_BAND_SELECT,
                          move        = NoStackTrait.SELECT_MOVE,
                          canStack    = False,
                          description = 'Terrain does not stack'),
                      MarkTrait(name  = 'PieceLayer',
                                value = 'Terrains'),
                      BasicTrait()]
            protos.addPrototype(name        = 'Terrain prototype',
                                description = 'Prototype for terrain',
                                traits      = traits)

            traits = [PrototypeTrait(name = 'Basic prototype'),
                      MarkTrait(name  = 'PieceLayer',
                                value = 'Pieces'),
                      BasicTrait()]

            protos.addPrototype(name        = 'Piece prototype',
                                description = 'Prototype for pieces',
                                traits      = traits)

            traits = [PrototypeTrait(name = 'Basic prototype'),
                      MarkTrait(name  = 'PieceLayer',
                                value = 'Cards'),
                      BasicTrait()]

            protos.addPrototype(name        = 'Card prototype',
                                description = 'Prototype for cards',
                                traits      = traits)
            
    # ----------------------------------------------------------------
    def addPieces(self):
        with VerboseGuard(f'Adding pieces') as v:
            window = self._game.addPieceWindow(name = 'Pieces',
                                               hotkey = key('C',ALT))

            combo  = window.addCombo(entryName = 'Pieces')
            
            self._piece_slots = {}

            for sheet in self._gamebox._counter_sheets:
                v(sheet._name)
                if len(sheet._piece) <= 0 and len(sheet._card) <= 0:
                    continue
                plist = self.addPieceContainer(combo, sheet._name)
                self.addSheetPieces(plist,sheet._piece,sheet._card)
            
    # ----------------------------------------------------------------
    def addSheetPieces(self,container,pieces,cards):
        with VerboseGuard(f'Adding pieces to {container["entryName"]} '+
                          f'{len(pieces)} pieces, {len(cards)} cards'):
            for piece in pieces+cards:
                boardName = container['entryName']
                board     = self._game.getBoards(asdict=True).get(boardName,None)
                mapName   = board.getMap()['mapName'] if board else ''
                no     = self._gamebox._piece_id[piece]
                traits = [
                    PrototypeTrait(
                        name = (('Terrain' if piece._terrain else
                                 ('Card' if piece._card else 'Piece'))+
                                ' prototype')),
                    SendtoTrait(
                        mapName     = boardName,
                        boardName   = mapName,
                        name        = f'Return to {boardName}',
                        key         = key('R',CTRL_SHIFT),
                        restoreName = '',
                        restoreKey  = '',
                        x           = piece._x,
                        y           = piece._y,
                        description = 'Return to where it came from',
                        destination = SendtoTrait.LOCATION)
                ]
                name       = f'{no:06d}'
                front_name = f'{name}_front.{piece._front.format.lower()}'
                back_name  = (f'{name}_back.{piece._back.format.lower()}'
                              if piece.two_sides else None)
                if back_name is not None:
                    traits.extend([
                        LayerTrait(
                            images       = [front_name,back_name],
                            newNames     = ['','+ reversed'],
                            activateName = '',
                            decreaseName = '',
                            increaseName = 'Flip',
                            increaseKey  = key('F'),
                            decreaseKey  = '',
                            name         = 'Step'),
                        ReportTrait(key('F'))])
                gpid = self._game.nextPieceSlotId()
                size = piece.size
                traits.append(
                    BasicTrait(name     = name,
                               filename = front_name,
                               gpid     = gpid))
                
                self._piece_slots[piece] = container.addPieceSlot(
                    entryName = name,
                    gpid      = gpid,
                    traits    = traits,
                    width     = piece.width,
                    height    = piece.height)

                for img,fname in zip([piece._front,piece._back],
                                     [front_name,back_name]):
                    if img is None:
                        continue
                    fnameext = fname
                    self.savePNG(self._vmod,fnameext,img)
                #piece._front = None
                #piece._back  = None
                    
            # self.saveImages(self,vmod)
    # ----------------------------------------------------------------
    def addPieceContainer(self,container,name):
        #panel = container.addPanel(entryName = name,
        #                           fixed = False,
        #                           vert  = True)
        #return panel
        panel = container.addPanel(entryName = name, fixed = False)
        plist = panel.addList(entryName = f'{name}',
                              width     = 300,
                              height    = 300,
                              divider   = 150)
        return plist
    
    # ----------------------------------------------------------------
    def addMapLayers(self,map):
        layerDesc = {'Terrains': {'t': 'Terrain', 'i': ''},
                     'Cards':    {'t': 'Cards',   'i': ''},
                     'Pieces':   {'t': 'Pieces',  'i': ''}}
        layers = map.addLayers(property = 'PieceLayer',
                               layerOrder = layerDesc)
        for layerTitle, layerData in layerDesc.items():
            layers.addControl(name    = layerTitle,
                              tooltip = f'Toggle display of {layerTitle}',
                              text    = f'Toggle {layerData["t"]}',
                              icon    = layerData['i'],
                              layers  = [layerTitle])
        layers.addControl(name = 'Show all',
                          tooltip = 'Show all',
                          text    = 'Show all',
                          command = LayerControl.ENABLE,
                          layers  = list(layerDesc.keys()))
        map.addMenu(description = 'Toggle layers',
                    text        = '',
                    tooltip     = 'Toggle display of layers',
                    icon        = '/images/inventory.gif',
                    menuItems   = ([f'Toggle {ln["t"]}'
                                        for ln in layerDesc.values()]
                                       +['Show all']))         

    # ----------------------------------------------------------------
    def addMapDefaults(self,map):
        s      = ZTImage.target_dpi / 150
        z      = [0.05,0.1,0.2,0.25,0.333,0.4,0.5,
                  0.555,0.625,0.75,1.0,1.25,1.6,1.8,2]        
        if s >  4: z = z[:-3]
        if s <  2: z = z[2:]
        z0           = 6
        map.addGlobalMap()
        # Basics
        map.addStackMetrics(
            exSepX    = int(s * 12 + .5),
            exSepY    = int(s * 16 + .5),
            unexSepX  = int(s *  8 + .5),
            unexSepY  = int(s * 10 + .5)
        )
        map.addImageSaver()
        map.addTextSaver()
        map.addForwardToChatter()     
        map.addMenuDisplayer()        
        map.addMapCenterer()          
        map.addStackExpander()        
        map.addPieceMover()           
        map.addKeyBufferer()
        map.addForwardKeys()
        map.addSelectionHighlighters()
        map.addHighlightLastMoved()
        map.addScroller()
        map.addZoomer(zoomLevels = z, zoomStart = z0)
        
    # ----------------------------------------------------------------
    def addMaps(self):
        with VerboseGuard(f'Adding maps') as v:
            if not self._allmaps:
                self.addMap(*self._gamebox._maps)
                return

            mapNames = [self.addMap(m) for m in self._gamebox._maps]

            filtered = [n for n in mapNames if n != '' and n != self._main_map]
            v(f'Filtered set of maps: {filtered}')
            if len(filtered) > 0:
                self._game.addMenu(description = 'Maps',
                                   text        = 'Maps',
                                   tooltip     = 'Show or hide maps',
                                   icon        = '/images/map.gif',
                                   menuItems   = filtered)
                
                
    # ----------------------------------------------------------------
    def addMap(self,*maps):
        with VerboseGuard(f'Adding maps') as v:
            isMain = False
            mapName     = maps[0]._name
            if not self._main_map or self._main_map == mapName:
                self._main_map = mapName
                isMain = True
                
            map = self._game.addMap(mapName    = mapName,
                                    buttonName = '' if isMain else mapName,
                                    hotkey     = '' if isMain else key('M',ALT),
                                    launch     = not isMain
                                    )
            self.addMapDefaults(map)
            map.addLOS()
            map.addCounterDetailViewer()
            self.addMapLayers(map)
            
            picker  = map.addBoardPicker()
            self._picker = picker
            for m in maps:
                imgname = m.filename
                size    = m.size
                brd     = picker.addBoard(name   = m._name,
                                          image  = imgname,
                                          width  = size[0],
                                          height = size[1])
                zoned  = brd.addZonedGrid()
                zoned.addHighlighter()
                zone   = zoned.addZone(name = 'Full',
                                       useParentGrid = False,
                                       path=(f'{0},{0};' +
                                             f'{size[0]},{0};' +
                                             f'{size[0]},{size[1]};' +
                                             f'{0},{size[1]}'))

                self.savePNG(self._vmod,imgname,m._image._image)
                m._image._image = None

            return mapName
    
    # ----------------------------------------------------------------
    def addCounterSheets(self):
        with VerboseGuard(f'Adding Charts') as v:
            window = \
                self._game.addChartWindow(name='Charts',
                                          hotkey = key('A',ALT),
                                          description = 'Charts',
                                          text        = '',
                                          icon       = '/images/chart.gif',
                                          tooltip     = 'Show/hide Charts')
            tabs = window.addTabs(entryName='Charts')

            for sheet in self._gamebox._counter_sheets:
                widget = tabs.addMapWidget(entryName=sheet._name)
                self.addCounterSheet(widget,sheet)

    # ----------------------------------------------------------------
    def addCounterSheet(self,widget,sheet):
        with VerboseGuard(f'Adding counter sheet {sheet._name}') as v:
            map = widget.addWidgetMap(mapName   = sheet._name,
                                      markMoved = 'Never',
                                      hotkey    = '')
            self.addMapDefaults(map)
            self.addMapLayers(map)
            
            size   = sheet.size
            picker = map.addPicker()
            brd    = picker.addBoard(name  = sheet._name,
                                     image = sheet.filename)
            zoned  = brd.addZonedGrid()
            zoned.addHighlighter()
            zone   = zoned.addZone(name = 'Full',
                                   useParentGrid = False,
                                   path=(f'{0},{0};' +
                                         f'{size[0]},{0};' +
                                         f'{size[0]},{size[1]};' +
                                         f'{0},{size[1]}'))

            self.savePNG(self._vmod,sheet.filename,sheet._front._image)
            self.addAtStart(map,sheet._piece+sheet._card)
            sheet._front._image = None
            
    # ----------------------------------------------------------------
    def addAtStart(self,map,pieces):
        with VerboseGuard(f'Adding at-start to {map["mapName"]} '+
                          f'{len(pieces)} pieces and cards') as g:
            toAdd = {}
            
            for piece in pieces:
                x    = piece._x
                y    = piece._y
                grid = (x,y)
                slot = self._piece_slots[piece]
                #g(f'Adding piece at {x},{y}')
                if grid not in toAdd:
                    toAdd[grid] = {'center': (x,y),
                                   'pieces': [] }
                toAdd[grid]['pieces'].append(slot)

            for grid, dpieces in toAdd.items():
                center  = dpieces['center']
                name    = f'{grid[0]:06d}{grid[1]:06d}'
                atstart = map.addAtStart(name            = name,
                                         useGridLocation = False,
                                         owningBoard     = map["mapName"],
                                         x               = center[0],
                                         y               = center[1])
                atstart.addPieces(*dpieces['pieces'])

    # ----------------------------------------------------------------
    def addDeadMap(self,sides):
        pass

    # ----------------------------------------------------------------
    def addScenarios(self):
        menu = self._game.addPredefinedSetup(name = 'Setups',
                                             isMenu = True)

        menu.addPredefinedSetup(name = 'No setup',
                                file = '',
                                useFile = False,
                                description = 'No initial setup')
        
        for sc in self._gamebox._scenarios:
            self.addScenario(sc,menu)

    # ----------------------------------------------------------------
    def remapIds(self,scenario):
        from pprint import pprint
        with VerboseGuard(f'Remapping piece ID for scenario '
                          f'"{scenario._name}"') as v:
            tmp = []
            for layout in scenario._layouts:
                cs = self._gamebox._sheets_map.get(layout._name,None)
                if not cs:
                    v(f'Missing counter sheet {layout._name} - maybe map')
                    continue
                
                tmp.extend(cs._piece+cs._card)


            # Map from ID to piece - only used counter sheets in this scenario
            # pprint(tmp)
            piece_map = {i: p for i,p in enumerate(tmp)}
            # print(piece_map)
            # piece_id  = {v: k for k,v in piece_map.items()}

        return piece_map
    
    # ----------------------------------------------------------------
    def changeSlot(self,slot,flipped,angle,changed):
        if angle == 0 and not flipped:
            return

        # Valid angles are
        #
        # for i in range(nangles):
        #    angle[i] = - i * 360 // nangles
        #
        # validAngles = [-i * 360 // nangles for i in range(nangles)]
        changed[slot['entryName']] = {'angle':angle,
                                      'step': 2 if flipped else 1}

    # ----------------------------------------------------------------
    def updateSlot(self,name,traits,changed):
        changes  = changed.get(name,None)
        if not changes:
            return

        with VerboseGuard(f'Updating rotation and step state of '
                          f'{name} to {changes}') as v:
            rot      = Trait.findTrait(traits, RotateTrait.ID)
            lyr      = Trait.findTrait(traits, LayerTrait.ID,
                                       key='name', value='Step')
            if not rot and not lyr:
                v(f'No traits to modify!')
                return
            
            angle    = changes['angle']
            step     = changes['step']
            nangle   = int(rot['nangles'])
            fangle   = angle
            if nangle != 1:
                # Funny calculation in VASSAL 
                a        = ((angle % 360) - 360) % 360
                e        = (-a / 360) * nangle
                fangle   = int(round(e) % nangle)
            # v(f'nangle={nangle} fangle={fangle}')
            if rot: rot.setState(angle = fangle)
            if lyr: lyr.setState(level = step)
        

    # ----------------------------------------------------------------
    def restoreSlot(self,slot,step,angle):
        # traits   = slot.getTraits()
        # rot      = Trait.findTrait(traits, RotateTrait.ID)
        # lyr      = Trait.findTrait(traits, LayerTrait.ID,
        #                            key='name', value='Step')
        # 
        # rot.setState(angle=rot)
        # lyr.setState(level=step)
        # 
        # slot.setTraits(*traits)
        pass 
    
    # ----------------------------------------------------------------
    def addScenario(self,scenario,menu):
        from sys import stderr
        from pprint import pprint
        
        with VerboseGuard(f'Adding a scenario {scenario._name}') as v:
            vsav    = VSav(self._build,self._vmod)
            save    = vsav.addSaveFile()
            changed = {}

            # ZunTzu reads in the counter sheets specified in a given
            # scenario, and then builds and array of those counters.
            # However, since we already have read in the counters, we
            # need to simply remap the index here.
            piece_map = self.remapIds(scenario)#self._gamebox._piece_map
            # pprint(piece_map)
            
            selectedBoard = None
            selectedMap   = None
            # First, loop over layouts and see if we can find the map
            # we're looking for.
            for layout in scenario._layouts:
                boardName = layout._name
                board     = self._game.getBoards(asdict=True).get(boardName,
                                                                  None)
                if not board:
                    # Try the next layout
                    continue

                map = board.getMap()
                if not map:
                    # A board without a map?
                    continue

                if not isinstance(map.getParent(),Game):
                    # Parent of map is not the game
                    continue

                selectedMap   = map
                selectedBoard = board
                break

            if not selectedMap:
                print(f'No map found for scenario {scenario._name}')

            mapName = selectedMap['mapName']
            boardName = selectedBoard['name']
            
            for layout in scenario._layouts:
                v(f'Layout {layout._name} with {len(layout._stacks)}')
                if len(layout._stacks) <= 0:
                    continue

                thisMap = mapName
                if self._allmaps:
                    boardName = layout._name
                    board     = self._game.getBoards(asdict=True)\
                                          .get(boardName, None)
                    
                    map = board.getMap() if board else None
                    if map:
                        # A board without a map?
                        thisMap = map['mapName']

                # In principle, it could be done like this, but to be
                # on the safe side, we do it a tad more laboriously.
                #
                # mapped = {(s._x,s._y):
                #           [self._piece_slots[self._gamebox._piece_map[i]]
                #            for i in s._ids]
                #           for s in layout._stacks}
                mapped  = {}
                v(f'Layout has {len(layout._stacks)}')
                for s in layout._stacks:
                    slots = []
                    for i,f,r in zip(s._ids,s._flip,s._rot):
                        v(f'Piece {i}')
                        piece = piece_map.get(i, None)
                        if not piece:
                            print(f'Could not find piece for id {i}',
                                  file=stderr)
                            continue
                        slot = self._piece_slots.get(piece, None)
                        if not slot:
                            print(f'Could not find slot for piece {piece}',
                                  file=stderr)
                            continue

                        # Set states
                        self.changeSlot(slot, f, r, changed)
                        
                        # v(f'id={i} -> piece={piece} -> slot={slot}')
                        slots.append(slot)

                    mapped[(int(s._x+.5),int(s._y+.5))] = slots

                # self._picker.getMap()['mapName']
                v(f'Add pieces to map: {thisMap}')
                save.addNoGrid(thisMap, mapped)

            v(f'Selected map/board {mapName}/{boardName}')
            
            picker = selectedMap.getBoardPicker(single=True)[0]
            
            if picker:
                picker.selectBoard(boardName)
                v(f'Selected map: {picker["selected"]}')
            
            # print('\n'.join(save.getLines()))
            # lines = []
            # save._otherLines(lines)
            # print('\n'.join(lines))
            vsav.run(savename    = scenario._file+'.vsav',
                     description = scenario._desc,
                     update      = lambda n,t : self.updateSlot(n,t,changed))

            if picker:
                picker.selectBoard(None)

            menu.addPredefinedSetup(name=scenario._name,
                                    useFile=True,
                                    file=scenario._file+'.vsav',
                                    description=scenario._desc)
#
# EOF
#
