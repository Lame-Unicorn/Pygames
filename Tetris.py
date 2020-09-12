import pygame
from pygame.locals import *
import random
pygame.init()

clock = pygame.time.Clock()

#bg color sets:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
#block color sets for S、Z、L、J、I、O、T:
S = (255, 136, 136)     #Pink for S shape
Z = (102, 255, 163)     #Light green for Z shape
L = (85, 187, 255)      #Light blue for L shape
J = (221, 146, 34)      #Brown for J shape
I = (247, 9, 9)         #Red for I shape
O = (128, 128, 128)     #Gray for O shape
T = (247, 247, 9)       #Light yellow for T shape

class Block:
    def __init__(self, x, y, color=BLACK):
        self.pos = x, y
        self.color = color

    def draw(self):
        map_x, map_y = self.pos
        
        #transfer position in map to position in program
        x = map_x * 32
        y = 608 - map_y * 32

        pygame.draw.rect(game_screen, self.color, (x+1, y+1, 30, 30))

class Map:
    def __init__(self, width=10, height=20):
        self.blocks = []
        self.size = width, height
        for i in range(height):
            self.blocks.append([])
            for j in range(width):
                self.blocks[i].append(Block(j, i))         #Attention:the position we stored in Map is (y, x) because we retrieve x axis preferentially

    def draw(self):
        width, height = self.size
        for j in range(height):
            for i in range(width):
                if self[i, j].color != BLACK:
                    self[i, j].draw()

    def __getitem__(self, index:'(x, y)'):
        if index[0] >= 0 and index[0] < 10 and index[1] >= 0:
            if index[1] < 20:
                return self.blocks[index[1]][index[0]]  #We use (x, y) outside but (y, x) inside
            else:
                #If it is beyond the top.We don't limit the ceiling
                return 1
        else:
            #Illegal position
            return 0
        

    def set_blocks(self, blocks, new_color):
        #if game is over
        if max(block[1] for block in blocks) >= 20:
            global stage
            stage = 2
            screen.fill(BLACK)
            screen.blit(game_over, (160-game_over.get_width()//2, 200))
            screen.blit(score_text, (160-score_text.get_width()//2, 400))
            pygame.display.flip()
            return
        for (x, y) in blocks:
            self[x, y].__setattr__('color', new_color)

    #Check collide
    def get_blocks(self, unit):
        ox, oy = unit.pos
        blocks = [(ox+x, oy+y) for (x, y) in unit.blocks+[(0, 0)]]
        blocks = list(filter(lambda x:False if (x[0], x[1]-1) in blocks else True, blocks))
        for (x, y) in blocks:
            temp = self[x, y-1]
            if temp == 0 or temp.color != BLACK or y == 0:
                return True
        return False

    #Check if there is completed row and eliminate them
    def check(self):
        global new_score
        width, height = self.size
        for i in range(height):
            state = True
            for block in self.blocks[i]:
                if block.color == BLACK:
                    state = False
                    break
            #If this is a completed row
            if state:
                new_score += 1
                for j in range(i, height):
                    for k in range(width):
                        self[k, j].__setattr__('color', self[k, j+1].color if j < height-1 else BLACK)

        
class Unit:
    def __init__(self, shape:'the shape of the unit', phase:'the original phase of the unit', pos:'(x, y)'):
        self.shape = shape
        self.color = eval(shape)
        self.pos = pos              #the position of basis
        if shape == 'S':
            self.blocks = [(-1, 0), (0, 1), (1, 1)]     #based on the block in the middle of the bottom
        elif shape == 'Z':
            self.blocks = [(-1, 1), (0, 1), (1, 0)]     #based on the block in the middle of the bottom
        elif shape == 'L':
            self.blocks = [(0, 1), (1, 0)]              #based on the block in the middle of the bottom
        elif shape == 'J':
            self.blocks = [(-1, 0), (0, 1), (0, 2)]     #based on the block in the middle of the bottom
        elif shape == 'I':
            self.blocks = [(0, -1), (0, 1), (0, 2)]     #based on the second block from bottom to top
        elif shape == 'O':
            self.blocks = [(1, 0), (0, 1), (1, 1)]      #based on the block in the left of the bottom
        elif shape == 'T':
            self.blocks = [(-1, 0), (0, -1), (1, 0)]    #based on the center block of the top
        self.rotate(phase)

    def rotate(self, phase):
        #shape O is symmetrical
        if self.shape == 'O':
            return
        
        blocks = self.blocks[:]
        ox, oy = self.pos
        while phase > 0:
            blocks = list(map(lambda x:(-x[1], x[0]), blocks))
            phase -= 1
            #check if the rotation is illegal
            for (x, y) in blocks:
                temp = game_map[x+ox, y+oy]
                if temp == 1:
                    continue
                elif temp == 0 or temp.color != BLACK:
                    return
        while phase < 0:
            blocks = list(map(lambda x:(x[1], -x[0]), blocks))
            phase += 1
            #check if the rotation is illegal
            for (x, y) in blocks:
                temp = game_map[x+ox, y+oy]
                if temp == 1:
                    continue
                elif temp == 0 or temp.color != BLACK:
                    return
        self.blocks = blocks

    def move(self, direction:'-1 for Left and Down and 0 for Down only and 1 for Right and Donw'):
        end_x, end_y = (self.pos[0]+direction, self.pos[1])
        for block in [(end_x+x, end_y+y) for (x, y) in self.blocks+[(0, 0)]]:
            temp = game_map[block]
            if temp == 1:
                continue
            elif temp == 0 or temp.color != BLACK:
                return
        self.pos = end_x, end_y

    def draw(self):
        for block in self.blocks+[(0, 0)]:
            map_x, map_y = (block[0]+self.pos[0], block[1]+self.pos[1])
            
            #transfer position in map to position in program
            x = map_x * 32
            y = 608 - map_y * 32

            pygame.draw.rect(game_screen, self.color, (x+1, y+1, 30, 30))
        

font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 36)
game_title = title_font.render('Tetris', True, WHITE)
control_helps = [font.render('Press [A or K_LEFT] to go left', True, WHITE),
                 font.render('Press [D or K_RIGHT] to go right', True, WHITE),
                 font.render('Press [W or K_UP] to go counterclockwise', True, WHITE),
                 font.render('Press [S or K_DOWN] to go clockwise', True, WHITE),
                 font.render('Press [BACKSPACE] to speed up', True, WHITE)]
start_help = font.render('Press [Enter] to start', True, WHITE)
game_over = title_font.render('GAME OVER', True, WHITE)

screen = pygame.display.set_mode((320, 680))
pygame.display.set_caption('Tetris Game')
game_screen = screen.subsurface((0, 40, 320, 640))
score_screen = screen.subsurface((0, 0, 320, 40))

game_map = Map()
target = None
direction = 0
rotation = 0
acceleration = False
stage = 0   #0 for overtrue; 1 for gaming;2 for over
t = 0       #timer to control speed
score = new_score = 0   #Monitor the change of score

#Beginning:
screen.fill(BLACK)
screen.blit(game_title, (160-game_title.get_width()//2, 200))
pre_h = 300
for control_help in control_helps:
    screen.blit(control_help, (160-control_help.get_width()//2, pre_h))
    pre_h += control_help.get_height()
screen.blit(start_help, (160-start_help.get_width()//2, pre_h+50))
pygame.display.flip()

while True:
    
    #if no target exist in screen, create a new one
    if not target:
        target = Unit(random.choice('SZLJIOT'), random.randint(0, 3), (random.randint(2, 7), 19))
        

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

        if event.type == KEYDOWN:
            key = event.key
            if stage == 0:
                if key == K_RETURN:
                    screen.fill(BLACK)
                    pygame.draw.rect(score_screen, WHITE, (2, 2, 316, 38), 1)
                    score_text = title_font.render('Your Score: 0', True, WHITE)
                    score_screen.blit(score_text, (85, 22-score_text.get_height()//2))
                    pygame.display.flip()
                    stage = 1
            
            if stage == 1:
                if key == K_RIGHT or key == K_d:
                    direction = 1
                elif key == K_LEFT or key == K_a:
                    direction = -1
                elif key == K_UP or key == K_w:
                    rotation = 1
                elif key == K_DOWN or key == K_s:
                    rotation = -1
                elif key == K_SPACE:
                    acceleration = True

        if acceleration:
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    acceleration = False
        
    #if score is changed          
    if stage == 1 and score != new_score:
        score_screen.fill(BLACK)
        pygame.draw.rect(score_screen, WHITE, (2, 2, 316, 38), 1)
        score_text = title_font.render('Your Score: %d'%new_score, True, WHITE)
        score_screen.blit(score_text, (85, 22-score_text.get_height()//2))
        pygame.display.update((0, 0, 320, 40))
        score = new_score
    
    if stage == 1:
        game_screen.fill(BLACK)
        if rotation:
            target.rotate(rotation)
            rotation = 0
        if direction:
            target.move(direction)
            direction = 0
        if game_map.get_blocks(target):
            ox, oy = target.pos
            game_map.set_blocks([(ox+x, oy+y) for (x, y) in target.blocks+[(0, 0)]], target.color)
            target = None
        if stage == 1:
            game_map.check()
            game_map.draw()
            if target:
                if t == 0:
                    target.pos = (target.pos[0], target.pos[1]-1)
                target.draw()
            pygame.display.update((0, 40, 320, 640))
            if acceleration:
                t = 0 if t < 0.5 else 1
                t = not t
            else:
                t += 1/4
                t %= 1
            clock.tick(4)
