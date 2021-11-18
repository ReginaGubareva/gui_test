import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np


class PolicyNetwork(nn.Module):
    def __init__(self, ALPHA, input_dims, output_dims, fc1_dims, fc2_dims,
                 n_actions):
        super(PolicyNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.output_dims = output_dims
        self.fc1 = nn.Linear(*self.input_dims, self.fc1_dims)
        self.fc2 = nn.Linear(self.fc1_dims, self.fc2_dims)
        self.fc3 = nn.Linear(self.fc2_dims, 10)
        self.optimizer = optim.Adam(self.parameters(), lr=ALPHA)

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')
        self.to(self.device)

    def forward(self, observation):
        # print('observation', observation)
        state = T.tensor(observation).float().to(self.device)
        # print('state:', state)
        x = F.relu(self.fc1(state))
        print('fc1 x:', x)
        x = F.relu(self.fc2(x))
        print('fc2 x:', x)
        x = self.fc3(x)
        print('fc3 x:', x)
        return x


class PolicyGradientAgent(object):
    def __init__(self, ALPHA, input_dims, output_dims, GAMMA=0.99, n_actions=2,
                 layer1_size=256, layer2_size=256):
        self.gamma = GAMMA
        self.reward_memory = []
        self.action_memory = []
        self.policy = PolicyNetwork(ALPHA, input_dims, output_dims, layer1_size, layer2_size,
                                    n_actions)

    def choose_action(self, observation):
        # print('observation', self.policy.forward(observation))
        probabilities = F.softmax(self.policy.forward(observation), dim=0)
        # print('probabilities', probabilities)
        action_probs = T.distributions.Categorical(probabilities)
        print('action probs shape: ', action_probs.__sizeof__())
        action = action_probs.sample()
        log_probs = action_probs.log_prob(action)
        self.action_memory.append(log_probs)
        print('aciton:', action)
        return action.item()

    def store_rewards(self, reward):
        self.reward_memory.append(reward)

    def learn(self):
        self.policy.optimizer.zero_grad()
        # Assumes only a single episode for reward_memory
        G = np.zeros_like(self.reward_memory, dtype=np.float64)
        for t in range(len(self.reward_memory)):
            G_sum = 0
            discount = 1
            for k in range(t, len(self.reward_memory)):
                G_sum += self.reward_memory[k] * discount
                discount *= self.gamma
            G[t] = G_sum
        mean = np.mean(G)
        std = np.std(G) if np.std(G) > 0 else 1
        G = (G - mean) / std

        G = T.tensor(G, dtype=T.float).to(self.policy.device)

        loss = 0
        for g, logprob in zip(G, self.action_memory):
            loss += -g * logprob

        loss.backward()
        self.policy.optimizer.step()

        self.action_memory = []
        self.reward_memory = []