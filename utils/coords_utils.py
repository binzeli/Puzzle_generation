import numpy as np
from typing import Sequence

def coords_c2r(x,screen_size=84):
    # if x > 1:
    #     print("Warning: may be using wrong function")
    res_list = []
    if isinstance(x,Sequence):
        for ele in x:
            res_list.append(((ele + 1)/2 )* screen_size)
        return type(x)(res_list)
    return ((x + 1)/2 )* screen_size

def coords_r2c(x,screen_size=84):
    # if np.abs(x) < 1 :
    #     print("Warning: may be using wrong function, r2c used")
    res_list = []
    if isinstance(x,Sequence):
        for ele in x:
            res_list.append((ele/screen_size)*2 - 1)
        return type(x)(res_list)
    return (x/screen_size)*2 - 1

def get_object_boundary_points(pos, angle, width, height):
    x1,y1 = width/2,height/2
    x2,y2 = -width/2,height/2
    x3,y3 = -width/2,-height/2
    x4,y4 = width/2,-height/2
    def transform_point(X, Y):
        X_translated = X + pos[0]
        Y_translated = Y + pos[1]
        # Rotate point to align with the X,Y axis
        X_out = X_translated * np.cos(angle) - Y_translated * np.sin(angle)
        Y_out = X_translated * np.sin(angle) + Y_translated * np.cos(angle)

        return X_out, Y_out
    final_points = [transform_point(x1,y1),transform_point(x2,y2),transform_point(x3,y3),transform_point(x4,y4)]
    return final_points

def edge_equations(pos, angle, width, height):
    def find_edge(point1,point2):
        x1,y1 = point1
        x2,y2 = point2
        if x2-x1 == 0:
            return np.inf,x1
        m = (y2-y1)/(x2-x1)
        c = y1 - m*x1
        return m,c

    final_points = get_object_boundary_points(pos, angle, width, height)
    edges = [find_edge(final_points[0],final_points[1]),find_edge(final_points[1],final_points[2]),find_edge(final_points[2],final_points[3]),find_edge(final_points[3],final_points[1])]
    return edges

def is_point_inside_non_aligned_rectangle(x0, y0, edges):
    """
    Check if a point is inside a non-axis-aligned rectangle.

    Parameters:
    - x0, y0: Coordinates of the point.
    - edges: A list of tuples representing the edges of the rectangle. Each tuple is (m, b) where m is the slope and b is the y-intercept of an edge.

    Returns:
    - True if the point is inside the rectangle, False otherwise.
    """
    sign_changes = 0
    for i, edge in enumerate(edges):
        m, b = edge
        y_predicted = m * x0 + b
        # Determine if the point is above or below the edge
        above = y0 > y_predicted
        
        # Compare with the next edge to determine if the point is "inside" between them
        next_edge = edges[(i + 1) % len(edges)]
        m_next, b_next = next_edge
        y_next_predicted = m_next * x0 + b_next
        next_above = y0 > y_next_predicted
        
        # If the point transitions from being above one edge to below the next (or vice versa), it's crossing an edge
        if above != next_above:
            sign_changes += 1
    
    # For a simple rectangle, there should be 2 sign changes: entering and exiting the enclosed area
    return sign_changes == 2
