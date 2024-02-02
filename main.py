import os
import pygame
from process import *

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("Ocsilllation Simulation")
    
    screen = pygame.display.set_mode((1280, 720))
    fps = 60
    clock = pygame.time.Clock()
    game = process(screen, clock, fps)
    game.run()


if __name__ == "__main__":
    os._exit(main())

