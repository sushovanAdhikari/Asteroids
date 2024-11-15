import pygame
from model import Game
from view import View

class Controller:
    def __init__(self, model: Game, view: View):
        self.model = model
        self.view = view
        self.game_started = False
        self.music_path = 'ChiptuneGameDubstep.mp3'

    def load_music(self):
        pygame.mixer.music.load(self.music_path)
        pygame.mixer.music.play(-1)  # Loop the music indefinitely

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key release (braking both UP and DOWN)
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    self.model.player.brake_me_down()
        keys = pygame.key.get_pressed()

        # Player controls
        if keys[pygame.K_ESCAPE]: 
            running = False

        if not self.game_started:
            # Handle start menu controls
            if keys[pygame.K_RETURN]:  # Start the game
                self.game_started = True
                self.load_music()
                # self.model.game_start()
        elif self.game_started and not self.model.player.destroyed:
            if keys[pygame.K_LEFT]:
                if (self.model.player.velocity > 0):
                    self.model.player.turn_me(3)
                else:
                    self.model.player.turn_me(1)
            if keys[pygame.K_RIGHT]:
                if (self.model.player.velocity > 0):
                    self.model.player.turn_me(-3)
                else:
                    self.model.player.turn_me(-1)
            if keys[pygame.K_UP]:
                self.model.player.speed_me_up(1)
            if keys[pygame.K_DOWN]:
                self.model.player.speed_me_up(-1)
            if keys[pygame.K_SPACE]:
                self.model.player.fire_bullet()
        else:
            if keys[pygame.K_RETURN]: 
                self.model.game_restart()

    def update(self):
        self.handle_input()
        if not self.model.player.destroyed and self.game_started:
            self.model.update()
        # self.model.check_collisions()

    def render(self):
        if not self.game_started:
            self.view.render_start_menu()
        else:
            self.view.update(self.model)
