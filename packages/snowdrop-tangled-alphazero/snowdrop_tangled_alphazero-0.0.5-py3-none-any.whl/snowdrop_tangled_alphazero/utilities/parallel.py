""" functions for parallelizing alphazero """
import os
import torch
import time
import numpy as np

from concurrent.futures import ProcessPoolExecutor, as_completed, process

from snowdrop_tangled_alphazero.monte_carlo.AZMCTS import AZ_MCTS
from snowdrop_tangled_alphazero.utilities.utilities import load_model_and_optimizer, save_model_and_optimizer
from snowdrop_tangled_alphazero.game.TangledGame import TangledGame


def execute_episode(game, model, args):
    """
    This function executes one episode of self-play, starting with player 1.
    As the game is played, each turn is added as a training example to
    trainExamples. The game is played till the game ends. After the game
    ends, the outcome of the game is used to assign values to each example
    in trainExamples.

    It uses temp=1 if episodeStep < tempThreshold, and thereafter uses temp=0.

    Returns:
        trainExamples: a list of examples of the form (canonicalBoard, currPlayer, pi,v)
                       pi is the MCTS informed policy vector, v is +1 if
                       the player eventually won the game, else -1.
    """

    # create a new mcts for each execute_episode
    mcts = AZ_MCTS(game, model, args)  # reset search tree

    train_examples = []
    board = game.getInitBoard()
    current_player = 1
    episode_step = 0

    while True:
        episode_step += 1
        canonical_board = game.getCanonicalForm(board, current_player)
        temp = int(episode_step < args["tempThreshold"])

        pi = mcts.get_action_prob(canonical_board, temp=temp)
        sym = game.getSymmetries(canonical_board, pi)
        for b, p in sym:
            train_examples.append([b, current_player, p, None])

        action = np.random.choice(len(pi), p=pi)
        board, current_player = game.getNextState(board, current_player, action)

        # only place where adjudicator is called
        r, adjudication_result = game.getGameEnded(board, current_player)

        if r != 0:
            # returns [board, policy_vector, who_won_value], list of terminal state adjudications
            all_terminal_state_adjudications = mcts.terminal_state_adjudications + [adjudication_result]
            return [(x[0], x[2], r * ((-1) ** (x[1] != current_player))) for x in train_examples], all_terminal_state_adjudications


def self_play_worker(args, graph_args, games_per_worker):

    game = TangledGame(graph_args=graph_args,
                       fixed_token_game=args["fixed_token_game"])

    model = load_model_and_optimizer(board_size=graph_args["get_board_size"],
                                     action_size=graph_args["get_action_size"],
                                     graph_number=graph_args["graph_number"],
                                     filepath=os.path.join(args["checkpoints"], 'best.pth'))

    model.eval()  # Set the model to evaluation mode

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    worker_data = [execute_episode(game, model, args) for _ in range(games_per_worker)]

    del model
    torch.cuda.empty_cache()

    return worker_data


def parallel_self_play(model, args, graph_args):
    # save current model as best.pth; if first time, random NN
    save_model_and_optimizer(model=model, filepath=os.path.join(args["checkpoints"], 'best.pth'))

    num_workers = args["num_workers"]  # Adjust based on GPU memory
    games_per_worker = args["numEps"] // num_workers  # if numEps = 100, eg games_per_worker = 25

    print(f'beginning parallel self-play with {num_workers} workers...')
    start_parallel_self_play = time.time()

    self_play_data = []
    terminal_state_adjudications = []
    completed_workers = 0

    try:
        with ProcessPoolExecutor(max_workers=args["num_workers"]) as executor:
            futures = [executor.submit(self_play_worker, args, graph_args, games_per_worker)
                       for _ in range(num_workers)]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=600)  # Add timeout to prevent hanging
                    for each_result in result:
                        self_play_data.extend(each_result[0])   # extend here because there are lots of moves
                        terminal_state_adjudications += each_result[1]    # adding list
                    completed_workers += 1
                except process.BrokenProcessPool as e:
                    print(f"Process pool broke: {e}")
                    break  # Break out of loop since the pool is broken
                except Exception as e:
                    print(f"Worker failed with error: {e}")

    except process.BrokenProcessPool as e:
        print(f"Process pool broke during creation or execution: {e}")

    finally:
        duration = time.time() - start_parallel_self_play
        print(f'Parallel self-play completed with {completed_workers}/{num_workers} workers')
        print(f'It took {duration:.2f} seconds.')

        # If we have at least some data, we can still proceed
        if len(self_play_data) == 0:
            print("Warning: No self-play data was collected. Check worker logs for errors.")
        else:
            print(f"Collected data from {len(self_play_data)} games")

    return self_play_data, terminal_state_adjudications


