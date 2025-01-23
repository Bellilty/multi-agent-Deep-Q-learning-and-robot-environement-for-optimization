from Config import EnvConfig
from Environement import RestaurantEnv
from utils import find_best_possible_action
from DQN import DeepQLearning_MultiAgent
import os
import numpy as np
import torch

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK']='True'

dirt_level = {'level_1':5,
              'score_level_1': 0.2,
              'level_2':10,
              'score_level_2': 0.4,
              'level_3':15,
              'score_level_3': 0.6,
              'level_4':20,
              'score_level_4': 0.8,
              'level_5':25,
              'score_level_5': 1}

def simulate_a_day(env, model, render=True):
    """
    Simulate a random day in the restaurant
    :param env:
    :param model:
    :param render:
    :return:
    """
    obs = env.start_new_day(train=False)

    for t in range(0, env.config.max_arrival_time + 1):
        env.t = t
        if render == True:
            env.render()
        actions_robot_score = model.predict(obs, explore=False)
        action_chosen = []
        for i, actions_score in enumerate(actions_robot_score):
            possible_actions = env.Action.give_possible_actions(env.state, env.robot_list[i])
            best_action = find_best_possible_action(actions_score, possible_actions)
            env.state = env.Action.lock_ressources(env.state, env.robot_list[i], best_action)
            action_chosen.append(best_action)
        if render == True:
            env.render(actions=action_chosen)
        next_obs, reward, done = env.step(action_chosen)
        obs = next_obs
    print("Daily income: " + str(env.state.Daily_income))
    print("Customer satisfaction: " + str(env.global_satisfaction))
    efficiency, number_customer = env.compute_efficiency()
    print("number of customer : " + str(number_customer))
    print("Efficiency of the service : " + str(efficiency))


if __name__ == "__main__":
    config = EnvConfig(dirt_dictionary=dirt_level)
    env = RestaurantEnv(config)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = DeepQLearning_MultiAgent(env.observation_space, env.action_space, env.robot_list, config, device)
    model.load_state_dict()
    stat_of_stat = []
    for i in range(0, config.day_in_year):
        print("day : " + str(i))
        simulate_a_day(env, model, render=True)







  


