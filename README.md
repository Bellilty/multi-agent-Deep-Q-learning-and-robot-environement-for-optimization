# Multi-Agent Deep Q-Learning for Restaurant Optimization with Robots

Welcome to the *Multi-Agent Deep Q-Learning and Restaurant Optimization* project!  
This repository features an AI solution that leverages reinforcement learning for robot collaboration to optimize restaurant management and customer satisfaction.

---

## 📖 Project Overview

This project simulates a *fast-food pizza restaurant* managed by robots using *multi-agent deep Q-learning*.  
The robots, split into *waiters* and *cookers*, work together to handle tasks like taking orders, cooking pizzas, cleaning, and ensuring timely service to maximize customer satisfaction and restaurant profits.

### Key Objectives:
1.⁠ ⁠*Customer Satisfaction*: Ensure orders are served quickly and maintain cleanliness to encourage customer return.
2.⁠ ⁠*Profit Optimization*: Balance resources and teamwork to maximize daily and yearly income.
3.⁠ ⁠*Robot Collaboration*: Train robots to cooperate efficiently in a dynamic, partially observable environment.

---

## 🚀 Environment & Simulation

•⁠  ⁠*Restaurant Setup*: 
  - Maximum capacity: 200 customers/day.
  - Operational time: 4 hours/day (240 timestamps).
  - Customer behavior: 
    - Arrival follows a normal distribution (mean: 120, variance: 60).
    - Satisfaction influences return probability (based on waiting time and cleanliness).

•⁠  ⁠*Robots*:
  - *Cooker Robots*: Can cook pizzas, wash plates, or recharge.
  - *Waiter Robots*: Handle orders, serve pizzas, clean the restaurant, or recharge.

•⁠  ⁠*Dynamic Challenges*:
  - Partial observability (robots don't know customer arrival times or satisfaction levels).
  - Limited resources (time, battery, plates).
  - Coordination required to handle tasks efficiently.

---

## 🧠 AI Model and Algorithm

### Multi-Agent Deep Q-Learning:
•⁠  ⁠Each robot has an individual *neural network* to make decisions based on its observations.
•⁠  ⁠The training uses *reinforcement learning* with rewards based on customer satisfaction and penalties for inefficiencies.

### Training Highlights:
•⁠  ⁠*Duration*: 10,000 simulated years (~6 days of real training time).
•⁠  ⁠*Policy*: Robots learn to prioritize tasks like serving customers in arrival order, recharging proactively, and maintaining cleanliness.

---

## 📂 Code Structure

The project is modular, with a clear separation between environment, agents, actions, and training.  
Key files include:

•⁠  ⁠*⁠ config.py ⁠*: Set environment parameters (e.g., robot energy costs, customer probabilities).
•⁠  ⁠*⁠ state.py ⁠*: Represent robot and environment states numerically.
•⁠  ⁠*⁠ action.py ⁠*: Define actions, preconditions, and effects for robots.
•⁠  ⁠*⁠ environment.py ⁠*: Simulate the restaurant environment using OpenAI Gym structure.
•⁠  ⁠*⁠ dqn.py ⁠*: Implement the multi-agent Deep Q-Learning algorithm.
•⁠  ⁠*⁠ simulator.py ⁠*: Train and test the model, visualize results.

---

## 📊 Results

*Achievements after training*:
•⁠  ⁠*150 customers/day handled* with a satisfaction rate of *0.8*.
•⁠  ⁠Daily income: *$1,100–$1,200* (near maximum potential).
•⁠  ⁠Robots learned effective task prioritization and collaboration strategies.

*Visualization*:  
Watch a demo showcasing the results of our model on [YouTube](https://youtu.be/e6wnH9OFvDk).  

---

## 🌟 Key Takeaways

•⁠  ⁠*Impact*: Demonstrates the potential of reinforcement learning for collaborative robotics in real-world applications like restaurant management.
•⁠  ⁠*Limitations*: The model faces challenges handling >125 customers/day and struggles with predicting customer arrival patterns. Further training and parameter tuning could enhance performance.

---

## 📌 How to Run

1.⁠ ⁠Clone this repository.
2.⁠ ⁠Install dependencies (⁠ gym ⁠, ⁠ numpy ⁠, etc.).
3.⁠ ⁠Configure parameters in ⁠ config.py ⁠ as desired.
4.⁠ ⁠Run ⁠ simulator.py ⁠ to train the model or test its performance.

---

## 🤔 Future Work

•⁠  ⁠Improve training to better predict customer arrival patterns.
•⁠  ⁠Scale the model to handle higher customer volumes.
•⁠  ⁠Integrate advanced collaboration strategies for robots.

Feel free to explore, experiment, and contribute to this project!

Feel free to explore, test, and modify the code to suit your needs. Feedback and contributions are welcome!
