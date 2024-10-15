import json
import sys
sys.path.insert(0, '..')
sys.path.append('/home/bili/Desktop/scenario_generation_llm/create')
from create.create_game import register_json_folder, register_json_str

import matplotlib.pyplot as plt
plt.rcParams["animation.html"] = "html5"
import matplotlib.animation
import gym
import pygame
import numpy as np
from utils.trampoline_physics import trampoline_exit_details
from utils.fan_physics import fan_motion_exit_details
from utils.projectile_motion import ProjectileMotion
from utils.entrapment import entrapment
from utils.coords_utils import coords_r2c,coords_c2r
from utils.play_game import play_game
from IPython.display import display, clear_output
import time
import json
import os
from create.create_game.tools import globals
from llama_index.core.tools.tool_spec.base import BaseToolSpec
from llama_index.core.schema import ImageDocument
from llama_index.core.agent.react_multimodal.types import Visualization
from typing import Tuple
from PIL import Image
import ast
import math
import cv2
import copy
from llama_index.core import SimpleDirectoryReader
from llama_index.multi_modal_llms.openai import OpenAIMultiModal


BALL_MASS = 10.0
SCREEN_SIZE = 84
BALL_RADIUS = 4
G = 2
CANNON_WIDTH = 10.0
CANNON_HEIGHT = 7.3



