from .segment import LINE_THICKNESS
from .ramp import Ramp
import pygame as pg
import numpy as np
from .basic_obj import BasicObj
from .img_tool import ImageTool
from .gravity_obj import MOVING_OBJ_COLLISION_TYPE
from . import globals


TRAMPOLINE_ELASTICITY = 1.2

def trampoline_collision_get_ball_data(arbiter, space, data):
    ball = arbiter.shapes[0]
    # print("Ball details on collison with trampoline: ")
    # print("position = ",ball.body.position)
    # print("velocity = ",ball.body.velocity)
    globals.global_collision_data = {'position': ball.body.position, 'velocity': ball.body.velocity}
        
    return True

class Trampoline(Ramp):
    def __init__(self, pos, length, angle, elasticity=TRAMPOLINE_ELASTICITY, friction=1.0):
        if angle > np.pi/2:
            self.actual_angle = angle + np.pi
        else:
            self.actual_angle = angle

        self.angle = angle
        self.length = length

        super().__init__(pos, length, self.actual_angle, friction, elasticity)


    def add_to_space(self, space):
        super().add_to_space(space, use_friction=False)
        self.img = ImageTool('trampoline.png', self.actual_angle,
                self.pos[:],
                debug_render=False,
                use_shape=self.shape)
        trampoline = self.img.get_shape()
        trampoline.collision_type = 1
        # trampoline.sensor = True
        # space.add(trampoline)
        handler = space.add_collision_handler(MOVING_OBJ_COLLISION_TYPE,1)
        handler.begin = trampoline_collision_get_ball_data


    def render(self, screen, scale=None, anti_alias=False):
        if scale is None:
            scale = 1

        self.img.render(screen, scale, self.flipy)


# The sizes refer to the power of the bounce.

class MediumTrampoline(Trampoline):
    def __init__(self, pos, elasticity=TRAMPOLINE_ELASTICITY):
        super().__init__(pos, length=16.0, angle=0.0, elasticity=elasticity)
        self.color = 'purple'


class Trampoline45(Trampoline):
    def __init__(self, pos):
        super().__init__(pos, length=16.0, angle=np.pi/4)
        self.color = 'purple'


class ReverseTrampoline45(Trampoline):
    def __init__(self, pos):
        super().__init__(pos, length=16.0, angle=-np.pi/4)
        self.color = 'purple'

class VerticalTrampoline(Trampoline):
    def __init__(self, pos):
        super().__init__(pos, length=16.0, angle=np.pi/2)
        self.color = 'purple'
