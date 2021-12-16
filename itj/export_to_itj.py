import sys, os
from termcolor import cprint

try:
    import integral_timber_joints
    ITJ_PATH = os.path.dirname(integral_timber_joints.__file__)

    from integral_timber_joints.planning.parsing import parse_process, save_process, get_process_path
    from integral_timber_joints.process.action import LoadBeamAction, PickGripperFromStorageAction, PickBeamWithGripperAction, PickClampFromStorageAction, PlaceClampToStructureAction, BeamPlacementWithClampsAction, PlaceGripperToStorageAction, PlaceClampToStorageAction, PickClampFromStructureAction, BeamPlacementWithoutClampsAction, AssembleBeamWithScrewdriversAction,  RetractGripperFromBeamAction, PickScrewdriverFromStorageAction, PlaceScrewdriverToStorageAction, ManaulAssemblyAction, OperatorAttachScrewdriverAction, DockWithScrewdriverAction, RetractScrewdriverFromBeamAction
except ImportError:
    ITJ_PATH = None

from pddlstream.utils import mkdir

from itj.parse import load_symbolic_json

#####################################################

def action_compute_movements(process, action):
    action.create_movements(process)
    action.assign_movement_ids()
    for movement in action.movements:
        movement.create_state_diff(process)
    return action

