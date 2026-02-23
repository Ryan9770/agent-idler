import pygame
from pygame.locals import *

# Define constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Utility function for linear interpolation of colors
def lerp_color(start, end, t):
    return tuple(int(s + (e - s) * t) for s, e in zip(start, end))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.color = WHITE

    def update(self, map, dt):
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class NPC:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.color = BLACK

    def update(self, player):  # Add player as an argument
        pass

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

class Map:
    def __init__(self):
        self.player = Player(100, 100)
        self.npcs = [NPC(200, 200), NPC(300, 300)]

    def update(self):
        for npc in self.npcs:
            npc.update(self.player)

    def draw(self, screen):
        self.player.draw(screen)
        for npc in self.npcs:
            npc.draw(screen)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.map = Map()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            self.screen.fill(BLACK)
            self.map.update()
            self.map.draw(self.screen)

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()