import pygame
import pymunk.pygame_util
import numpy as np
from library.button import *
#import next_scenes

class Plot():
    def __init__(self, screen, xlabel, ylabel, position = (1010, 20), width=250, height=250):
        self.screen = screen
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.center = (0, 0)
        self.position = position
        self.width = width
        self.height = height
        self.scale_x = 1
        self.scale_y = 1
        
        self.surface = pygame.Surface((width, height))
        self.data = []
        self.data_conv = []
        self.data_inside = []
        
    def update(self, x, y):
        self.data.append((x, y))
        converted_point = self.point_convert(x, y)
        self.data_conv.append(converted_point)
        if 0 < converted_point[0] < self.width and 0 < converted_point[1] < self.height:
            self.data_inside.append(True)
        else:
            self.data_inside.append(False)
        
        if len(self.data) > 30:
            self.data.pop(0)
            self.data_conv.pop(0)
                 
    def draw(self):
        self.surface.fill((255, 255, 255))
        pygame.draw.line(self.surface, (0, 0, 0), (0, 0), (0, self.height))
        pygame.draw.line(self.surface, (0, 0, 0), (0, self.height - 1), (self.width, self.height - 1))
        pygame.draw.line(self.surface, (0, 0, 0), (0, 0), (self.width, 0))
        pygame.draw.line(self.surface, (0, 0, 0), (self.width - 1, 0), (self.width - 1, self.height))
        
        pygame.draw.line(self.surface, (0, 0, 0), (self.center[0], 0), (self.center[0], self.height))
        pygame.draw.line(self.surface, (0, 0, 0), (0, self.center[1]), (self.width, self.center[1]))
        
        for i in range(len(self.data) - 1):
            if self.data_inside[i] and self.data_inside[i + 1] and\
                abs(self.data_conv[i][0] - self.data_conv[i + 1][0]) < self.width - 10:
                pointA = (self.data_conv[i][0], self.data_conv[i][1])
                pointB = (self.data_conv[i + 1][0], self.data_conv[i + 1][1])
                pygame.draw.line(self.surface, (0, 0, 0), pointA, pointB, 2)
                # print("in range")
            else:
                # print("out of range")
                pass
        self.screen.blit(self.surface, self.position)
        
    def point_convert(self, x, y):
        rescale_x = x * self.scale_x
        rescale_y = y * self.scale_y
        return (self.center[0] + rescale_x, self.center[1] - rescale_y)
        
class Ball:
    def __init__(self, mass, radius, position, color, body_type=pymunk.Body.DYNAMIC):
        self.moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, self.moment, body_type=body_type)
        self.body.position = position
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.color = color
        self.initial_position = position

    def reset(self):
        self.body.position = self.initial_position
        self.body.velocity = 0, 0
        self.body.force = 0, 0


class Bar:
    def __init__(self, body_a, body_b, anchor_a, anchor_b, fps):
        self.body_a = body_a
        self.body_b = body_b
        self.anchor_a = anchor_a
        self.anchor_b = anchor_b
        self.constraint = pymunk.PinJoint(self.body_a, self.body_b, self.anchor_a, self.anchor_b)
        self.vector = self.body_b.position - self.body_a.position
        self.angle = np.pi / 2 - self.vector.angle
        self.last_angle = self.angle
        self.angular_velocity = 0
        self.fps = fps
        
    def update(self):
        self.vector = self.body_b.position - self.body_a.position
        self.last_angle = self.angle
        self.angle = np.pi / 2 - self.vector.angle
        if self.angle > np.pi:
            self.angle -= 2 * np.pi
        self.angular_velocity = (self.angle - self.last_angle) * self.fps


