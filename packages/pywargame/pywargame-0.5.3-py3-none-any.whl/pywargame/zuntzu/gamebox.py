## BEGIN_IMPORTS
from . base import DomInspect
from . map import ZTMap
from . piece import ZTPiece
from . countersheet import ZTCounterSheet
from . dicehand import ZTDiceHand
from pywargame.common import VerboseGuard
from . scenario import ZTScenario
## END_IMPORTS

# --------------------------------------------------------------------
class ZTGameBox(DomInspect):
    
    def __init__(self,file):
        from zipfile import ZipFile
        from xml.dom.minidom import parse

        with VerboseGuard('Reading gamebox') as v:
            self._zip = ZipFile(file,'r')
            
            with self._zip.open('game-box.xml','r') as xml:
                self._gamebox =parse(xml)
                
                self._root    = self._gamebox.firstChild
                self._name    = self._get_attr(self._root,'name')
                self._desc    = self._get_attr(self._root,'description')
                self._copy    = self._get_attr(self._root,'copyright')
                self._start   = self._get_attr(self._root,'startup-scenario')
                self._icon    = self._get_attr(self._root,'icon',None)
                self._splash  = None
                self._sheets_map = {}

                if not self._icon and 'icon.bmp' in self._zip.namelist():
                    self._icon = 'icon.bmp'
                v(f'Icon is {self._icon}')
                    
                if self._icon:
                    self._splash = self._read_image(self._zip, self._icon)
                    v(f'Got splash screen {self._icon}: {self._splash}')
            
                self._dice_hands = [
                    self.parse_dice_hand(dh)
                    for dh in self._root.getElementsByTagName('dice-hand')]
                # IF no dice was defined add a 1d6
                if len(self._dice_hands) <= 0:
                    self._dice_hands = [ ZTDiceHand(None) ]

                self._maps = [
                    self.parse_map(mp)
                    for mp in self._root.getElementsByTagName('map')]

                self._scenarios = [
                    self.parse_scenario(fn)
                    for fn in self._zip.namelist() if fn.endswith('.zts')]

                # counter-sheet or terrain-sheet 
                self._counter_sheets = [
                    self.parse_counter_sheet(sh)
                    for sh in self._find_children(self._root,
                                                  'counter-sheet',
                                                  'terrain-sheet')]

                self._pieces = sum([c._piece for c in self._counter_sheets],[])
                self._cards  = sum([c._card for  c in self._counter_sheets],[])
                self.map_pieces()
        
    def parse_dice_hand(self,elem):
        return ZTDiceHand(elem)

    def parse_map(self,elem):
        m = ZTMap(elem)
        m.read_image(self._zip)
        # self._master[m._name] = m
        return m

    def parse_counter_sheet(self,elem):
        s = ZTCounterSheet(elem)
        s.read_image(self._zip)
        s.make_pieces()
        self._sheets_map[s._name] = s
        return s

    def parse_scenario(self,fn):
        with self._zip.open(fn,'r') as inp:
            return ZTScenario(inp)

    def write_image(self,dir,name,image):
        if image is None:
            return
        
        fn  = dir / f'{name}.{image.format.lower()}'
        print(f'Writing {fn}')
        image.save(filename=fn)

    def map_pieces(self):
        with VerboseGuard(f'Mapping pieces to ID and back'):
            # Cards and pieces are intermingled
            tmp = sum([c._piece+c._card for c in self._counter_sheets],[])
            self._piece_map = {
                i: p for i,p in enumerate(tmp) }
            self._piece_id = {
                v: k for k,v in self._piece_map.items()}
        
        
    def write_images(self):
        from pathlib import Path

        dir = Path('images')
        dir.mkdir(0o755,parents=True,exist_ok=True)

        for m in self._maps:
            if not m._image:
                print(f'Missing image for map {m._name}')
                continue

            self.write_image(dir,m._name,m._image._image)
            
        for i,p in enumerate(self._pieces):
            for img,nam in zip([p._front,p._back],
                           ['front','back']):

                self.write_image(dir,f'{i:04d}_{nam}',img)

        for i,p in enumerate(self._cards):
            for img,nam in zip([p._front,p._back],
                           ['front','back']):

                self.write_image(dir,f'c{i:04d}_{nam}',img)
                
        for s in self._counter_sheets:
            name = s._name
            for fac,nam in zip([s._front,s._back],
                               ['front','back']):
                if not fac:
                    continue

                self.write_image(dir,f'{name}_{nam}',fac._image)
        

    def __str__(self):
        return (f'{self._name}'+'\n'+
                f' Description: {self._desc}'+'\n'+
                f' Copyright:   {self._copy}'+'\n'+
                f' Start:       {self._start}'+'\n'+
                f' Icon:        {self._icon}'+
                ('\n' if len(self._dice_hands)>0 else '')+
                '\n'.join([str(d) for d in self._dice_hands])+
                ('\n' if len(self._maps)>0 else '')+
                '\n'.join([str(m) for m in self._maps])+
                ('\n' if len(self._counter_sheets)>0 else '')+
                '\n'.join([str(s) for s in self._counter_sheets]))
#
# EOF
#
