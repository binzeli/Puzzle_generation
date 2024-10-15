import json
import sys
sys.path.insert(0, '..')
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
from utils.play_game import play_game
from utils.coords_utils import coords_r2c,coords_c2r
from IPython.display import display, clear_output
import time
import json
import os
from create.create_game.tools import globals
from llama_index.tools.base import BaseToolSpec


BALL_MASS = 10.0
SCREEN_SIZE = 84
BALL_RADIUS = 4
G = 2
CANNON_WIDTH = 10.0
CANNON_HEIGHT = 7.3


class CheckToolLocation(BaseToolSpec):
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        parent_dir = os.path.dirname(current_dir)

        self.starter_json_file = os.path.join(parent_dir, ,"data", 'starts", push_start.json")
        self.predefined_actions_json = os.path.join(parent_dir, "data", "predef_actions", "PushStart", "q3.json")

    spec_functions = ["check_tool_location"]
    
    def get_collision_data(self,starter_json_file,predefined_actions_json,final_action,auto_skip=True,max_steps=80,gap_radius=6):
        with open(os.path.join(parent_dir, "create", "tool_documentation.json"), 'r') as file:
            tools_list = json.load(file)
        with open(starter_json_file, 'r') as json_file:
            starter_json = json.load(json_file)
        with open(predefined_actions_json,'r') as json_file:
            predef_actions = json.load(json_file)

        starter_name = starter_json['name']
        starter_json_str = json.dumps(starter_json)
        try:
            register_json_str(starter_json_str)
        except:
            pass

        predef_actions.append(final_action)
        final_tool = final_action[0]
        play_game(starter_name,predef_actions,auto_skip,max_steps)

        collision_data = globals.global_collision_data

        if collision_data == None:
            print("tool did not come in contact with any elements")
            return None
        
        return collision_data
    

    def check_overlap(self,tool_location):
        #rewrite this to handle each start case
        if (tool_location[0] < 45 and tool_location[0] > 5) or (tool_location[1] < 45 and tool_location[1] > 5):
            return False
        return True
    
    def check_tool_location(self, tool_id: int, location: tuple):
        """
        Pass the tool_id of the main tool and a tuple containing the x and y coordinates describing the location where the main tool must be placed.
        This function then produces boolean telling whether or not it's a gool location, as well as a string sentence stating whether this is a good location to place the object and if not, then why not.

        Coordinates should be constrained between 0 and 84 in each dimension
        Example inputs:
            "288,(48,51)"
            "345,(21,60)"

        Args:
            tool_id (int): The tool_id of the main tool we want to use.
            location (tuple): The x and y coordinates to place the main_tool at.

        """
        if not self.check_overlap():
            return False, "The tool might overlap existing objects, try a different location"
        
        final_action = [tool_id,0,location[0],location[1]]
        collision_data = self.get_collision_data(self.starter_json_file,self.predefined_actions_json,final_action)

        if collision_data == None:
            return False,"The objects do not collide with the main tool at this location and hence have no interaction. Try a different location"
        
        else:
            return True, f"The target ball comes in contact with the main tool ({tool_id}) at {collision_data['position']}, with velocity components {collision_data['velocity']}"

        
    
