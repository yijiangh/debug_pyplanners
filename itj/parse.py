import os, sys
import json
from termcolor import cprint
from collections import defaultdict

from pddlstream.utils import read, str_from_object, write
from pddlstream.language.stream import StreamInfo, PartialInputs, WildOutput, DEBUG
from pddlstream.language.constants import And, PDDLProblem, Equal
from pddlstream.language.generator import from_gen_fn, from_fn, from_test

HERE = os.path.abspath(os.path.dirname(__file__))

######################################

def beam_ids_from_argparse_seq_n(beam_sequence, seq_n):
    full_seq_len = len(beam_sequence)
    seq_n = seq_n or list(range(full_seq_len))
    for seq_i in seq_n:
        assert seq_i < full_seq_len and seq_i >= 0, 'Invalid seq_n input {}'.format(seq_i)
    if len(seq_n) == 0:
        # defaults to solve all beams
        beam_ids = [beam_sequence[si] for si in range(seq_n, full_seq_len)]
    elif len(seq_n) == 1:
        beam_ids = [beam_sequence[seq_n[0]]]
    elif len(seq_n) == 2:
        beam_ids = [beam_sequence[seq_i] for seq_i in range(seq_n[0], seq_n[1]+1)]
    else:
        beam_ids = [beam_sequence[seq_i] for seq_i in seq_n]
    cprint('Solving for beam {}'.format(beam_ids), 'cyan')
    return beam_ids

def load_symbolic_json(json_file_name):
    json_file_path = os.path.join(HERE, json_file_name)
    with open(json_file_path, 'r') as f:
        process = json.load(f)
    return process

def get_itj_pddl_problem_from_json(json_file_name, debug=False,
        reset_to_home=True, use_fluents=False, seq_n=None):
    process = load_symbolic_json(json_file_name)
    cprint('Symbolic process json parsed from {}'.format(json_file_name), 'magenta')

    domain_pddl = read(os.path.join(HERE, 'debug_domain.pddl'))
    if not use_fluents:
        stream_pddl = read(os.path.join(HERE, 'debug_stream.pddl'))
    else:
        stream_pddl = read(os.path.join(HERE, 'debug_stream_fluents.pddl'))

    init = []

    constant_map = {}
    init.extend([
        ('RobotToolChangerEmpty',), 
    ])

    # * Beams
    beam_seq = beam_ids_from_argparse_seq_n([bd['beam_id'] for bd in process['assembly']['sequence']], seq_n)
    for i, e in enumerate(beam_seq):
        e_data = process['assembly']['sequence'][i]
        assert e_data['beam_id'] == e
        assert e_data['assembly_method'] != 'UNDEFINED'
        if e_data['assembly_method'] == 'ManualAssembly':
            init.append(('Scaffold', e))
        else:
            init.append(('Element', e))
            init.append((e_data['assembly_method']+'Element', e))
            for sf in e_data['associated_scaffolds']:
                init.append(('AssociatedScaffold', e, sf))

    joints_data = [j_data for j_data in process['assembly']['joints'] if j_data['joint_id'][0] in beam_seq and \
            j_data['joint_id'][1] in beam_seq]
    for j_data in joints_data:
        j = j_data['joint_id']
        init.extend([
            ('Joint', j[0], j[1]),
            # ('Joint', j[1], j[0]),
            # ('NoToolAtJoint', j[0], j[1]),
            # ('NoToolAtJoint', j[1], j[0]),
        ])

    # * assembly sequence
    cprint('Using beam sequence ordering: {}'.format(beam_seq), 'yellow')
    for e1, e2 in zip(beam_seq[:-1], beam_seq[1:]):
        init.append(('Order', e1, e2))

    # * Clamps
    for c_name in process['clamps']:
        init.extend([
            ('Clamp', c_name),
            ('Tool', c_name),
            ('AtRack', c_name),
            ('ToolNotOccupiedOnJoint', c_name),
        ])

    # * Screw Drivers
    if 'screwdrivers' in process:
        for sd_name in process['screwdrivers']:
            init.extend([
                ('ScrewDriver', sd_name),
                ('Tool', sd_name),
                ('AtRack', sd_name),
                ('ToolNotOccupiedOnJoint', sd_name),
            ])

    # * joint to clamp/scewdriver tool type assignment
    clamp_from_joint = defaultdict(set)
    screwdriver_from_joint = defaultdict(set)
    for j_data in joints_data:
        j = j_data['joint_id']
        joint_clamp_type = j_data['tool_type']
        for c_name, c in process['clamps'].items():
            if c['type_name'] == joint_clamp_type:
                init.extend([
                    ('JointToolTypeMatch', j[0], j[1], c_name),
                    # ('JointToolTypeMatch', j[1], j[0], c_name),
                ])
                clamp_from_joint[j[0]+','+j[1]].add(c_name)
                # clamp_from_joint[j[1]+','+j[0]].add(c_name)
        if 'screwdrivers' in process:
            for sd_name, sd in process['screwdrivers'].items():
                if sd['type_name'] == joint_clamp_type:
                    init.extend([
                        ('JointToolTypeMatch', j[0], j[1], sd_name),
                        # ('JointToolTypeMatch', j[1], j[0], sd_name),
                    ])
                    screwdriver_from_joint[j[0]+','+j[1]].add(sd_name)
                    # screwdriver_from_joint[j[1]+','+j[0]].add(sd_name)

    # * Grippers
    for g_name in process['grippers']:
        init.extend([
            ('Gripper', g_name),
            ('Tool', g_name),
            ('AtRack', g_name),
        ])
    # * gripper type
    gripper_from_beam = defaultdict(set)
    for beam_data in process['assembly']['sequence']:
        if not beam_data['beam_id'] in beam_seq:
            continue
        beam_gripper_type = beam_data["beam_gripper_type"]
        for g_name, g_data in process['grippers'].items():
            if g_data['type_name'] == beam_gripper_type:
                beam_id = beam_data['beam_id']
                init.append(('GripperToolTypeMatch', beam_id, g_name))
                gripper_from_beam[beam_id].add(g_name)
                gripper_from_beam[beam_id].add(g_name)

    if debug:
        stream_map = DEBUG
    else:
        stream_map = {
            'sample-place-tool': from_fn(lambda obj: (None,)),
        }

    goal_literals = []
    goal_literals.extend(('Assembled', e) for e in beam_seq)
    if reset_to_home:
        goal_literals.extend(('AtRack', t_name) for t_name in list(process['clamps']) + list(process['grippers']))
        if 'screwdrivers' in process:
            goal_literals.extend(('AtRack', t_name) for t_name in list(process['screwdrivers']))
    goal = And(*goal_literals)

    pddlstream_problem = PDDLProblem(domain_pddl, constant_map, stream_pddl, stream_map, init, goal)
    return pddlstream_problem, gripper_from_beam, clamp_from_joint, screwdriver_from_joint

######################################################

def export_plan_to_file(plan, file_path=None):
    if file_path is None:
        file_path = 'tmp_pddlstream_plan.txt'
    long_str = ''
    for i, action in enumerate(plan):
        name, args = action
        long_str += '{:2}) {} {}\n'.format(i, name, ' '.join(map(str_from_object, args)))
        # f.write(line)
    write(file_path, long_str)
    cprint('Plan written to {}'.format(file_path), 'green')