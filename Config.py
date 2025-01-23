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

class EnvConfig:
    def __init__(self,
                 dirt_dictionary,
                 energy_cook_cost=4,
                 energy_wash_cost=2,
                 energy_clean_cost=2,
                 energy_deliver_cost=5,
                 energy_take_order_cost=3,
                 energy_recharge_cost=1,
                 cleaning_efficiency=2,
                 washing_efficiency=1,
                 cook_efficiency=1,
                 food_price=10,
                 recharge_efficiency=5,
                 max_battery=100,
                 cook_dirt=3,
                 deliver_dirt=1,
                 food_cost=2,
                 total_number_plate=30,
                 CookerRobot_num=3,
                 WaiterRobot_num=3,
                 Max_customer=200,
                 Average_waiting_time=15,
                 max_arrival_time=240,
                 mean_arrival_time=120,
                 var_arrival_time=60,
                 time_render=2,
                 day_in_year=365,
                 ):
        self.energy_cook_cost = energy_cook_cost
        self.energy_wash_cost = energy_wash_cost
        self.energy_clean_cost = energy_clean_cost
        self.energy_deliver_cost = energy_deliver_cost
        self.energy_take_order_cost = energy_take_order_cost
        self.energy_recharge_cost = energy_recharge_cost
        self.cleaning_efficiency = cleaning_efficiency
        self.washing_efficiency = washing_efficiency
        self.cook_efficiency = cook_efficiency
        self.food_price = food_price
        self.recharge_efficiency = recharge_efficiency
        self.max_battery = max_battery
        self.cook_dirt = cook_dirt
        self.deliver_dirt = deliver_dirt
        self.food_cost = food_cost
        self.total_number_plate = total_number_plate
        self.CookerRobot_num = CookerRobot_num
        self.WaiterRobot_num = WaiterRobot_num
        self.Max_customer = Max_customer
        self.average_waiting_time = Average_waiting_time
        self.max_arrival_time = max_arrival_time
        self.mean_arrival_time = mean_arrival_time
        self.var_arrival_time = var_arrival_time
        self.level_1 = dirt_dictionary['level_1']
        self.score_level_1 = dirt_dictionary['score_level_1']
        self.level_2 = dirt_dictionary['level_2']
        self.score_level_2 = dirt_dictionary['score_level_2']
        self.level_3 = dirt_dictionary['level_3']
        self.score_level_3 = dirt_dictionary['score_level_3']
        self.level_4 = dirt_dictionary['level_4']
        self.score_level_4 = dirt_dictionary['score_level_4']
        self.level_5 = dirt_dictionary['level_5']
        self.score_level_5 = dirt_dictionary['score_level_5']
        self.time_render = time_render
        self.day_in_year = day_in_year



