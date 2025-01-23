from Config import EnvConfig
from Environement import RestaurantEnv
from utils import find_best_possible_action
from DQN import DeepQLearning_MultiAgent
import os
import numpy as np
import torch

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['KMP_DUPLICATE_LIB_OK']='True'
TRAINING_YEAR = 10000

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
epsilon = 1.0
epsilon_decay = 0.00005
epsilon_min = 0.1


def train_for_year(env, model, epsilon, render=False):
    """
    Train the model for a year
    :param env:
    :param model:
    :param epsilon:
    :param render:
    :return:
    """
    statistic_dict = {'reward':[], 'incomes':[]}
    env.reset()
    for day in range(0, env.config.day_in_year+1):
        env.day = day
        if day%10==0:
            print("day : " + str(day))
        obs = env.start_new_day(train=True)
        for t in range(0, env.config.max_arrival_time+1):
            env.t = t
            if render == True:
               env.render()
            actions_robot_score = model.predict(obs, epsilon=epsilon)
            action_chosen = []
            for i, actions_score in enumerate(actions_robot_score):
                possible_actions = env.Action.give_possible_actions(env.state, env.robot_list[i])
                best_action = find_best_possible_action(actions_score, possible_actions)
                env.state = env.Action.lock_ressources(env.state, env.robot_list[i], best_action)
                action_chosen.append(best_action)
            if render == True:
               env.render(actions=action_chosen)
            next_obs, reward, done = env.step(action_chosen)
            model.learn(day, t, obs, action_chosen, next_obs, reward)
            obs = next_obs
        statistic_dict['incomes'].append(env.state.Daily_income)
        if day%10==0:
           print("Incomes: " + str(statistic_dict['incomes'][-1]))
           print("Global customer satisfaction: " + str(env.global_satisfaction))
           total_customer, delivered_customer = env.state.get_num_customer_delivered(env.scheduler)
           print("number of customers served is: " + str(delivered_customer) + " out of " + str(total_customer))
    return model, statistic_dict




if __name__ == "__main__":
    config = EnvConfig(dirt_dictionary=dirt_level)
    env = RestaurantEnv(config)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = DeepQLearning_MultiAgent(env.observation_space, env.action_space, env.robot_list, config, device)
    stat_of_stat = []
    for i in range(0, TRAINING_YEAR):
        print("year : " + str(i))
        epsilon = max(epsilon - epsilon_decay, epsilon_min)
        model, statistics = train_for_year(env, model, epsilon, render=False)
        print("total income of the year : " + str(sum(statistics['incomes'])))
        stat_of_stat.append(statistics)
        if i%100==0 and i != 0:
          model.save_state_dict()

    model.save_state_dict()