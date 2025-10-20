""" implements a residual network with policy and value heads"""
import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F   # stateless torch functions

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# suggests num_channels=256, num_res_blocks=11
class ResBlock1D(nn.Module):
    def __init__(self, num_channels):
        super().__init__()
        self.conv1 = nn.Conv1d(num_channels, num_channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm1d(num_channels)
        self.conv2 = nn.Conv1d(num_channels, num_channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm1d(num_channels)

    def forward(self, x):
        identity = x
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += identity
        out = F.relu(out)
        return out


class AlphaZeroNet(nn.Module):
    def __init__(self, board_size, action_size, graph_number, verbose=False):
        super().__init__()   # necessary to initialize nn.Module
        self.nn_args = {
            'lr': 0.0001,       # probably don't modify these unless you want to try a specific type of neural net
            'dropout': 0.1,     # start by modifying the structure of the net to be what you want and then change
            'epochs': 10,       # these parameters as appropriate
            'batch_size': 64,
            # # 1,471,055 trainable parameters
            # # 'num_channels': 64,
            # # 'num_res_blocks': 7,
            # # 'first_out_layer_size': 128,
            # # 'second_out_layer_size': 64
        }

        if graph_number in [2, 18, 19, 20]:
            self.nn_args.update(   # 34,188 trainable parameters -- for paper, used for graphs 2, 18, 19, 20
                {'num_channels': 16,
                'num_res_blocks': 2,
                'first_out_layer_size': 32,
                'second_out_layer_size': 64})

        if graph_number in [11]:
            self.nn_args.update(   # 4,002 trainable parameters -- used for graph 11
                {'num_channels': 8,
                 'num_res_blocks': 2,
                 'first_out_layer_size': 16,
                 'second_out_layer_size': 32})

        if graph_number in [12]:
            self.nn_args.update(   # 223,437 trainable parameters -- for paper, used for Moser Spindle
                {'num_channels': 32,
                 'num_res_blocks': 5,
                 'first_out_layer_size': 64,
                 'second_out_layer_size': 128})

        if graph_number in [24]:
            self.nn_args.update(   # 6,056,015 trainable parameters  -- for paper, used for mutant C_60
                {'num_channels': 128,
                 'num_res_blocks': 9,
                 'first_out_layer_size': 256,
                 'second_out_layer_size': 128})

        self.board_x: int = board_size[0]
        self.board_y: int = board_size[1]
        self.action_size: int = action_size

        self.criterion_pi = nn.KLDivLoss(reduction='batchmean')  # Use KLDivLoss for probabilities
        self.criterion_v = nn.MSELoss()

        # Initial input processing; generally recommended to set bias=False if followed by batch norm
        self.conv1 = nn.Conv1d(self.board_y, self.nn_args["num_channels"], 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm1d(self.nn_args["num_channels"])

        # Residual tower
        self.res_blocks = nn.ModuleList([
            ResBlock1D(self.nn_args["num_channels"]) for _ in range(self.nn_args["num_res_blocks"])
        ])

        # Calculate size after residual tower
        self.flat_size = self.nn_args["num_channels"] * self.board_x

        # Policy head with BatchNorm
        self.policy_fc1 = nn.Linear(self.flat_size, self.nn_args["first_out_layer_size"], bias=False)
        self.policy_bn1 = nn.BatchNorm1d(self.nn_args["first_out_layer_size"])
        self.policy_fc2 = nn.Linear(self.nn_args["first_out_layer_size"], self.action_size, bias=True)

        # Value head with BatchNorm
        self.value_fc1 = nn.Linear(self.flat_size, self.nn_args["first_out_layer_size"], bias=False)
        self.value_bn1 = nn.BatchNorm1d(self.nn_args["first_out_layer_size"])
        self.value_fc2 = nn.Linear(self.nn_args["first_out_layer_size"], self.nn_args["second_out_layer_size"], bias=False)
        self.value_bn2 = nn.BatchNorm1d(self.nn_args["second_out_layer_size"])
        self.value_fc3 = nn.Linear(self.nn_args["second_out_layer_size"], 1, bias=True)

        self.dropout = nn.Dropout(self.nn_args["dropout"])   # not being used for current net

        self.optimizer = optim.Adam(self.parameters(), lr=self.nn_args["lr"])

        self.to(device)   # Move the model to the GPU

        if verbose:
            print(self)
            print('number of trainable parameters: ', sum(p.numel() for p in self.parameters() if p.requires_grad))

    def forward(self, x):
        x = x.view(-1, self.board_y, self.board_x)  # Reshape to (batch_size, board_y, board_x)

        x = F.relu(self.bn1(self.conv1(x)))

        # Residual tower
        for block in self.res_blocks:
            x = block(x)

        x = x.view(x.size(0), -1)  # Flatten

        # Policy head
        policy = F.relu(self.policy_bn1(self.policy_fc1(x)))
        policy = self.policy_fc2(policy)
        policy = F.softmax(policy, dim=1)

        # Value head
        value = F.relu(self.value_bn1(self.value_fc1(x)))
        value = F.relu(self.value_bn2(self.value_fc2(value)))
        value = torch.tanh(self.value_fc3(value))

        return policy, value

    def train_net(self, examples):
        """
        Train the neural network using the provided examples.

        Args:
            examples (list): List of training examples, where each example is a tuple of (state, pi, v).
            state and pi should be numpy arrays, and v should be a float.
        """
        self.train()  # Set the model to training mode

        total_loss = None
        loss_v = None
        loss_pi = None

        for epoch in range(self.nn_args["epochs"]):

            for i in range(0, len(examples), self.nn_args["batch_size"]):
                batch = examples[i:i + self.nn_args["batch_size"]]
                states, target_pis, target_vs = zip(*batch)

                # Convert to tensors and move to the GPU
                states = torch.FloatTensor(np.array(states)).to(device)
                target_pis = torch.FloatTensor(np.array(target_pis)).to(device)
                target_pis = target_pis / target_pis.sum(dim=1, keepdim=True)  # Normalize
                target_vs = torch.FloatTensor(np.array(target_vs)).unsqueeze(1).to(device)   # makes it shape (batch,1) instead of (batch,) to match v

                # Zero the gradients
                self.optimizer.zero_grad()

                # Forward pass
                pi, v = self(states)   # same as self.forward(states)

                # Compute losses
                loss_pi = self.criterion_pi(torch.log(pi.clamp(min=1e-10)), target_pis)  # pi.clamp(min=1e-10)) makes all values of pi at least min for numerical stability
                loss_v = self.criterion_v(v, target_vs)
                total_loss = loss_pi + loss_v

                # Backward pass and optimization
                total_loss.backward()
                torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
                self.optimizer.step()

            print(
                f"Epoch {epoch + 1}/{self.nn_args['epochs']} |||| Total Loss: {total_loss.item()} || Policy Loss: {loss_pi.item()}, Value Loss: {loss_v.item()}")

    def inference(self, states):
        """
        Perform inference on a batch of states or a single state.

        Args:
            states (torch.Tensor or numpy.ndarray): A batch of states with shape (batch_size, board_x, board_y)
                                                   or a single state with shape (board_x, board_y).

        Returns:
            pi (torch.Tensor): Policy predictions (action probabilities) with shape (batch_size, action_size).
            v (torch.Tensor): Value predictions (expected outcomes) with shape (batch_size, 1).
        """
        self.eval()  # Set the model to evaluation mode

        with torch.no_grad():  # Disable gradient tracking
            # Convert input to a tensor if it's a numpy array
            if isinstance(states, np.ndarray):
                states = torch.FloatTensor(states)

            # Ensure the input has a batch dimension
            if states.dim() == 2:  # Shape: (board_x, board_y)
                states = states.unsqueeze(0)  # Add batch dimension -> (1, board_x, board_y)
            elif states.dim() == 3:  # Shape: (batch_size, board_x, board_y)
                pass  # Already has a batch dimension
            else:
                raise ValueError(
                    f"Input shape {states.shape} is not supported. Expected (board_x, board_y) or (batch_size, board_x, board_y).")

            # Move input to the GPU
            states = states.to(device)

            # Forward pass
            pi, v = self(states)

        # Move the tensors to the CPU and convert them to NumPy arrays
        pi_cpu = pi.cpu().numpy()
        v_cpu = v.cpu().numpy()

        return pi_cpu[0], v_cpu[0][0]   # pi_cpu[0] is ndarray (N,) and v[0][0] is float32
