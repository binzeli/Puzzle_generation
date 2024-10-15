import numpy as np
import sys
import os
current_dir = os.path.dirname(__file__)

parent_dir = os.path.dirname(current_dir)

utils_path = os.path.join(parent_dir, 'utils')

sys.path.insert(0, utils_path)

def trampoline_exit_details(trampoline_angle, v0_x, v0_y, trampoline_elasticity):
    if trampoline_angle > np.pi/2:
        trampoline_angle = np.pi - trampoline_angle
    v0_perp = v0_x*np.sin(trampoline_angle) + v0_y*np.cos(trampoline_angle)
    v0_parr = v0_x*np.cos(trampoline_angle) - v0_y*np.sin(trampoline_angle)

    v1_perp = -v0_perp*trampoline_elasticity
    v1_parr = v0_parr

    v1_x = v1_perp*np.sin(trampoline_angle) + v1_parr*np.cos(trampoline_angle)
    v1_y = v1_perp*np.cos(trampoline_angle) - v1_parr*np.sin(trampoline_angle)
    # v1_x = v1_parr*np.cos(-trampoline_angle) - v1_perp*np.sin(-trampoline_angle)
    # v1_y = v1_parr*np.sin(-trampoline_angle) + v1_perp*np.cos(-trampoline_angle)

    return v1_x,v1_y