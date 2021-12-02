from load_path import *
from pddlstream.language.conversion import pddl_from_object, obj_from_pddl
from misc.objects import str_object
from termcolor import cprint, colored

################################

def print_sorted_list(data, rows=0, columns=0, ljust=2):
    if not data:
        return
    if rows:
        lines = {}
        for count, item in enumerate(sorted(data)):
            lines.setdefault(count % rows, []).append(item)
        for key, value in sorted(lines.items()):
            for item in value:
                print(item.ljust(ljust), end="\t")
            print()
    elif columns:
        for count, item in enumerate(sorted(data), 1):
            print(item.ljust(ljust), end="\t")
            if count % columns == 0:
                print()
    else:
        print(sorted(data))  # the default print behaviour
    print()

################################

def print_state(state, tag='', color='yellow'):
    atoms = []
    for atom in state.atoms:
        atoms.append(atom.predicate + str_object([obj_from_pddl(n) for n in atom.args]))
        # if 'assembled' in atoms[-1]:
    print(colored('State: {}'.format(tag), color))
    print_sorted_list(atoms, columns=6)
    # for atom in atoms:
    #     if ATOM_SEARCH_KEYWORD in atom:
    #         input('Stop!')

def print_operator(py_operator, state=None, color='green'):
    if 'fd_action' in py_operator.args:
        fd_action = py_operator.args['fd_action']
        action_name = fd_action.name
        action_name = action_name.replace('(', '')
        action_name = action_name.replace(')', '')
        action_name = action_name.split(' ')
        print('+'*5)
        cprint(action_name[0] + str_object([obj_from_pddl(n) for n in action_name[1:]]), color)
        print(str_object([[atom.predicate] + [obj_from_pddl(n) for n in atom.args] for atom in fd_action.precondition]))
    if state:
        is_contains = py_operator.contains(state)
        cprint('Contains:' + colored(is_contains, 'green' if is_contains else 'red'))

