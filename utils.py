import random


def generate_bernouli_sample(customer_satisfaction):
    """
    Return if the customer will come this day to the restaurant or not
    :param customer_satisfaction:
    :return: True/False
    """
    if 0 <= customer_satisfaction <= 1:
        return True if random.random() < customer_satisfaction else False
    else:
        raise ValueError("Parameter should be between 0 and 1.")

def generate_normal_sample(mean, std, max_arrival_time, average_waiting_time):
    """
    Return the time when the customer will get to the restaurant, following a normal law
    :param mean:
    :param std:
    :param max_arrival_time:
    :param average_waiting_time:
    :return: the time when the customer will enter the restaurant
    """
    arrival_time = random.gauss(mean, std)
    return max(0, min(arrival_time, max_arrival_time-average_waiting_time))

def find_best_possible_action(actions_score, possible_actions):
    """
    Find the action with the greatest Q value among the possible actions
    :param actions_score: The Q value for every actions
    :param possible_actions: The possible actions
    :return: The possible action with the greatest Q value
    """
    max_score = -1000000
    best_action = -100000
    for i, score in enumerate(actions_score):
        if i in possible_actions:
            if score > max_score:
                max_score = score
                best_action = i
    return best_action
