import pygame
from controller import Controller
from model import Game
from view import View
from constants import screen_width, screen_height

def initialize_game():
    pygame.init()
    flags = pygame.NOFRAME
    screen = pygame.display.set_mode((screen_width, screen_height), flags)
    clock = pygame.time.Clock()
    return screen, clock

def game_loop():
    screen, clock = initialize_game()
    model = Game()
    view = View(screen)
    controller_obj = Controller(model, view)

    running = True
    while running:
        # Update the game logic
        controller_obj.update()

        # Render the game state
        controller_obj.render()

        clock.tick(60)  # Cap the frame rate

    pygame.quit()

game_loop()
