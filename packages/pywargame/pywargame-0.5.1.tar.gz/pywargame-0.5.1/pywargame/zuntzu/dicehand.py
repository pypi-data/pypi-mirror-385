## BEGIN_IMPORTS
from . base import DomInspect
from pywargame.common import VerboseGuard
## END_IMPORTS

# --------------------------------------------------------------------
class ZTDiceHand(DomInspect):
    
    def __init__(self,elem,type=6,count=1):
        with VerboseGuard(f'Got a dice hand') as v:
            if elem is None:
                self._type = type
                self._dice = [
                    {'color': 'black',
                     'pips':  'white',
                     'texture': ''}] * count
                return 
            
            self._type  = int(self._get_attr(elem,'type','D6')
                              .lower().replace('d',''))
            self._dice  = []

            # v(f'{elem.getElementsByTagName("dice")} child dice')
            for dice in elem.getElementsByTagName('dice'):
                count    = int(self._get_attr(dice,'count',1))
                colour   = self._parse_hex(self._get_attr(dice,'color',
                                                          0xFFFFFF))
                pips     = self._parse_hex(self._get_attr(dice,'pips',
                                                          0x000000))
                texture  = self._get_attr(dice,'texture-file')

                #v(f'Adding another dice: "{colour}" "{pips}" "{count}"')
                self._dice.extend([{
                    'color': colour,
                    'pips':  pips,
                    'texture': texture}]*count)
                
            # v(f'{len(self._dice)} dice of type d{self._type}')


    def __str__(self):
        return (f' Dice-hand: {self._type}'+
                ('\n' if len(self._dice) > 0 else '')+
                '\n'.join([f'  {d["color"]},{d["pips"]},{d["texture"]}'
                           for d in self._dice]))
#
# EOF
#
