## BEGIN_IMPORT
from ... common import VerboseGuard
from .. trait import Trait
## END_IMPORT

# --------------------------------------------------------------------
class ReportTrait (Trait):
    ID = 'report'
    def __init__(self,
                 *keys,
                 nosuppress = True,
                 description = '',
                 report      = '$location$: $newPieceName$ $menuCommand$ *',
                 cyclekeys   = '',
                 cyclereps   = ''):
        '''Create a report trait (VASSAL.counters.ReportActon)'''
        super(ReportTrait,self).__init__()
        esckeys = ','.join([k.replace(',',r'\,') for k in keys])
        esccycl = ','.join([k.replace(',',r'\,') for k in cyclekeys])
        escreps = ','.join([k.replace(',',r'\,') for k in cyclereps])
        
        self.setType(keys         = esckeys,
                     report       = report,
                     cycleKeys    = esccycl,
                     cycleReports = escreps,
                     description  = description,
                     nosuppress   = nosuppress)
        self.setState(cycle = -1)

Trait.known_traits.append(ReportTrait)

#
# EOF
#
