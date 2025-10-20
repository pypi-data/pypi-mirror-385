""" utility files for tangled-alphazero """
import os
import torch
import glob
import re
import numpy as np
import pickle
from pickle import Pickler

from snowdrop_tangled_alphazero.neural_net.AlphaZeroNet import AlphaZeroNet


def find_most_recent_checkpoint(directory_path="."):
    """
    Find the most recent checkpoint file matching pattern 'checkpoint_*.pth.examples'
    where * is an integer.

    Args:
        directory_path (str): Directory to search in (default: current directory)

    Returns:
        str or None: Path to the most recent matching file, or None if no files found
    """
    # Create the search pattern
    pattern = os.path.join(directory_path, "checkpoint_*.pth.examples")

    # Find all files matching the pattern
    matching_files = glob.glob(pattern)

    # Filter to ensure the * part is actually an integer
    valid_files = []
    for file_path in matching_files:
        filename = os.path.basename(file_path)
        # Extract the part between 'checkpoint_' and '.pth.examples'
        match = re.match(r'checkpoint_(\d+)\.pth\.examples$', filename)
        if match:
            valid_files.append(file_path)

    if not valid_files:
        return None

    # Find the most recent file based on modification time
    most_recent_file = max(valid_files, key=os.path.getmtime)

    return most_recent_file


def find_most_recent_adjudications(directory_path="."):
    """
    Find the most recent adjudications file matching pattern 'adjudications_*.pkl'
    where * is an integer.

    Args:
        directory_path (str): Directory to search in (default: current directory)

    Returns:
        str or None: Path to the most recent matching file, or None if no files found
    """
    # Create the search pattern
    pattern = os.path.join(directory_path, "adjudications.pkl")

    # Find all files matching the pattern
    matching_files = glob.glob(pattern)

    # Filter to ensure the * part is actually an integer
    valid_files = []
    for file_path in matching_files:
        filename = os.path.basename(file_path)
        # Extract the part between 'checkpoint_' and '.pth.examples'
        match = re.match(r'adjudications.pkl$', filename)
        if match:
            valid_files.append(file_path)

    if not valid_files:
        return None

    # Find the most recent file based on modification time
    most_recent_file = max(valid_files, key=os.path.getmtime)

    return most_recent_file


def load_train_examples(folder):
    """Load the train_examples_history using pickle.load()"""
    path_to_data_file = find_most_recent_checkpoint(directory_path=folder)
    print('Loading previous self-play games from:', path_to_data_file)

    try:
        with open(path_to_data_file, "rb") as f:
            train_examples_history = pickle.load(f)
        return train_examples_history
    except Exception as e:
        print(f"Error loading {path_to_data_file}: {e}")
        return None


def load_terminal_state_adjudications(folder):
    """Load the terminal_state_adjudications_history using pickle.load()"""
    path_to_data_file = find_most_recent_adjudications(directory_path=folder)
    print('Loading previous terminal state adjudications from:', path_to_data_file)

    try:
        with open(path_to_data_file, "rb") as f:
            terminal_state_adjudications_history = pickle.load(f)
        return terminal_state_adjudications_history
    except Exception as e:
        print(f"Error loading {path_to_data_file}: {e}")
        return None


def save_train_examples(iteration, train_examples_history, folder):

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, 'checkpoint_' + str(iteration) + '.pth.examples')

    with open(filename, "wb+") as f:
        Pickler(f).dump(train_examples_history)


def save_terminal_state_adjudication_examples(terminal_state_adjudications_history, folder):

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, 'adjudications.pkl')

    with open(filename, "wb+") as f:
        Pickler(f).dump(terminal_state_adjudications_history)


def save_model_and_optimizer(model, filepath):
    # Save current model and optimizer states
    torch.save(
        {
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': model.optimizer.state_dict()
        }, filepath)

    # print(f"Model and optimizer saved to {filepath}")


def load_model_and_optimizer(board_size, action_size, graph_number, filepath, verbose=False):
    # Detect device (GPU if available, otherwise CPU)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if verbose:
        print('loading model using:', device)

    # Load checkpoint with map_location to handle GPU/CPU
    checkpoint = torch.load(filepath, map_location=device, weights_only=False)

    model = AlphaZeroNet(board_size=board_size, action_size=action_size, graph_number=graph_number)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

    # Move model to the detected device
    model = model.to(device)

    # print(f"Model and optimizer loaded from {filepath} on {device}")

    return model


