from State import State
from Config import EnvConfig
from gym import spaces


class Action:
    def __init__(self, config: EnvConfig, robot_dict: dict, customer_list: list):
        self.config = config
        self.robot_dict = robot_dict
        self.customer_list = customer_list
        self.action_space = dict()
        self.actions_map = {
            'cooker_robot': {0: 'Cook', 1: 'Wash', 2: 'Recharge', 3: 'Is not doing anything'},
            'waiter_robot': {0: 'Clean', 1: 'Recharge'}
        }
        for i in range(0, len(customer_list)):
            self.actions_map['waiter_robot'][i+2] = 'Take order of Customer_'+str(i)
        for i in range(0, len(customer_list)):
            self.actions_map['waiter_robot'][i + 2 + len(customer_list)] = 'Deliver to Customer_' + str(i)
        self.actions_map['waiter_robot'][2 + 2*len(customer_list)] = 'Is not doing anything'

        # number of actions is clean, cook, wash, recharge, take_order*nb_customer, serve*nb_customer
        self.General_action_space = spaces.Discrete(4 + 2 * self.config.Max_customer + 1)
        for robot in self.robot_dict.keys():
            agent_type = self.robot_dict[robot]
            if agent_type == 'cooker_robot':
                self.action_space[robot] = spaces.Discrete(4)
            else:
                self.action_space[robot] = spaces.Discrete(3 + 2*self.config.Max_customer)

    def check_clean(self, state: State, robot_name: str):
        """
        Check is the action clean can be performed
        :param state:
        :param robot_name:
        :return: True if it can or false if it cannot
        """
        if self.robot_dict[robot_name] != 'waiter_robot':
            return False
        if state.BatteryLevel[robot_name] < self.config.energy_clean_cost:
            return False
        if state.Accumulated_Dirt < 1 or state.lock['Accumulated_Dirt'] < 1:
            return False
        return True

    def perform_clean(self, state: State, robot_name: str):
        """
        Execute the action clean and change the current state of the day
        :param state:
        :param robot_name:
        :return:
        """
        state.Accumulated_Dirt -= self.config.cleaning_efficiency
        state.BatteryLevel[robot_name] -= self.config.energy_clean_cost
        return state

    def check_recharge(self, state: State, robot_name: str):
        """
        Check if the acton recharge can be perfomed
        :param state:
        :param robot_name:
        :return: True or False
        """

        if state.BatteryLevel[robot_name] < self.config.energy_recharge_cost:
            return False
        if state.BatteryLevel[robot_name] == self.config.max_battery:
            return False
        return True

    def perform_recharge(self, state: State, robot_name: str):
        """
        Perfom the action recharge
        :param state:
        :param robot_name:
        :return: the changed state
        """
        state.BatteryLevel[robot_name] += self.config.recharge_efficiency
        if state.BatteryLevel[robot_name] > self.config.max_battery:
            state.BatteryLevel[robot_name] = self.config.max_battery
        return state

    def check_wash(self, state: State, robot_name: str):
        """
        Check if the action wash can be performed
        :param state:
        :param robot_name:
        :return: True/False
        """
        if self.robot_dict[robot_name] != 'cooker_robot':
            return False
        if state.BatteryLevel[robot_name] < self.config.energy_wash_cost:
            return False
        if state.Available_plate == self.config.total_number_plate or state.lock['Available_plate'] == self.config.total_number_plate:
            return False
        return True

    def perform_wash(self, state: State, robot_name: str):
        """
        Perform the action wash (wash the plate of the restaurant)
        :param state:
        :param robot_name:
        :return: the changed state
        """
        state.BatteryLevel[robot_name] -= self.config.energy_wash_cost
        state.Available_plate += self.config.washing_efficiency
        if state.Available_plate > self.config.total_number_plate:
            state.Available_plate = self.config.total_number_plate
        return state

    def check_cook(self, state: State, robot_name: str):
        """
        Check if the action cook can be performed
        :param state:
        :param robot_name:
        :return: True/False
        """
        if self.robot_dict[robot_name] != 'cooker_robot':
            return False
        if state.BatteryLevel[robot_name] < self.config.energy_cook_cost:
            return False
        if state.Available_plate == 0 or state.lock['Available_plate'] == 0:
            return False
        if state.non_cooked_pizza == 0 or state.lock['non_cooked_pizza'] == 0:
            return False
        return True

    def perform_cook(self, state: State, robot_name: str):
        """
        Perform the action cook and change the state of the world
        :param state:
        :param robot_name:
        :return:
        """
        state.BatteryLevel[robot_name] -= self.config.energy_cook_cost
        state.Available_plate -= 1
        state.non_cooked_pizza -= 1
        state.PizzaAvailable += 1
        state.Daily_income -= self.config.food_cost
        return state

    def check_deliver(self, state: State, robot_name: str, customer_name: str):
        """
        Check if the action deliver can be performed
        :param state:
        :param robot_name:
        :param customer_name:
        :return: True/False
        """
        if self.robot_dict[robot_name] != 'waiter_robot':
            return False
        if state.BatteryLevel[robot_name] < self.config.energy_deliver_cost:
            return False
        if state.PizzaAvailable == 0 or state.lock['PizzaAvailable'] == 0:
            return False
        if state.customer_status[customer_name] != 2 or state.lock['customer_status'][customer_name] != 2:
            return False
        return True

    def perform_deliver(self, state: State, robot_name: str, customer_name: str):
        """
        Perform the deliver action to a customer and changed the state of the world
        :param state:
        :param robot_name:
        :param customer_name:
        :return:
        """
        state.BatteryLevel[robot_name] -= self.config.energy_deliver_cost
        state.PizzaAvailable -= 1
        state.customer_status[customer_name] = 3
        state.Daily_income += self.config.food_price
        return state

    def check_take_order(self, state: State, robot_name: str, customer_name: str):
        """
        Check if the waiter robot can take the order of a customer
        :param state:
        :param robot_name:
        :param customer_name:
        :return: True/False
        """
        if self.robot_dict[robot_name] != 'waiter_robot':
            return False
        if state.BatteryLevel[robot_name] < self.config.energy_take_order_cost:
            return False
        if state.customer_status[customer_name] != 1 or state.lock['customer_status'][customer_name] != 1:
            return False
        return True

    def perform_take_order(self, state: State, robot_name: str, customer_name: str):
        """
        Perform the action take order and change the state of the world
        :param state:
        :param robot_name:
        :param customer_name:
        :return:
        """
        state.BatteryLevel[robot_name] -= self.config.energy_take_order_cost
        state.customer_status[customer_name] = 2
        state.non_cooked_pizza += 1
        return state

    def give_possible_actions(self, state: State, agent):
        """
        Give for a given agent and a given state all the possible actions the agent can perform
        :param state:
        :param agent:
        :return: The numbers corresponding to the possible action the robot can perform
        """
        possible_actions = []
        if self.robot_dict[agent] == 'cooker_robot':
            if self.check_cook(state, agent) == True:
                possible_actions.append(0)

            if self.check_wash(state, agent) == True:
                possible_actions.append(1)

            if self.check_recharge(state, agent) == True:
                possible_actions.append(2)

            if len(possible_actions) == 0:
                possible_actions.append(3)

        else:
            if self.check_clean(state, agent) == True:
                possible_actions.append(0)

            if self.check_recharge(state, agent) == True:
                possible_actions.append(1)

            idx = 1
            for c in self.customer_list:
                idx += 1
                if self.check_take_order(state, agent, c) == True:
                    possible_actions.append(idx)

            for c in self.customer_list:
                idx += 1
                if self.check_deliver(state, agent, c) == True:
                    possible_actions.append(idx)

            if len(possible_actions) == 0:
                possible_actions.append(idx+1)
        return possible_actions

    def lock_ressources(self, state: State, agent, action: int):
        """
        Allow the robot to lock the resources when he decides to perform an action,
        Locking the resources is important to forbid the other robot to use the same resources twice at the same time
        it also allow robots to not perfom the same action on the same customer
        :param state:
        :param agent:
        :param action:
        :return:
        """
        agent_type = self.robot_dict[agent]

        if agent_type == 'cooker_robot':
            if action == 0:
                state.lock['non_cooked_pizza'] -= 1
                state.lock['PizzaAvailable'] += 1
                state.lock['Available_plate'] -= 1

            elif action == 1:
                state.lock['Available_plate'] += 1

        else:
            if action == 0:
                state.lock['Accumulated_Dirt'] -= self.config.cleaning_efficiency

            elif 2 <= action < self.config.Max_customer + 2:
                customer_id = action - 2
                customer = self.customer_list[customer_id]
                state.lock["customer_status"][customer] = 2
                state.lock["non_cooked_pizza"] += 1

            elif self.config.Max_customer + 2 <= action < 2 * (self.config.Max_customer) + 2:
                customer_id = action - 2 - self.config.Max_customer
                customer = self.customer_list[customer_id]
                state.lock["customer_status"][customer] = 3
                state.lock["PizzaAvailable"] -= 1

        return state

    def execute_action(self, state: State, agent: str, action: int):
        """
        Execute the actions that have been decided, by the model
        :param state:
        :param agent:
        :param action:
        :return: the changed state
        """
        agent_type = self.robot_dict[agent]

        if agent_type == 'cooker_robot':
            if action == 0:
                state = self.perform_cook(state, agent)

            elif action == 1:
                state = self.perform_wash(state, agent)

            elif action == 2:
                state = self.perform_recharge(state, agent)
            else:
                pass

        else:
            if action == 0:
                state = self.perform_clean(state, agent)

            elif action == 1:
                state = self.perform_recharge(state, agent)

            elif 2 <= action < self.config.Max_customer + 2:
                customer_id = action - 2
                customer = self.customer_list[customer_id]
                state = self.perform_take_order(state, agent, customer)

            elif self.config.Max_customer + 2 <= action < 2 *self.config.Max_customer + 2:
                customer_id = action - 2 - self.config.Max_customer
                customer = self.customer_list[customer_id]
                state = self.perform_deliver(state, agent, customer)
            else:
                pass
        return state

