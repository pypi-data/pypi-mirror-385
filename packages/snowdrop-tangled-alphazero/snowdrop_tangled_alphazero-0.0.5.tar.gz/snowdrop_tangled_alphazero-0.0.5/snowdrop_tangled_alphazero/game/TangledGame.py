""" Game subclass for Tangled """
import numpy as np
from importlib.resources import files

from snowdrop_tangled_alphazero.game.Game import Game
from snowdrop_tangled_alphazero.utilities.utilities import get_symmetries, convert_from_az_board

from snowdrop_adjudicators import SimulatedAnnealingAdjudicator, SchrodingerEquationAdjudicator
from snowdrop_special_adjudicators import (QuantumAnnealingAdjudicator, LookupTableAdjudicator, get_automorphisms,
                                           convert_state_key_to_game_state)

from snowdrop_tangled_game_engine import GraphProperties


class TangledGame(Game):
    def __init__(self, graph_args, fixed_token_game):
        super().__init__()

        # This flag tells the game to augment data using game board symmetries; default True
        self.use_symmetries = True

        self.graph_number = graph_args["graph_number"]
        gp = GraphProperties()
        self.graph_properties = gp.graph_database[self.graph_number]
        self.fixed_token_game = fixed_token_game

        data_directory = str(files('snowdrop_special_adjudicators').joinpath('data'))

        # it is possible that the adjudicator_to_use passed in here is already an adjudicator and not a label.
        if isinstance(graph_args["rollout_adjudicator"], str):   # this is if we pass in e.g. 'lookup_table'
            self.adjudicator = None
            graph_index = gp.allowed_graphs.index(graph_args["graph_number"])
            args = {'data_dir': data_directory,
                    'graph_number': self.graph_number,
                    'epsilon': gp.epsilon_values[graph_index]}

            if graph_args["rollout_adjudicator"] == 'simulated_annealing':
                self.adjudicator = SimulatedAnnealingAdjudicator()
                args.update({'num_reads': graph_args["adjudicator_args"]['num_reads']})
            else:
                if graph_args["rollout_adjudicator"] == 'quantum_annealing':
                    self.adjudicator = QuantumAnnealingAdjudicator()
                    args.update({'num_reads': graph_args["adjudicator_args"]['num_reads'],
                                 'anneal_time': graph_args["adjudicator_args"]['anneal_time'],
                                 'solver_name': 'Advantage2_system1.6'})
                else:
                    if graph_args["rollout_adjudicator"] == 'lookup_table':
                        self.adjudicator = LookupTableAdjudicator()
                    else:
                        if graph_args["rollout_adjudicator"] == 'schrodinger_equation':
                            self.adjudicator = SchrodingerEquationAdjudicator()
                            args.update({'anneal_time': graph_args["adjudicator_args"]['anneal_time']})

            self.adjudicator.setup(**args)
        else:   # this is if we pass in a fully set up adjudicator, e.g. LookupTableAdjudicator()
            self.adjudicator = graph_args["rollout_adjudicator"]

        self.vertex_count = self.graph_properties["num_nodes"]
        self.edge_list = self.graph_properties["edge_list"]
        self.bits_per_edge = 3        # (0,0,0) = unselected, (1,0,0) = zero, (0,1,0) = FM, (0,0,1) = AFM
        # this is where board size is defined
        self.board_size = self.vertex_count + self.bits_per_edge * len(self.edge_list)

        self.graph_automorphisms_list = get_automorphisms(graph_number=self.graph_number, data_dir=data_directory)

    def getInitBoard(self):
        # returns all zeros if self.fixed_token_game is False, otherwise starts with owned vertices

        initial_board = np.array([0] * self.board_size)

        if self.fixed_token_game:
            initial_board[self.graph_properties["player1_node"]] = 1       # player 1 == red
            initial_board[self.graph_properties["player2_node"]] = -1      # player 2 == blue

        return initial_board      # return initial board (numpy board)

    def getBoardSize(self):
        # this is what is passed into AlphaZeroNet
        return (self.board_size, 1)                 # Returns: (x,y): a tuple of board dimensions

    def getActionSize(self):
        return self.board_size                      # Returns: actionSize: number of all possible actions

    def getNextState(self, board, player, action):
        """ Input: board: current board; player: current player (1 or -1); action: action taken by current player
        Returns: nextBoard: board after applying action; nextPlayer: player who plays next (should be -player) """

        final_state = board.copy()

        if action < self.vertex_count:
            final_state[action] = player    # +-1
        else:
            final_state[action] = 1         # should match 1-hot encoding

        return (final_state, -player)

    def getValidMoves(self, board, player):
        """ Input: board: current board; player: current player
        Returns: validMoves: a binary vector of length self.getActionSize(), 1 for moves that are valid from the
        current board and player, 0 for invalid moves """

        valids = [0] * self.getActionSize()

        vertex_states = board[:self.vertex_count]
        edge_states = board[self.vertex_count:]

        selected_edges = [sum(edge_states[self.bits_per_edge*k:self.bits_per_edge*(k+1)])
                          for k in range(int(len(edge_states)/self.bits_per_edge))]

        number_of_unselected_edges = selected_edges.count(0)

        has_chosen_a_vertex = False
        if player in vertex_states:    # player = +1 or -1
            has_chosen_a_vertex = True

        if number_of_unselected_edges > 1:
            # if there is more than one unselected edge, players can either select a vertex if they haven't
            # already, or select an edge
            if not has_chosen_a_vertex:  # if you haven't selected a vertex you can
                for k in range(len(vertex_states)):
                    if vertex_states[k] == 0:  # unselected, could be an action
                        valids[k] = 1
            indices_of_unselected_edges = [i for i, x in enumerate(selected_edges) if x == 0]
            for each in indices_of_unselected_edges:
                for k in range(self.bits_per_edge):
                    valids[self.vertex_count + self.bits_per_edge * each + k] = 1
        else:   # in this case, exactly one unselected edge
            if not has_chosen_a_vertex:  # if you haven't selected a vertex you have to
                for k in range(len(vertex_states)):
                    if vertex_states[k] == 0:   # unselected, could be an action
                        valids[k] = 1
            else:   # you have selected a vertex, need to select an edge
                edge_to_select = selected_edges.index(0)   # will only be one
                for k in range(self.bits_per_edge):
                    valids[self.vertex_count + self.bits_per_edge * edge_to_select + k] = 1

        return np.array(valids)

    def getGameEnded(self, board, player):
        """ Input: board: current board; player: current player (1 or -1)
        Returns:  r: 0 if game has not ended. 1 if player won, -1 if player lost, small non-zero value for draw """

        # a state is terminal if both players have chosen vertices and all edges have been played

        draw_value = 0.01

        vertex_states = board[:self.vertex_count]
        edge_states = board[self.vertex_count:]
        selected_edges = [sum(edge_states[self.bits_per_edge * k:self.bits_per_edge * (k + 1)])
                          for k in range(int(len(edge_states) / self.bits_per_edge))]

        if selected_edges.count(0) == 0 and 1 in vertex_states and -1 in vertex_states:

            new_state = convert_from_az_board(board, self.vertex_count)
            game_state = convert_state_key_to_game_state(new_state, self.vertex_count, self.edge_list)

            results = self.adjudicator.adjudicate(game_state)

            winner = None

            if results['winner'] == 'red':
                winner = player  # red wins. if it's red's turn, reward = +1, if blue's turn, reward = -1
            else:
                if results['winner'] == 'blue':
                    winner = -player  # blue wins. if it's red's turn, reward = -1, if blue's turn, reward = +1
                else:
                    if results['winner'] == 'draw':
                        winner = draw_value  # draw. regardless of player, small +ive value
                    else:
                        print('something went wrong, check it out!')

            return winner, results
        else:
            return 0, None  # not terminal state, game not over

    def getCanonicalForm(self, board, player):
        """ Input: board: current board; player: current player (1 or -1)
        Returns: returns canonical form of board. The canonical form should be independent of player. For e.g. in chess,
        the canonical form can be chosen to be from the pov of white. When the player is white, we can return board as
        is. When the player is black, we can invert the colors and return the board. """
        vertex_states = board[:self.vertex_count]
        edge_states = board[self.vertex_count:]

        return np.concatenate([player*vertex_states, edge_states])

    def getSymmetries(self, board, pi):
        """ Input: board: current board; pi: policy vector of size self.getActionSize()
        Returns: a list of [(board,pi)] where each tuple is a symmetrical form of the board and the corresponding pi
        vector. This is used when training the neural network from examples """

        # for graph_number=2, board is an ndarray of length 12 and pi is a list of floats of length 12

        if self.use_symmetries:
            l = get_symmetries(board, pi,
                               self.graph_automorphisms_list,
                               self.vertex_count,
                               self.edge_list,
                               self.fixed_token_game)
            return l
        else:
            return [(board, pi)]

    def stringRepresentation(self, board):
        return board.tobytes()
        # Note: used to be board.tostring()

    @staticmethod
    def display(board):
        print(board)