def convert_to_az_board(my_board, vertex_count):
    # my_board should be a list of length N+E, like [0,0,0,0,0,0] or [1,2,0,2,3,1]

    vertex_state = my_board[:vertex_count]
    edge_state = my_board[vertex_count:]

    new_vertex_state = []
    for each in vertex_state:
        if each == 2:
            new_vertex_state.append(-1)
        else:
            new_vertex_state.append(each)

    new_edge_state = []
    for each in edge_state:
        if each == 0:
            new_edge_state += [0, 0, 0]
        if each == 1:
            new_edge_state += [1, 0, 0]
        if each == 2:
            new_edge_state += [0, 1, 0]
        if each == 3:
            new_edge_state += [0, 0, 1]

    # returns np.array of length N+3*E, like [0,0,0, 0,0,0, 0,0,0, 0,0,0]
    #     # or [1,-1,0, 0,1,0, 0,0,1, 1,0,0]
    return np.array(new_vertex_state + new_edge_state)


def convert_from_az_board(az_board, vertex_count):
    # az_board should be np.array of length N+3*E, like [0,0,0, 0,0,0, 0,0,0, 0,0,0]
    # or [1,-1,0, 0,1,0, 0,0,1, 1,0,0]

    az_board_list = list(az_board)

    vertex_state = az_board_list[:vertex_count]
    edge_state = az_board_list[vertex_count:]

    my_vertex_state = []
    for each in vertex_state:
        if each == -1:
            my_vertex_state.append(2)
        else:
            my_vertex_state.append(int(each))

    edge_groups = [edge_state[3 * k:3 * (k + 1)] for k in range(int(len(edge_state) / 3))]

    my_edge_state = []
    for each in edge_groups:  # each is a list of three bits like [0,1,0]
        if sum(each) == 0:
            edge_int = 0
        else:
            edge_int = 1 + each.index(1)

        my_edge_state.append(edge_int)

    return my_vertex_state + my_edge_state   # should be a list length N+E like [0,0,0,0,0,0] or [1,2,0,2,3,1]


