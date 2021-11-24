import os, sys
from termcolor import cprint

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
try:
    # prioritize local pddlstream first
    # add your PDDLStream path here: https://github.com/caelan/pddlstream
    sys.path.append(os.environ['PDDLSTREAM_PATH'])
except KeyError:
    cprint('No `PDDLSTREAM_PATH` found in the env variables, using pddlstream submodule', 'yellow')
    pddlstream_local_path = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'external', 'pddlstream'))
    assert os.path.exists(pddlstream_local_path)
    sys.path.extend([
        pddlstream_local_path
    ])

try:
    sys.path.append(os.environ['PYPLANNERS_PATH'])
except KeyError:
    cprint('No `PYPLANNERS_PATH` found in the env variables, using pyplanner submodule', 'yellow')
    local_pyplanner_path = os.path.abspath(os.path.join(CUR_PATH, '..', '..', 'external', 'pyplanners'))
    assert os.path.exists(local_pyplanner_path)
    # Inside PDDLStream, it will look for 'PYPLANNERS_PATH'
    os.environ['PYPLANNERS_PATH'] = local_pyplanner_path

import pddlstream
cprint("Using pddlstream from {}".format(pddlstream.__file__), 'yellow')

import strips # pyplanners
cprint("Using strips (pyplanners) from {}".format(strips.__file__), 'yellow')

