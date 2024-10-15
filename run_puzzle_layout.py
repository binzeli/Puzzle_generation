 
import gym
from PIL import Image
from create.create_game import register_json_folder, register_json_str
import json

starter_json_file =  "/home/bili/Desktop/scenario_generation_llm/example_puzzle_layout.json"
visualization_path = "/home/bili/Desktop/scenario_generation_llm/example_puzzle.jpg"
with open(starter_json_file, 'r') as json_file:
            env_json = json.load(json_file)
starter_json_str = json.dumps(env_json)
register_json_str(starter_json_str)

env_name = env_json['name']
env = gym.make(f'CreateLevel{env_name}-v0')
env.reset()
frame = env.render('rgb_array_high_mega_changed_colors')
Image.fromarray(frame).save(visualization_path)
env.close()