import tkinter as tk
import time


class Modelization:
    def __init__(self, robot_dict, time):
        self.robot_dict = robot_dict
        self.agents_order = list(robot_dict.keys())
        self.time = time



    def draw_state(self,day, timestamp, customers_status, customers_waiting_time, data, battery_level):
        # Draw the restaurant
        self.root = tk.Tk()
        self.root.title("Modelization")
        self.canvas = tk.Canvas(self.root, width=1200, height=1000)
        self.canvas.pack()
        self.canvas.create_rectangle(170, 75, 925, 725, fill='lightblue', outline='')
        self.canvas.create_text(550, 30, text="Restaurant Robotissimo", font=("Rockwell", 18, "bold"))
        self.canvas.create_text(550, 55, text="Day: " + str(day) +',     Timestamp: ' +str(timestamp), font=("Rockwell", 16, "bold"))
        #Draw the agents
        self.draw_agents(self.robot_dict)
        #Draw customers
        self.draw_clients(customers_status, customers_waiting_time)
        #draw fluents
        self.display_data(data)
        #draw_battery_level
        self.display_battery_level(battery_level)
        self.root.after(3000, self.close_window)
        self.root.mainloop()



    def draw_action_state(self,day, timestamp, customers_status, customers_waiting_time, data, actions, battery_level):
        self.root = tk.Tk()
        self.root.title("Modelization2")
        self.canvas = tk.Canvas(self.root, width=1200, height=1000)
        self.canvas.pack()
        self.canvas.create_rectangle(170, 75, 925, 725, fill='lightblue', outline='')
        self.canvas.create_text(550, 30, text="Restaurant Robotissimo", font=("Rockwell", 18, "bold"))
        self.canvas.create_text(550, 55, text="Day: " + str(day) +',     Timestamp: ' +str(timestamp), font=("Rockwell", 16, "bold"))
        #Draw the agents
        self.draw_agents(self.robot_dict)
        #Draw customers
        self.draw_clients(customers_status, customers_waiting_time)
        #draw data
        self.display_data(data)
        #draw actions
        self.display_actions(actions)
        #draw battery_level
        self.display_battery_level(battery_level)
        self.root.after(3000, self.close_window)
        self.root.mainloop()


    def close_window(self):
        self.root.destroy()


    def draw_agents(self, agents):
        colors = {'cooker_robot': 'yellow', 'waiter_robot': 'orange'}
        padding = 10
        y_start = 95
        y_end = 705
        total_agents = len(agents)
        y_spacing = (y_end - y_start) / (total_agents - 1)

        for idx, (name, agent_type) in enumerate(agents.items()):
            color = colors[agent_type]
            x = 185
            y = y_start + idx * y_spacing
            text_id = self.canvas.create_text(x + padding, y, text=name)
            bbox = self.canvas.bbox(text_id)
            self.canvas.create_oval(bbox[0] - padding, bbox[1] - padding,
                                    bbox[2] + padding, bbox[3] + padding,
                                    fill=color, outline='')
            self.canvas.tag_raise(text_id)

        self.canvas.create_rectangle(335, 730, 432, 750, fill="yellow", outline="")
        self.canvas.create_text(380, 740, text="cooker robots", fill="black", font=("Arial", 10))
        self.canvas.create_rectangle(335, 755, 432, 775, fill="orange", outline="")
        self.canvas.create_text(380, 765, text="waiter robots", fill="black", font=("Arial", 10))

    def draw_clients(self, client_statuses, client_waiting_times):
        colors = {1: 'pink', 2: 'lightgreen'}
        x_start = 875
        y_start = 95
        y_end = 705
        total_clients = sum(status in (1, 2) for status in client_statuses.values())
        max_clients_in_row = min(total_clients, 12)
        if total_clients == 1:
            y_spacing = 50
        else:
            y_spacing = (y_end - y_start) / (max_clients_in_row - 1)

        idx = 0
        for name, status in client_statuses.items():
            if status in (1, 2):
                color = colors[status]
                row = idx // 12
                x = x_start - 50 * row
                y = y_start + (idx % 12) * y_spacing
                self.canvas.create_rectangle(x - 10, y - 10, x + 10, y + 10, fill=color, outline='')
                self.canvas.create_text(x, y, text=client_waiting_times[name], fill='black', font=("Arial", 12))
                self.canvas.create_text(x, y - 15, text=name, fill='black', font=("Arial", 12))
                idx += 1
        self.canvas.create_rectangle(535, 730, 650, 750, fill='pink', outline='')
        self.canvas.create_text(580, 740, text='waiting to order', font=("Arial", 10))
        self.canvas.create_rectangle(535, 755, 650, 775, fill='lightgreen', outline='')
        self.canvas.create_text(590, 765, text='waiting to be served', font=("Arial", 10))

    def display_data(self, data):
        x_start = 950
        y_start = 100
        y_spacing = 30

        self.canvas.create_text(x_start+100, y_start, text="Statistics: ", font=("Rockwell", 12, "bold"))

        for idx, (key, value) in enumerate(data.items()):
            y = y_start + (idx + 1) * y_spacing
            self.canvas.create_text(x_start, y, text=f"{key}: ", font=("Rockwell", 12), anchor='w')
            self.canvas.create_text(x_start + 200, y, text=f"{value}", font=("Rockwell", 12, "bold"), anchor='w')

    def display_actions(self, actions):

        x_start = 275
        y_start = 95
        y_end = 705
        total_agents = len(self.robot_dict)
        y_spacing = (y_end - y_start) / (total_agents - 1)

        for idx, agent in enumerate(self.robot_dict.keys()):
            if agent not in actions:
                continue

            y = y_start + idx * y_spacing

            # Draw action text and box
            action_text = actions[agent]
            text_id = self.canvas.create_text(x_start + 250, y, text=action_text, font=("Arial", 14, "bold"))
            bbox = self.canvas.bbox(text_id)
            self.canvas.create_rectangle(bbox[0] - 10, bbox[1] - 10, bbox[2] + 10, bbox[3] + 10, fill="light grey",
                                         outline="")
            self.canvas.tag_raise(text_id)

            # Draw arrow from agent to action box
            agent_x = 185
            text_id_agent = self.canvas.create_text(agent_x, y, text=agent)
            bbox_agent = self.canvas.bbox(text_id_agent)
            arrow_start_x = bbox_agent[2] + 10  # Increase the offset for the arrow start
            arrow_end_x = bbox[0] - 10
            self.canvas.create_line(arrow_start_x, y, arrow_end_x, y, arrow=tk.LAST, width=2)
            self.canvas.tag_lower(text_id_agent)  # remove the duplicate agent name

    def display_battery_level(self, battery_level):
        x_start = 10
        y_start = 150
        y_spacing = 30
        font = ('Rockwell', 12, 'bold')

        self.canvas.create_text(x_start + 75, y_start - 50, text='Battery level:', font=font)

        for idx, (name, level) in enumerate(battery_level.items()):
            y = y_start + idx * y_spacing
            self.canvas.create_text(x_start + 20, y, text=name + ':', font=font, anchor='w')
            self.canvas.create_text(x_start + 110, y, text=str(level) + '%', font=font, anchor='w')



