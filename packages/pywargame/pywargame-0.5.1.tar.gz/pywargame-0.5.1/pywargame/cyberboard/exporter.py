## BEGIN_IMPORTS
from .. common import VerboseGuard, Verbose
from .. vassal.buildfile import BuildFile
from .. vassal.documentation import Documentation
from .. vassal.traits import *
from .. vassal.base import *
from .. vassal.moduledata import ModuleData
from .. vassal.exporter import Exporter
from .. vassal.mapelements import LayerControl
## END_IMPORTS

class CbExporter(Exporter):
    def __init__(self,
                 d,
                 title         = None,
                 version       = None,
                 rules         = None,
                 tutorial      = None,
                 visible       = False,
                 main_board    = None,
                 map_regex     = None,
                 vassalVersion = '3.6',
                 do_scenario   = False):
        self._d             = d
        self._title         = title
        self._version       = version
        self._rules         = rules
        self._tutorial      = tutorial
        self._visible       = visible
        self._vassalVersion = vassalVersion
        self._flipped       = False
        self._mainBoard     = main_board
        self._mapRegex      = map_regex
        self._do_scenario   = do_scenario
        self._description   = d['description']
        self._placements    = {}

    # ----------------------------------------------------------------
    def createModuleData(self):
        '''Create the `moduleData` file in the module
        '''
        with VerboseGuard(f'Creating module data'):
            self._moduleData = ModuleData()
            data             = self._moduleData.addData()
            data.addVersion      (version     = self._version)
            data.addVASSALVersion(version     = self._vassalVersion)
            data.addName         (name        = self._title)
            data.addDescription  (description = self._description)
            data.addDateSaved    ()

    # ----------------------------------------------------------------
    def addMoreDocumentation(self,doc):
        pass
    
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
            
            keys = [
                ['Alt-A',	'-',	'Show the charts panel'],
                ['Alt-B',	'-',	'Show the OOBs'],
                ['Alt-C',	'-',	'Show the counters panel'],
                ['Alt-E',	'-',	'Show the eliminated units'],
                ['Alt-I',	'-',	'Show/refresh inventory window'],
                ['Alt-M',	'-',	'Show map'],
                ['Alt-T',	'-',	'Increase turn track'],
                ['Alt-Shift-T', '-',	'Decrease turn track'],
                ['Alt-6',	'-',	'Roll the dice'],
                ['Ctrl-D',	'Board,Counter','Delete counters'],
                ['Ctrl-E',	'Board,Counter','Eliminate counters'],
                ['Ctrl-F',	'Board,Counter','Flip counters'],
                ['Ctrl-M',	'Board,Counter','Toggle "moved" markers'],
                ['Ctrl-O',	'Board',	'Hide/show counters'],
                ['Ctrl-R',	'Board,Counter','Restore unit'],
                ['Ctrl-T',	'Board,Counter','Toggle move trail'],
                ['Ctrl-+',	'Board',	'Zoom in'],
                ['Ctrl--',	'Board',	'Zoom out'],
                ['Ctrl-=',	'Board',	'Select zoom'],
                ['Ctrl-Shift-O',	'Board','Show overview map'],
                ['&larr;,&rarr;,&uarr;&darr;','Board',
                 'Scroll board left, right, up, down (slowly)'],
                ['PnUp,PnDn','Board',	'Scroll board up/down (fast)'],
                ['Ctrl-PnUp,Ctrl-PnDn','Board',
                 'Scroll board left/right (fast)'],
                ['Mouse-scroll up/down',	'Board',
                 'Scroll board up//down'],
                ['Shift-Mouse-scroll up/down','Board',
                 'Scroll board right/leftown'],
                ['Ctrl-Mouse-scroll up/down','Board','Zoom board out/in'],
                ['Mouse-2',	'Board',	'Centre on mouse']]
            
            
            self._vmod.addFile('help/keys.html',
                               Documentation.createKeyHelp(
                                   keys,
                                   title=self._d['title'],
                                   version=self._d['version']))
            doc.addHelpFile(title='Key bindings',fileName='help/keys.html')

            self.addMoreDocumentation(doc)

    # ----------------------------------------------------------------
    def saveImages(self,d,vmod):
        for serial,board in d['boards'].items():
            self.saveSVG(board,vmod)

        for piece in d['pieces']['map'].values():
            if 'back' in piece: self._flipped = True
            
            for which in ['front','back']:
                if which not in piece:
                    continue
            
                side     = piece[which]
                self.savePNG(side,vmod)
            
        for mark in d['marks']['map'].values():
            self.savePNG(mark,vmod)
            
    # ----------------------------------------------------------------
    def saveSVG(self,d,vmod):

        with VerboseGuard(f'Saving rendered SVG image {d["filename"]}') as vg:
            from wand.image import Image as WandImage
            from pathlib import Path

            path          = Path(d['filename'])
            filename      = path.with_suffix('.png')
            image         = d['image']
            size          = d['size']
            d['filename'] = filename
            svg           = image.encode()
            svgout        = path.with_suffix('.svg')
            pngout        = path.with_suffix('.png')
            vmod.addFile('images/'+str(svgout),svg)
            vg(f'Creating WandImage')
            
            # We write the SVG to file, because Wand seems to have
            # some issues reading from a bytes.  The same applies for
            # the command line
            if vg:
                vg(f'=== Write the SVG image to {svgout} ===')
                with open(svgout,'w') as out:
                    out.write(image)
                
            with WandImage() as wimage:
                # Reading the bytes directly fails.  It doesn't work
                # from reading BytesIO stream either.
                vg(f'Reading in SVG code')                
                wimage.read(filename=svgout,
                            # blob=image,#.encode(),
                            width=size[0],
                            height=size[1],
                            format='svg')

                # Make a PNG
                vg(f'Making blob')
                png = wimage.make_blob('png')

                # Write to the VMOD 
                vg(f'Write to VMOD')
                vmod.addFile('images/'+str(pngout),png)
                vg(f'Done writing SVG as PNG to VMOD')

    # ----------------------------------------------------------------
    def savePNG(self,d,vmod):
        with VerboseGuard(f'Saving PNG image {d["filename"]}'):
            from io import BytesIO
        
            filename  = d['filename']
            img       = d['image']
            d['size'] = img.size
            stream   = BytesIO()
            img.save(stream,format='PNG')
            vmod.addFile('images/'+filename,stream.getvalue())

    # ----------------------------------------------------------------
    def addPrototypes(self,sides):
        with VerboseGuard('Adding prototypes') as v:
            protos = self._game.addPrototypes()
            traits = [ReportTrait(key('E'),key('R'),key('M')),
                      TrailTrait(),
                      RotateTrait(),
                      DeleteTrait(),
                      MarkTrait(name='PieceLayer',value='Pieces'),
                      SendtoTrait(mapName     = 'DeadMap',
                                  boardName   = f'Pool',
                                  name        = 'Eliminate',
                                  key         = key('E'),
                                  restoreName = 'Restore',
                                  restoreKey  = key('R'),
                                  description = 'Eliminate unit'),
                      BasicTrait()]
            
            protos.addPrototype(name        = f'Piece prototype',
                                description = f'Prototype for pieces',
                                traits      = traits)
            traits = [DeleteTrait(),
                      RotateTrait(),
                      MarkTrait(name='PieceLayer',value='Markers'),
                      BasicTrait()]
            protos.addPrototype(name        = f'Marker prototype',
                                description = f'Prototype for markers',
                                traits      = traits)

            for side in sides:
                v(f'Making prototype trait for faction: "{side}"')
                escside = side.replace('/','\\/')
                traits = [MarkTrait(name='Faction',value=escside),
                          BasicTrait()]
                protos.addPrototype(name        = f'{side} prototype',
                                    description = f'Prototype for {side}',
                                    traits      = traits)
            
    # ----------------------------------------------------------------
    def sanitise(self,txt):
        for special in ['/',',',';','\\','\n','\t','\r']:
            txt = txt.replace(special,' ')
        return txt

    # ----------------------------------------------------------------
    def getToAdd(self,master,mapping,children):
        toAdd = {}
        for iden in children:
            if iden not in master:
                print(f'ID={iden} not found')
                continue
            if iden in mapping:
                # Already added
                continue

            toAdd[iden] = master[iden]

        return toAdd

    # ----------------------------------------------------------------
    def addPieceContainer(self,container,name):
        #panel = container.addPanel(entryName = name,
        #                           fixed = False,
        #                           vert  = True)
        #return panel
        panel = container.addPanel(entryName = name, fixed = False)
        plist = panel.addList(entryName = f'{name}',
                              width=300,
                              height=300,
                              divider=150)
        return plist
        
    # ----------------------------------------------------------------
    def addPieces(self,container,pieces,*pieceSets):
        from pathlib import Path 
        with VerboseGuard('Adding pieces') as v:
            # Store a map from pieceID to PieceSlot
            self._pieceMap = {}
            for sets in pieceSets:
                for set in sets:
                    toAdd = self.getToAdd(pieces,self._pieceMap,set['pieces'])
                    if len(toAdd) <= 0:
                        # Nothing to add from this set
                        continue 

                    name  = set.get('name',set.get('description',None))
                    if name is None:
                        print(f'No name for set: {set}')
                        continue
                    
                    plist = self.addPieceContainer(container, name)
                    
                    for pieceID, piece in toAdd.items():
                        v(f'Make piece with faction: "{name}"')
                        escname = name.replace('/','\\/')
                        front  = piece['front']['filename']
                        size   = piece['front']['size']
                        back   = piece.get('back',{}).get('filename',None)
                        traits = [MovedTrait(xoff=size[0]//2,
                                             yoff=-size[1]//2),
                                  MarkTrait(name='Faction',value=escname),
                                  MarkTrait(name='PieceLayer',value='Pieces'),
                                  PrototypeTrait(name='Piece prototype')]
                
                        if back is not None:
                            traits.extend([
                                LayerTrait(images = [front, back],
                                           newNames = ['','Reduced +'],
                                           activateName = '',
                                           decreaseName = '',
                                           increaseName = 'Flip',
                                           increaseKey  = key('F'),
                                           decreaseKey  = '',
                                           name         = 'Step'),
                                ReportTrait(key('F'))])
                        if 'description' in piece:
                            desc = self.sanitise(piece['description'])
                            traits.append(MarkTrait(name='description',
                                                    value=desc))
                
                        pname = Path(front).stem.replace('_front','')
                        gpid  = self._game.nextPieceSlotId()
                        traits.extend([BasicTrait(name     = pname,
                                                  filename = front,
                                                  gpid     = gpid)])
                                      
                        ps = plist.addPieceSlot(entryName = pname,
                                                gpid      = gpid,
                                                traits    = traits,
                                                width     = size[0],
                                                height    = size[1])

                        # print(f'Piece: {pieceID}')
                        self._pieceMap[pieceID] = ps

    # ----------------------------------------------------------------
    def addMarks(self,container,marks,*markSets):
        from pathlib import Path 
        with VerboseGuard('Adding marks') as v:
            # Store a map from markID to PieceSlot
            self._markMap = {}
            for sets in markSets:
                for set in sets:
                    toAdd = self.getToAdd(marks,self._markMap,set['marks'])
                    if len(toAdd) <= 0:
                        # Nothing to add from this set
                        continue 

                    name  = set.get('name',set.get('description',None))
                    if name is None:
                        print(f'No name for set: {set}')
                        continue
                    
                    mlist = self.addPieceContainer(container, name)
                    
                    for markID, mark in toAdd.items():
                        file   = mark['filename']
                        size   = mark['size']
                        traits = [PrototypeTrait(name='Mark prototype'),
                                  MarkTrait(name='PieceLayer',
                                            value='Markers')]
                        if 'description' in mark:
                            desc = self.sanitise(mark['description'])
                            traits.append(MarkTrait(name='description',
                                                    value=desc))
            
                        mname = Path(file).stem
                        gpid  = self._game.nextPieceSlotId()
                        traits.extend([BasicTrait(name     = mname,
                                                  filename = file,
                                                  gpid     = gpid)])
                                      
                        ps = mlist.addPieceSlot(entryName = mname,
                                                gpid      = gpid,
                                                traits    = traits,
                                                width     = size[0],
                                                height    = size[1])

                        # print(f'Mark:   {markID}')
                        self._markMap[markID] = ps
            
    # ----------------------------------------------------------------
    def addBoards(self,boards):
        with VerboseGuard(f'Adding boards '
                          f'{[n["gboard"]["name"] for n in  boards]}') as v:
            first = True
            names = []
            for board in boards:
                names.append(self.addBoard(first,**board))
                first = False

            filtered = [n for n in names
                        if n != '' and n != self._mainBoard]
            v(f'Filtered set of maps: {filtered}')
            if len(filtered) > 1:
                self._game.addMenu(description = 'Maps',
                                   text        = 'Maps',
                                   tooltip     = 'Show or hide maps',
                                   icon        = '/images/map.gif',
                                   menuItems   = filtered)

    # ----------------------------------------------------------------
    def addMapDefaults(self,map):
            # map.addHidePiecesButton()
            # Basics
            map.addStackMetrics()
            map.addImageSaver()
            map.addTextSaver()
            map.addForwardToChatter()     
            map.addMenuDisplayer()        
            map.addMapCenterer()          
            map.addStackExpander()        
            map.addCounterDetailViewer()
            map.addPieceMover()           
            map.addKeyBufferer()
            map.addForwardKeys()
            map.addScroller()
            map.addSelectionHighlighters()
            map.addHighlightLastMoved()   
            map.addZoomer()               
        
    # ----------------------------------------------------------------
    def addMapLayers(self,map):
        layerDesc = {'Pieces':   {'t': 'Pieces', 'i': ''},
                     'Markers':  {'t': 'Markers','i': ''}}
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
    def addBoard(self,first,gboard,color=0xFF0000,pieces=None,indicators=None):
        with VerboseGuard(f'Adding board {gboard["name"]}') as v:
            mapName = gboard['name']
            map     = self._game.addMap(
                mapName    = mapName,
                buttonName = '' if first else mapName,
                hotkey     = '' if first else key('M',ALT),
                launch     = not first
            )
            self.addMapDefaults(map)
            self.addMapLayers(map)
            map.addGlobalMap()
            
            map.addMassKey(name='Eliminate',
                           buttonHotkey = key('E'),
                           hotkey       = key('E'),
                           icon         = '/icons/16x16/edit-undo.png',
                           tooltip      = 'Eliminate selected units')
            map.addMassKey(name='Delete',
                           buttonHotkey = key('D'),
                           hotkey       = key('D'),
                           icon         = '/icons/16x16/no.png',
                           tooltip      = 'Delete selected units')
            if self._flipped:
                map.addMassKey(name='Flip',
                               buttonHotkey = key('F'),
                               hotkey       = key('F'),
                               icon         = '/images/Undo16.gif',
                               tooltip      = 'Flip selected units')
                

            size   = gboard['size']
            picker = map.addBoardPicker()
            board  = picker.addBoard(name   = gboard['name'],
                                     image  = gboard['filename'],
                                     width  = size[0],
                                     height = size[1])
            zoned  = board.addZonedGrid()
            zoned.addHighlighter()
            zone   = zoned.addZone(name = 'Full',
                                   useParentGrid = False,
                                   path=(f'{0},{0};' +
                                         f'{size[0]},{0};' +
                                         f'{size[0]},{size[1]};' +
                                         f'{0},{size[1]}'))

            self.addGrid(zone,gboard,color)
            self.addAtStart(map,pieces)
            self.addAtStart(map,indicators)

            return mapName
            
    # ----------------------------------------------------------------
    def addCharts(self,gcharts):
        if len(gcharts) <= 0:
            return
        
        with VerboseGuard(f'Adding Charts '
                          f'{[n["gboard"]["name"] for n in gcharts]}') as v:
            charts = \
                self._game.addChartWindow(name='Charts',
                                          hotkey = key('A',ALT),
                                          description = 'Charts',
                                          text        = '',
                                          icon       = '/images/chart.gif',
                                          tooltip     = 'Show/hide Charts')
            tabs = charts.addTabs(entryName='Charts')

            for chart in gcharts:
                widget = tabs.addMapWidget(entryName=chart['gboard']['name'])
                self.addChart(widget,**chart)
                
    # ----------------------------------------------------------------
    def addChart(self,widget,gboard,color=0xFF0000,pieces=None,indicators=None):
        with VerboseGuard(f'Adding Chart {gboard["name"]}') as v:
            map = widget.addWidgetMap(mapName   = gboard['name'],
                                      markMoved = 'Never',
                                      hotkey    = '')
            self.addMapDefaults(map)
            self.addMapLayers(map)
            
            size   = gboard['size']
            picker = map.addPicker()
            board  = picker.addBoard(name  = gboard['name'],
                                     image = gboard['filename'])
            zoned  = board.addZonedGrid()
            zoned.addHighlighter()
            zone   = zoned.addZone(name = 'Full',
                                   useParentGrid = False,
                                   path=(f'{0},{0};' +
                                         f'{size[0]},{0};' +
                                         f'{size[0]},{size[1]};' +
                                         f'{0},{size[1]}'))
            
            self.addGrid(zone,gboard,color)
            self.addAtStart(map,pieces)
            self.addAtStart(map,indicators)
            
    # ----------------------------------------------------------------
    def getNumParam(self,col,gboard,geom):
        rcol = (col >> 16) & 0xFF
        gcol = (col >> 8)  & 0xFF
        bcol = (col >> 0)  & 0XFF
        fid  = gboard['numbering']['order'].lower()
        sid  = 'h' if fid=='v' else 'v'
        side = 'sideways' in geom['shape']
        hex  = 'hexagon'  in geom['shape']
        d = {'first':      fid.upper(),
             'color':      rgb(rcol,gcol,bcol),
             'visible':    self._visible,
             'vOff':       gboard['rows']['offset']+1,
             'vDescend':   gboard['rows']['inverted'],
             'hOff':       gboard['columns']['offset']+1, # CB start at 1
             'vOff':       gboard['columns']['inverted']+1, # VSL start at 0
             'hLeading':   1 if gboard['numbering']['padding'] else 0,
             'vLeading':   1 if gboard['numbering']['padding'] else 0,
             'stagger':    geom['stagger'] == 'in',
             f'{fid}Type': gboard['numbering']['first'],
             f'{sid}Type': 'N'
             }
        # Coord 0 -> A in VSL, Coord 1 -> A in CB
        d[f'{fid}Off'] += 0 if gboard['numbering']['first'] != 'A' else -1
        return d
            
    # ----------------------------------------------------------------
    def addGrid(self,zone,gboard,col=0x000000):
        geom = gboard.get('cells',{}).get('geometry',None)
        if geom is None:
            return

        if geom['shape'] == 'rectangle':
            self.addRegularGrid(zone,gboard,geom,col)
        elif 'brick' in geom['shape']:
            self.addRegionGrid(zone,gboard,geom,col)
        elif 'hexagon' in geom['shape']:
            self.addHexGrid(zone,gboard,geom,col)

        

    # ----------------------------------------------------------------
    def addHexGrid(self,zone,gboard,geom,col=0x000000):
        from math import sin, pi
        with VerboseGuard(f'Adding hex grid') as v:
            size = geom['size']
            side = 'sideways' in geom['shape']
            npar = self.getNumParam(col,gboard,geom)
            dx   = int(size[0] * sin(pi/3) ** 2)
            dy   = size[1]
            x0   = size[0]//2
            y0   = size[1]//2 + (0 if geom['stagger']=='out' else dy//2)
            if side:
                dy            = size[0]
                dx            = dy * sin(pi/3)
                x0, y0        = y0, x0
                npar['first'] = 'V' if npar['first'] == 'H' else 'H'
                
            v(f'Size = {size}, side = {side} dx={dx} dy={dy}')
            grid = zone.addHexGrid(dx           = dx,
                                   dy           = dy,
                                   x0           = x0,
                                   y0           = y0,
                                   sideways     = side,
                                   visible      = self._visible,
                                   color        = npar['color'],
                                   edgesLegal   = True,
                                   cornersLegal = True,
                                   snapTo       = True
                                   #gboard['snap']['enable']
                                   )
            grid.addNumbering(**npar)

    # ----------------------------------------------------------------
    def addRegularGrid(self,zone,gboard,geom,col=0x000000):
        size = geom['size']
        npar = self.getNumParam(col,gboard,geom)
        grid = zone.addSquareGrid(dx      = size[0],
                                  dy      = size[1],
                                  x0      = size[0]//2,
                                  y0      = size[1]//2,
                                  visible = self._visible,
                                  color   = npar['color'],
                                  snapTo  = gboard['snap']['enable'])
        grid.addNumbering(**npar)
                          
                          

    # ----------------------------------------------------------------
    def addRegionGrid(self,zone,gboard,geom):
        grid = zone.addRegionGrid(snapto  = True,
                                  visible = self._visible)
        
        for row in gboard['cells']['list']:
            for cell in row:
                name = f'r{cell["row"]}_{cell["column"]}'
                pixel = cell['pixel']
                grid.addRegion(name      = name,
                               originx   = pixel[0],
                               originy   = pixel[1],
                               alsoPiece = False)
    # ----------------------------------------------------------------
    def addAtStart(self,map,pieces):
        with VerboseGuard(f'Adding at-start to {map["mapName"]}') as g:
            toAdd = {}
            mapName = map['mapName']
            
            for piece in pieces:
                pmap = None
                if piece['type'] == 'Piece':
                    pmap = self._pieceMap
                elif piece['type'] == 'Mark':
                    pmap = self._markMap
                else:
                    continue
            
            
                iden = piece['id']
                pm   = pmap.get(iden,None)
                #print(piece,pm)
                if pm is None:
                    print(f'Cannot fine {piece["type"]} {iden}')
                    print(list(pmap.keys()))
                    continue

                grid = tuple(piece['grid'])
                x = piece['pixel']['x']
                y = piece['pixel']['y']
                if grid not in toAdd:
                    toAdd[grid] = {'center': (x,y),
                                   'pieces': [] }
                toAdd[grid]['pieces'].append(pm)

            if self._do_scenario:
                mapped = {
                    a['center']: a['pieces'] for a in toAdd.values()}

                if mapName not in self._placements:
                    self._placements[mapName] = {}

                mapPlacements = self._placements[mapName]
                
                # We have to do this carefully, because we may have
                # already added something to the placements for this
                # map and specific locations.
                for coord, pieces in mapped.items():
                    if coord in mapPlacements:
                        mapPlacements[coord].extend(pieces)
                    else:
                        mapPlacements[coord] = pieces 

            else:
                for grid, dpieces in toAdd.items():
                    center  = dpieces['center']
                    name    = f'{grid[0]:02d}{grid[1]:02d}'
                    atstart = map.addAtStart(name=name,
                                             useGridLocation=False,
                                             owningBoard=mapName,
                                             x = center[0],
                                             y = center[1])
                    atstart.addPieces(*dpieces['pieces'])
        
    # ----------------------------------------------------------------
    def addDeadMap(self,sides):
        '''Add a "Dead Map" element to the module 
        '''
        name = 'DeadMap'
        with VerboseGuard(f'Adding board {name}') as v:
            map    = self._game.addMap(mapName       = name,
                                       buttonName    = '',
                                       markMoved     = 'Never',
                                       launch        = True,
                                       icon          = '/images/playerAway.gif',
                                       allowMultiple = True,
                                       hotkey        = key('E',ALT))
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
            
            map.addMassKey(name='Restore',
                           buttonHotkey = key('R'),
                           hotkey       = key('R'),
                           icon         = '/images/Undo16.gif',
                           tooltip      = 'Restore selected units')

            if sides is None or len(sides) <= 0:
                sides = ['A']
            picker = map.addBoardPicker()
            picker.addSetup(maxColumns=len(sides),mapName=name,
                            boardNames=[s+' pool' for s in sides])
            
            for i, s in enumerate(sides):
                v(f'Adding {s} pool')
                color        = [0,0,0,64]
                color[i % 3] = 255
                w            = 400
                h            = 400
                c            = rgba(*color)
                board        = picker.addBoard(name   = f'{s} pool',
                                               image  = '',
                                               width  = w,
                                               height = h,
                                               color  = c)
                 
# ====================================================================
class GBXExporter(CbExporter):
    def __init__(self,
                 d,
                 title         = None,
                 version       = None,
                 rules         = None,
                 tutorial      = None,
                 visible       = False,
                 main_board    = None,
                 map_regex     = None,
                 vassalVersion = '3.6',
                 do_scenario   = False):
        super(GBXExporter,self).__init__(d,
                                         title         = title,
                                         version       = version,
                                         rules         = rules,
                                         tutorial      = tutorial,
                                         visible       = visible,
                                         main_board    = main_board,
                                         map_regex     = map_regex,
                                         vassalVersion = vassalVersion,
                                         do_scenario   = do_scenario)

    # ----------------------------------------------------------------
    def setup(self):
        self.saveImages(self._d,self._vmod)
        self._title       = self._d['title']
        self._version     = self._d['version']
        self._description = self._d['description']
        
    # ----------------------------------------------------------------
    def createBuildFile(self,
                        ignores = ['all',
                                   'common',
                                   'marker',
                                   'markers',
                                   ' ']):
        with VerboseGuard(f'Creating build file') as v:
            self._build = BuildFile() # 'buildFile.xml')
            self._game  = self._build.addGame(name        = self._title,
                                              version     = self._version,
                                              description = self._description)
            self.addDocumentation()
            self._game.addBasicCommandEncoder()


# ====================================================================
class GSNExporter(CbExporter):
    def __init__(self,
                 d,
                 title         = None,
                 version       = None,
                 rules         = None,
                 tutorial      = None,
                 visible       = False,
                 main_board    = None,
                 map_regex     = None,
                 vassalVersion = '3.6',
                 do_scenario   = False):
        super().__init__(d,
                         title         = title,
                         version       = version,
                         rules         = rules,
                         tutorial      = tutorial,
                         visible       = visible,
                         main_board    = main_board,
                         map_regex     = map_regex,
                         vassalVersion = vassalVersion,
                         do_scenario   = do_scenario)

    # ----------------------------------------------------------------
    def setup(self):
        with VerboseGuard('Setup') as v:
            from pathlib import Path
                
            self.saveImages(self._d['gamebox'],self._vmod)
            self.setupTitle()

    def setupTitle(self):
        with VerboseGuard('Setup titles and such') as v:
            v(f'Before: '
              f'title={self._title}, '
              f'version={self._version}, '
              f'description={self._description}')
            v(f'Game box: '
              f'title={self._d["gamebox"]["title"]}, '
              f'version={self._d["gamebox"]["version"]}, '
              f'description={self._d["gamebox"]["description"]}')
            v(f'Scenario: '
              f'title={self._d["title"]}, '
              f'version={self._d["version"]}, '
              f'description={self._d["description"]}')
            
            if self._title is None or self._title == '':
                # If we are making a scenario, then do not take the
                # title from the scenario file
                self._title = None if self._do_scenario else self._d['title']
                if self._title is None or self._title == '':
                    self._title = self._d['gamebox']['title']
                    if self._title is None or self._title == '':
                        from random import choice
                        from string import ascii_lowercase
                        self._title = Path(self._vmod.fileName()).stem
                        # self._title = ''.join([choice(ascii_lowercase)
                        #                        for _ in range(32)])
            if not self._do_scenario:
                self._d['title'] = self._title
                
            if self._version is None or self._version == '':
                # If we are doing a scenario, do not take the version
                # from the scenario file.
                self._version = (None if self._do_scenario else
                                 self._d['version'])
                if self._version is None or self._version == '':
                    self._version = self._d['gamebox']['version']
                    if self._version is None or self._version == '':
                        self._version = '0.0'
            if not self._do_scenario:
                self._d['version'] = self._version

            if self._do_scenario:
                # Take overall description form game box
                self._description = self._d['gamebox']['description']
            v(f'After: '
              f'title={self._title}, '
              f'version={self._version}, '
              f'description={self._description}')
        
    # ----------------------------------------------------------------
    def createBuildFile(self,
                        ignores = '(.*markers?|all|commons|[ ]+)'):
        '''Create the XML buildFile.xml
 
        Parameters
        ----------
        ignores : str
            Regular expression to match ignored categories for factions
            determination. Python's re.fullmatch is applied to this
            regular exression against chit categories.  If the pattern
            is matched, then the chit is not considered to belong to a
            faction.
        '''
        with VerboseGuard(f'Creating build file') as v:                    
            desc = None if self._do_scenario else self._d['description']
            if desc is None or desc == '':
                desc = self._d['gamebox']['description']
            if len(desc) > 32:
                desc = desc[:32]
            self._build = BuildFile() # 'buildFile.xml')
            self._game  = self._build.addGame(name        = self._title,
                                              version     = self._version,
                                              description = desc)

            self._sides  = self._d['players']
            self._sides  = [p.replace(' player','').replace(' Player','')
                            for p in self._sides]

            if not self._sides:
                self._sides = [s['description'] for s in
                               self._d['gamebox']['pieces']['sets']]

            v(f'Sides: {self._sides}')
            
            v(f'Adding documentation')
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
            
            v(f'Adding player roster {self._sides}')
            roster = self._game.addPlayerRoster()
            for side in self._sides:
                roster.addSide(side)
            
            v(f'Adding global properties')
            glob = self._game.addGlobalProperties()
            glob.addProperty(name='TurnTracker.defaultDocked',
                             initialValue=True)
            
            v(f'Adding notes')
            self._game.addNotes()
            
            v(f'Adding turn track')
            turns = self._game.addTurnTrack(name='Turn',
                                            counter={
                                                'property': 'Turn',
                                                'phases': {
                                                    'property': 'Phase',
                                                    'names': self._sides } })

            
            self.addPrototypes(self._sides)
            self.addPiecesMarks()
            self.addBoards()
            self.addCharts()
            self.addDeadMap(self._sides)
            self.addScenario()
            

    #
    def addMoreDocumentation(self,doc):
        desc = f'''<html><body>
        <h1>Module</h1>
        <p>
        This module was created from CyberBoard Scenario
        {self._d["title"]} version {self._d["version"]} and game box
        {self._d["gamebox"]["title"]} version {self._d["gamebox"]["version"]} '
        'by the Python script <code>gsnexport.py</code> available from
        </p>
        <pre>
        htps://gitlab.com/wargames_tex/pywargame
        </pre>
        <h1>Game</h1>
        <table>
          <tr><td>Title:</td><td>{self._d["gamebox"]["title"]}</td></tr>
          <tr><td>Version:</td><td>{self._d["gamebox"]["version"]}</td></tr>
          <tr><td>Author:</td><td>{self._d["gamebox"]["author"]}</td></tr>
          <tr><td>Description:</td><td>{self._d["gamebox"]["description"]}</td></tr>
        </table>
        <h1>Scenario</h1>
        <table>
          <tr><td>Title:</td><td>{self._d["title"]}</td></tr>
          <tr><td>Version:</td><td>{self._d["version"]}</td></tr>
          <tr><td>Author:</td><td>{self._d["author"]}</td></tr>
          <tr><td>Description:</td><td>{self._d["description"]}</td></tr>
        </table>
        </body></html>;'''
        self._vmod.addFile('help/description.html',desc)
        doc.addHelpFile(title='Description',fileName='help/description.html')
        

    # ----------------------------------------------------------------
    def addPiecesMarks(self):
        with VerboseGuard(f'Adding pieces and marks') as v:
            window = self._game.addPieceWindow(name   = 'Counters',
                                               hotkey = key('C',ALT))
            combo  = window.addCombo(entryName='Counters')
            self.addPieces(combo,
                           self._d['gamebox']['pieces']['map'],
                           self._d['trays'],
                           self._d['gamebox']['pieces']['sets'])
            self.addMarks(combo,
                          self._d['gamebox']['marks']['map'],
                          self._d['gamebox']['marks']['sets'])
    # ----------------------------------------------------------------
    def boardMatch(self,name):
        if self._mapRegex is None:
            return False
        
        from re import match

        ret = match(self._mapRegex, name) is not None

        return ret
    
    # ----------------------------------------------------------------
    def addBoards(self):
        with VerboseGuard(f'Adding boards') as v:
            toAdd = []
            for serial, sboard in self._d['boards'].items():
                board = self._d['gamebox']['boards'].get(serial,None)
                if board is None:
                    continue
                # print('BOARD (gsn)',board)
                #
                # If not set to start map in GBX, and name does not
                # the user specified main board and board name does
                # not match the board regular expression, then
                # continue on (the board will be made chart instead).
                if not sboard['onload'] and \
                   board['name'] != self._mainBoard and \
                   not self.boardMatch(board['name']):
                    continue

                # Here, we add pieces and indicators as at-start on
                # the map.  Perhaps we should _not_ do that, and write
                # a scenario file instead.
                d = {'gboard':      board,
                     'color':       sboard['grid']['color'],
                     'pieces':      sboard['pieces'],
                     'indicators':  sboard['indicators'] }
                if board['name'] == self._mainBoard:
                    # If this is the main board, as selected by user,
                    # then put first in the queue.
                    toAdd.insert(0,d)
                else:
                    toAdd.append(d)

            super(GSNExporter,self).addBoards(toAdd)
            
    # ----------------------------------------------------------------
    def addCharts(self):
        with VerboseGuard(f'Adding Charts') as v:
            toAdd = [] 
            for serial, sboard in self._d['boards'].items():
                board = self._d['gamebox']['boards'].get(serial,None)
                if board is None:
                    continue
                # print('BOARD (gbx)',board)
                #
                # If the board is set to start at load on GBX, or the
                # name of the board matches the main board name set by
                # user, or board name matched the user-defined board
                # regular expression, the skip this board (was added
                # previously as a board).
                if sboard['onload'] or \
                   board['name'] == self._mainBoard or \
                   self.boardMatch(board['name']):
                    continue

                # Here, we add pieces and indicators as at-start on
                # the map.  Perhaps we should _not_ do that, and write
                # a scenario file instead.
                d = {'gboard':      board,
                     'color':       sboard['grid']['color'],
                     'pieces':      sboard['pieces'],
                     'indicators':  sboard['indicators'] }
                if board['name'] == self._mainBoard:
                    # If this is the main board, as selected by user,
                    # then put first in the queue.
                    #
                    # Should this be done for charts? Probably not. 
                    toAdd.insert(0,d)
                else:
                    toAdd.append(d)
            
            super(GSNExporter,self).addCharts(toAdd)
            
    # ----------------------------------------------------------------
    def addScenario(self):
        if not self._do_scenario or len(self._placements) <= 0:
            # Nothing to do
            return

        from pathlib import Path 

        menu = self._game.addPredefinedSetup(name = 'Setups',
                                             isMenu = True)

        menu.addPredefinedSetup(name = 'No setup',
                                file = '',
                                useFile = False,
                                description = 'No initial setup')

        with VerboseGuard(f'Adding a scenario {self._d["title"]}') as v:
            vsav    = VSav(self._build,self._vmod)
            save    = vsav.addSaveFile()

            # from pprint import pprint
            # pprint(self._placements)
            
            for mapName,placements in self._placements.items():
                
                save.addNoGrid(mapName, placements)

            # print('\n'.join(save.getLines()))
            
            savfile = self._d['title'].replace(' ','_')+'.vsav'
            vsav.run(savename    = savfile,
                     description = self._d['description'])

            menu.addPredefinedSetup(name=self._d['title'],
                                    useFile=True,
                                    file=savfile,
                                    description=self._d['description'])

        
# ====================================================================
            
#
# EOF
#

            
            

