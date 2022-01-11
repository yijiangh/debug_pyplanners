import os, sys
import argparse
from termcolor import cprint

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(HERE, ".."))

from load_path import *
from utils import VerboseToFile
from itj.parse import get_itj_pddl_problem_from_json, export_plan_to_file
from itj.export_to_itj import save_pddlstream_plan_to_itj_process

################################

from pddlstream.utils import str_from_object, read
from pddlstream.algorithms.downward import get_cost_scale
from pddlstream.algorithms.downward import set_cost_scale, parse_action
from pddlstream.algorithms.meta import solve
from pddlstream.utils import INF
from pddlstream.language.constants import print_plan, is_plan
from pddlstream.utils import flatten, Profiler, SEPARATOR, inf_generator, INF

###############################

FILE_NAME_FROM_PROBLEM = {
    'nine_pieces' : 'nine_pieces_process_symbolic.json',
    'pavilion' : 'pavilion_process_symbolic.json',
    'cantibox' : 'CantiBoxLeft_process_symbolic.json',
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--algorithm', default='incremental', help='PDDLSteam planning algorithm.')
    parser.add_argument('--pp_search', default='eager', help='pyplanner search configuration.')
    parser.add_argument('--pp_evaluator', default='greedy', help='pyplanner evaluator configuration.')
    parser.add_argument('--pp_h', default='ff', help='pyplanner heuristic configuration.')
    parser.add_argument('--fd_search', default='ff-eager', help='downward search configuration.')

    parser.add_argument('--problem', default='nine_pieces', help='Problem to solve.')
    parser.add_argument('--seq_n', nargs='+', type=int, help='Zero-based index according to the Beam sequence in process.assembly.sequence. If only provide one number, `--seq_n 1`, we will only plan for one beam. If provide two numbers, `--seq_n start_id end_id`, we will plan from #start_id UNTIL #end_id. If more numbers are provided. By default, all the beams will be checked.')

    # parser.add_argument('--reset_to_home', action='store_true', help='Require all tools to be back on rack as goals.')
    parser.add_argument('--nofluents', action='store_true', help='Not use fluent facts in stream definitions.')
    parser.add_argument('--write', action='store_true', help='Export plan.')
    parser.add_argument('--save_dir', type=str, default='results', help='Subdir to save the process to.')
    parser.add_argument('--debug', action='store_true', help='Debug mode.')
    args = parser.parse_args()

    log_file_path = os.path.join(HERE, 'results', args.problem + \
        '_{}'.format('downward' if args.nofluents else 'pyplanner') + '.log')

    set_cost_scale(1)
    print('FD cost scale: ', get_cost_scale())

    with VerboseToFile(args.write, log_file_path):
        print('Arguments:', args)
        cprint('Using {} backend.'.format('pyplanner' if not args.nofluents else 'downward'), 'cyan')

        debug_problem_name = FILE_NAME_FROM_PROBLEM[args.problem] 
        debug_pddl_problem = get_itj_pddl_problem_from_json(debug_problem_name,
            debug=True, reset_to_home=True, use_fluents=not args.nofluents, seq_n=args.seq_n)[0]

        print()
        print('Initial:', debug_pddl_problem.init)
        print()
        print('Goal:', debug_pddl_problem.goal)
        print()

        additional_config = {}
        if not args.nofluents:
            additional_config['planner'] = {
                'search': args.pp_search, # eager | lazy | hill_climbing | a_star | random_walk | mcts
                # lazy might be faster because it performs fewer heuristic evaluations but the solution quality might be lower
                # NOTE(caelan): eager is actually faster here because evaluating heuristic goal is cheap
                'evaluator': args.pp_evaluator, # 'bfs' | 'uniform' | 'astar' | 'wastar2' | 'wastar3' | 'greedy'
                'heuristic': args.pp_h, # goal | add | ff | max | blind
                #'heuristic': ['ff', get_bias_fn(element_from_index)],
                # * tiebreaker
                'successors': 'all', # all | random | first_goals | first_operators
                # 'successors': order_fn,
            }
        else:
            # https://github.com/caelan/pddlstream/blob/4914667a13a80831cadaf115a70938e9f93b021e/pddlstream/algorithms/downward.py#L87
            additional_config['planner'] = args.fd_search # 'dijkstra' # 'max-astar' # 'lmcut-astar' # 'dijkstra' # 'ff-eager' # | 'add-random-lazy'

        effort_weight = 1. / get_cost_scale()
        with Profiler(num=25):
            solution = solve(debug_pddl_problem, algorithm=args.algorithm,
                             max_time=INF,
                             unit_costs=True,
                             success_cost=INF,
                             unit_efforts=True,
                             effort_weight=effort_weight,
                             max_planner_time=INF,
                             debug=args.debug, verbose=1, **additional_config)

        plan, cost, evaluations = solution
        plan_success = is_plan(plan)

    print('-'*10)
    # print_plan(plan)
    cprint('Planning {}'.format('succeeds' if plan_success else 'fails'), 'green' if plan_success else 'red')
    print('Plan length: ', len(plan))

    if plan_success and args.write:
        plan_path = os.path.join(HERE, 'results', args.problem + '_plan' + \
            '_{}'.format('downward' if args.nofluents else 'pyplanner') + '.txt')
        export_plan_to_file(plan, plan_path)
        save_pddlstream_plan_to_itj_process(debug_problem_name, plan, verbose=0, save_subdir=args.save_dir)

if __name__ == '__main__':
    main()
