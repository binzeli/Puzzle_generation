import math
import numpy as np
class ProjectileMotion:
    def __init__(self,g = 9.807) -> None:
        self.v_x = None
        self.v_y = None
        self.launch_pos = (0,0)
        self.g = g
        self.intial_impulse = None
    
    def init_with_v_comps(self,v_x,v_y,launch_pos):
        self.v_x = v_x
        self.v_y = v_y
        self.launch_pos = launch_pos
        disc_pos = math.sqrt(self.v_y**2 + 2*self.g*self.launch_pos[1])
        # disc_neg = -math.sqrt(self.v_y**2 + 2*g*self.launch_pos[1])
        self.flight_time = (self.v_y + disc_pos)/self.g
        self.range = self.v_x * self.flight_time
        self.max_height = self.launch_pos[1] + (self.v_y**2)/(2*self.g)
    
    def init_with_v_angle(self,v, launch_angle,launch_pos):
        self.v_x = v*math.cos(launch_angle)
        self.v_y = v*math.sin(launch_angle)
        self.init_with_v_comps(self.v_x,self.v_y,launch_pos)
    
    def init_with_impulse(self,impulse, mass, launch_angle,launch_pos):
        v = impulse / mass
        self.initial_impulse = impulse
        self.init_with_v_angle(v, launch_angle, launch_pos) 
    
    def given_x_coord(self,x):
        x = x - self.launch_pos[0]
        t = x / self.v_x
        y = self.v_y*t - 0.5*self.g*(t**2)
        v_y = self.v_y - self.g*t
        angle = np.arctan2(v_y,self.v_x)
        # if self.v_x > 0 and self.v_y < 0:
        #     approach_angle = angle + np.pi
        # elif self.v_x > 0 and self.v_y > 0:
        #     approach_angle = angle + np.pi
        # elif self.v_x < 0 and self.v_y < 0:
        #     approach_angle = np.pi + angle
        # else:
        #     approach_angle = np.pi + angle
        return x + self.launch_pos[0],y + self.launch_pos[1],np.pi + angle
    
    def find_x_dist_point(self,x,y,n,angle):
        if angle < 0:
            angle = angle + 2*np.pi
        if angle < math.pi/2:
            # new_x = x - (n+2)*math.cos(angle)
            new_x = x + n
        elif np.pi/2 <angle < np.pi:
            new_x = x - n
        elif np.pi <angle < 3*np.pi/2:
            new_x = x - n
        else:
            new_x = x + n
        # else:
        #     # new_x = x + (n+2)*math.cos(angle)
        #     new_x = x + n
        #     _,new_y,new_angle = self.given_x_coord(new_x)
        _,new_y,new_angle = self.given_x_coord(new_x)
        return new_x,new_y,new_angle
