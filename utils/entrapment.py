import numpy as np
import sys
sys.path.insert(0,'/home/bili/Desktop/gen_env_llm/utils')
from projectile_motion import ProjectileMotion
import os
from coords_utils import coords_c2r,coords_r2c

RAMP_THICKNESS = 0.5

def entrapment(goal_x, distance_to_goal_approx, projectileMotion: ProjectileMotion,gap_radius=6,max_length_ramp = 100,start_id = 0):
    env_objects = []
    goal_x,goal_y,goal_approach_angle = projectileMotion.given_x_coord(goal_x)
    gap_x,gap_y,gap_approach_angle = projectileMotion.find_x_dist_point(goal_x,goal_y,distance_to_goal_approx,goal_approach_angle)
    if gap_approach_angle < 0 :
        gap_approach_angle += 2*np.pi
    if 0 < gap_approach_angle < np.pi/2:
        ramp_angle = gap_approach_angle + np.pi/2
    elif np.pi/2 < gap_approach_angle < np.pi:
        ramp_angle = gap_approach_angle  - np.pi/2
    elif np.pi < gap_approach_angle < 3*np.pi/2:
        ramp_angle = gap_approach_angle - np.pi/2
    else:
        ramp_angle = gap_approach_angle + np.pi/2 - 2*np.pi
    # ramp_angle = np.pi /2 - (2 * np.pi  - gap_approach_angle)
    # if ramp_angle < 0:
    #     ramp_angle += 2*np.pi
    # if ramp_angle <= np.pi:
    #     ramp_write_angle = ramp_angle
    # else:
    #     ramp_write_angle = ramp_angle - np.pi
    ramp_write_angle = ramp_angle
    
    #ramp_reaching_goal_y
    l = np.abs((gap_y - goal_y)/np.sin(ramp_angle)) - gap_radius
    if l > max_length_ramp: #cut the ramp short and finish it with a vertical wall
        l = max_length_ramp
        # vertical wall to augment vert ramp
        if ramp_angle <= np.pi:
            ramp_reach_y = (gap_y - (gap_radius + l)*np.sin(ramp_angle))
            wall_vert_l = np.abs(ramp_reach_y - goal_y)
            wall_vert_y = ramp_reach_y - (wall_vert_l/2) - 2
        else:
            ramp_reach_y = gap_y + (gap_radius + l)*np.sin(ramp_angle)
            wall_vert_l = np.abs(ramp_reach_y - goal_y)
            wall_vert_y = ramp_reach_y + (wall_vert_l/2) + 2
        if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
            wall_vert_x = gap_x - (gap_radius + l)*np.cos(ramp_angle) + 2
        else:
            wall_vert_x = gap_x + (gap_radius + l)*np.cos(ramp_angle) + 2
        # env_objects.append(f'{{\n\t"name": "wall",\n\t"pos": "[{coords_r2c(wall_vert_x)}, {coords_r2c(wall_vert_y)}]",\n\t"length": {wall_vert_l},\n\t"id": {start_id}\n}}')
        env_objects.append({"name":"wall","pos":str([coords_r2c(wall_vert_x), coords_r2c(wall_vert_y)]),"length":wall_vert_l,"id":start_id})
        start_id += 1
    
    if l > 0:
        # if ramp_angle <= np.pi:
        if 0 < gap_approach_angle <= np.pi/2:
            ra = np.pi - ramp_angle
            ramp_vert_y = gap_y - (gap_radius + l/2)*np.sin(ra)
            ramp_vert_x = gap_x + (gap_radius + l/2)*np.cos(ra)
            
        elif np.pi/2 <= gap_approach_angle <= np.pi:
            ra = ramp_angle
            ramp_vert_y = gap_y - (gap_radius + l/2)*np.sin(ramp_angle)
            ramp_vert_x = gap_x - (gap_radius + l/2)*np.cos(ramp_angle)
        elif  np.pi <= gap_approach_angle <= (3*np.pi)/2:
            ra = np.pi - ramp_angle
            ramp_vert_y = gap_y + (gap_radius + l/2)*np.sin(ra)
            ramp_vert_x = gap_x - (gap_radius + l/2)*np.cos(ra)  
        else:
            ra = ramp_angle
            ramp_vert_y = gap_y + (gap_radius + l/2)*np.sin(ra)
            ramp_vert_x = gap_x + (gap_radius + l/2)*np.cos(ra)
            
        # ramp_vert_y = gap_y - (gap_radius + l/2)*np.sin(ramp_angle)
        # # else:
        # #     ramp_vert_y = gap_y + (gap_radius + l/2)*np.sin(ramp_angle)
        # if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
        #     ramp_vert_x = gap_x - (gap_radius + l/2)*np.cos(ramp_angle)
        # else:
        #     ramp_vert_x = gap_x + (gap_radius + l/2)*np.cos(ramp_angle)
        # env_objects.append(f'{{\n\t"name": "ramp",\n\t"pos": "[{coords_r2c(ramp_vert_x)}, {coords_r2c(ramp_vert_y)}]",\n\t"length": {l},\n\t"angle": {ramp_angle},\n\t"id": {start_id}\n}}')
        env_objects.append({"name":"ramp","pos":str([coords_r2c(ramp_vert_x), coords_r2c(ramp_vert_y)]),"length":l,"angle": ramp_write_angle,"id":start_id,"thickness": RAMP_THICKNESS})
        start_id += 1
    
    #vert end floor
    tot_reach_x = gap_x - (gap_radius + l/2)*np.cos(ramp_angle)
    # floor_len = np.abs(goal_x - tot_reach_x)-2
    floor_len = np.abs(goal_x - tot_reach_x)
    if 0 < gap_approach_angle <= np.pi/2:
        floor_x = goal_x + floor_len/2
        floor_y = goal_y - gap_radius
    elif np.pi/2 <= gap_approach_angle <= np.pi:
        floor_x = goal_x - floor_len/2
        floor_y = goal_y - gap_radius
    elif np.pi <= gap_approach_angle <= (3*np.pi)/2:
        floor_x = goal_x - floor_len/2
        floor_y = goal_y + gap_radius
    else:
        floor_x = goal_x + floor_len/2
        floor_y = goal_y + gap_radius
    # if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
    #     # floor_x = goal_x - floor_len/2 - 1
    #     floor_x = goal_x - floor_len/2
    # else:
    #     # floor_x = goal_x + floor_len/2 + 1
    #     floor_x = goal_x + floor_len/2
    # if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
        # tot_reach_x = gap_x - (gap_radius + l/2)*np.cos(ramp_angle)
        # floor_len = np.abs(goal_x - tot_reach_x)-2
        # floor_x = goal_x - floor_len/2 - 1
    # else:
    #     tot_reach_x = gap_x + (gap_radius + l/2)*np.cos(ramp_angle)
    #     floor_len = np.abs(goal_x - tot_reach_x)-2
    #     floor_x = goal_x + floor_len/2 + 1
    
    # if ramp_angle <= np.pi:
    #     floor_y = goal_y - gap_radius
    # else:
    #     floor_y = goal_y + gap_radius
    # env_objects.append(f'{{\n\t"name": "floor",\n\t"pos": "[{coords_r2c(floor_x)}, {coords_r2c(floor_y)}]",\n\t"length": {floor_len},\n\t"id": {start_id}\n}}')
    env_objects.append({"name":"floor","pos":str([coords_r2c(floor_x), coords_r2c(floor_y)]),"length":floor_len,"id":start_id})
    start_id += 1
    
    # ramp reaching goal_x
    l = np.abs((gap_x - goal_x)/np.cos(ramp_angle)) - gap_radius
    if l > max_length_ramp: #cut the ramp short and finish it with a horizontal wall
        l = max_length_ramp
        # horizontal ceil to augment vert ramp
        if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
            ramp_reach_x = (gap_x + (gap_radius + l)*np.cos(ramp_angle))
            ceil_horz_l = np.abs(ramp_reach_x - goal_x)
            ceil_horz_x = ramp_reach_x + (ceil_horz_l/2) + 2
        else:
            ramp_reach_x = gap_x - (gap_radius + l)*np.cos(ramp_angle)
            ceil_horz_l = np.abs(ramp_reach_x - goal_x)
            ceil_horz_x = ramp_reach_x - (ceil_horz_l/2) - 2
        if ramp_angle <= np.pi:
            ceil_horz_y = gap_y + (gap_radius + l)*np.sin(ramp_angle) + 2
        else:
            ceil_horz_y = gap_y - (gap_radius + l)*np.sin(ramp_angle) - 2
        # env_objects.append(f'{{\n\t"name": "floor",\n\t"pos": "[{coords_r2c(ceil_horz_x)}, {coords_r2c(ceil_horz_y)}]",\n\t"length": {ceil_horz_l},\n\t"id": {start_id}\n}}')
        env_objects.append({"name":"floor","pos":str([coords_r2c(ceil_horz_x), coords_r2c(ceil_horz_y)]),"length":ceil_horz_l,"id":start_id})
        start_id += 1
    
    if l > 0:
        if 0 < gap_approach_angle <= np.pi/2:
            ra = np.pi - ramp_angle
            ramp_horz_y = gap_y + (gap_radius + l/2)*np.sin(ra)
            ramp_horz_x = gap_x - (gap_radius + l/2)*np.cos(ra)
        elif np.pi/2 <= gap_approach_angle <= np.pi:
            ra = ramp_angle
            ramp_horz_y = gap_y + (gap_radius + l/2)*np.sin(ra)
            ramp_horz_x = gap_x + (gap_radius + l/2)*np.cos(ra)
        elif  np.pi <= gap_approach_angle <= (3*np.pi)/2:
            ra = np.pi - ramp_angle
            ramp_horz_y = gap_y - (gap_radius + l/2)*np.sin(ra)
            ramp_horz_x = gap_x + (gap_radius + l/2)*np.cos(ra)  
        else:
            ra = ramp_angle
            ramp_horz_y = gap_y - (gap_radius + l/2)*np.sin(ra)
            ramp_horz_x = gap_x - (gap_radius + l/2)*np.cos(ra)
        # ramp_horz_y = gap_y + (gap_radius + l/2)*np.sin(ramp_angle)
        # ramp_horz_x = gap_x + (gap_radius + l/2)*np.cos(ramp_angle)
        # if ramp_angle <= np.pi:
        #     ramp_horz_y = gap_y + (gap_radius + l/2)*np.sin(ramp_angle)
        # else:
        #     ramp_horz_y = gap_y - (gap_radius + l/2)*np.sin(ramp_angle)
        # if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
        #     ramp_horz_x = gap_x + (gap_radius + l/2)*np.cos(ramp_angle)
        # else:
        #     ramp_horz_x = gap_x - (gap_radius + l/2)*np.cos(ramp_angle)
        # env_objects.append(f'{{\n\t"name": "ramp",\n\t"pos": "[{coords_r2c(ramp_horz_x)}, {coords_r2c(ramp_horz_y)}]",\n\t"length": {l},\n\t"angle": {ramp_angle},\n\t"id": {start_id}\n}}')
        env_objects.append({"name":"ramp","pos":str([coords_r2c(ramp_horz_x), coords_r2c(ramp_horz_y)]),"length":l,"angle": ramp_write_angle,"id":start_id,"thickness":RAMP_THICKNESS})
        start_id += 1

    #horz end wall
    tot_reach_y = gap_y + (gap_radius + l)*np.sin(ramp_angle)
    wall_len = np.abs(goal_y - tot_reach_y)
    if 0 < gap_approach_angle <= np.pi/2:
        wall_y = goal_y + wall_len/2
        wall_x = goal_x - gap_radius
    elif np.pi/2 <= gap_approach_angle <= np.pi:
        wall_y = goal_y + wall_len/2
        wall_x = goal_x + gap_radius
    elif  np.pi <= gap_approach_angle <= (3*np.pi)/2:
        wall_y = goal_y - wall_len/2
        wall_x = goal_x + gap_radius  
    else:
        wall_y = goal_y - wall_len/2
        wall_x = goal_x - gap_radius
    # if ramp_angle <= np.pi:
    #     # tot_reach_y = gap_y + (gap_radius + l)*np.sin(ramp_angle)
    #     # wall_len = np.abs(goal_y - tot_reach_y)
    #     # wall_y = goal_y + wall_len/2 + 1
    #     wall_y = goal_y + wall_len/2
    
    # else:
    #     # tot_reach_y = gap_y - (gap_radius + l)*np.sin(ramp_angle)
    #     # wall_len = np.abs(goal_y - tot_reach_y)
    #     # wall_y = goal_y - wall_len/2 - 1
    #     wall_y = goal_y - wall_len/2
    
    # if ramp_angle <= np.pi/2 or ramp_angle >= 3*(np.pi/2):
    #     wall_x = goal_x + gap_radius
    
    # else:
    #     wall_x = goal_x - gap_radius
    
    # env_objects.append(f'{{\n\t"name": "wall",\n\t"pos": "[{coords_r2c(wall_x)}, {coords_r2c(wall_y)}]",\n\t"length": {wall_len},\n\t"id": {start_id}\n}}')
    env_objects.append({"name":"wall","pos":str([coords_r2c(wall_x), coords_r2c(wall_y)]),"length":wall_len,"id":start_id})
    start_id += 1

    return env_objects


