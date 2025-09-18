import pygame as p
import math as m
import random
from generic_functions import y_axis_point, deg2rad, dist, orient_me, generate_circle_points, get_random_color, do_intersect
from constants import screen_width, screen_height, WHITE, BLACK, YELLOW, RED, ORANGE, GREEN
import logging
from logger import setup_logging
import time

ship_top_point = [30,0]
ship_btm_left = [-10,15]
ship_btm_right = [-10, -15]
ship_left_intercept_point = y_axis_point(*(ship_top_point + ship_btm_left))
ship_right_intercept_point = y_axis_point(*(ship_btm_right + ship_top_point))

points = [ship_top_point, ship_btm_left, ship_left_intercept_point, ship_right_intercept_point, ship_btm_right]


class SpaceShip:
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.velocity = 0
        self.color = get_random_color()
        self.lives = 3
        self.score = 0
        self.destroyed = False
        self.respawn = False

        self.heading = heading
        self.ship_points = points

        xc = yc = 0
        for sp in (self.ship_points):
            xc = xc + sp[0]
            yc = yc + sp[1]
        n = len(self.ship_points)
        xc = xc/n # calculating centroid
        yc = yc/n # calculating centroid
        self.xc = xc 
        self.yc = yc
        self.vertices = []
        self.update_vertices()
        self.bullets = []
        self.last_shot_time = 0  # Track the time of the last shot
        self.shot_delay = 0.3  # Cooldown time between shots (in seconds)
        self.hit_displacement = []
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 60
        self.under_protection = False
        self.protection_duration = self.hit_duration * 10
        self.protection_timer = 0
        print("init - xc = "+str(xc)+" yc = "+str(yc))
        # self.rocket = p.mixer.Sound('mixkit_rocket.wav')  # courtesy of mixkit.co
        return
    
    def update(self):
        if self.is_hit:        
            self.vertices = [
                (vx + dx, vy + dy) 
                for (vx, vy), (dx, dy) in zip(self.vertices, self.hit_displacement)
            ]
            self.hit_timer += 1
            
            # End the hit effect
            if self.hit_timer > self.hit_duration and not self.destroyed:
                self.is_hit = False
                self.hit_timer = 0
                self.reset_for_respawn()
        else:
            if self.under_protection:
                self.protection_timer += 1
                if self.protection_timer > self.protection_duration:
                    self.under_protection = False
                    self.protection_timer = 0

            self.update_vertices()
            # Regular movement logic
            self.move_me()
            self.update_position()
            self.update_bullets()
    
    def trigger_hit_effect(self):
        """ Start the hit animation and calculate displacement directions for vertices. """
        self.lose_life()
        self.is_hit = True
        self.original_vertices = self.vertices[:]
        self.hit_displacement = []

        # Calculate outward displacement vectors for each vertex
        for vx, vy in self.vertices:
            angle = m.atan2(vy - self.y, vx - self.x)
            dx = m.cos(angle) * 2  # Displacement speed
            dy = m.sin(angle) * 2
            self.hit_displacement.append((dx, dy))

    def protective_shield(self, extend_protection = False):
        if extend_protection:
            self.protection_timer = 0
        self.under_protection = True
    
    def reset_for_respawn(self):
        self.x, self.y, self.heading = screen_width//2, screen_height//2, 90
        self.update_vertices()
        self.bullets = []
        self.respawn = False
    
    def lose_life(self):
        """ Reduces one life from the spaceship. """
        if self.lives > 0:
            self.lives -= 1
            self.respawn = True
            print(f"Lives remaining: {self.lives}")
        if self.lives == 0:
            self.destroy()  # Call a method to handle game-over or respawn logic

    def destroy(self):
        """ Handle the spaceship's destruction when lives reach zero. """
        self.respawn = False
        self.destroyed = True
        print("Game Over!")
        # Add code to end the game or respawn the spaceship
    
    def update_position(self):
        # Screen wrapping logic for the ship's center position
        if self.x < 0:  # Left edge
            self.x = screen_width
            print("Wrapped to right edge")
        elif self.x > screen_width:  # Right edge
            self.x = 0
            print("Wrapped to left edge")

        if self.y < 0:  # Top edge
            self.y = screen_height
            print("Wrapped to bottom edge")
        elif self.y > screen_height:  # Bottom edge
            self.y = 0
            print("Wrapped to top edge")

    def get_position(self):
        return (self.x, self.y)

    def brake_me_down(self):
        self.velocity = 0
    
    def move_me(self):
        hRad = deg2rad(self.heading)
        self.x = self.x + self.velocity*m.cos(hRad)
        self.y = self.y + self.velocity*m.sin(hRad)
        self.update_vertices()
        return
    
    def turn_me(self, inc):
        self.heading = self.heading + inc
        if (self.heading > 359):
            self.heading = 0
        if (self.heading < 0):
            self.heading = 359
        return
    
    def fix_point(self, p):
        x = p[0]
        y = p[1]
        x = x + self.x
        y = y + self.y
        x, y = orient_me(x, y)
        fixed = [int(x), int(y)]
        return fixed
    
    def update_vertices(self):
        self.vertices = []
        r = []
        # Rotate the ship points to the correct heading.
        for my_point in (self.ship_points):
            
            x0 = my_point[0]
            y0 = my_point[1]
            myRadius = dist(self.xc, self.yc, x0, y0)
            theta = m.atan2(y0 - self.yc, x0 - self.xc)
            radAng = deg2rad(self.heading)
            
            xr = round(self.xc + myRadius*m.cos(radAng+theta), 2)
            yr = round(self.yc + myRadius*m.sin(radAng+theta), 2)
            
            rp = [xr, yr]
            
            r.append(rp)
            
        # Draw the points, translate to location of ship.     
        n = len(self.ship_points)
        for j in range(1, n):
            p0 = r[j-1]
            p1 = r[j]

            d0 = self.fix_point(p0)
            d1 = self.fix_point(p1)
    
            self.vertices.append(d0)
            self.vertices.append(d1)
        
        p0 = r[n-1]
        p1 = r[0]
       
        d0 = self.fix_point(p0)
        d1 = self.fix_point(p1)
        
        self.vertices.append(d0)
        self.vertices.append(d1)


    def speed_me_up(self, inc):
        # self.rocket.play()
        self.velocity = self.velocity + inc
        if (self.velocity > 3):
            self.velocity = 3
        elif (self.velocity < 0):
            self.velocity = 0
        return
    
    def fire_bullet(self):
        """ Fire a bullet from the spaceship's nose, with a cooldown. """
        current_time = time.time()  # Get the current time
        
        # Check if enough time has passed since the last shot
        if current_time - self.last_shot_time >= self.shot_delay:
            # Get the position of the spaceship's nose (the first point in the vertices)
            nose_x, nose_y = self.vertices[0]

            # Create a new Bullet instance
            bullet = Bullet(nose_x, nose_y, self.heading, velocity=5)

            # Add the bullet to the spaceship's list of bullets
            self.bullets.append(bullet)

            # Update the last shot time to the current time
            self.last_shot_time = current_time

    def update_bullets(self):
        """ Update the positions of all bullets and remove off-screen bullets. """
        for bullet in self.bullets[:]:
            if bullet.update_position():
                self.bullets.remove(bullet)  # Remove the bullet if it goes off-screen
    

