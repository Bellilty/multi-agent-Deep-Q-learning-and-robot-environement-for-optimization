import gym
import numpy as np
from Config import EnvConfig
from utils import generate_bernouli_sample, generate_normal_sample
from Actions import Action
from State import State
from Modelization import Modelization



class RestaurantEnv(gym.Env):
    def __init__(self, config:EnvConfig):
        super(RestaurantEnv, self).__init__()
        self.config = config
        self.customer_list = []
        self.robot_dict = dict()
        self.modelization = Modelization(self.robot_dict, self.config.time_render)

        for i in range(0, self.config.Max_customer):
            self.customer_list.append("customer_" + str(i))

        for i in range(0, self.config.CookerRobot_num):
            self.robot_dict["robot_" + str(i)] = "cooker_robot"

        for i in range(self.config.CookerRobot_num, self.config.CookerRobot_num + self.config.WaiterRobot_num):
            self.robot_dict["robot_" + str(i)] = "waiter_robot"

        self.robot_list = list(self.robot_dict.keys())
        self.global_satisfaction = 0.5
        self.state = State(self.robot_dict, self.customer_list, self.config)
        self.observation_space = self.state.observable_space
        self.Action = Action(self.config, self.robot_dict, self.customer_list)
        self.action_space = self.Action.action_space
        self.reset()


    def initialize_customer_satisfaction(self, train=False):
        """
        Create the first satisfaction rate of each customer with a rate of 0.5
        :param customer_list:
        :return: the first instance of the satisfaction dictionary
        """
        customer_satisfaction = {}
        for customer in self.customer_list:
            if train == False:
                customer_satisfaction[customer] = 0.5
            else:
                customer_satisfaction[customer] = 1
        return customer_satisfaction

    def start_new_day(self, train=False):

        self.Accumulated_dirt = []
        self.state.start_new_day()
        if train == True:
            self.customers_satisfaction = self.initialize_customer_satisfaction(train)
        self.scheduler = self.create_scheduler_customers()
        obs = []
        for robot in self.robot_list:
            obs.append(self.state.get_agent_observation_space(robot))
        return obs


    def compute_self_satisfaction(self, dirt_level, arrivalTime, time_served):
        """
        Compute the self satisfaction of the customer at the end of the day, more its satisfaction is great, more
        its mean satisfaction increase and more he has chances to come the next day.
        :param dirt_level: The dirt level mean during the time he was waiting
        :param arrivalTime: The arrival time in the restaurant
        :param time_served: the time the customer received its food
        :return:
        """
        k = self.config.average_waiting_time
        dirt_rate = 1 - dirt_level
        if time_served == -2:
            return 0
        else:
            waiting_time = time_served - arrivalTime
            if waiting_time <= k:
                return 1 * dirt_rate
            else:
                return (1 - waiting_time / (waiting_time + k)) * dirt_rate


    def create_scheduler_customers(self):
        """
        Create the scheduler of the day for the customer, it determine those who will come and their arrival time
        :param customer_satisfaction: the dictionary that maintains the customers satisfaction along the simulations
        :return: the scheduler of the day with the arrival time of the customers that will come
        """
        scheduler = {}
        for customer in self.customers_satisfaction.keys():
            will_come = generate_bernouli_sample(self.customers_satisfaction[customer])
            if will_come == True:
                arrival_time = int(generate_normal_sample(mean=self.config.mean_arrival_time,
                                                          std=self.config.var_arrival_time,
                                                          max_arrival_time=self.config.max_arrival_time,
                                                          average_waiting_time=self.config.average_waiting_time))
                scheduler[customer] = arrival_time
            else:
                scheduler[customer] = -1

        return scheduler


    def update_customer_satisfaction(self):
        """
        At the end of each day, we compute the satisfaction rate of the customers that came in function of the
        waiting time and the cleanness level of the restaurant
        :param customer_satisfaction: The dictionary that contains the satisfaction historic for each customer
        :param scheduler: The scheduler that indicates when the customer arrived and when it has been served
        :param accumulated_dirt: The list of accumulated dirt at each timestamp, for each customer we compute the
        accumulated dirt he saw during the time he was on the restaurant
        :return: The updated customer satisfaction historic
        """
        for customer in self.customers_satisfaction.keys():
            if self.scheduler[customer] != -1:
                arrival_time = self.scheduler[customer]
                if self.state.customer_status[customer] != 3: #mean the customer has not been served
                    time_served = -2
                    dirt_level = 1
                else:
                    time_served = self.state.customer_waiting_time[customer] + arrival_time
                    dirt_level = np.mean(self.Accumulated_dirt[arrival_time:time_served])
                self_satisfaction = self.compute_self_satisfaction(dirt_level, arrival_time, time_served)
                self.customers_satisfaction[customer] = self_satisfaction
        self.global_satisfaction = np.mean([score for score in self.customers_satisfaction.values()])



    def update_cleanness_level(self):
        """
        Update the cleaness level of the restaurant at each timestamp
        :param accumulated_dirt:
        :param dirt_at_t:
        :return:
        """
        dirt_at_t = self.state.Accumulated_Dirt
        if dirt_at_t < self.config.level_1:
            self.Accumulated_dirt.append(0)
        elif self.config.level_1 <= dirt_at_t < self.config.level_2:
            self.Accumulated_dirt.append(self.config.score_level_1)
        elif self.config.level_2 <= dirt_at_t < self.config.level_3:
            self.Accumulated_dirt.append(self.config.score_level_2)
        elif self.config.level_3 <= dirt_at_t < self.config.level_4:
            self.Accumulated_dirt.append(self.config.score_level_3)
        elif self.config.level_4 <= dirt_at_t < self.config.level_5:
            self.Accumulated_dirt.append(self.config.score_level_4)
        else:
            self.Accumulated_dirt.append(self.config.score_level_5)


    def render(self,actions=None):
        """
        Print the modelization of the environement at the current state
        :param actions:
        :return:
        """

        statistics = {'Number of delivered customers: ': self.state.get_num_customer_delivered(self.scheduler),
                      'Daily income: ': self.state.Daily_income,
                      'Accumulated dirt: ': self.state.Accumulated_Dirt,
                      'Available plate: ': self.state.Available_plate,
                      'Number of cooked Pizza: ': self.state.PizzaAvailable,
                      'Un-cooked Pizza ordred: ': self.state.non_cooked_pizza,
                      'CustomerSatisfaction mean: ': np.mean(self.global_satisfaction),
                      }

        if actions == None:
            self.modelization.draw_state(self.day, self.t, self.state.customer_status, self.state.customer_waiting_time,
                                         statistics, self.state.BatteryLevel)

        else:
            action_dict = {}
            for i in range(0, len(actions)):
                agent_type = list(self.robot_dict.values())[i]
                action_dict[self.robot_list[i]] = self.Action.actions_map[agent_type][actions[i]]

            self.modelization.draw_action_state(self.day, self.t, self.state.customer_status, self.state.customer_waiting_time,
                                                statistics, action_dict, self.state.BatteryLevel)

    def compute_reward(self, actions_robot):
        """
        Compute the reward of a global observatin space for every robot
        :return:
        """
        robot_reward = []
        for i, robot in enumerate(self.robot_list):
            robot_reward.append(self.state.give_robot_reward(robot, actions_robot[i]))
        return robot_reward


    def reset(self):
        """
        Reset the environement and reinitialize it
        :return:
        """
        self.state.initialize()
        self.customers_satisfaction = self.initialize_customer_satisfaction()
        self.scheduler = self.create_scheduler_customers()
        self.day = 0
        self.t = 0


    def step(self, actions_robots):
        """
        Execute a step, execute the action and change the current state of the world
        :param actions_robots:
        :return:
        """
        reward = self.compute_reward(actions_robots)
        for i in range(0, len(actions_robots)):
            self.state = self.Action.execute_action(self.state, self.robot_list[i], actions_robots[i])

        self.scheduler = self.state.update_customers_state(self.scheduler, self.t)
        self.update_cleanness_level()

        obs = []
        for robot in self.robot_list:
            obs.append(self.state.get_agent_observation_space(robot))

        if self.t == self.config.max_arrival_time:
            self.update_customer_satisfaction()
            global_satisfaction_reward = [self.global_satisfaction*100 for robot in self.robot_list]
            reward = global_satisfaction_reward
            done = True
        else:
            done = False

        return obs, reward, done

    def compute_efficiency(self):
        """
        Compute the efficiency of the restaurant at the end of the day, an efficiency of 100% means that every customers
        succed to get their order
        :return:
        """
        customer_total = 0
        custumer_served = 0
        for customer in self.customer_list:
            if self.scheduler[customer] != -1:
                customer_total += 1
                if self.state.customer_status[customer] == 3:
                    custumer_served += 1
        return (custumer_served/customer_total)*100, customer_total




if __name__ == "__main__":
    config = EnvConfig()

    env = RestaurantEnv(config)
    env.start_new_day()
    env.render()