class scene1:

    def __init__(self, screen, clock, fps):
        self.screen = screen
        self.clock = clock
        self.fps = fps
        self.running = True
        
        #Ture if the scene is ended by regular procedure.
        self.done = False
        
        #Put all the "next scenes" in this list.
        self.next = [0]
        
        #Load background image here.
        self.background = None
        
        #create buttons here.
        self.buttons = []
        self.buttons.append(button(self.screen, 1080, 600, 100, 50, color = (182, 250, 248), color2 = (182, 250, 188), TFF = True))
        
        #pymunk space definition
        self.space = pymunk.Space()
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.space.gravity = (0, 0)
        
        #generate an anchor point at the middle of the screen
        self.anchor = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.anchor.position = (640, 360)
        self.anchor_shape = pymunk.Circle(self.anchor, 10)
        self.anchor_shape.sensor = True
        self.anchor_shape.color = (27, 183, 245, 255)
        self.space.add(self.anchor, self.anchor_shape)
        
        #genetate a ball below the anchor point
        self.ball = Ball(5, 30, (640, 480), (242, 143, 44, 255))
        self.space.add(self.ball.body, self.ball.shape)
        
        #generate a string connecting the ball and the anchor point
        self.string_length, self.string_stiffness, self.string_damp = 0, 200, 0
        self.string = pymunk.constraints.DampedSpring(self.ball.body, self.anchor, (0, 0), (0, 0),
                                                      self.string_length, self.string_stiffness, self.string_damp)
        self.space.add(self.string)
        
        #generate a bar connecting the ball and the anchor point
        self.bar = Bar(self.anchor, self.ball.body, (0, 0), (0, 0), self.fps)
        self.bar_length = 120
        
        #last states
        self.last_mouse_state = pygame.mouse.get_pressed()
        self.last_mouse_velocity = pymunk.Vec2d(0, 0)
        self.last_b1_state = False
        
        #set up the plot
        self.plot = Plot(self.screen, "theta", "theta_dot", position = (1010, 20), width=250, height=250)
        self.plot.center = (self.plot.width / 2, self.plot.height / 2)
        self.plot.scale_x = 125 / np.pi
        self.plot.scale_y = 25 / np.pi
        
        
    def run(self):
        print("scene1 running")
        while self.running and not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    condition = True
                    self.running = False
                
            #Put the condition to end the scene here, if there are more than one, use "and" or "or" to combine them.
            condition = False
            if condition:
                self.done = True
            
            self.game_logic()
            
            self.render()
            
            if self.buttons[0].state:
                self.plot.update(self.bar.angle, self.bar.angular_velocity)

            self.clock.tick(self.fps)
            
        if self.running == False:
            return 0
        #Use the condition to choose the next scene here, if there are more than one, use multiple elif.
        elif self.done and condition:
            return self.next[0]
        else:
            return -1

    #Put all the renderings here.
    def render(self):
        self.screen.fill((255, 250, 214))
        self.space.debug_draw(self.draw_options)
        for button in self.buttons:
            button.draw()
        self.plot.draw()
        pygame.display.flip()
        
    
    #Calculations and game logic should be put here.
    def game_logic(self):
        mouse_state = pygame.mouse.get_pressed()
        if not self.buttons[0].state:
            if mouse_state[0] and not self.buttons[0].hovered and not self.buttons[0].pressed:
                self.ball.body.position = pygame.mouse.get_pos()
                self.ball.body.velocity = (0, 0)
            elif not mouse_state[0] and self.last_mouse_state[0] and not self.buttons[0].hovered and not self.buttons[0].pressed:
                self.ball.body.velocity = self.last_mouse_velocity * self.fps
        elif self.buttons[0].state:
            if mouse_state[0] and not self.buttons[0].hovered and not self.buttons[0].pressed:
                self.ball.body.position = self.anchor.position + (pymunk.Vec2d(*pygame.mouse.get_pos()) - self.anchor.position).scale_to_length(self.bar_length)
                self.ball.body.velocity = (0, 0)
            elif not mouse_state[0] and self.last_mouse_state[0] and not self.buttons[0].hovered and not self.buttons[0].pressed:
                self.ball.body.velocity = self.last_mouse_velocity * self.fps * self.bar_length / pymunk.Vec2d(*pygame.mouse.get_pos()).length
            
        
        if self.last_b1_state != self.buttons[0].state:
            self.ball.reset()
            if self.buttons[0].state:
                self.space.remove(self.string)
                self.space.add(self.bar.constraint)
                self.space.gravity = (0, 3000)
            elif not self.buttons[0].state:
                self.space.remove(self.bar.constraint)
                self.space.add(self.string)
                self.space.gravity = (0, 0)
                
        self.bar.update()
        
        self.space.step(1 / self.fps)
            
        self.last_mouse_state = mouse_state
        self.last_mouse_velocity = pymunk.Vec2d(*pygame.mouse.get_rel())
        self.last_b1_state = self.buttons[0].state