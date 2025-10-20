import math
import numpy as np


class AZ_MCTS(object):
    """ This class handles the AlphaZero MCTS tree """

    def __init__(self, game, neural_net, args, verbose=False):
        self.game = game
        self.neural_net = neural_net
        self.args = args
        self.verbose = verbose

        self.Qsa = {}  # stores Q values for (s,a) (as defined in the paper)
        self.Nsa = {}  # stores # times edge (s,a) was visited
        self.Ns = {}  # stores # times board s was visited
        self.Ps = {}  # stores initial policy (returned by neural net)
        self.Es = {}  # stores game.getGameEnded ended for board s
        self.Vs = {}  # stores game.getValidMoves for board s

        self.terminal_state_adjudications = []   # stores all terminal state adjudications performed

        # dirichlet noise parameters
        self.did_I_apply_noise_to_s = {}
        self.epsilon = 0.25
        self.alpha = 0.2

    def get_action_prob(self, canonical_board, temp=1, self_play=True, add_dirichlet_noise=True):
        """
        This function performs numMCTSSims simulations of MCTS starting from canonicalBoard.

        Returns:
            probs: a policy vector where the probability of the ith action is proportional to Nsa[(s,a)]**(1./temp)
        """

        if self_play:
            num_sims = self.args["numMCTSSimsSelf"]
        else:
            num_sims = self.args["numMCTSSimsComp"]

        for i in range(num_sims):
            self.search(canonical_board, first_call=True, add_dirichlet_noise_internal=add_dirichlet_noise)
            if self.verbose:
                print('sim # ' + str(i) + ' is done.')

        s = self.game.stringRepresentation(canonical_board)
        counts = [self.Nsa[(s, a)] if (s, a) in self.Nsa else 0 for a in range(self.game.getActionSize())]

        if self.verbose:
            print('counts: ' + str(counts))

        if temp == 0:
            best_actions = np.array(np.argwhere(counts == np.max(counts))).flatten()
            best_action = np.random.choice(best_actions)
            probs = [0] * len(counts)
            probs[best_action] = 1

        else:
            counts = [x ** (1. / temp) for x in counts]
            counts_sum = float(sum(counts))
            probs = [x / counts_sum for x in counts]

        if self.verbose:
            print('policy vector:', probs)

        return probs

    def search(self, canonical_board, first_call=False, add_dirichlet_noise_internal=True):
        """
        This function performs one iteration of MCTS. It is recursively called
        till a leaf node is found. The action chosen at each node is one that
        has the maximum upper confidence bound as in the paper.

        Once a leaf node is found, the neural network is called to return an
        initial policy P and a value v for the state. This value is propagated
        up the search path. In case the leaf node is a terminal state, the
        outcome is propagated up the search path. The values of Ns, Nsa, Qsa are
        updated.

        NOTE: the return values are the negative of the value of the current
        state. This is done since v is in [-1,1] and if v is the value of a
        state for the current player, then its value is -v for the other player.

        Returns:
            v: the negative of the value of the current canonicalBoard
        """

        s = self.game.stringRepresentation(canonical_board)

        # first step: is s an already visited state? If not, add it to visited state list, and ask if it is terminal
        if s not in self.Es:
            self.Es[s], tsa = self.game.getGameEnded(canonical_board, 1)
            if tsa is not None:
                self.terminal_state_adjudications.append(tsa)

        if self.Es[s] != 0:     # if it is a terminal node, return reward; this search iteration is done
            return -self.Es[s]

        if s not in self.Ps:
            # leaf node
            # currently canonical_board is an ndarray (9,)
            # this returns self.Ps[s] as an ndarray (9,) and v as a numpy float32
            self.Ps[s], v = self.neural_net.inference(np.expand_dims(canonical_board, axis=1))

            valid_moves = self.game.getValidMoves(canonical_board, 1)
            self.Ps[s] = self.Ps[s] * valid_moves  # masking invalid moves
            sum_Ps_s = np.sum(self.Ps[s])

            if sum_Ps_s > 0:
                self.Ps[s] /= sum_Ps_s  # renormalize
            else:
                # if all valid moves were masked make all valid moves equally probable
                # NB! All valid moves may be masked if either your NNet architecture is insufficient or you've got overfitting or something else.
                # If you have got dozens or hundreds of these messages you should pay attention to your NNet and/or training process.
                print("All valid moves were masked, doing a workaround.")
                self.Ps[s] = self.Ps[s] + valid_moves
                self.Ps[s] /= np.sum(self.Ps[s])

            self.Vs[s] = valid_moves
            self.Ns[s] = 0

            return -v

        if first_call and s not in self.did_I_apply_noise_to_s and add_dirichlet_noise_internal:
            self.Ps[s] = ((1 - self.epsilon) * self.Ps[s] + self.epsilon * np.random.dirichlet([self.alpha] * len(self.Ps[s])))
            self.did_I_apply_noise_to_s[s] = True

        valid_moves = self.Vs[s]
        cur_best = -float('inf')
        best_act = -1

        # pick the action with the highest upper confidence bound
        for a in range(self.game.getActionSize()):
            if valid_moves[a]:
                if self.verbose:
                    print('trying move ', a)

                if (s, a) in self.Qsa:
                    u = self.Qsa[(s, a)] + self.args["cpuct"] * self.Ps[s][a] * math.sqrt(self.Ns[s]) / (
                            1 + self.Nsa[(s, a)])
                    if self.verbose:
                        print('gives puct ', u)
                else:
                    u = self.args["cpuct"] * self.Ps[s][a] * math.sqrt(self.Ns[s] + 1e-8)  # Q = 0 ?
                    if self.verbose:
                        print('gives puct ', u)

                if u > cur_best:
                    cur_best = u
                    best_act = a

        a = best_act
        if self.verbose:
            print('picked action:', a, 'with u of', cur_best)

        next_s, next_player = self.game.getNextState(canonical_board, 1, a)
        next_s = self.game.getCanonicalForm(next_s, next_player)

        if self.verbose:
            print('now in state', next_s)

        # as this is a recursive call, by defn not a root and therefore first_call=False
        v = self.search(next_s, first_call=False, add_dirichlet_noise_internal=False)

        if self.verbose:
            print(' from recursive search v=', v)
            print('adding v to Q and augmenting Nsa')
        if (s, a) in self.Qsa:
            self.Qsa[(s, a)] = (self.Nsa[(s, a)] * self.Qsa[(s, a)] + v) / (self.Nsa[(s, a)] + 1)
            self.Nsa[(s, a)] += 1

        else:
            self.Qsa[(s, a)] = v
            self.Nsa[(s, a)] = 1

        self.Ns[s] += 1

        return -v
