
# Import `create_game` package, wherever it is located for you. 
import sys
sys.path.insert(0, '/home/bili/Desktop/scenario_generation_llm')
from create.create_game import register_json_folder, register_json_str
from create.create_game.create_game import CreateGame

# Set the matplotlib settings for rendering the result video to the notebook.
# See the comment at the bottom for more information. 
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
from utils.play_game import play_game
import copy
import cv2

def convert_to_frames():
        """
        This function converts the simulation to frames.
        It does not take any inputs.
        """
        frames_path = "/home/bili/Desktop/scenario_generation_llm/frames"
        animation_path = "/home/bili/Desktop/scenario_generation_llm/ani_10.mp4"

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
        for filename in os.listdir(frames_path):
            file_path = os.path.join(frames_path, filename)
            os.unlink(file_path)

        extract_frames(animation_path, frames_path, frame_rate = 1)


def main():
    
    i =10
    with open(f'/home/bili/Desktop/scenario_generation_llm/example_puzzle_layout.json', 'r') as f:
        data = json.load(f)

    json_str = json.dumps(data)
    register_json_str(json_str)


    predef = [[2365, 0, 0] for _ in range(100)]
    predef[0] =  [1710, -0.6, -1]
    short_action = []
    tools_list_path = "/home/bili/Desktop/gen_env_llm/create/tool_documentation.json"
    with open(tools_list_path, 'r') as file:
            tools_list = json.load(file)["tools"]
    for i in range(len(predef)):
        if predef[i][0] != 2365:
            new_action = copy.deepcopy(predef[i])
            new_action[0] = tools_list[predef[i][0]]['tool_type']
            short_action.append(new_action)
    animation, message, not_collide  = play_game("NavigateStart",predef_actions=predef, short_action=short_action)
    print(message)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, f'simulation.mp4')
    animation.save(output_path,fps=1)
    convert_to_frames()

if __name__ == "__main__":
    main()
