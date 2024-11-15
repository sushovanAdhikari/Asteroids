from decimal import Decimal, getcontext
from constants import screen_height, WHITE, YELLOW, RED, ORANGE, GREEN, DARK_GRAY, LIGHT_GRAY
import math as m
import random


# Set decimal precision to a higher value
getcontext().prec = 10  # Adjust precision as needed

def calculate_slope(x1, y1, x2, y2):
    m = (y2 - y1) / (x2 - x1)
    return m

def find_b(x1, y1, x2, y2):
    m = calculate_slope(x1, y1, x2, y2)
    b = y1 - m * x1
    return b

def find_x_intercept(b, m):
    x = -b/m
    return x

def x_axis_point(x1, y1, x2, y2):
    x1, y1, x2, y2 = Decimal(x1), Decimal(y1), Decimal(x2), Decimal(y2)
    b = find_b(x1, y1, x2, y2)
    m = calculate_slope(x1, y1, x2, y2)
    x_intercept = round(find_x_intercept(b, m), 2)
    return [float(x_intercept), 0]

def y_axis_point(x1, y1, x2, y2):
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
    b = find_b(x1, y1, x2, y2)
    y_intercept = round(b, 2)
    return [0, float(y_intercept)]

def dist(x0, y0, x1, y1):
    dist = m.sqrt((x1 - x0)*(x1 - x0) + (y1 - y0)*(y1 - y0))
    return dist

def deg2rad(deg):
    rad = deg * (3.14159/180.0)
    return rad

def rotate_me(xc, yc, degrees, x0, y0):
    myRadius = dist(xc, yc, x0, y0)
    radAng = deg2rad(degrees)
    xr = xc + myRadius*m.cos(radAng)
    yr = yc + myRadius*m.sin(radAng)
    return xr, yr

def orient_me(x0, y0):
    x = x0
    y = screen_height - y0
    return x, y


def generate_circle_points(center, radius = 50, num_points = 360):

    # Calculate the points on the circle
    points = []
    for i in range(num_points):
        # Calculate the angle in radians
        angle = 2 * m.pi * i / num_points
        
        # Calculate the (x, y) position on the circle using sine and cosine
        x = int(center[0] + radius * m.cos(angle))
        y = int(center[1] + radius * m.sin(angle))
        
        # Append the point to the list
        points.append((x, y))
    
    for i, (x, y) in enumerate(points):
        points[i] = orient_me(x,y)
    
    return points

def get_random_color():
    colors = [WHITE, YELLOW, RED, ORANGE, GREEN, DARK_GRAY, LIGHT_GRAY]
    pick = random.choice(colors)
    return pick

def orientation(p, q, r):
    """ Calculate the orientation of the triplet (p, q, r) """
    return (r[1] - p[1]) * (q[0] - p[0]) - (r[0] - p[0]) * (q[1] - p[1])

def on_segment(p, q, r):
    """ Check if point q lies on the segment pr """
    return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])

def do_intersect(p1, q1, p2, q2):
    """ Check if line segments p1q1 and p2q2 intersect """
    # Find the four orientations needed for the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if o1 * o2 < 0 and o3 * o4 < 0:
        return True

    # Special case: Checking if the points are collinear
    if o1 == 0 and on_segment(p1, p2, q1): return True
    if o2 == 0 and on_segment(p1, q2, q1): return True
    if o3 == 0 and on_segment(p2, p1, q2): return True
    if o4 == 0 and on_segment(p2, q1, q2): return True

    # Otherwise, the segments do not intersect
    return False