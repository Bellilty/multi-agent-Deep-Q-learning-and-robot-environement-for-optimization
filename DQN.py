import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import copy
import random
import os
from Config import EnvConfig


class QNetwork(nn.Module):
    def __init__(self, observation_space, action_space):
        super(QNetwork, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(observation_space, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_space),
        )

    def forward(self, x):
        return self.layers(x)


class DeepQLearning_MultiAgent:
    def __init__(self, observation_spaces, action_spaces, robot_list, config: EnvConfig, device, target_update=10, learning_rate=0.001):
        self.observation_spaces = observation_spaces
        self.robot_list = robot_list
        self.action_spaces = action_spaces
        self.config = config
        self.Robot_brains = [QNetwork(observation_spaces[robot].shape[0], action_spaces[robot].n) for robot in robot_list]
        self.Robot_brains_target = copy.deepcopy(self.Robot_brains)
        self.learning_rate = learning_rate
        self.optimizers = [optim.Adam(self.Robot_brains[i].parameters(), lr=self.learning_rate) for i in range(len(self.Robot_brains))]
        self.target_update = target_update
        self.buffer_memory = {}
        self.device = device
        for i in range(0, len(self.Robot_brains)):
            self.Robot_brains[i] = self.Robot_brains[i].to(self.device)
            self.Robot_brains_target[i] = self.Robot_brains_target[i].to(self.device)


    def predict(self, observations, explore=True, epsilon=0.0, target=False):
        Q_scores = []
        for i, robot in enumerate(self.robot_list):
            if explore == True and random.random() < epsilon:
                q_value = np.random.rand(self.action_spaces[robot].n)
                Q_scores.append(q_value)
            else:
                with torch.no_grad():
                    x = torch.tensor(observations[i], dtype=torch.float32)
                    x = x.to(self.device)
                    if target == False:
                        q_value = self.Robot_brains[i](x)
                    else:
                        q_value = self.Robot_brains_target[i](x)
                    del x
                    Q_scores.append(q_value)
        return Q_scores


    def learn(self, day, timestamp, observations, actions, next_observations, reward, gamma = 0.99):


        if day not in self.buffer_memory.keys():
            self.buffer_memory[day] = [[], [], [], []]
        self.buffer_memory[day][0].append([torch.tensor(observations[i]) for i in range(len(observations))])
        self.buffer_memory[day][1].append([torch.tensor(actions[i]) for i in range(len(actions))])
        self.buffer_memory[day][2].append([torch.tensor(next_observations[i]) for i in range(len(next_observations))])
        self.buffer_memory[day][3].append(reward)

        if day == self.config.day_in_year and timestamp == self.config.max_arrival_time:
            for index in self.buffer_memory.keys():
                batch_observations = self.buffer_memory[index][0]
                batch_actions = self.buffer_memory[index][1]
                batch_next_observations = self.buffer_memory[index][2]
                batch_reward = self.buffer_memory[index][3]

                q_values = {}
                for robot in self.robot_list:
                    q_values[robot] = []

                for i, observation in enumerate(batch_observations):
                    Q_scores = self.predict(observation, explore=False, target=False)
                    for j, q_val in enumerate(Q_scores):
                       max_q_val = q_val[batch_actions[i][j]]
                       q_values[self.robot_list[j]].append(max_q_val.item())

                target_q_values = {}
                for robot in self.robot_list:
                    target_q_values[robot] = []
                for i, n_observation in enumerate(batch_next_observations):
                    next_Q_score = self.predict(n_observation, target=True, explore=False)
                    for j, next_q_val in enumerate(next_Q_score):
                       max_next_q_val = next_q_val.max(0)[0]
                       target_q_values[self.robot_list[j]].append(batch_reward[i][j] + gamma * max_next_q_val.item())

                for i, model in enumerate(self.Robot_brains):
                    q_val = torch.tensor(q_values[self.robot_list[i]], requires_grad=True)
                    target_q_val = torch.tensor(target_q_values[self.robot_list[i]], requires_grad=True)
                    target_q_val = target_q_val.float()
                    q_val = q_val.to(self.device)
                    target_q_val = target_q_val.to(self.device)
                    loss = nn.MSELoss()(q_val, target_q_val)
                    self.optimizers[i].zero_grad()
                    loss.backward()
                    self.optimizers[i].step()
                    if index%self.target_update == 0:
                         self.Robot_brains_target[i].load_state_dict(self.Robot_brains[i].state_dict())
                    del q_val
                    del target_q_val
            self.buffer_memory = {}


    def save_state_dict(self):
        for i in range(0, len(self.Robot_brains)):
            torch.save(self.Robot_brains[i].state_dict(), "models/Models_robot" +str(i) + ".pt")

    def load_state_dict(self):
        for i in range(0, len(self.Robot_brains)):
            self.Robot_brains[i].load_state_dict(torch.load("models/Models_robot" +str(i) + ".pt", map_location=torch.device('cpu')))















