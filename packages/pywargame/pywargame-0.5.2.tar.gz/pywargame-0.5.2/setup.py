#
#
# 
from setuptools import setup

def get_version():
    from os import getenv

    for e in ['CI_COMMIT_REF_NAME','CI_JOB_ID']:
        v = getenv(e,False)
        if v:
            return {'version':str(v)}

    return {}

setup(**get_version())

#
# EOF
#
