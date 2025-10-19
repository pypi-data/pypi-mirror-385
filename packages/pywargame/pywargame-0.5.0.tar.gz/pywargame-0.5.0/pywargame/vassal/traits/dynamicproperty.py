## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
# 
# 
class ChangePropertyTrait(Trait):
    DIRECT    = 'P'
    INCREMENT = 'I'
    PROMPT    = 'R'
    LIST      = 'E'
    def __init__(self,
                 *commands,
                 numeric     = False,
                 min         = 0,
                 max         = 100,
                 wrap        = False):
        '''Base class for property (piece or global) change traits.
        
           Encodes constraints and commands.
        '''
        # assert name is not None and len(name) > 0, \
        #     'No name specified for ChangePropertyTriat'
        super(ChangePropertyTrait,self).__init__()
        self._constraints = self.encodeConstraints(numeric,wrap,min,max)
        self._commands    = self.encodeCommands(commands)

    def encodeConstraints(self,numeric,wrap,min,max):
        isnum             = f'{numeric}'.lower()
        iswrap            = f'{wrap}'.lower()
        return f'{isnum},{min},{max},{iswrap}'

    def decodeConstraints(self,constraints):
        f = Trait.decodeKeys(constraints)
        return f[0]=='true',f[3]=='true',int(f[1]),int(f[2])
    
    def encodeCommands(self,commands):
        cmds              = []
        for cmd in commands:
            # print(cmd)
            com = cmd[0] + ':' + cmd[1].replace(',',r'\,') + ':' + cmd[2]
            if cmd[2] == self.DIRECT:
                com += r'\,'+cmd[3].replace(',',r'\\,').replace(':',r'\:')
            elif cmd[2] == self.INCREMENT:
                com += r'\,'+cmd[3].replace(',',r'\\,').replace(':',r'\:')
            cmds.append(com)
        # print(cmds)
        return ','.join(cmds)

    def decodeCommands(self,commands):
        cmds = Trait.decodeKeys(commands)
        ret  = []
        for cmd in cmds:
            parts = Trait.decodeKeys(cmd,':')
            # print('parts',parts)
            if parts[-1][0] == self.DIRECT:
                parts = parts[:-1]+Trait.decodeKeys(parts[-1],',')
            if parts[-1][0] == self.INCREMENT:
                parts = parts[:-1]+Trait.decodeKeys(parts[-1],',')
            ret.append(parts)
        # print(commands,parts)
        return ret
    
    def getCommands(self):
        return self.decodeCommands(self['commands'])

    def setCommands(self,commands):
        self['commands'] = self.encodeCommands(commands)
        
    def check(self):
        assert len(self['name']) > 0,\
            f'No name given for ChangePropertyTrait'
        
        
# --------------------------------------------------------------------
class DynamicPropertyTrait(ChangePropertyTrait):
    ID = 'PROP'
    def __init__(self,
                 *commands,
                 name        = '',
                 value       = 0,
                 numeric     = False,
                 min         = 0,
                 max         = 100,
                 wrap        = False,
                 description = ''):
        '''Commands are

            - menu
            - key
            - Type (only 'P' for now)
            - Expression
        '''
        super(DynamicPropertyTrait,self).__init__(*commands,
                                                  numeric = numeric,
                                                  min     = min,
                                                  max     = max,
                                                  wrap    = wrap)
        # print(commands,'Name',name)
        self.setType(name        = name,
                     constraints = self._constraints,
                     commands    = self._commands,
                     description = description)
        self.setState(value=value)

    
Trait.known_traits.append(DynamicPropertyTrait)

#
# EOF
#
