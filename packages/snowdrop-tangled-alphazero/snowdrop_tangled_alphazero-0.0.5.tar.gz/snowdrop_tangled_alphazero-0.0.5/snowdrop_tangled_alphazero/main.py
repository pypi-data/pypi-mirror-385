""" parallelized AlphaZero for training Tangled agents """
import math
import os
import sys
import time
import random
import cProfile
import pstats
import logging
import coloredlogs
from collections import deque
from pickle import Pickler
from typing import Any

import multiprocessing as mp

from snowdrop_tangled_alphazero.neural_net.AlphaZeroNet import AlphaZeroNet
from snowdrop_tangled_alphazero.utilities.utilities import (load_model_and_optimizer, save_model_and_optimizer,
                                                   save_train_examples, load_train_examples,
                                                   load_terminal_state_adjudications,
                                                   save_terminal_state_adjudication_examples)
from snowdrop_tangled_alphazero.utilities.parallel import parallel_self_play, parallel_competitive_play

from snowdrop_tangled_game_engine import GraphProperties

# for X-Prize game graphs, only change graph_number + rollout_adjudicator * keep all other params the same *
# neural nets are defined in AlphaZeroNet.py


def main():

    log = logging.getLogger(__name__)
    coloredlogs.install(level='INFO')  # Change this to DEBUG to see more info.

    # choosing graph to train your agent for and terminal state adjudication method & parameters
    graph_args : dict[str, Any] = {
        'graph_number': 20,   # 11 P_3, 2 K_3, 20 diamond, 19 barbell, 18 3-prism, 12 moser, 24 C_60
        'rollout_adjudicator': 'lookup_table'} # ['lookup_table', 'simulated_annealing', 'quantum_annealing']

    gp = GraphProperties()
    graph_properties = gp.graph_database[graph_args["graph_number"]]
    board_size = graph_properties["num_nodes"] + 3 * len(graph_properties["edge_list"])
    graph_args["get_board_size"] = (board_size, 1)
    graph_args["get_action_size"] = board_size

    graph_index = gp.allowed_graphs.index(graph_args["graph_number"])

    graph_args['adjudicator_args'] = {'epsilon': gp.epsilon_values[graph_index],
                                      'anneal_time': gp.anneal_times[graph_index],
                                      'num_reads': 10000}

    # these are the parameters of the solver used to generate the lookup table
    if graph_args["rollout_adjudicator"] in ['lookup_table']:
        lookup_args = {'solver': 'quantum_annealing'}   # this is which solver generated the lookup table you want
    else:
        lookup_args = None

    args = {
        'fixed_token_game': True,   # if True, red/blue have fixed token locations; if False, players choose vertices
        # 'lookup_args': lookup_args,   # only relevant if you are using a lookup table for adjudication
        'numIters': 20,    # number of self-play/nn training/competition cycles
        'numEps': 256,     # Number of complete self-play games to simulate during a new iteration; number of training
        # examples = numEps*# moves per game*# symmetries; make this a multiple of num_workers
        'tempThreshold': len(graph_properties["edge_list"]) - 2,   # Training uses temp=1 if episodeStep < tempThreshold, and thereafter uses temp=0;
        # set to E-2 for all but last 2 moves, E-4 for all but last 4 moves, etc. (set to E-2 for paper)
        'updateThreshold': 0,  # During arena playoff, new neural net will be accepted if >= threshold of Elo gain
        'maxlenOfQueue': 5000000,  # Number of game examples to train the neural networks
        'numMCTSSimsSelf': 1000,  # Moves for MCTS to simulate during self-play; higher means higher game quality
        'numMCTSSimsComp': 10,  # Moves for MCTS to simulate during competitive play
        # each traverses a tree down to a leaf. once it gets there it calls the neural net to establish an initial
        # policy and value for the node. if the leaf is a terminal state, it evaluates the value by adjudication
        'arenaCompare': 1600,  # Half the number of games to play during arena play to determine if new net will be
        # accepted; small Elo differences need large numbers (1000-3000 total games) to be sure; make this a multiple
        # of num_workers 592*2
        'cpuct': 2.0,  # constant for polynomial upper confidence bound (larger=more exploration), default=2
        'initial_elo': 1000,   # assuming starting from baseline of equivalence to 10-rollout MCTS
        # 'checkpoints': './results/graph_' +    str(graph_args.graph_number) + '_parallel_fixed_token_results/',
        'load_model': False,  # set to true if you want to start training from a previous checkpoint
        'load_previous_training_examples': False,   # set to True to load previous self-play games
        'load_previous_terminal_state_adjudications': False,  # set to True to load previous terminal state adjudications
        'numItersForTrainExamplesHistory': 4,
        'num_workers': 8   # number of cpu workers; test different values for your setup to find optimal number
    }

    # place where data goes
    if args["fixed_token_game"]:
        args["checkpoints"] = './results/graph_' + str(graph_args["graph_number"]) + '_fixed_token/'
    else:
        args["checkpoints"] = './results/graph_' + str(graph_args["graph_number"]) + '_free_token/'

    args["checkpoints"] += graph_args["rollout_adjudicator"] + '/'

    if graph_args["rollout_adjudicator"] in ['lookup_table']:
        args["checkpoints"] += lookup_args["solver"] + '/'

    if graph_args["rollout_adjudicator"] in ['quantum_annealing']:
        args["checkpoints"] += str(graph_args["adjudicator_args"]['epsilon']) + '_' + str(graph_args["adjudicator_args"]['anneal_time']) + '_' + str(graph_args["adjudicator_args"]['num_reads']) + '/'

    if graph_args["rollout_adjudicator"] in ['simulated_annealing']:
        args["checkpoints"] += str(graph_args["adjudicator_args"]['epsilon']) + '_' + str(graph_args["adjudicator_args"]['num_reads']) + '/'

    if args["load_model"]:
        log.info('Loading checkpoint "%s/%s"...', args["checkpoints"], 'best.pth')
        model = load_model_and_optimizer(board_size=graph_args["get_board_size"],
                                         action_size=graph_args["get_action_size"],
                                         graph_number=graph_args["graph_number"],
                                         filepath=os.path.join(args["checkpoints"], 'best.pth'))
    else:
        log.info('Loading %s...', AlphaZeroNet.__name__)
        model = AlphaZeroNet(board_size=graph_args["get_board_size"],
                             action_size=graph_args["get_action_size"],
                             graph_number=graph_args["graph_number"])
        if not os.path.exists(args["checkpoints"]):
            os.makedirs(args["checkpoints"])
            print("Directory ", args["checkpoints"], " created.")

    # train_examples_history should be a list of length (# of iterations) of deques of length # examples, each a 3-tuple
    if args["load_previous_training_examples"]:
        train_examples_history = load_train_examples(args["checkpoints)"])
    else:
        train_examples_history = []

    if args["load_previous_terminal_state_adjudications"]:
        terminal_state_adjudications_history = load_terminal_state_adjudications(args["checkpoints)"])
    else:
        terminal_state_adjudications_history = []

    list_of_results = []
    elo_list = []
    elo_best = args["initial_elo"]

    for i in range(1, args["numIters"] + 1):

        log.info(f'Starting Iter #{i} ...')

        self_play_data, terminal_state_adjudications = parallel_self_play(model=model, args=args, graph_args=graph_args)
        # self_play_data is a list of 3-tuples
        terminal_state_adjudications_history += terminal_state_adjudications

        train_examples_history.append(deque((self_play_data), maxlen=args["maxlenOfQueue"]))

        if len(train_examples_history) > args["numItersForTrainExamplesHistory"]:
            log.warning(f"Removing the oldest entry in trainExamples. len(trainExamplesHistory) = {len(train_examples_history)}")
            train_examples_history.pop(0)  # this pops the zeroth (oldest) item from the list

        # backup history to a file: examples collected using model from previous iteration, so (i-1)
        save_train_examples(i - 1, train_examples_history, args["checkpoints"])

        # shuffle examples before training
        train_examples = []
        for e in train_examples_history:
            train_examples.extend(e)
        random.shuffle(train_examples)   # train_examples is a list of 3-tuples

        save_model_and_optimizer(model=model, filepath=os.path.join(args["checkpoints"], 'temp.pth'))

        print('NN training starting on', len(train_examples), 'examples...')
        start_nn_training = time.time()

        try:
            model.train_net(train_examples)
        except AttributeError:
            print('data collection failed on first run... try again!')
            sys.exit()

        print('NN training took', time.time() - start_nn_training, 'seconds.')

        # save new trained NN as challenger
        save_model_and_optimizer(model=model, filepath=os.path.join(args["checkpoints"], 'challenger.pth'))

        competition_data, terminal_state_adjudications = parallel_competitive_play(args=args, graph_args=graph_args)

        terminal_state_adjudications_history += terminal_state_adjudications

        champ_wins = 0
        challenger_wins = 0
        draws = 0

        for each in competition_data:
            champ_wins += each[0].count(1) + each[1].count(-1)
            challenger_wins += each[0].count(-1) + each[1].count(1)
            draws += each[0].count(-0.01) + each[1].count(-0.01) + each[0].count(0.01) + each[1].count(0.01)

        log.info('NEW/PREV WINS : %d / %d ; DRAWS : %d' % (challenger_wins, champ_wins, draws))

        try:
            elo_diff = -400*math.log10(2*args["arenaCompare"]/(challenger_wins + 0.5*draws+0.01) - 1)
        except (ZeroDivisionError, ValueError):
            elo_diff = 0

        elo_list.append([elo_best, elo_best + elo_diff])
        log.info('NEW/PREV ELO ESTIMATES : %d / %d ; ELO DIFF : %d' % (elo_best + elo_diff, elo_best, elo_diff))

        if elo_diff < args["updateThreshold"]:
            log.info('REJECTING NEW MODEL')
            list_of_results.append([challenger_wins, champ_wins, draws, 'REJECT'])
            model = load_model_and_optimizer(board_size=graph_args["get_board_size"],
                                             action_size=graph_args["get_action_size"],
                                             graph_number=graph_args["graph_number"],
                                             filepath=os.path.join(args["checkpoints"], 'temp.pth'))
        else:
            log.info('ACCEPTING NEW MODEL')
            list_of_results.append([challenger_wins, champ_wins, draws, 'ACCEPT'])
            elo_best += elo_diff
            save_model_and_optimizer(model=model,
                                     filepath=os.path.join(args["checkpoints"], 'checkpoint_' + str(i) + '.pth'))
            save_model_and_optimizer(model=model,
                                     filepath=os.path.join(args["checkpoints"], 'best.pth'))

        # if using hardware, save most recent history of terminal state adjudications after whole iteration complete
        if graph_args["rollout_adjudicator"] == "quantum_annealing":
            print('saving', len(terminal_state_adjudications_history), 'terminal state evals to disk...')
            save_terminal_state_adjudication_examples(terminal_state_adjudications_history, os.path.join("D:", "quantum_adjudications"))

        with open(os.path.join(args["checkpoints"], 'elo_list.pkl'), "wb") as f:
            Pickler(f).dump(elo_list)   # type: ignore


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)  # Ensures correct behavior in PyCharm

    start = time.time()

    with cProfile.Profile() as pr:
        main()

    print('total time elapsed:', time.time() - start, 'seconds...')

    stats = pstats.Stats(pr)
    stats.strip_dirs().sort_stats('tottime').print_stats(10)   # show top 10 results