BALL_MASS = 10.0
SCREEN_SIZE = 84
BALL_RADIUS = 4
G = 2
CANNON_WIDTH = 10.0
CANNON_HEIGHT = 7.3
class CreateEnv(BaseToolSpec):
    def __init__(self):
        self.basename = "Push"
        self.starter_json_file = "/home/bili/Desktop/scenario_generation_llm/example_puzzle_layout.json"
        self.tools_list_path = "/home/bili/Desktop/scenario_generation_llm/create/tool_documentation.json"
        with open(self.tools_list_path, 'r') as file:
            self.tools_list = json.load(file)["tools"]
        with open(self.starter_json_file, 'r') as json_file:
            self.env_json = json.load(json_file)
        starter_json_str = json.dumps(self.env_json)
        
        self.env_json['env'] = [item for item in self.env_json['env'] if item['name'] != 'floor' and item['name'] != 'wall']
        with open(self.starter_json_file, 'w') as file:
            json.dump(self.env_json, file, indent=4)

        try:
            register_json_str(starter_json_str)
        except:
            pass
        #self.visualization_path = "/home/bili/Desktop/scenario_generation_llm/other_images/env10.jpg"
        self.animation_path = "/home/bili/Desktop/scenario_generation_llm/data/animations/push_start_demo.mp4"
        self.gap_radius = 6
        self.tool_visualized = False
        self.tools = {}
        self.frames_path = "/home/bili/Desktop/scenario_generation_llm/frames"
        self.frame = "/home/bili/Desktop/scenario_generation_llm/frame.jpg"
        self.tool_message = ''
        self.ball_message = ''


    spec_functions = ["place_red_ball_blue_ball_goal", "place_floor", "place_wall", "adjust_red_ball_position", "adjust_goal_position",
                      "place_ramp", "visualize_simulation", 'place_fixed_hexagon', 'place_cannon']


    def place_red_ball_blue_ball_goal(self, red_ball, blue_ball, goal):
        """
        This function helps you place the red ball, blue ball and goal in the environment.
        Pass a tuple of x and y coordinates of the red ball, blue ball and goal as a tuple.

        Args:
        red_ball: Tuple of x and y coordinates of the red ball.
        blue_ball: Tuple of x and y coordinates of the blue ball.
        goal: Tuple of x and y coordinates of the goal.

        Example:
        place_red_ball_blue_ball_goal((-0.5, 0.1), (0.5, 0.1), (0.5, -0.1))
        """
        
        red = f"[{red_ball[0]},{red_ball[1]}]"
        blue = f"[{blue_ball[0]},{blue_ball[1]}]"
        goal_str = f"[{goal[0]},{goal[1]}]"
        self.env_json['target'] = red
        self.env_json['goal'] = goal_str
        for obj in self.env_json['env']:
            if obj['name'] == 'marker_ball':
                obj['pos'] = blue
            if obj['name'] == 'medium_floor' and obj['id'] == 0:
                floor_y = float(red_ball[1]) - 0.11
                obj['pos'] = f"[{red_ball[0]},{floor_y}]"
            if obj['name'] == 'medium_floor' and obj['id'] == 1:
                floor_y = float(goal[1]) - 0.11
                obj['pos'] = f"[{goal[0]},{floor_y}]"
        with open(self.starter_json_file, 'w') as file:
            json.dump(self.env_json, file, indent=4)
        if abs(float(red_ball[0])  - float(goal[0])) > 1:
            return 'The red ball and goal are too far apart. Please place again without calling the designer.'
        if math.sqrt((goal[0] - red_ball[0])**2 + (goal[1] - red_ball[1])**2) < 0.3:
            return 'The red ball and goal are too close. Please place again by moving the goal a little further from the red ball without calling the designer.'
        if float(red_ball[1]) == float(goal[1]):
            return 'The red ball and goal are on the same y-axis. Please place again by adjusting the y coordinate of either one a little bit without calling the designer.'
        if float(red_ball[0]) == float(goal[0]):
            return 'The red ball and goal are on the same x-axis. Please place again by adjusting the x coordinate of either one a little bit without calling the designer.'
        if red_ball[1] == blue_ball[1]:
            return 'The red ball and blue ball are on the same y-axis. Please place again by adjusting the y coordinate of either one a little bit without calling the designer.'
        if red_ball[0] == blue_ball[0]:
            return 'The red ball and blue ball are on the same x-axis. Please place again by adjusting the x coordinate of either one a little bit without calling the designer.'
        if blue_ball[1] == goal[1]:
            return 'The blue ball and goal are on the same y-axis. Please place again by adjusting the y coordinate of either one a little bit without calling the designer.'
        if blue_ball[0] == goal[0]:
            return 'The blue ball and goal are on the same x-axis. Please place again by adjusting the x coordinate of either one a little bit without calling the designer.'
        
        if blue_ball[0] < -0.6 or blue_ball[0] > 0.6:
            return 'The blue ball should not be placed outside the range of -0.6 to 0.6 in the x-axis. Please place again without calling the designer.'
        if blue_ball[1] < -0.8 or blue_ball[1] > 0.8:
            return 'The blue ball should not be placed outside the range of -0.8 to 0.8 in the y-axis. Please place again without calling the designer.'
        if red_ball[0] < -0.6 or red_ball[0] > 0.6:
            return 'The red ball should not be placed outside the range of -0.6 to 0.6 in the x-axis. Please place again without calling the designer.'
        if red_ball[1] < -0.8 or red_ball[1] > 0.8:
            return 'The red ball should not be placed outside the range of -0.8 to 0.8 in the y-axis. Please place again without calling the designer.'
        if goal[0] < -0.6 or goal[0] > 0.6:
            return 'The goal should not be placed outside the range of -0.6 to 0.6 in the x-axis. Please place again without calling the designer.'
        if goal[1] < -0.8 or goal[1] > 0.8:
            return 'The goal should not be placed outside the range of -0.8 to 0.8 in the y-axis. Please place again without calling the designer.'

        if goal[0] < red_ball[0]:
            sub_goal_x = float(red_ball[0]) - 0.2
            self.env_json["target_sec_goals"][0]= f"[{sub_goal_x},{red_ball[1]}]"
        else:
            sub_goal_x = float(red_ball[0]) + 0.2
            self.env_json["target_sec_goals"][0]= f"[{sub_goal_x},{red_ball[1]}]"
        
        return 'Red ball, blue ball and goal placed successfully.'


    def place_floor(self, floor):
        """
        This function helps you place the floor in the environment.
        Pass a tuple of x and y coordinates of the floor as a tuple.

        Example:
        place_floor(floor=(-0.5, 0.1))
        """
        floor_str = f"[{floor[0]},{floor[1]}]"
        
        red_ball_pos = self.env_json['target']
        red = ast.literal_eval(red_ball_pos)
        blue = self.env_json['env'][0]['pos']
        blue = ast.literal_eval(blue)
        if abs(float(floor[0]) - float(red[0])) >= 0.6:
            return 'The floor is too far from the red ball. Please place the floor on a new x coordinate.'
        # if abs(float(floor[0]) - float(red[0])) < 0.3:
        #     return 'The floor is too close to the red ball. Please place the floor on a new x coordinate.'
        if abs(float(floor[1]) - float(red[1])) <= 0.2:
            return 'The floor is too close to the red ball. Please place the floor on a new y coordinate that is smaller than the blue ball but bigger than the red ball.'
        # if abs(float(floor[1]) - float(red[1])) > 0.4:
        #     return 'The floor is too far to the red ball. Please place the floor on a new y coordinate that is smaller than the blue ball but bigger than the red ball.'
        if abs(float(floor[0]) - float(blue[0])) > 0.7:
            return 'The floor is too far from the blue ball. Please place the floor on a new x coordinate.'
        if abs(float(floor[1]) - float(blue[1])) < 0.4:
            return 'The floor is too close from the blue ball. Please place the floor on a new y coordinate.'
        self.env_json['env'].append({"name": "floor", "pos": floor_str,"length": 20, "color": "STEELBLUE"})
        with open(self.starter_json_file, 'w') as file:
            json.dump(self.env_json, file, indent=4)
        return 'Floor placed successfully.'


    def place_wall(self, wall):
        """
        This function helps you place the wall in the environment.
        Pass a tuple of x and y coordinates of the wall as a tuple.

        Example:
        place_wall(wall=(-0.5, 0.1))
        """
        blue = self.env_json['env'][0]['pos']
        blue = ast.literal_eval(blue)
        wall_str = f"[{wall[0]},{wall[1]}]"
        self.env_json['env'].append({"name": "wall", "pos": wall_str})
        with open(self.starter_json_file, 'w') as file:
            json.dump(self.env_json, file, indent=4)
        dis = blue[1] - wall[1]
        if (dis) < 0.7:
            return f'The y coordinate of the blue ball is only {dis} greater than the y coordinate of the wall. Place the blue ball to make it at least more than 0.7 higher than the wall.'
        return 'Wall placed successfully.'
    
    

    def adjust_red_ball_position(self, x, y):
        """
        This function helps you adjust the position of the red ball in the environment.
        Pass the x coordinate of the red ball.
        Pass the y coordinate of the red ball.

        Example:
        adjust_red_ball_position(-0.5, 0.1)
        """

        y = y - 0.15
        goal_pos = self.env_json['goal']
        goal = ast.literal_eval(goal_pos)
        if goal[0] > x:
            x = x + 0.1
            sub_goal_x = float(x) + 0.2
            self.env_json["target_sec_goals"][0]= f"[{sub_goal_x},{y}]"
        else:
            x = x - 0.1
            sub_goal_x = float(x) - 0.2
            self.env_json["target_sec_goals"][0] = f"[{sub_goal_x},{y}]"
        red_ball_pos = f"[{x},{y}]"
        self.env_json['target'] = red_ball_pos
        for obj in self.env_json['env']:
            if obj['name'] == 'medium_floor' and obj['id'] == 0:
                floor_y = float(y) - 0.11
                obj['pos'] = f"[{x},{floor_y}]"
       
        with open(self.starter_json_file, 'w') as file:
            json.dump(self.env_json, file, indent=4)
        goal = self.env_json['goal']
        goal = json.loads(goal)
        if math.sqrt((goal[0] - x)**2 + (goal[1] - y)**2) < 0.3:
            return 'The red ball and goal are too close. Please adjust the goal position a little further from the red ball without calling the designer.'
        return 'Red ball position adjusted successfully.'
    

    def adjust_goal_position(self, x, y, red_ball_moving_direction):
        """
        This function helps you adjust the position of the goal in the environment.
        Pass the x coordinate of the goal.
        Pass the y coordinate of the goal.
        Pass the direction in which the red ball is moving to reach the goal (left or right).

        Example:
        adjust_goal_position(-0.5, 0.1, 'left')
        """

        if red_ball_moving_direction == 'left':
            x = x + 0.1
        else:
            x = x - 0.1
        goal_pos = f"[{x},{y}]"
        self.env_json['goal'] = goal_pos
        for obj in self.env_json['env']:
            if obj['name'] == 'medium_floor' and obj['id'] == 1:
                floor_y = float(y) - 0.11
                obj['pos'] = f"[{x},{floor_y}]"
        with open(self.starter_json_file, 'w') as file:
            json.dump(self.env_json, file, indent=4)
        return 'Goal position adjusted successfully.'

    
    def check_overlap(self, action_pos):
        all_pos = self.get_placed_pos()
        if len(all_pos) == 0:
            return False
        cur_pos = np.repeat(np.expand_dims(action_pos, 0),
                            all_pos.shape[0], axis=0).squeeze()
        dist = np.sqrt(np.sum((cur_pos - all_pos) ** 2, axis=-1))
        return (dist <= self.settings.overlap_threshold).any()
            
    
    def check_location(self, x, y, **kwargs):
        message = 'The following sentences describe the relative positions of the tool to the objects in the environment to help you better understand the spatial relationships shown in the image: '
        target = self.env_json['target']
        target = json.loads(target)
        if (target[0] < x):
            message += "The red ball is on the right of the tool."
        if (target[0] > x):
            message += "The red ball is on the left of the tool."
        
        goal = self.env_json['goal']
        goal = json.loads(goal)
        if (goal[0] < x):
            message += "The goal is on the right of the tool."
        if (goal[0] > x):
            message += "The goal is on the left of the tool."
        
        
        for obj in self.env_json['env']:
            if 'floor' in obj['name']:
                floor_pos = obj['pos']
                floor = ast.literal_eval(floor_pos)
                if floor[0] != target[0] and floor[0] != goal[0]:
                    floor_x = floor[0]
                    floor_y = floor[1]
                    if (floor_x < x):
                        message += f"the floor at ({coords_c2r(floor_x)}, {coords_c2r(floor_y)}) is on the right of the tool."
                    else:
                        message += f"the floor at ({coords_c2r(floor_x)}, {coords_c2r(floor_y)}) is on the left of the tool."
            elif 'marker_ball' not in obj['name']:
                obj_pos = obj['pos']
                item = ast.literal_eval(obj_pos)
                obj_x = item[0]
                obj_y = item[1]
                if (obj_x < x):
                    message += f"{obj['name']} at ({coords_c2r(obj_x)}, {coords_c2r(obj_y)}) is on the right of the tool."
                else:
                    message += f"{obj['name']} at ({coords_c2r(obj_x)}, {coords_c2r(obj_y)}) is on the left of the tool."
        
        return message
                          


    def get_initial_object_pos(self):
        """
        This function is helpful in getting the initial position of the red ball, blue ball, the goal and other elements.
        It does not take any inputs.
        """
        coor_message = ''
        red_ball_pos = self.env_json['target']
        red = ast.literal_eval(red_ball_pos)
        red_x = coords_c2r(red[0])
        red_y = coords_c2r(red[1])
        blue_ball_pos = None
        goal_pos = self.env_json['goal']
        goal = ast.literal_eval(goal_pos)
        goal_x = goal[0]
        goal_y = goal[1]
        coor_message += f"The goal is placed at: [{goal_x}, {goal_y}]. "

        for obj in self.env_json['env']:
            if 'floor' in obj['name']:
                floor_pos = obj['pos']
                floor = ast.literal_eval(floor_pos)
                if floor[0] != red[0] and floor[0] != goal[0]:
                    floor_x = floor[0]
                    floor_y = floor[1]
                    coor_message += f"The floor is placed at: [{floor_x}, {floor_y}], "
            elif 'marker_ball' not in obj['name']: 
                obj_pos = obj['pos']
                item = ast.literal_eval(obj_pos)
                obj_x = item[0]
                obj_y = item[1]
                name = obj['name']
                coor_message += f"The {name} is placed at: [{obj_x}, {obj_y}], "
        return coor_message


    def get_obj_position(self, obj_name):
        if obj_name == 'red_ball':
            return ast.literal_eval(self.env_json['target'])[0], ast.literal_eval(self.env_json['target'])[1] 
        elif obj_name == 'goal':
            return ast.literal_eval(self.env_json['goal'])[0], ast.literal_eval(self.env_json['goal'])[1]
        for obj in self.env_json['env']:
            if obj_name == 'blue_ball' and obj['name'] == 'marker_ball':
                return ast.literal_eval(obj['pos'])[0], ast.literal_eval(obj['pos'])[1]
            elif 'floor' in obj_name and 'floor' in obj['name']:
                floor_pos = obj['pos']
                floor = ast.literal_eval(floor_pos)
                if floor[0] != ast.literal_eval(self.env_json['target'])[0] and floor[0] != ast.literal_eval(self.env_json['goal'])[0]:
                    return ast.literal_eval(obj['pos'])[0], ast.literal_eval(obj['pos'])[1]
            elif obj['name'] == obj_name:
                return ast.literal_eval(obj['pos'])[0], ast.literal_eval(obj['pos'])[1]
        for tool in self.tools:
            if obj_name in tool:
                return self.tools[tool]['x'], self.tools[tool]['y']
        return None, None
    

    def place_ramp(self, first_obj, direction1, second_obj, direction2, blue_ball_moving_direction, length):
        """
        This function is helpful in placing a ramp to the environment.
        Pass a string for the name of the first object: 'red_ball', 'blue_ball', 'goal', 'floor', 'wall', 'Ramp', 'Fixed_Triangle'.
        Pass a string for whether the ramp should be placed to the 'top', 'bottom', 'left' or 'right' of the first object.
        Pass a string for the name of the second object: 'red_ball', 'blue_ball', 'goal', 'floor', 'wall', 'Ramp', 'Fixed_Triangle'.
        Pass a string for whether the ramp should be placed to the 'top', 'bottom', 'left' or 'right' of the second object.
        Pass a string for the direction the blue ball should be moving toward to reach the red ball: 'left', 'right'
        Pass an integer for the length of the ramp.
        
        Angle Range: From 0 to 180 degrees (exclusive), with a step size of 15.
        Length Range: 10, 14, 18, 22 units


        """

        first_obj_x, first_obj_y = self.get_obj_position(first_obj)
        if first_obj_x == None:
            return (f"The object {first_obj} does not exist in the environment yet. Please give the name of another object.", '')
        second_obj_x, second_obj_y = self.get_obj_position(second_obj)
        if second_obj_x == None:
            return (f"The object {second_obj} does not exist in the environment yet. Please give the name of another object.", '')


        ramp_y = (first_obj_y + second_obj_y)/2
        if direction1 == 'bottom':
            if direction2 == 'left':
                if first_obj_x > second_obj_x:
                    ramp_x = first_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = second_obj_x + 0.4
            elif direction2 == 'right':
                if second_obj_x > first_obj_x:
                    ramp_x = first_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = second_obj_x - 0.4
            elif direction2 == 'bottom':
                ramp_x = (first_obj_x + second_obj_x)/2
            else:
                if first_obj_x > second_obj_x:
                    ramp_x = first_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = first_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
        elif direction1 == 'top':
            if direction2 == 'left':
                if first_obj_x > second_obj_x:
                    ramp_x = second_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = second_obj_x + 0.4
            elif direction2 == 'right':
                if second_obj_x > first_obj_x:
                    ramp_x = second_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = second_obj_x - 0.4
            elif direction2 == 'top':
                ramp_x = (first_obj_x + second_obj_x)/2
            else:
                if first_obj_x > second_obj_x:
                    ramp_x = first_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = first_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
        elif direction1 == 'left':
            if direction2 == 'left':
                ramp_x = max(first_obj_x, second_obj_x) + 0.4
            elif direction2 == 'right':
                if first_obj_y > second_obj_y:
                    ramp_x = first_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else: 
                    ramp_x = second_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
            elif direction2 == 'top':
                if first_obj_x < second_obj_x:
                    ramp_x = first_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = first_obj_x + 0.4
            else:
                if first_obj_x < second_obj_x:
                    ramp_x = second_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else:
                    ramp_x = first_obj_x + 0.4
                
        elif direction1 == 'right':
            if direction2 == 'left':
                if first_obj_y > second_obj_y:
                    ramp_x = first_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
                else: 
                    ramp_x = second_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)
            elif direction2 == 'right':
                ramp_x = min(first_obj_x, second_obj_x) - 0.4
            elif direction2 == 'top':
                if first_obj_x < second_obj_x:
                    ramp_x =  first_obj_x - 0.4
                else:
                    ramp_x = first_obj_x - min( abs(first_obj_x - second_obj_x)/2, 0.4)
            else:
                if first_obj_x < second_obj_x:
                    ramp_x = first_obj_x - 0.4
                else:
                    ramp_x = second_obj_x + min( abs(first_obj_x - second_obj_x)/2, 0.4)

        if first_obj == "blue_ball":
            ramp_x = first_obj_x
        elif second_obj == "blue_ball":
            ramp_x = second_obj_x


        if blue_ball_moving_direction == 'left':
            angle = 150
        else:
            angle = 30
        print(range(len(self.tools)))
        print(self.tools)

        num_ramp = 0
        for i, key in enumerate(reversed(self.tools)):
            if "Ramp" in key:
                num_ramp += 1
        self.tools[f'Ramp_{num_ramp}'] = {
            "tool_id": 0,
            "x": ramp_x,
            "y": ramp_y,
            "angle": angle * (math.pi / 180),
            "length": 18
        }
        self.tool_message = self.check_location(ramp_x, ramp_y)
        return (f"A ramp has been placed at [{coords_c2r(ramp_x)}, {coords_c2r(ramp_y)}] with an angle of {angle} degrees and a length of 18 units.", "I must go to next step to visualize the simulation.")
 

    def place_fixed_hexagon(self, first_obj, direction):
        """
        This function is helpful in placing a fixed hexagon to the environment.
        Pass a string for the name of the first object: 'red_ball', 'blue_ball', 'goal', 'floor', 'wall', 'Ramp', 'Fixed_Triangle'.
        Pass a string for whether the fixed hexagon should be placed to the 'left' or 'right' of the first object.
        
        Coordinates should be constrained between 0 and 84 in each dimension

        """
        first_obj_x, first_obj_y = self.get_obj_position(first_obj)
        if first_obj_x == None:
            return (f"The object {first_obj} does not exist in the environment yet. Please give the name of another object.", '')
        if direction == 'left':
            hexagon_x = first_obj_x + 0.4
        else:
            hexagon_x = first_obj_x - 0.4
        hexagon_y = first_obj_y + 0.1

        num_hexagon = 0
        for i, key in enumerate(reversed(self.tools)):
            if "Fixed_Hexagon" in key:
                num_hexagon += 1
        self.tools[f'Fixed_Hexagon_{num_hexagon}'] = {
            "tool_id": 0,
            "x": hexagon_x,
            "y": hexagon_y,
            "angle": 0,
            "length": 6
        }
        self.tool_message = self.check_location(hexagon_x, hexagon_y)
        return (f"A fixed hexagon has been placed at [{coords_c2r(hexagon_x)}, {coords_c2r(hexagon_y)}] with a length of 5 units.", "I must go to next step to visualize the simulation.")


    def place_cannon(self, first_obj, direction):
        """
        This function is helpful in placing a cannon to the environment.
        Pass a string for the name of the first object: 'red_ball', 'blue_ball', 'goal', 'floor', 'wall', 'Ramp', 'Fixed_Triangle', 'Cannon'.
        Pass a string for whether the cannon should be placed to the 'left' or 'right' of the first object.
        
        Coordinates should be constrained between 0 and 84 in each dimension

        """
        if direction != 'left' and direction != 'right':
            return "Please ask the solver again to provide a valid direction for the cannon. It should be either 'left' or 'right'."
        first_obj_x, first_obj_y = self.get_obj_position(first_obj)
        if first_obj_x == None:
            return (f"The object {first_obj} does not exist in the environment yet. Please give the name of another object.", '')
        if direction == 'left':
            angle = 75
        else:
            angle = 105
        cannon_y = first_obj_y - 0.3

        num_cannon = 0
        for i, key in enumerate(reversed(self.tools)):
            if "Cannon" in key:
                num_cannon += 1
        self.tools[f'Cannon_{num_cannon}'] = {
            "tool_id": 0,
            "x": first_obj_x,
            "y": cannon_y,
            "angle": angle * (math.pi / 180),
            "length": None
        }
        self.tool_message = self.check_location(first_obj_x, cannon_y)
        return (f"A cannon has been placed at [{coords_c2r(first_obj_x)}, {coords_c2r(cannon_y)}]. ", "I must go to next step to visualize the simulation.")


    def adjust_tool(self, tool,  direction):
        """
        This function is helpful in adjusting the position of the tool in the environment.
        Pass a string for the name of the tool: 'Ramp', 'Fixed_Hexagon'.
        Pass a string for whether the tool should be moved 'up' or 'down'. 

        """
        keys = list(self.tools.keys())
        for i, key in enumerate(reversed(keys)):
            if tool in key:
                tool_x = self.tools[key]['x']
                tool_y = self.tools[key]['y']
                if direction == 'up':
                    tool_y += 0.2
                else:
                    tool_y -= 0.2
                self.tools[key] = {"tool_id": 0, "x": tool_x, "y": tool_y, "angle": self.tools[key]['angle'], "length": self.tools[key]['length']}
                message = self.check_location(tool_x, tool_y)
                return (f"A {tool} has been replaced at ({tool_x}, {tool_y}).", message)
        return f"The {tool} you are trying to adjust does not exist in the environment yet. Please use the place_shape function to add the {tool} to the environment first."
        



    def adjust_shape(self, shape, pos, length, angle):
        """
        This function is helpful in adjusting the angle, or length, or position of the shape in the environment.
        Pass a string for the shape of the object.
        Pass a tuple with regular brackets of 2 integers, the x and y coordinates describing the location of the shape.
        Pass an integer for the length of the object.
        Pass an integer for the angle of the object.

        Coordinates should be constrained between 0 and 84 in each dimension
        Angle Range: From 0 to 105 degrees (exclusive) for triangle, 0 to 90 degrees (exclusive) excluding 45 degrees for square, 0 to 72 degrees (exclusive) for pentagon, 0 to 60 degrees (exclusive) for hexagon all with step size of 15.]
        Length Range: From 3 to 9 units

        Args:
            shape (str): The shape of the object. It can be 'Fixed_Triangle', 'Fixed_Square', 'Fixed_Pentagon', 'Fixed_Hexagon'.
            pos (tuple): A tuple containing the x and y coordinates of the object.
            length (int): The length of the object. 
            angle (int): The angle of the object. 
        """
        shape_x, shape_y = pos
        overlap, message = self.check_overlap(shape,coords_r2c(shape_x),coords_r2c(shape_y))
        if overlap:
            return message
        else:
            keys = list(self.tools.keys())
            for i, key in enumerate(reversed(keys)):
                if shape in key:
                    self.tools[key] = {"tool_id": 0, "x": coords_r2c(shape_x), "y": coords_r2c(shape_y), "angle": angle * (math.pi / 180), "length": length}
                    message = self.check_location(coords_r2c(shape_x),coords_r2c(shape_y))
                    return (f"A {shape} has been replaced at {pos} with an angle of {angle} degrees and a length of {length} units.", message)
            return f"The {shape} you are trying to adjust does not exist in the environment yet. Please use the place_shape function to add the {shape} to the environment first."
        

    def plan_next_tool(self):
        message = self.tool_message + self.ball_message
        object_pos = self.get_initial_object_pos()
        return generate_response(message, object_pos)



    def visualize_simulation(self):
        """
        This function helps you visualize the simulation of the environment after placing one tool to see if the blue successfully push the red ball.
        
        """
        self.ball_message = ''
        env_name = self.env_json['name']
        env = gym.make(f'CreateLevel{env_name}-v0')
        env.reset()
        frame = env.render('rgb_array_high_mega_changed_colors')
        #Image.fromarray(frame).save(self.visualization_path)
        env.close()

        json_str = json.dumps(self.env_json,indent=4)
        register_json_str(json_str)
        print(self.tools)
        predef = [[2365, 0, 0] for _ in range(100)]
        for i in range(len(self.tools)):
            tool_id = 0
            tool_name = list(self.tools.keys())[i]
            tool_name = tool_name.rsplit('_', 1)[0]
            tool = list(self.tools.values())[i]
            angle = tool['angle']
            length = tool['length']
            print(tool_name, angle, length, type(angle), type(length))

            for j in self.tools_list:
                if j['tool_type'] == tool_name:
                    if tool_name == 'Cannon':
                        if math.isclose(j['angle'], angle, abs_tol=0.01) and j['extra_info']['force'] == 120:
                            tool_id = j['tool_id']
                            break
                    elif angle is None:
                        if j['length'] == length:
                            tool_id = j['tool_id']
                            break
                    elif length is None:
                        if math.isclose(j['angle'], angle, abs_tol=0.01):
                            tool_id = j['tool_id']
                            break
                    elif math.isclose(j['angle'], angle, abs_tol=0.01) and j['length'] == length:
                        tool_id = j['tool_id']
                        break

            predef[i] = [tool_id, tool['x'], tool['y']]
        print(predef)
        short_action = []
        for i in range(len(predef)):
            if predef[i][0] != 2365:
                new_action = copy.deepcopy(predef[i])
                new_action[0] = self.tools_list[predef[i][0]]['tool_type']
                short_action.append(new_action)
        print (short_action)

        animation, message, not_collide = play_game("NavigateStart",predef_actions=predef, short_action=short_action)
        animation.save(self.animation_path,fps=1)

        # change videos to frames
        self.convert_to_frames()
        # put frames in one image
        #self.combine_images_into_grid(self.frames_path, task=task)

        message += self.get_initial_object_pos()
        self.ball_message = message
        return Visualization(json_str=json.dumps(self.env_json),image_documents=[ImageDocument(image_path=self.frames_path)],explanation_str="we are using the tools to help the blue ball push the red ball to the goal"), self.tool_message, message

        

    # def visualize_simulation(self, task):
    #     """
    #     This function helps you visualize the simulation of the environment after placing one tool to see if the blue successfully push the red ball.
    #     Pass a string for the task: 
    #         if the current task is for the blue ball push the red ball, then task = 'blue_red'
    #         if the current task is for the red ball reach the goal, then task = 'red_goal'
    #     """

    #     self.ball_message = self.run_simulation(task)


    #     return Visualization(json_str=json.dumps(self.env_json),image_documents=[ImageDocument(image_path=self.frame)],explanation_str="we are using the tools to help the blue ball push the red ball to the goal"), self.tool_message, self.ball_message

    


    def convert_to_frames(self):
        """
        This function converts the simulation to frames.
        It does not take any inputs.
        """

        def extract_frames(video_path, output_folder, frame_rate):
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
    
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))

            frame_interval = int(fps / frame_rate)
    
            current_frame = 0
            saved_frame_count = 0
    
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
        
                if current_frame % frame_interval == 0:
                    frame_filename = os.path.join(output_folder, f'frame_{saved_frame_count:04d}.png')
                    cv2.imwrite(frame_filename, frame)
                    saved_frame_count += 1
        
                current_frame += 1
    
            cap.release()
            return saved_frame_count

        
        # delete everything in the folder
        for filename in os.listdir(self.frames_path):
            file_path = os.path.join(self.frames_path, filename)
            os.unlink(file_path)

        extract_frames(self.animation_path, self.frames_path, frame_rate = 1)


    def combine_images_into_grid(self, image_folder, grid_size=(1,8), task = "blue_red"):
        
        image_files = sorted([img for img in os.listdir(image_folder) if img.endswith(('png', 'jpg', 'jpeg'))])
        if task == "blue_red":
            if len(image_files) > 20:
                specific_frames = ['frame_0000.png', 'frame_0003.png', 'frame_0005.png', 'frame_0007.png',  'frame_0009.png',  'frame_0011.png', 'frame_0014.png', 'frame_0017.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 15:
                specific_frames = ['frame_0000.png', 'frame_0002.png', 'frame_0004.png', 'frame_0006.png',  'frame_0008.png',  'frame_0010.png', 'frame_0012.png', 'frame_0014.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 8:
                specific_frames = ['frame_0000.png', 'frame_0002.png', 'frame_0003.png', 'frame_0004.png',  'frame_0005.png',  'frame_0006.png', 'frame_0007.png', 'frame_0008.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 5:
                specific_frames = ['frame_0000.png', 'frame_0002.png', 'frame_0003.png', 'frame_0004.png',  'frame_0005.png',  'frame_0006.png', 'frame_0006.png', 'frame_0006.png']
                image_files = [img for img in image_files if img in specific_frames]
            else:
                grid_size_list = list(grid_size)
                grid_size_list[1] = len(image_files)
                grid_size = tuple(grid_size_list)
        elif task == "red_goal":
            if len(image_files) > 30:
                specific_frames = ['frame_0000.png', 'frame_0010.png', 'frame_0015.png', 'frame_0017.png',  'frame_0020.png',  'frame_0023.png', 'frame_0026.png', 'frame_0029.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 25:
                specific_frames = ['frame_0000.png', 'frame_0005.png', 'frame_0010.png', 'frame_0013.png',  'frame_0016.png',  'frame_0019.png', 'frame_0022.png', 'frame_0025.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 20:
                specific_frames = ['frame_0000.png', 'frame_0003.png', 'frame_0005.png', 'frame_0008.png',  'frame_0011.png',  'frame_0014.png', 'frame_0017.png', 'frame_0020.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 15:
                specific_frames = ['frame_0000.png', 'frame_0002.png', 'frame_0004.png', 'frame_0006.png',  'frame_0008.png',  'frame_0010.png', 'frame_0012.png', 'frame_0014.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 10:
                specific_frames = ['frame_0000.png', 'frame_0002.png', 'frame_0004.png', 'frame_0005.png',  'frame_0006.png',  'frame_0007.png', 'frame_0008.png', 'frame_0010.png']
                image_files = [img for img in image_files if img in specific_frames]
            elif len(image_files) > 8:
                image_files = image_files[:8] 
            else: 
                grid_size_list = list(grid_size)
                grid_size_list[1] = len(image_files)
                grid_size = tuple(grid_size_list)
        images = [Image.open(os.path.join(image_folder, img)) for img in image_files]
        print('images', images)
        print(grid_size)
        if len(images) != grid_size[0] * grid_size[1]:
            raise ValueError("Number of images does not match the grid size")

        max_width = max(image.width for image in images)
        max_height = max(image.height for image in images)
        new_im = Image.new('RGB', (max_width * grid_size[1], max_height * grid_size[0]), (255, 255, 255))
        for index, image in enumerate(images):
            row = index // grid_size[1]
            col = index % grid_size[1]
            new_im.paste(image.resize((max_width, max_height)), (col * max_width, row * max_height))


        new_im.save(self.frame)






     