class Asteroid:
    def __init__(self, screen_width, screen_height, position = None, radius = None, velocity = None, color = None, vitamin = False, log_file='asteroid.log'):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.radius = random.randint(20, 50) if not radius else radius
        self.position = self.get_random_edge_position() if not position else position
        self.x = self.position[0]
        self.y = self.position[1]
        print(f"Position at {self.position}")  # Debugging: check position coordinates
        self.velocity = self.get_inward_velocity() if not velocity else velocity
        self.vertices_state = {}
        self.vertices = self.generate_vertices()
        self.off_screen = False
        self.logger = setup_logging(log_file, 'asteroid_logger')
        self.color = get_random_color() if not color else color
        self.vitamin_asteroid = vitamin
        # Log the initialization message
        self.logger.debug(f'Initialized {self!r}')

    def __repr__(self):
        return f'Asteroid({self.screen_width, self.screen_height}) | id: {id(self)} | position:{self.position} | velocity: {self.velocity} | vertices: {self.vertices}'
        ...

    def log_message(self, message):
        self.logger.debug(f'{message}: {self!r}')

    def get_position(self):
        return self.position
    
    def split_asteroid(self):
        """ Split the asteroid into smaller fragments """
        fragments = []
        
        if self.radius > 30:  # Only split if the asteroid is large enough
            num_fragments = 2  # Create two fragments
            off_set_value = self.radius
            position_offsets = [(-off_set_value, -off_set_value), (off_set_value, off_set_value)]
            angle_base = m.atan2(self.velocity[1], self.velocity[0])
            
            for i in range(num_fragments):
                # Each fragment is half the size of the original
                new_radius = self.radius * 0.5

                if new_radius < 15:  # Limit smallest size to avoid endless splitting
                    continue
                
                # Slightly randomize the angle for each fragment’s velocity
                angle_variation = angle_base + (random.uniform(-0.5, 0.5) if i == 0 else random.uniform(0.5, 1.0))
                new_velocity = (
                    self.velocity[0] * m.cos(angle_variation) - self.velocity[1] * m.sin(angle_variation),
                    self.velocity[0] * m.sin(angle_variation) + self.velocity[1] * m.cos(angle_variation)
                    )
                
                # Offset new position slightly to prevent overlapping
                position_offset = position_offsets[i]
                new_position = [
                    self.position[0] + position_offset[0],
                    self.position[1] + position_offset[1]
                ]
                
                # Create a new asteroid fragment
                fragment = Asteroid(self.screen_width, self.screen_height, position = new_position, radius = new_radius, velocity = new_velocity)
                fragment.log_message(f'Collision Created Asteroid')
                fragments.append(fragment)

        return fragments
    

    def get_inward_velocity(self):
            # Target the screen center
            center_x = self.screen_width / 2
            center_y = self.screen_height / 2

            # Calculate the direction vector towards the center
            dx = center_x - self.position[0]
            dy = center_y - self.position[1]
            
            # Calculate the distance to the center
            distance = m.sqrt(dx ** 2 + dy ** 2)

            # Normalize the direction vector and scale it to a reasonable speed
            speed = random.uniform(1.5, 2.5)  # Control speed range for asteroids
            vx = (dx / distance) * speed
            vy = (dy / distance) * speed
            
            # Add a slight random variation to the velocity to make it less uniform
            vx += random.uniform(-0.5, 0.5)
            vy += random.uniform(-0.5, 0.5)

            return [vx, vy]

    def select_circle_points(self):
        num_points = 360
        selected_points = []
        min_interval = 36
        max_interval = 50
        # Initialize the list of selected points and starting point
        selected_points = []
        current_point = 0

        while current_point < num_points:
            selected_points.append(current_point)
            
            # Randomly select an interval between 36 and 50
            interval = random.randint(min_interval, max_interval)
            
            # Update current point
            current_point += interval
            
            # Check if the next point is within the range
            if current_point >= num_points:
                break
        return selected_points
    
    def calculate_circle_point(self, radius, point, total_points):
        angle = 2 * m.pi * point / total_points
        x_one = int(self.position[0] + radius * m.cos(angle))
        y_one = int(self.position[1] + radius * m.sin(angle))
        return (x_one, y_one)


    def generate_vertices(self):
        options = [0, 10, -10]
        if len(self.vertices_state) != 0:
            chosen_points = self.vertices_state.get('chosen_points', [])
            pick = self.vertices_state.get('pick', [])
            vertices = self.vertices_calculation(chosen_points, pick, options = options, select_random = False)
        else:
            chosen_points = self.select_circle_points()
            if 'chosen_points' not in self.vertices_state:
                self.vertices_state['chosen_points'] = []
            self.vertices_state['chosen_points'].extend(chosen_points)
            pick = None
            vertices = self.vertices_calculation(chosen_points, pick, options = options, select_random = True)        
        return vertices
    
    def vertices_calculation(self, chosen_points, pick, options = None, select_random = True):
        num_points = 360
        vertices = []
        for i in range(1, len(chosen_points)):
            picked = random.choice(options) if select_random else pick[i-1]
            self.vertices_state['pick'] = self.vertices_state.get('pick', [])
            self.vertices_state['pick'].append(picked) if select_random else ...
            temp_radius = self.radius + picked
            x_one, y_one = self.calculate_circle_point(temp_radius, chosen_points[i], num_points)
            x_one, y_one = orient_me(x_one, y_one)
            x_zero, y_zero = self.calculate_circle_point(temp_radius, chosen_points[i-1], num_points)
            x_zero, y_zero = orient_me(x_zero, y_zero)
            vertices.append((round(x_zero, 2), round(y_zero,2)))
            vertices.append((round(x_one, 2), round(y_one,2)))
        temp_radius = random.choice(options) if select_random else self.radius + pick[i-1]
        point = chosen_points[-1]
        x_zero, y_zero = self.calculate_circle_point(temp_radius, point, num_points)
        x_zero, y_zero = orient_me(x_zero, y_zero)
        point = chosen_points[0]
        x_one, y_one = self.calculate_circle_point(temp_radius, point, num_points)
        x_one, y_one = orient_me(x_one, y_one)
        vertices.append((round(x_zero, 2), round(y_zero,2)))
        vertices.append((round(x_one, 2), round(y_one,2)))
        return vertices
        ...
        
    def move(self):
        # Update position based on velocity
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.x += self.velocity[0]
        self.y += self.velocity[1]

        # self.log_message('Movement')
        # print(f"Position: {self.position}")  # Debugging: check position updates

        # Check if the asteroid is fully off-screen
        if (self.position[0] < -self.radius or self.position[0] > self.screen_width + self.radius or
            self.position[1] < -self.radius or self.position[1] > self.screen_height + self.radius):
            self.off_screen = True
            print(f"Off-screen detected at {self.position}")  # Debugging: check off-screen status


    def get_random_edge_position(self):
        # Randomly spawn at one of the edges
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return [round(random.uniform(0, self.screen_width),2), 0]
        elif side == 'bottom':
            return [round(random.uniform(0, self.screen_width),2), self.screen_height]
        elif side == 'left':
            return [0, round(random.uniform(0, self.screen_height),2)]
        elif side == 'right':
            return [self.screen_width, round(random.uniform(0, self.screen_height),2)]
        

