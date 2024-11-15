import pygame as p
from constants import BLACK, WHITE, RED, screen_width, screen_height
import math as m
import random
from generic_functions import dist, deg2rad
import logging
from logger import setup_logging

class View:
    def __init__(self, screen, log_file='view.log'):
        self.screen = screen
        self.logger = setup_logging(log_file, 'view_logger')
        self.font_game_title = p.font.SysFont("Times New Roman", 150)
        self.font_instruction = p.font.SysFont("Times New Roman", 50)


    def render_start_menu(self):
        self.screen.fill((0, 0, 0))  # Fill screen with black
        game_text = self.font_game_title.render("Asteroids", True, RED)
        start_text = self.font_instruction.render("Press Enter to Start", True, WHITE)
        self.screen.blit(game_text, (screen_width // 2 - 250, screen_height // 2 - 200))
        self.screen.blit(start_text, (screen_width // 2 - 150, screen_height // 2))

        p.display.update()
        
    def draw_noise(self, noise_intensity=100):
        """Draw random noise on the screen."""
        for _ in range(noise_intensity):
            x = random.randint(0, self.screen.get_width() - 1)  # Ensure x is within bounds
            y = random.randint(0, self.screen.get_height() - 1)  # Ensure y is within bounds
            color = random.choice([(255, 255, 255), (0, 0, 0)])  # White or black pixels
            self.screen.set_at((x, y), color)  # Set pixel color

    def draw_object(self, object, use_polygon=True):
       
        vertices = object.vertices
        pos = object.get_position()
        '''
        for i in range(0, len(vertices) - 1):
            p.draw.line(self.screen, WHITE, vertices[i], vertices[i+1], 2)
        '''
        color = object.color
        if use_polygon:
            p.draw.polygon(self.screen, color, vertices)
        else:
            for i in range(0, len(vertices) - 1):
                p.draw.line(self.screen, WHITE, vertices[i], vertices[i+1], 2)
        return None

    def draw_bullet(self, bullet):
        # Placeholder for bullet drawing logic, assuming use of Pygame or similar
        self.draw_circle(bullet.x, bullet.y, bullet.radius, bullet.color)

    def log_message(self, message):
        self.logger.debug(f'{message}')

    def draw_asteroids(self, asteroids):
        asteroid_surfaces = []
        for asteroid in asteroids:
            asteroid_surface = self.draw_object(asteroid)
            # asteroid_surfaces.append(asteroid_surface)
        return asteroid_surfaces

    def draw_bullets(self, bullets):
        for bullet in bullets:
            p.draw.circle(self.screen, WHITE, (bullet.x, bullet.y), 5)

    def draw_score(self, score):
        font = p.font.SysFont("Arial", 30)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def draw_game_over(self, player_ship):
        font_size = 100
        font = p.font.SysFont("Times New Roman", font_size)
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        self.screen.blit(game_over_text, (screen_width//2 - font_size - 75, screen_height//2 - font_size))

    def explode_bullets(self, bullets_to_remove):
        # self.explosion_sound.play()
        for bullet in bullets_to_remove:
            for i in range(1, 6):
                p.draw.circle(self.screen, RED, [int(bullet.x), int(bullet.y)], bullet.radius + 2 * i, 1)
        bullets_to_remove.clear()

    def draw_hud(self, player_ship):
        """Draw the player's score and lives on the screen."""
        font = p.font.SysFont("Arial", 30)
        
        # Display Score
        score_text = font.render(f"Score: {player_ship.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))  # Position in the top-left corner
        
        # Display Lives
        lives_text = font.render(f"Lives: {player_ship.lives}", True, (255, 255, 255))
        self.screen.blit(lives_text, (screen_width - 150, 10))  # Position near the top-right corner

    def update(self, model):
        self.screen.fill(BLACK)
        self.draw_noise()
        # self.draw_object(model.player, use_polygon=False) if not model.player.respawn else self.player_respawn(model.player)
        self.draw_object(model.player, use_polygon=False)
        self.draw_asteroids(model.asteroids)
        self.draw_bullets(model.player.bullets)
        self.explode_bullets(model.bullets_to_remove)
        self.draw_hud(model.player)
        if model.player.destroyed:
            self.draw_game_over(model.player)
        # self.player_respawn(model.player)
        # self.draw_asteroids(model.asteroids)
        '''
        self.draw_asteroids(model.asteroids)
        self.draw_bullets(model.bullets)
        self.draw_score(model.score)
        if model.game_over:
            self.draw_game_over()
        '''
        p.display.flip()  # Update the display
