from Config import EnvConfig
import numpy as np
import gym
from gym import spaces

class State:
    def __init__(self, robot_dict:dict, customer_list:list, config:EnvConfig):
        self.robot_list = list(robot_dict.keys())
        self.robot_dict = robot_dict
        self.customer_list = customer_list
        self.config = config
        self.BatteryLevel = dict()
        self.customer_status = dict()
        self.customer_waiting_time = dict()
        self.Accumulated_Dirt = 0
        self.Daily_income = 0
        self.Available_plate = 0
        self.PizzaAvailable = 0
        self.non_cooked_pizza = 0
        self.num_agents = len(self.robot_list)
        self.lock = dict()
        self.observable_space = dict()
        for robot in self.robot_dict.keys():
            agent_type = self.robot_dict[robot]
            self.observable_space[robot] = self.create_observable_space_for_agent(agent_type)

        #observable_space = [non_cooked_pizza, Pizza_available, Accumulated_dirt, AvailablePlate, batteryRobtot, statusCustomers, waintig_time_customers]
        low_bounds = np.array([-1, -1, -1, -1] + [-1]*self.num_agents + [-1]*self.config.Max_customer + [-1]*self.config.Max_customer)
        high_bounds = np.array([self.config.Max_customer, self.config.Max_customer, 200,
                                self.config.total_number_plate] + [self.config.max_battery]*self.num_agents
                               + [3]*self.config.Max_customer + [self.config.max_arrival_time]*self.config.Max_customer)
        self.General_observable_space = gym.spaces.Box(low=low_bounds, high=high_bounds, dtype=np.int32)

    def initialize(self):
        """
        Initialize the fluents of the environement
        :return:
        """
        self.PizzaAvailable = 0
        self.non_cooked_pizza = 0
        self.Accumulated_Dirt = 0
        self.Daily_income = 0
        self.Available_plate = 0
        self.BatteryLevel = dict()
        self.customer_status = dict()
        self.lock = dict()

    def create_observable_space_for_agent(self, agent_type):
        """
        Create the space environement for each agent
        :param agent_type:
        :return: the observable space size
        """
        if agent_type == 'cooker_robot':
            low_bounds = np.array([0, 0, 0])
            high_bounds = np.array([self.config.Max_customer, self.config.total_number_plate, self.config.max_battery])
            return gym.spaces.Box(low=low_bounds, high=high_bounds, dtype=np.int32)

        else:
            low_bounds = np.array([0, 0, 0] + [0] * self.config.Max_customer + [0] * self.config.Max_customer)
            high_bounds = np.array([self.config.Max_customer, 300, self.config.max_battery] + [3]*self.config.Max_customer + [self.config.max_arrival_time]*self.config.Max_customer)
            return gym.spaces.Box(low=low_bounds, high=high_bounds, dtype=np.int32)

    def start_new_day(self):
        """
        The function start a new day in the restaurant, meaining that all the fluents are initialized,
        And the customers fluents are returning to 0
        :return:
        """
        self.Daily_income = 0
        self.Available_plate = self.config.total_number_plate
        self.PizzaAvailable = 0
        self.non_cooked_pizza = 0
        self.Accumulated_Dirt = 0
        self.lock["PizzaAvailable"] = 0
        self.lock["Accumulated_Dirt"] = 0
        self.lock["Available_plate"] = self.config.total_number_plate
        self.lock["non_cooked_pizza"] = 0

        #set all robots as available, set all robot battery at maximum
        for robot_name in self.robot_list:
            self.BatteryLevel[robot_name] = self.config.max_battery

        self.lock["customer_status"] = dict()
        #set all customers
        for customer_name in self.customer_list:
            self.customer_status[customer_name] = 0
            self.lock["customer_status"][customer_name] = 0
            self.customer_waiting_time[customer_name] = 0

    def get_agent_observation_space(self, agent):
        """
        Get the agent observation space at timestamp t
        :param agent:
        :return:
        """
        agent_type = self.robot_dict[agent]
        agent_observation_space = []

        if agent_type == 'waiter_robot':
            agent_observation_space.append(self.PizzaAvailable)
            agent_observation_space.append(self.Accumulated_Dirt)
            agent_observation_space.append(self.BatteryLevel[agent])
            for customer in self.customer_list:
                agent_observation_space.append(self.customer_status[customer])
            for customer in self.customer_list:
                agent_observation_space.append(self.customer_waiting_time[customer])

        else:
            agent_observation_space.append(self.non_cooked_pizza)
            agent_observation_space.append(self.Available_plate)
            agent_observation_space.append(self.BatteryLevel[agent])
        return agent_observation_space


    def update_customers_state(self, scheduler:dict, t):
        """
        Update the customers state at each timestamp, update the scheduler and the fluents values
        :param scheduler: the scheduler of the environement
        :param t: timestamp
        :return:
        """
        for customer in self.customer_list:
            if self.customer_status[customer] == 1 or self.customer_status[customer] == 2:
                self.customer_waiting_time[customer] += 1

            if scheduler[customer] == t:
                self.customer_status[customer] = 1
                self.lock['customer_status'][customer] = 1
        return scheduler

    def give_robot_reward(self, robot, action):
        """
        Compute the robot reward for a given reward and scheduler,
        we punish the cooker robot if he is charging when he has lot of battery or if he is not doing anything if there are thing to do
        We punish the waiter robot if he is not doing anything if there are things to do or if he deliver customer that are not waiting since a lot of time
        We reward the waiter when he is cleaning if the dirt level is to much and if he is serving the older customer in term of time
        :param scheduler:
        :return: the reward of an action of the robot, the goal is to reward a robot when he makes the good choice and punish him
        when he make a bad choice
        """
        type = self.robot_dict[robot]
        if type == 'cooker':
            if (self.non_cooked_pizza > 0 or self.Available_plate < self.config.total_number_plate or self.BatteryLevel[robot] < self.config.max_battery) and action == 0:
                return -1
            if (self.non_cooked_pizza>0 or self.Available_plate>0) and self.BatteryLevel[robot]>20 and action==2:
                return -0.5

            return 0

        else:
            waiting_list = sorted(self.customer_waiting_time, key=self.customer_waiting_time.get, reverse=True)
            waiting_list_idx = [self.customer_list.index(waiting_list[i]) for i in range(0, len(waiting_list))]
            time_list = sorted(self.customer_waiting_time.values(), reverse=True)
            if action == 2*self.config.Max_customer + 2 and (time_list[0]>0 or self.Accumulated_Dirt != 0):
                return -1
            if 2 <= action < self.config.Max_customer + 2:
                customer = action - 2
                customer_time_queue = waiting_list_idx.index(customer)
                reward = np.exp(- customer_time_queue)
                return reward

            if self.config.Max_customer + 2 <= action < 2*self.config.Max_customer + 2:
                customer = action - 2 - self.config.Max_customer
                customer_time_queue = waiting_list_idx.index(customer)
                reward = np.exp(- customer_time_queue)
                return reward

            if action == 0:
                if self.Accumulated_Dirt <= self.config.level_1:
                    return 0
                else:
                    return 1

            return 0


    def get_num_customer_delivered(self, scheduler:dict):
        """
        Getthe number of customer delivered and the number of customer that were present in the restuarant
        :param scheduler:
        :return:
        """
        count = 0
        total = 0
        for customer in self.customer_status:
            if self.customer_status[customer] == 3:
                count += 1
            if scheduler[customer] != -1:
                total += 1
        return total, count