class Bullet:
    def __init__(self, x, y, heading, velocity):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.heading = heading
        self.radius = 5  # Bullet size
        self.exist = True
        
        # Initializing velocity in x and y components based on heading
        self.vel_x = self.velocity * m.cos(deg2rad(self.heading)) 
        self.vel_y = -(self.velocity * m.sin(deg2rad(self.heading)))
        self.explosion_sound = p.mixer.Sound('shatter_shot.wav')  # courtesy of mixkit.co
        # self.vel_x, self.vel_y = orient_me(vel_x, vel_y)

    def update_position(self):
        # Update position based on the bullet's velocity
        self.x = self.x + self.vel_x
        self.y = self.y + self.vel_y
        # self.x, self.y = orient_me(x, y)

        # Check if the bullet goes off-screen, if so, reset its position or mark it for removal
        if self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height or not self.exist:
            return True  # Indicating the bullet should be removed
        return False


class Game:
    def __init__(self, log_file='game.log'):
        self.player = SpaceShip(screen_width//2, screen_height//2, 90)
        self.asteroids = []
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.bullets_to_remove = set()
        self.logger = setup_logging(log_file, 'game_logger')
        self.vitamin_counter = 0


    def game_restart(self):
        self.player = SpaceShip(screen_width//2, screen_height//2, 90)
        self.asteroids = []
        self.bullets = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.bullets_to_remove = set()

    
    def spawn_asteroid(self, vitamin):
        asteroid = Asteroid(screen_width, screen_height, vitamin = vitamin)
        self.asteroids.append(asteroid)
    
    def update_asteroids(self):
        for asteroid in self.asteroids:
            asteroid.move()  # Move each asteroid
            if asteroid.off_screen:
                # asteroid.log_message('Removed')
                self.asteroids.remove(asteroid)
            else:
                asteroid.vertices = asteroid.generate_vertices()
                if asteroid.vitamin_asteroid:
                    asteroid.color = get_random_color()

    #  new logic for collision start
    def detect_player_asteroid_collision(self, polygon, line_start, line_end):
        """ Check if a line segment intersects with the polygon """
        n = len(polygon)
        for i in range(n):
            # Get the current edge of the polygon
            p1 = polygon[i]
            p2 = polygon[(i + 1) % n]  # Wrap around to the first vertex

            # Check if the line intersects with the polygon edge
            if do_intersect(p1, p2, line_start, line_end):
                return True
        return False
        
    def asteroid_collide_player(self, spaceship_vertices, asteroid_vertices, asteroid):
        for i in range(0, len(spaceship_vertices) - 1):
            line_start = spaceship_vertices[i]
            line_end = spaceship_vertices[i+1]
            collision_detected = self.detect_player_asteroid_collision(asteroid_vertices, line_start, line_end)
            if collision_detected:
                if not self.player.is_hit:
                    if asteroid.vitamin_asteroid and not self.player.under_protection:
                        self.player.protective_shield()
                        self.asteroids.remove(asteroid)
                    elif asteroid.vitamin_asteroid and self.player.under_protection:
                        self.player.protective_shield(extend_protection = True)
                        self.asteroids.remove(asteroid)
                        ...
                    elif self.player.under_protection:
                        self.asteroids.remove(asteroid)
                    else:
                        self.player.trigger_hit_effect()
                break
        ...

    def asteroid_collision(self):
        spaceship_vertices = self.player.vertices
        for asteroid in self.asteroids:
            asteroid_vertices = asteroid.vertices
            if not self.player.is_hit:
                self.asteroid_collide_player(spaceship_vertices, asteroid_vertices, asteroid)

        self.asteroid_collide_asteroid()


    def lump_asteroid(self, asteroid1, asteroid2):
        if asteroid1.radius >= asteroid2.radius:
            radius = asteroid1.radius + asteroid2.radius
            position = asteroid1.position
            velocity = asteroid1.velocity
            color = asteroid1.color
        else:
            radius = asteroid1.radius + asteroid2.radius
            position = asteroid2.position
            velocity = asteroid2.velocity
            color = asteroid2.color
        one_big_asteroid = Asteroid(screen_width, screen_height, position = position, radius = radius, velocity = velocity, color = color)
        return one_big_asteroid

    def handle_asteroid_collision(self, asteroid1, asteroid2):
        """ Handle the collision response, like splitting asteroids or applying velocity changes """
        new_fragments = []

        if asteroid1.color != asteroid2.color:
            if asteroid1.radius > 30:
                new_asteroids = asteroid1.split_asteroid()
                new_fragments.extend(new_asteroids)
            if asteroid2.radius > 30:
                new_asteroids = asteroid2.split_asteroid()
                new_fragments.extend(new_asteroids)
        else:
            new_fragments.append(self.lump_asteroid(asteroid1, asteroid2))
            
        return new_fragments

    def detect_collision(self, polygon1, polygon2):
        """ Check if any edge of polygon1 intersects with any edge of polygon2 """
        n1 = len(polygon1)
        n2 = len(polygon2)
        
        # Loop through each edge of polygon1
        for i in range(n1):
            line_start1 = polygon1[i]
            line_end1 = polygon1[(i + 1) % n1]  # Wrap around to the first vertex

            # Loop through each edge of polygon2
            for j in range(n2):
                line_start2 = polygon2[j]
                line_end2 = polygon2[(j + 1) % n2]  # Wrap around to the first vertex

                # Check if these two edges intersect
                if do_intersect(line_start1, line_end1, line_start2, line_end2):
                    return True

        # No collision detected
        return False


    def asteroid_collide_asteroid(self):
        """ Check for collisions between asteroids """
        asteroids_to_remove = set()
        new_fragments = []
        # Iterate only over unique pairs of asteroids
        for i in range(len(self.asteroids)):
            asteroid1 = self.asteroids[i]
            asteroid1_vertices = asteroid1.vertices
            for j in range(i + 1, len(self.asteroids)):  # Start j from i+1 to avoid double-checking
                asteroid2 = self.asteroids[j]
                asteroid2_vertices = asteroid2.vertices

                # Detect collision between asteroid1 and asteroid2
                collision_detected = self.detect_collision(asteroid1_vertices, asteroid2_vertices)
                if collision_detected:
                    # Handle collision response here, e.g., split the asteroid or destroy them
                    new_fragments.extend(self.handle_asteroid_collision(asteroid1, asteroid2))
                    asteroids_to_remove.add(asteroid1)
                    asteroids_to_remove.add(asteroid2)

        for fragment in new_fragments:
            self.asteroids.append(fragment)
        for asteroid in asteroids_to_remove:
            asteroid.log_message(f'Collision Removed Asteroid')
            self.asteroids.remove(asteroid)

    def update(self):
        self.player.update()
        self.update_asteroids()
        self.asteroid_collision()
        self.handle_bullet_asteroid_collisions()
        self.spawn_asteroid_periodically()

    def point_in_polygon(self, x, y, vertices):
        """Check if a point (x, y) is inside a polygon defined by vertices."""
        inside = False
        n = len(vertices)
        px, py = x, y

        for i in range(n):
            j = (i + 1) % n
            xi, yi = vertices[i]
            xj, yj = vertices[j]
            intersect = ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi)
            if intersect:
                inside = not inside
        return inside

    def handle_bullet_asteroid_collisions(self):
        """Detect and handle collisions between bullets and polygonal asteroids."""
        asteroids_to_remove = set()
        new_fragments = []

        for bullet in self.player.bullets:
            for asteroid in self.asteroids:
                # Perform point-in-polygon test for bullet-asteroid collision
                if bullet.exist and self.point_in_polygon(bullet.x, bullet.y, asteroid.vertices):
                    bullet.exist = False
                    self.bullets_to_remove.add(bullet)
                    self.player.score += 25
                    bullet.explosion_sound.play()

                    if asteroid.radius < 30:  # Check the size of the asteroid
                        asteroids_to_remove.add(asteroid)  # Obliterate small asteroids
                    else:
                        new_fragments.extend(asteroid.split_asteroid())  # Fragment large asteroids
                        asteroids_to_remove.add(asteroid)

        # Remove collided bullets and asteroids
        self.bullets = [bullet for bullet in self.bullets if bullet not in self.bullets_to_remove]
        self.asteroids = [asteroid for asteroid in self.asteroids if asteroid not in asteroids_to_remove]
        # Add new fragments to the asteroid list
        self.asteroids.extend(new_fragments)
    
    def spawn_asteroid_periodically(self):
        # Log the initialization message
        self.logger.debug(f"Spawn Timer: {self.spawn_timer}")
        self.spawn_timer += 1
        if self.spawn_timer > 50:
            vitamin = False
            if self.vitamin_counter == 10:
                vitamin = True
                self.vitamin_counter = 0
            self.spawn_asteroid(vitamin)
            self.spawn_timer = 0
            self.vitamin_counter += 1
            
    def check_collisions(self):
        # Check for collisions between bullets and asteroids, player and asteroids
        pass
