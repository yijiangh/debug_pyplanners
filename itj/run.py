import os, sys
import argparse
from termcolor import cprint

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(HERE, ".."))

from load_path import *
from itj.parse import get_itj_pddl_problem_from_json

################################

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
    parser.add_argument('--problem', default='nine_pieces', help='Problem to solve.')
    parser.add_argument('--seq_n', nargs='+', type=int, help='Zero-based index according to the Beam sequence in process.assembly.sequence. If only provide one number, `--seq_n 1`, we will only plan for one beam. If provide two numbers, `--seq_n start_id end_id`, we will plan from #start_id UNTIL #end_id. If more numbers are provided. By default, all the beams will be checked.')

    parser.add_argument('--reset_to_home', action='store_true', help='Require all tools to be back on rack as goals.')
    parser.add_argument('--fluents', action='store_false', help='Use fluent facts in stream definitions.')
    parser.add_argument('--debug', action='store_true', help='Debug mode.')
    args = parser.parse_args()
    print('Arguments:', args)
    
    cprint('Using {} backend.'.format('pyplanner' if args.fluents else 'downward'), 'cyan')

    debug_problem_name = FILE_NAME_FROM_PROBLEM[args.problem] # 'CantiBoxLeft_process_symbolic.json' # "nine_pieces_process_symbolic.json"
    debug_pddl_problem = get_itj_pddl_problem_from_json(debug_problem_name, use_partial_order=True, 
        debug=True, reset_to_home=args.reset_to_home, use_fluents=args.fluents, seq_n=args.seq_n)[0]

    # print()
    # print('Initial:', debug_pddl_problem.init)
    print()
    print('Goal:', debug_pddl_problem.goal)
    print()

    additional_config = {}
    if args.fluents:
        additional_config['planner'] = {
            'search': 'eager', # eager | lazy | hill_climbing | a_star | random_walk | mcts
            # lazy might be faster because it performs fewer heuristic evaluations but the solution quality might be lower
            # NOTE(caelan): eager is actually faster here because evaluating heuristic goal is cheap
            'evaluator': 'greedy', # 'bfs' | 'uniform' | 'astar' | 'wastar2' | 'wastar3' | 'greedy'
            'heuristic': 'ff', # goal | add | ff | max | blind
            #'heuristic': ['ff', get_bias_fn(element_from_index)],
            # * tiebreaker
            'successors': 'all', # all | random | first_goals | first_operators
            # 'successors': order_fn,
        }
    else:
        additional_config['planner'] = 'ff-eager' # | 'add-random-lazy'

    set_cost_scale(1)
    # with Profiler(num=25):
    if True:
        solution = solve(debug_pddl_problem, algorithm=args.algorithm,
                         max_time=INF,
                         unit_costs=True,
                         max_planner_time=INF,
                         debug=args.debug, verbose=0, **additional_config)

    plan, cost, evaluations = solution
    plan_success = is_plan(plan)

    print('-'*10)
    print_plan(plan)
    cprint('Planning {}'.format('succeeds' if plan_success else 'fails'), 'green' if plan_success else 'red')

    # plan_success &= len(plan) == 53 if plan_success and not args.fluents else len(plan) == 60
    # if not plan_success:
    #     cprint('Plan length not correct.', 'red')

if __name__ == '__main__':
    main()