def play_game(game, player1, player2):
    """
    Executes one episode of a game.

    Returns:
        either
            winner: player who won the game (1 if player1, -1 if player2)
        or
            draw result returned from the game that is neither 1, -1, nor 0.
    """

    players = [player2, None, player1]
    current_player = 1
    board = game.getInitBoard()
    it = 0
    game_ended = 0
    terminal_state_adjudication = None

    while game_ended == 0:
        it += 1

        action = players[current_player + 1](game.getCanonicalForm(board, current_player))

        valid_moves = game.getValidMoves(game.getCanonicalForm(board, current_player), 1)

        if valid_moves[action] == 0:
            print(f'Action {action} is not valid!')
            print(f'valid_moves = {valid_moves}')
            assert valid_moves[action] > 0

        board, current_player = game.getNextState(board, current_player, action)
        game_ended, terminal_state_adjudication = game.getGameEnded(board, current_player)

    return current_player * game_ended, terminal_state_adjudication


def competition_worker(args, graph_args, games_per_worker):

    game = TangledGame(graph_args=graph_args,
                       fixed_token_game=args["fixed_token_game"])

    champ_model = load_model_and_optimizer(board_size=graph_args["get_board_size"],
                                           action_size=graph_args["get_action_size"],
                                           graph_number=graph_args["graph_number"],
                                           filepath=os.path.join(args["checkpoints"], 'best.pth'))

    challenger_model = load_model_and_optimizer(board_size=graph_args["get_board_size"],
                                                action_size=graph_args["get_action_size"],
                                                graph_number=graph_args["graph_number"],
                                                filepath=os.path.join(args["checkpoints"], 'challenger.pth'))

    champ_model.eval()  # Set the model to evaluation mode
    challenger_model.eval()  # Set the model to evaluation mode

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    champ_model.to(device)
    challenger_model.to(device)

    champ_mcts = AZ_MCTS(game, champ_model, args)
    challenger_mcts = AZ_MCTS(game, challenger_model, args)

    player1 = lambda x: np.argmax(champ_mcts.get_action_prob(x, temp=0, self_play=False, add_dirichlet_noise=False))
    player2 = lambda x: np.argmax(challenger_mcts.get_action_prob(x, temp=0, self_play=False, add_dirichlet_noise=False))

    worker_data_red = []
    worker_data_blue = []
    terminal_state_adjudications = []

    for _ in range(games_per_worker):
        r, tsa = play_game(game, player1, player2)
        worker_data_red.append(r)
        terminal_state_adjudications.append(tsa)
        r, tsa = play_game(game, player2, player1)
        worker_data_blue.append(r)
        terminal_state_adjudications.append(tsa)

    del champ_model
    del challenger_model
    torch.cuda.empty_cache()

    terminal_state_adjudications += champ_mcts.terminal_state_adjudications
    terminal_state_adjudications += challenger_mcts.terminal_state_adjudications

    return [worker_data_red, worker_data_blue], terminal_state_adjudications


def parallel_competitive_play(args, graph_args):
    num_workers = args["num_workers"]
    games_per_worker = args["arenaCompare"] // num_workers

    print(f'beginning parallel competitive play with {num_workers} workers...')
    start_parallel_competitive_play = time.time()

    competition_data = []
    terminal_state_adjudications = []
    completed_workers = 0
    failed_workers = 0

    try:
        with ProcessPoolExecutor(max_workers=args["num_workers"]) as executor:
            futures = [executor.submit(competition_worker, args, graph_args, games_per_worker)
                       for _ in range(args["num_workers"])]

            for future in as_completed(futures):
                try:
                    result = future.result(timeout=600)  # Add timeout to prevent hanging
                    competition_data.append(result[0])
                    terminal_state_adjudications += result[1]    # append here cuz just one adjudication
                    completed_workers += 1
                except process.BrokenProcessPool as e:
                    print(f"Process pool broke: {e}")
                    failed_workers += 1
                    break  # Break out of loop since the pool is broken
                except Exception as e:
                    print(f"Worker failed with error: {type(e).__name__}: {e}")
                    failed_workers += 1

    except process.BrokenProcessPool as e:
        print(f"Process pool broke during creation or execution: {e}")

    finally:
        duration = time.time() - start_parallel_competitive_play
        print(f'Parallel competitive play completed with {completed_workers}/{num_workers} workers')
        print(f'Failed workers: {failed_workers}')
        print(f'It took {duration:.2f} seconds.')

        # Display warning if no data was collected
        if len(competition_data) == 0:
            print("WARNING: No competition data was collected. Check worker logs for errors.")
        else:
            # number of workers returned * 2 (blue/red) * games per worker
            games_completed = len(competition_data) * len(competition_data[0]) * len(competition_data[0][0])
            print(f"Collected data from {games_completed} champ vs challenger games")

    return competition_data, terminal_state_adjudications
