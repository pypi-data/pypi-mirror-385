## BEGIN_IMPORT
from . verboseguard import VerboseGuard
from . verbose import Verbose
## END_IMPORT


class Collector:
    def __init__(self,executable=True):
        '''This could be done with SED, but we don't need to rely on that'''
        self._executable = executable

    def readFile(self,filename):
        '''Reads lines from a file and returns them.

        Lines fenced by with `##` are not returned.

        Lines starting with `#!` are not returned
        '''
        with VerboseGuard(f'Reading lines from {filename}') as g:
            ret = [f'# {"="*68}\n'
                   f'# From {filename}\n' ]
            with open(filename,'r') as file:
                lines  = file.readlines()
                nlines = len(lines)
                lineno = 0
            
                g(f'{filename} has {nlines} lines')
                while lineno < nlines:
                    line = lines[lineno]
                    if line.strip().startswith('##'):
                        start   = line
                        startno = lineno
            
                        while lineno < nlines:
                            lineno += 1
                            if lineno >= nlines:
                                raise RuntimeError(f'At {filename}:{lineno}:'
                                                   f' No end to {start} in '
                                                   f'line {startno}')
                            
                            line   =  lines[lineno]
                            if line.strip().startswith('##'):
                                g(f'Skipped lines {startno} to {lineno}')
                                break
                        lineno += 1
                        continue
            
                    if line.startswith('#!'):
                        g(f'Skipping line {lineno}')
                        lineno += 1
                        continue
            
                    ret.append(line)
                    lineno += 1
            
                return ret

    def run(self,output,*filenames):
        lines = ['#!/usr/bin/env python\n',
                 '# Script collected from other scripts\n',
                 '#\n']
        lines.extend([f'#   {filename}\n' for filename in filenames])
        lines.append('#\n')
            

        for filename in filenames:
            lines.extend(self.readFile(filename))

        lines.extend(['##\n',
                      '# End of generated script\n'
                      '##\n'])


        output.writelines(lines)

        if not self._executable:
            return
        
        from os import chmod
        chmod(output.name,0o755)


#
# EOF
#

            