def save_pddlstream_plan_to_itj_process(symbolic_json_file_name, plan, save_subdir='results', verbose=False):
    if not ITJ_PATH:
        cprint('integral_timber_joints package not installed. Related functions are disabled. Please install it if needed: https://github.com/gramaziokohler/integral_timber_joints', 'yellow')
        return

    sym_process_data = load_symbolic_json(symbolic_json_file_name)
    assert 'design_dir' in sym_process_data['metadata'] and 'process_json_file_name' in sym_process_data['metadata']
    design_dir = sym_process_data['metadata']['design_dir']
    assembly_name = sym_process_data['metadata']['process_json_file_name']

    process = parse_process(design_dir, assembly_name, subdir='.')

    # # Double check entire solution is valid
    # for beam_id in process.assembly.sequence:
    #     if not process.dependency.beam_all_valid(beam_id):
    #         process.dependency.compute_all(beam_id)
    #         assert process.dependency.beam_all_valid(beam_id)

    # place_actions = [action for action in plan if action.name == 'place_element_on_structure']
    # beam_sequence = [ac.args[0] for ac in place_actions]
    # assert beam_sequence == process.assembly.sequence, 'Don\'t support auto-plan assembly sequence for now!'

    beam_id = last_beam_id = ''
    seq_n = 0
    acts = []
    for pddl_action in plan:
        itj_act = None
        if pddl_action.name == 'pick_beam_with_gripper':
            beam_id = pddl_action.args[0]
            gripper_id = pddl_action.args[1]
            gripper = process.gripper(gripper_id)
            # * double-check tool type consistency
            gt_gripper_type = process.assembly.get_beam_attribute(beam_id, "gripper_type")
            assert gt_gripper_type == gripper.type_name, '{} should use gripper with type {} but {} with type {} assigned.'.format(beam_id, gt_gripper_type, gripper.name, gripper.type_name)

            itj_act = PickBeamWithGripperAction(seq_n, 0, beam_id, gripper_id)

        elif pddl_action.name == 'beam_placement_with_clamps' or \
            pddl_action.name == 'beam_placement_without_clamp' or \
            pddl_action.name == 'assemble_beam_with_screwdrivers':
            beam_id = pddl_action.args[0]
            gripper_id = pddl_action.args[2]
            gripper = process.gripper(gripper_id)
            # * double-check tool type consistency
            gt_gripper_type = process.assembly.get_beam_attribute(beam_id, "gripper_type")
            assert gt_gripper_type == gripper.type_name, '{} should use gripper with type {} but {} with type {} assigned.'.format(beam_id, gt_gripper_type, gripper.name, gripper.type_name)

            # ! these should be updated by previous place clamp actions already
            joint_id_of_clamps = list(process.assembly.get_joint_ids_with_tools_for_beam(beam_id))
            joint_tool_ids = [process.assembly.get_joint_attribute(joint_id, 'tool_id') for joint_id in joint_id_of_clamps]
            if pddl_action.name == 'beam_placement_without_clamp':
                itj_act = BeamPlacementWithoutClampsAction(seq_n, 0, beam_id, gripper_id)
            elif pddl_action.name == 'beam_placement_with_clamps':
                itj_act = BeamPlacementWithClampsAction(seq_n, 0, beam_id, joint_id_of_clamps, gripper_id, joint_tool_ids)
            elif pddl_action.name == 'assemble_beam_with_screwdrivers':
                itj_act = AssembleBeamWithScrewdriversAction(seq_n, 0, beam_id, joint_id_of_clamps, gripper_id, screwdriver_ids=joint_tool_ids)

        elif pddl_action.name == 'retract_gripper_from_beam':
            beam_id = pddl_action.args[0]
            gripper_id = pddl_action.args[1]
            itj_act = RetractGripperFromBeamAction(beam_id=beam_id, gripper_id=gripper_id)

        elif pddl_action.name == 'operator_load_beam':
            beam_id = pddl_action.args[0]
            itj_act = LoadBeamAction(seq_n, 0, beam_id)

        elif pddl_action.name == 'manaul_assemble_scaffold':
            beam_id = pddl_action.args[0]
            itj_act = ManaulAssemblyAction(seq_n, 0, beam_id)

        elif pddl_action.name == 'operator_attach_screwdriver':
            tool_id = pddl_action.args[0]
            joint_id = (pddl_action.args[1], pddl_action.args[2])
            assert process.assembly.sequence.index(joint_id[0]) < process.assembly.sequence.index(joint_id[1])
            # * double-check tool type consistency
            screwdriver = process.screwdriver(tool_id)
            gt_sd_type = process.assembly.get_joint_attribute(joint_id, 'tool_type')
            assert gt_sd_type == screwdriver.type_name, 'Joint {} should use screwdriver with type {} but {} with type {} assigned.'.format(joint_id, gt_sd_type, screwdriver.name, screwdriver.type_name)

            # * screwdriver assignment to beam
            process.assembly.set_joint_attribute(joint_id, 'tool_id', tool_id)
            itj_act = OperatorAttachScrewdriverAction(seq_n, 0, beam_id, joint_id, screwdriver.type_name, tool_id, 'assembly_wcf_screwdriver_attachment_pose')

        elif pddl_action.name == 'pick_tool_from_rack':
            tool_id = pddl_action.args[0]
            if tool_id.startswith('g'):
                gripper = process.gripper(tool_id)
                itj_act = PickGripperFromStorageAction(seq_n, 0, gripper.type_name, tool_id)
            elif tool_id.startswith('c'):
                clamp = process.clamp(tool_id)
                itj_act = PickClampFromStorageAction(seq_n, 0, clamp.type_name, tool_id)
            elif tool_id.startswith('s'):
                screwdriver = process.screwdriver(tool_id)
                itj_act = PickScrewdriverFromStorageAction(seq_n, 0, screwdriver.type_name, tool_id)
            else:
                raise ValueError('Weird tool id {}'.format(tool_id))

        elif pddl_action.name == 'place_tool_at_rack':
            tool_id = pddl_action.args[0]
            if tool_id.startswith('g'):
                gripper = process.gripper(tool_id)
                itj_act = PlaceGripperToStorageAction(seq_n, 0, gripper.type_name, tool_id)
            elif tool_id.startswith('c'):
                clamp = process.clamp(tool_id)
                itj_act = PlaceClampToStorageAction(tool_type=clamp.type_name, tool_id=tool_id)
            elif tool_id.startswith('s'):
                screwdriver = process.screwdriver(tool_id)
                itj_act = PlaceScrewdriverToStorageAction(seq_n, 0, screwdriver.type_name, tool_id)
            else:
                raise ValueError('Weird tool id {}'.format(tool_id))

        elif pddl_action.name == 'place_clamp_to_structure':
            clamp_id = pddl_action.args[0]
            clamp = process.clamp(clamp_id)
            joint_id = (pddl_action.args[1], pddl_action.args[2])
            # ! convention: sequence id smaller first
            assert process.assembly.sequence.index(joint_id[0]) < process.assembly.sequence.index(joint_id[1])
            # * double-check clamp type consistency
            gt_clamp_type = process.assembly.get_joint_attribute(joint_id, 'tool_type')
            assert gt_clamp_type == clamp.type_name, 'Joint {} should use clamp with type {} but {} with type {} assigned.'.format(joint_id, gt_clamp_type, clamp.name, clamp.type_name)

            # * clamp assignment to beam
            process.assembly.set_joint_attribute(joint_id, 'tool_id', clamp_id)
            itj_act = PlaceClampToStructureAction(seq_n, 0, joint_id, clamp.type_name, clamp_id)

        elif pddl_action.name == 'pick_clamp_from_structure':
            clamp_id = pddl_action.args[0]
            clamp = process.clamp(clamp_id)
            joint_id = (pddl_action.args[1], pddl_action.args[2])
            assert process.assembly.sequence.index(joint_id[0]) < process.assembly.sequence.index(joint_id[1])
            itj_act = PickClampFromStructureAction(joint_id=joint_id, tool_type=clamp.type_name, tool_id=clamp_id)

        elif pddl_action.name == 'dock_with_screwdriver':
            tool_id = pddl_action.args[0]
            screwdriver = process.screwdriver(tool_id)
            joint_id = (pddl_action.args[1], pddl_action.args[2])
            assert process.assembly.sequence.index(joint_id[0]) < process.assembly.sequence.index(joint_id[1])
            itj_act = DockWithScrewdriverAction(joint_id=joint_id, tool_position='screwdriver_assembled_attached', tool_type=screwdriver.type_name, tool_id=tool_id)

        elif pddl_action.name == 'retract_screwdriver_from_beam':
            tool_id = pddl_action.args[0]
            screwdriver = process.screwdriver(tool_id)
            joint_id = (pddl_action.args[1], pddl_action.args[2])
            assert process.assembly.sequence.index(joint_id[0]) < process.assembly.sequence.index(joint_id[1])
            itj_act = RetractScrewdriverFromBeamAction(beam_id=beam_id, joint_id=joint_id, tool_id=tool_id)
        else:
            raise ValueError(pddl_action.name)

        assert itj_act is not None, 'Action creation failed for {}'.format(pddl_action.name)
        itj_act = action_compute_movements(process, itj_act)
        acts.append(itj_act)

        if 'beam_placement' in pddl_action.name or 'assemble_beam' in pddl_action.name:
            assert len(acts) > 0
            if beam_id != last_beam_id and beam_id != process.assembly.sequence[-1]:
                if verbose:
                    print('='*10)
                    print('Beam id: {}'.format(beam_id))
                    for act in acts:
                        print('|- ' + act.__str__())
                process.assembly.set_beam_attribute(beam_id, 'actions', acts)
                last_beam_id = beam_id
                seq_n += 1
                acts = []

    # * last beam and tool collection
    assert beam_id == process.assembly.sequence[-1] and len(acts) > 0
    if verbose:
        print('='*10)
        print('Beam id: {}'.format(beam_id))
        for act in acts:
            print('|- ' + act.__str__())
    process.assembly.set_beam_attribute(beam_id, 'actions', acts)

    # * write to file
    process_fp = get_process_path(design_dir, assembly_name, subdir=save_subdir)
    save_process(process, process_fp, deepcopy=False)