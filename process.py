import pygame
from scene1 import *

class process:
    def __init__(self, screen, clock, fps):
        self.screen = screen
        self.clock = clock
        self.fps = fps
        self.running = True
        self.current_scene = scene1(self.screen, self.clock, self.fps)
    
    def run(self):
        while self.running:
            
            next_scene = self.current_scene.run()
            # print(next_scene)
            
            if next_scene[0] == 0 or next_scene[0] == -1:
                self.running = False
            else:
                self.current_scene = next_scene[0](self.screen, self.clock, self.fps, next_scene[1] if len(next_scene) > 1 else None)
        
        pygame.quit()