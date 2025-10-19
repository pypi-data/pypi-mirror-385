## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
from .. base import *
## END_IMPORT

# --------------------------------------------------------------------
class SheetTrait(Trait):
    ID             = 'propertysheet'
    EVERY_KEY_TEXT = 'Every Keystroke'
    APPLY_TEXT     = 'Apply Button or Enter Key'
    CLOSE_TEXT     = 'Close Window or Enter Key'
    EVERY_KEY      = 0
    APPLY          = 1
    CLOSE          = 2
    TEXT           = 0
    AREA           = 1
    LABEL          = 2
    TICKS          = 3
    TICKS_MAX      = 4
    TICKS_VAL      = 5
    TICKS_BOTH     = 6
    SPINNER        = 7
    TYPE_DELIM     = ';'
    DEF_DELIM      = '~'
    STATE_DELIM    = '~'
    LINE_DELIM     = '|'
    VALUE_DELIM    = '/'

    @classmethod 
    def encodeState(cls,k,e):
        type = e['type']
        if type == cls.TEXT:    return f'{e["value"]}'
        if type == cls.AREA:    return f'{e["value"].replace("\n",LINE_DELIM)}'
        if type == cls.SPINNER: return f'{e["value"]}'
        if type in [cls.TICKS,cls.TICKS_MAX,cls.TICKS_VAL,cls.TICKS_BOTH]:
            try:
                val = int(e["value"])
            except:
                val = 0
            try:
                max = int(e["max"])
            except:
                max = 0
            return f'{val}{cls.VALUE_DELIM}{max}'
        return ''

    @classmethod
    def encodeDefinition(cls,rows):
        definition = cls.DEF_DELIM.join([f'{e["type"]}{k}'
                                     for k,e in rows.items()])
                                
        state      = cls.STATE_DELIM.join([self.encodeState(k,e)
                                       for k,e in rows.items()])
        return definition, state

    @classmethod
    def decodeDefinition(cls,definitions,state):
        tns  = definitions.split(cls.DEF_DELIM)
        sts  = state      .split(cls.STATE_DELIM)
        def decodeDef(d):
            try:
                type = int(d[0])
            except:
                type = cls.TEXT
            return type, d[1:]
        rows = {}
        for tn, st in zip(tns,sts):
            type, name = decodeDef(tn)
            rows[name] = { 'type': type }
            rows[name].update(cls.decodeState(name,type,st))
        return rows

    @classmethod 
    def decodeState(cls,name,type,state):
        if type == cls.TEXT:    return {'value': state}
        if type == cls.AREA:    return {'value': state.replace('|','\n') }
        if type == cls.SPINNER: return {'value': state}
        if type in [cls.TICKS,
                    cls.TICKS_MAX,
                    cls.TICKS_VAL,
                    cls.TICKS_BOTH]:
            fields = state.split(VALUE_DELIM)
            try:
                value = int(fields[0])
            except:
                value = 0
            try:
                max = int(fields[1])
            except:
                max = 0
            return {'value': value, 'max': max }
        return {}
    
    def __init__(self,
                 command         = '',
                 commit          = EVERY_KEY,
                 color           = ',,',
                 key             = '',
                 description     = '',
                 rows            = {}):
        '''Create a clone trait (VASSAL.counter.Clone)'''
        super().__init__()
        definition, state = self.encodeDefinition(rows)
        rgbcol = color.split(',')
        self.setType(definition      = definition,
                     command         = command,          # Context menu name
                     letter          = '',
                     commit          = commit,
                     red             = rgbcol[0],
                     green           = rgbcol[1],
                     blue            = rgbcol[2],
                     key             = key,              # Context menu key
                     description     = description)     
        self.setState(state=state)
        
        
    def getDefinitionState(self):
        return self.decodeDefinition(self['definition'],self['state'])

    def setDefinitionState(self,rows):
        self['definition'], self['state'] = self.encodeDefinition(rows)
    

Trait.known_traits.append(SheetTrait)

#
# EOF
#
