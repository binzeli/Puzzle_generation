
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
from utils.coords_utils import coords_r2c,coords_c2r
from IPython.display import display, clear_output
import time
import json
import os
from create.create_game.tools import globals
from create.create_game.tools.ball import TargetBall, MarkerBall
from create.create_game.tools.floor import MediumFloor, Floor
from create.create_game.tools.ramp import Ramp
from create.create_game.tools.goal import GoalStar
from create.create_game.tools.cannon import Cannon
from create.create_game.tools.trampoline import Trampoline
import re


BALL_MASS = 10.0
SCREEN_SIZE = 84
BALL_RADIUS = 4
G = 2
CANNON_WIDTH = 10.0
CANNON_HEIGHT = 7.3


def extract_details(obj):
    class_name = obj.__class__.__name__
    memory_address = hex(id(obj))
    return (class_name, memory_address)


def play_game(env_name,predef_actions = [],auto_skip=False,max_steps=100, short_action = []):
    env = gym.make(f'CreateLevel{env_name}-v0')
    obs = env.reset()
    done = False
    frames = []
    frames.append(env.render('rgb_array_high_mega_changed_colors'))
    i = 0
    actions = []
    rewards = []
    overlap = False
    collided_memory_addresses = []

    while i<max_steps and not done:
        # action = env.action_space.sample()
        clear_output(wait=True)
        if len(predef_actions) > i:
            action = [predef_actions[i][0], np.float32(predef_actions[i][1]), np.float32(predef_actions[i][2])]
        actions.append(action)
        print(action)
        obs, reward, done, info = env.step(action)
        if info['overlap']:
            overlap = True
        

        collide_objects = [(extract_details(pair[0]), extract_details(pair[1])) for pair in info['collide_objects']]
        if len(short_action) > 0 and len(collide_objects) > 0: 
            for pair in collide_objects:
                tool = short_action[0][0].replace('_', '')
                if pair[0][0] == tool:
                    if len(collided_memory_addresses) == 0 or pair[0][1] not in collided_memory_addresses:
                        collided_memory_addresses.append(pair[0][1])
                        del short_action[0]
                        break
                elif pair[1][0] == tool:
                    if len(collided_memory_addresses) == 0 or pair[1][1] not in collided_memory_addresses:
                        collided_memory_addresses.append(pair[1][1])
                        del short_action[0]
                        break       

        print('short_action:', short_action)

        rewards.append(reward)
        frame = env.render('rgb_array_high_mega_changed_colors')
        frames.append(frame)
        fig2, ax2 = plt.subplots()  # Create a figure and axis for this iteration
        
        ax2.imshow(frame, cmap='viridis')  # Display the image data
        ax2.set_title(f"Iteration {i}")
        
        display(fig2)  # Explicitly display the figure
        plt.close(fig2)  # Close the figure to prevent duplicate outputs

        time.sleep(1)
        i += 1


    not_collide = False
    message = ''
    # check other tools if they collide with the ball
    if len(short_action) > 0:
        for action in short_action:
            if "Cannon" in action[0]:
                if any(abs(blue[0] - action[1]) <= 0.2 and abs(blue[1] - action[2]) <= 0.3 for blue in info['blue_ball']):
                    del short_action[0]
                    break
                if any(abs(red[0] - action[1]) <= 0.2 and abs(red[1] - action[2]) <= 0.3 for red in info['red_ball']):
                    del short_action[0]
                    break

    if overlap:
        #message += "The last tool is overlapping with another obeject in the environment, please plan the next tool again. "
        not_collide = True
    else:  
        if len(short_action) > 0:
            #message += f"No balls collide with {short_action[-1][0]} at ({short_action[-1][1]}, {short_action[-1][2]}). Please place the tool again in another side of the same object. "
            not_collide = True
        # else: 
        #     message += f"All tools collide with either the blue ball or the red ball. "

    win = False

    if(sum(rewards) > 1):
        message += "the blue ball has successfully reached the red ball. "
    else:
        message += "the blue ball has not reached the red ball. "
    if done:
        if max(rewards) > 9:
            win = True
            message += "The red ball has reached the goal. "
        else:
            message += "The red ball has not reached the goal. "

    blue = info['blue_ball']
    red = info['red_ball']
    #   check blue and red relative position:
    if blue[0][0]> red[0][0]:
        message += 'The red ball is on the right of the blue ball in the beginning. '
    else:
        message += 'the red ball is on the left of the blue ball in the beginning. '
    if blue[0][1] > red[0][1]:
        message += 'The red ball is below the blue ball in the beginning. '
    else:
        message += 'The red ball is above the blue ball in the beginning. '
    if blue[-1][0] > red[-1][0]:
        message += 'The red ball is on the right of the blue ball in the end. '
    else:
        message += 'The red ball is on the left of the blue ball in the end. '
    if blue[-1][1] > red[-1][1]:
        message += 'The red ball is below the blue ball in the end. '
    else:
        message += 'The red ball is above the blue ball in the end. '


    message += "The trajectory of the blue ball is: "
    i = 0
    while i < len(blue)-1:
        if blue[i+1][0] <= 1 and blue[i+1][0] >= -1 and blue[i+1][1] <= 1 and blue[i+1][1] >= -1:
            cur_pos = (blue[i][0], blue[i][1])
            next_pos = (blue[i+1][0], blue[i+1][1])
            if blue[i+1][0] > blue[i][0]:
                if blue[i+1][1] > blue[i][1]:
                    message += f'The blue ball is at {cur_pos} now. It moves to the left and up at {next_pos}. '
                elif blue[i+1][1] < blue[i][1]:
                    message += f'The blue ball is at {cur_pos} now. It moves to the left and down at {next_pos}. '
                else:
                    message += f'The blue ball is at {cur_pos} now. It moves horizontally to the left at {next_pos}. '
            elif blue[i+1][0] < blue[i][0]:
                if blue[i+1][1] > blue[i][1]:
                    message += f'The blue ball is at {cur_pos} now. It moves to the right and up at {next_pos}. '
                elif blue[i+1][1] < blue[i][1]:
                    message += f'The blue ball is at {cur_pos} now. It moves to the right and down at {next_pos}. '
                else:
                    message += f'The blue ball is at {cur_pos} now. It moves horizontally to the right at {next_pos}. '
            else:
                if blue[i+1][1] > blue[i][1]:
                    message += f'The blue ball is at {cur_pos} now. It moves vertically up at {next_pos}. '
                elif blue[i+1][1] < blue[i][1]:
                    message += f'The blue ball is at {cur_pos} now. It moves vertically down at {next_pos}. '
                else:
                    message += f'The blue ball is at {cur_pos} now. It remains at the same position. '
        i += 1

    message += "The trajectory of the red ball is: "
    i = 0
    while i < len(red)-1:
        if red[i+1][0] <= 1 and red[i+1][0] >= -1 and red[i+1][1] <= 1 and red[i+1][1] >= -1:
            cur_pos = (red[i][0], red[i][1])
            next_pos = (red[i+1][0], red[i+1][1])
            if red[i+1][0] > red[i][0]:
                if red[i+1][1] > red[i][1]:
                    message += f'The red ball is at {cur_pos} now. It moves to the left and up at {next_pos}. '
                elif red[i+1][1] < red[i][1]:
                    message += f'The red ball is at {cur_pos} now. It moves to the left and down at {next_pos}. '
                else:
                    message += f'The red ball is at {cur_pos} now. It moves horizontally to the left at {next_pos}. '
            elif red[i+1][0] < red[i][0]:
                if red[i+1][1] > red[i][1]:
                    message += f'The red ball is at {cur_pos} now. It moves to the right and up at {next_pos}. '
                elif red[i+1][1] < red[i][1]:
                    message += f'The red ball is at {cur_pos} now. It moves to the right and down at {next_pos}. '
                else:
                    message += f'The red ball is at {cur_pos} now. It moves horizontally to the right at {next_pos}. '
            else:
                if red[i+1][1] > red[i][1]:
                    message += f'The red ball is at {cur_pos} now. It moves vertically up at {next_pos}. '
                elif red[i+1][1] < red[i][1]:
                    message += f'The red ball is at {cur_pos} now. It moves vertically down at {next_pos}. '
                else:
                    message += f'The red ball is at {cur_pos} now. It remains at the same position. '
        i += 1
    
    if info['goal'][0] < red[-1][0]:
        message += 'The goal is on the right of the red ball in the end. '
    else:
        message += 'The goal is on the left of the red ball in the end. '


    def update(i):
        ax.imshow(frames[i])

    fig, ax = plt.subplots(1,1)

    ani = matplotlib.animation.FuncAnimation(fig, update, frames=len(frames))

    return ani, message, not_collide