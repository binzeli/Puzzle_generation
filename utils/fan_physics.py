import numpy as np
import sys
import os
current_dir = os.path.dirname(__file__)

parent_dir = os.path.dirname(current_dir)

utils_path = os.path.join(parent_dir, 'utils')

sys.path.insert(0, utils_path)
from coords_utils import edge_equations

FAN_HEIGHT = 10.0
FAN_WIDTH = 6.7

def fan_motion_exit_details(vx_0, vy_0, x_0, y_0, mass, fan_force, fan_pos, fan_angle, fan_width=FAN_WIDTH, fan_height=FAN_HEIGHT, g = 2):
    """
    Returns
    pos: tuple representing (x,y) of exit position
    V: tuple representing (V_x,V_y) at exit position
    """

    edges = edge_equations(fan_pos,fan_angle,fan_width,fan_height)

    a_x = (fan_force*np.cos(fan_angle))/mass
    a_y = (fan_force*np.sin(fan_angle))/mass - g

    def intersection_time(edge):
        m,c = edge
        if m == np.inf:
            x = edge[1]
            t = (x - x_0 - vx_0*t) / (0.5 * a_x)
            return (t,t)

        A = (m*a_x - a_y)/2
        B = (m*vx_0 - vy_0)
        C = c
        disc = B**2 - 4*A*C
        if disc >= 0:
            t1 = (-B + disc)/(2*A)
            t2 = (-B - disc)/(2*A)
            return t1,t2
        return "NEVER"

    exit_time = np.inf
    for edge in edges:
        t = intersection_time(edge)
        if t != "NEVER":
            for t_opt in t:
                if t_opt > 0:
                    exit_time = min(exit_time,t_opt)

    x = vx_0*exit_time + 0.5*a_x*(exit_time**2)
    y = vy_0*exit_time + 0.5*a_y*(exit_time**2)

    v_x = vx_0 + a_x*exit_time
    v_y = vy_0 + a_y*exit_time

    return (x,y),(v_x,v_y)