def get_symmetries(board, policy, automorph_list, vertex_count, edge_list, fixed_token_game, verbose=False):

    # returns two lists of lists, each of length (# of automorphisms)
    # returned lists include the original state and policy as the 0th element of each
    # they look like these:
    # here are all 6 new states: [[-1, 0, 1, 1, 3, 2], [-1, 1, 0, 3, 1, 2], [0, -1, 1, 1, 2, 3], [0, 1, -1, 2, 1, 3], [1, -1, 0, 3, 2, 1], [1, 0, -1, 2, 3, 1]]
    # here are all 6 new policies: [[0.001, 0.101, 0.201, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.1, 0.11], [0.001, 0.201, 0.101, 0.6, 0.7, 0.8, 0.3, 0.4, 0.5, 0.9, 0.1, 0.11], [0.101, 0.001, 0.201, 0.3, 0.4, 0.5, 0.9, 0.1, 0.11, 0.6, 0.7, 0.8], [0.101, 0.201, 0.001, 0.6, 0.7, 0.8, 0.9, 0.1, 0.11, 0.3, 0.4, 0.5], [0.201, 0.001, 0.101, 0.9, 0.1, 0.11, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8], [0.201, 0.101, 0.001, 0.9, 0.1, 0.11, 0.6, 0.7, 0.8, 0.3, 0.4, 0.5]]

    token_for_red = 1
    token_for_blue = -1   # either 2 or -1

    board = list(board)

    only_vertices = board[:vertex_count]
    all_edges_in_alphazero_format = board[vertex_count:]   # list of len(graph.edge_list * 3)
    # there are 3 bits per edge in this format; convert to ints

    # 0,0,0 --> unselected edge (original encoding 0)
    # 1,0,0 --> set to zero coupling (original encoding 1)
    # 0,1,0 --> set to FM coupling (original encoding 2)
    # 0,0,1 --> set to AFM coupling (original encoding 3)

    # I think this does the map from three bit --> int edge encoding
    only_edges = []
    for k in range(len(edge_list)):
        three_bits_as_a_list = all_edges_in_alphazero_format[k * 3:k * 3 + 3]
        if sum(three_bits_as_a_list) == 0:
            resultant_int = 0
        else:
            resultant_int = 1 + three_bits_as_a_list.index(1)
        only_edges.append(resultant_int)

    # in fixed token variant, red_vertex_index and blue_vertex_index are the two fixed indices
    if token_for_red in only_vertices:
        red_vertex_index = only_vertices.index(token_for_red)
    else:
        red_vertex_index = None

    if token_for_blue in only_vertices:
        blue_vertex_index = only_vertices.index(token_for_blue)
    else:
        blue_vertex_index = None

    edge = np.zeros((vertex_count, vertex_count))
    new_edge = np.zeros((vertex_count, vertex_count))

    cnt = 0
    for each in edge_list:
        edge[each[0], each[1]] = only_edges[cnt]
        cnt += 1

    policy_vert = policy[:vertex_count]
    policy_edges = policy[vertex_count:]

    list_of_symmetrical_tuples = []

    if fixed_token_game:
        # in fixed token variant, we only want the automorphs that preserve red and blue index locations
        automorph_list_to_use = []
        for each in automorph_list:
            if each[red_vertex_index] == red_vertex_index and each[blue_vertex_index] == blue_vertex_index:
                automorph_list_to_use.append(each)
        if verbose:
            print('Original graph has', len(automorph_list), 'symmetries, fixed token variant has', len(automorph_list_to_use))
    else:
        automorph_list_to_use = automorph_list

    for automorph in automorph_list_to_use:
        if verbose:
            print('')
            print('this is for the following automorphism:', automorph)
            print('***************************************')
        new_vert = [0]*vertex_count

        if red_vertex_index is not None:
            new_red_vertex_index = automorph[red_vertex_index]
            new_vert[new_red_vertex_index] = token_for_red

        if blue_vertex_index is not None:
            new_blue_vertex_index = automorph[blue_vertex_index]
            new_vert[new_blue_vertex_index] = token_for_blue

        new_policy_vert = np.zeros(vertex_count)

        for k in range(vertex_count):
            new_policy_vert[automorph[k]] = policy_vert[k]

        if verbose:
            print('vert:', only_vertices)
            print('new vert:', new_vert)

            print('policy_vert:', policy_vert)
            print('new_policy_vert:', new_policy_vert)

        for j in range(vertex_count):
            for i in range(j):
                if automorph[i] < automorph[j]:
                    new_edge[automorph[i], automorph[j]] = edge[i, j]
                else:
                    new_edge[automorph[j], automorph[i]] = edge[i, j]

        cnt = 0
        edge_dict = {}
        edge_block = {}
        for each in edge_list:
            edge_dict[each] = only_edges[cnt]
            edge_block[each] = policy_edges[cnt*3:cnt*3+3]
            cnt += 1

        # works for graphs 2 & 3 & 4

        if verbose:
            print('edge blocks:', edge_block)

        # for each edge, map each index under automorph
        new_edge_dict = {}
        new_policy_edges = []
        for each in edge_list:
            smaller = min(automorph[each[0]], automorph[each[1]])
            bigger = max(automorph[each[0]], automorph[each[1]])
            new_edge_dict[(smaller, bigger)] = edge_dict[each]
            new_policy_edges += edge_block[(smaller, bigger)]
        sorted_dict = dict(sorted(new_edge_dict.items()))
        keys_in_order = [value for key, value in sorted_dict.items()]

        new_policy_under_automorph = list(new_policy_vert) + new_policy_edges

        # need to convert back to alphazero 3-bit encoding now
        three_bit_edges = []
        for each in keys_in_order:
            if each == 0:
                three_bit_edges += [0, 0, 0]
            if each == 1:
                three_bit_edges += [1, 0, 0]
            if each == 2:
                three_bit_edges += [0, 1, 0]
            if each == 3:
                three_bit_edges += [0, 0, 1]

        new_state_under_automorph = np.array(new_vert + three_bit_edges)

        list_of_symmetrical_tuples.append((new_state_under_automorph, new_policy_under_automorph))

        if verbose:
            print('old edges:', only_edges)
            print('new edges:', keys_in_order)

            print('previous state:', board)
            print('new state under automorph:', new_state_under_automorph)

            print('old policy:', policy)
            print('new policy:', new_policy_under_automorph)

    return list_of_symmetrical_tuples
