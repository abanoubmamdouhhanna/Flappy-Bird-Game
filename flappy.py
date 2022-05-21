from argparse import Action
from queue import Empty
from re import T
from time import time
from turtle import left
import pip
import pygame
from pygame.locals import *
import random
from pygame import mixer

pygame.init() #to initialize the game 

clock=pygame.time.Clock()
fps=60

screen_width=864
screen_height=936

screen=pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy_Bird')

#font
font=pygame.font.SysFont('Bauhaus 93', 60)

#colours
white=(255,255,255)
red=(255,0,42)
yellow=(250,222,59)

#variables
ground_scroll=0
scroll_speed=4   #scroll speed 4 pixels
flying = False
game_over = False
pipe_gap = 180
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

#load images
background = pygame.image.load('img/background.png')
ground_image = pygame.image.load('img/ground.png')
button_image = pygame.image.load('img/restart.png')
gameover_image = pygame.image.load('img/gameover.png')

#music

mixer.music.load('sfx_point.wav')

#display font on screen
def draw_text (text , font ,text_col ,x ,y):
    img=font.render(text ,True ,text_col)
    screen.blit(img ,(x,y))

#reset the game
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score

class Bird (pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.images=[]
        self.index = 0
        self.counter = 0
        for number in range(1,4):
            image=pygame.image.load(f'img/bird{number}.png')
            self.images.append(image)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center=[x , y]
        self.vel= 0 
        self.clicked = False

    def update(self):
        if flying == True :
            #Gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            #print(self.vel)
            if self.rect.bottom < 768 :
                self.rect.y += int(self.vel)

        if game_over == False:
            #jumping
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel= -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter >flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image=self.images[self.index]

            #rotation
            self.image = pygame.transform.rotate (self.images[self.index] , self.vel * -2)
        else:
            self.image = pygame.transform.rotate (self.images[self.index] ,-90)

class pipe (pygame.sprite.Sprite):
    def __init__ (self,x,y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        
        #position 1 is from the top ,-1 is from the bottom
        if position == 1:
            self.image=pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int (pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__ (self ,x ,y, image):
        self.image = image 
        self.rect = self.image.get_rect()
        self.rect.topleft = (x ,y)

    def draw(self):
        
        action = False    

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check the mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 :
                action = True

        #draw button
        screen.blit(self.image , (self.rect.x , self.rect.y))

        return action

bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

flappy = Bird (100 ,int(screen_height / 2))
bird_group.add(flappy)

#create restart button
button = Button(screen_width // 2 -50 , screen_height // 2 -100 , button_image)


run=True
while run:

    clock.tick(fps)

    #bg
    screen.blit(background, (0,0))


    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    
    #display game over and final score
    if game_over == True:
            screen.blit(gameover_image,(int(screen_width /2) - 150,200))
            draw_text("Your Score is: ", font ,red ,int(screen_width /2) -175 ,475)
            draw_text(str(score) , font ,yellow ,int(screen_width /2) + 200 ,475)




    #draw the ground
    screen.blit(ground_image,(ground_scroll,768))

    #check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
        and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
        and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
                if score > 0:
                    mixer.music.load('sfx_point.wav')
                    mixer.music.play()

    #print(score)  
    draw_text(str(score) , font ,white ,int(screen_width /2),50)

    #look for the collision
    if pygame.sprite.groupcollide(bird_group, pipe_group , False ,False) or flappy.rect.top < 0:
        game_over = True
        mixer.music.stop()
        

    #check if the bird has hit the ground
    if flappy.rect.bottom >= 768 :
        game_over = True
        flying = False
        mixer.music.stop()
        

    if game_over == False and flying == True:

        #generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100 , 100)
            btm_pipe = pipe (screen_width ,int(screen_height / 2) + pipe_height, -1)
            top_pipe = pipe (screen_width ,int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        
        pipe_group.update()
        
        #scroll bg
        ground_scroll-=scroll_speed
        if abs (ground_scroll) > 35:
            ground_scroll=0
        
    
    #Check if the game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True 

    pygame.display.update()        

pygame.quit()