import pygame
from pygame.locals import *
import random
pygame.init()

clock = pygame.time.Clock()

Directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  #RIGHT, UP, LEFT, DOWN
#bg color sets:
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
#elements color sets:
GRAY = (128, 128, 128)      #Gray for walls
GREEN = (0, 255, 0)         #Green for food
                            #Snake use White also
#state of block:
AVAILABLE = 0
WALL = 1
FOOD = 2

def draw(blocks, color):
    if type(blocks) != list:
        blocks = [blocks]
    for (x, y) in blocks:
        pygame.draw.rect(screen, color, (30*x+1, 30*(23-y)+1, 28, 28))

def vector_sum(vector_x, vector_y, sub=False):
    if type(vector_x) != tuple or type(vector_y) != tuple:
        raise TypeError('unsupported operand type(s) for +: \'{}\' and \'{}\''.format(type(vector_x),type(vector_y)))
    if len(vector_x) != len(vector_y):
        raise Exception('different dimensions')
    return tuple(vector_x[i]-vector_y[i]if sub else vector_x[i]+vector_y[i] for i in range(len(vector_x)))

class Map:
    def __init__(self, width=24, height=24, wall_set=None):
        self.blocks = []
        for i in range(height):
            self.blocks.append([])
            for j in range(width):
                self.blocks[i].append(AVAILABLE)
        self.size = width, height

        if not wall_set:
            for i in range(height):
                if i == 0 or i == height-1:
                    self.blocks[i] = [WALL] * width
                else:
                    self.blocks[i] = [WALL] + [AVAILABLE]*(width-2) + [WALL]
        else:
            for wall in wall_set:
                self.blocks[wall[1]][wall[0]] = WALL

        update_blocks = []
        for i in range(height):
            for j in range(width):
                if self.blocks[i][j] != WALL:
                    update_blocks.append((j, i))
        self.update_area = [(30*x+1, 30*(23-y)+1, 28, 28)for (x, y) in update_blocks]
        
    def __getitem__(self, index):
        width, height = self.size
        if index[0] < 0 or index[0] >= width or index[1] < 0 or index[1] >= height:
            return WALL
        return self.blocks[index[1]][index[0]]

    def __setitem__(self, index, value):
        width, height = self.size
        if index[0] < 0 or index[0] >= width or index[1] < 0 or index[1] >= height:
            return
        self.blocks[index[1]][index[0]] = value

    def clear(self):
        width, height = self.size
        for x in range(width):
            for y in range(height):
                if self[x, y] != WALL:
                    draw((x, y), BLACK)

class Snake:
    def __init__(self, length=3):
        self.passed = None

        def available_head_check(pos):
            if game_map[pos] == WALL:
                return False
            for direction in Directions:
                sum_direction = (0, 0)
                for i in range(3):
                    sum_direction = vector_sum(sum_direction, direction)
                    if game_map[vector_sum(sum_direction, pos)] == WALL:
                        return False
            return True
                    
        available_choices = list(filter(available_head_check, [(i, j)for i in range(24) for j in range(24)]))
        head_pos = random.choice(available_choices)
        self.blocks = [head_pos]
        def available_body_check(pos):
            return pos in available_choices and pos not in self.blocks
        while length > 1:
            choices = list(filter(lambda x:available_body_check(vector_sum(self.blocks[-1], x, sub=True)), Directions))
            temp_head = random.choice(choices)
            if len(self.blocks) == 1:
                self.head = temp_head
            self.blocks.append(vector_sum(self.blocks[-1], temp_head, sub=True))
            length -= 1

    def move(self, head):
        if head == None or vector_sum(self.head, head) == (0, 0):
            head = self.head
        self.head = head
        new_head_pos = vector_sum(self.blocks[0], head)
        if game_map[new_head_pos] == WALL or new_head_pos in self.blocks:
            global stage
            stage = 2
            return True
        if game_map[new_head_pos] == FOOD:
            self.blocks = [new_head_pos] + self.blocks
            game_map[new_head_pos] = AVAILABLE
            global food
            food = None
        else:
            passed = self.blocks[-1]
            draw(passed, BLACK)
            self.blocks = [new_head_pos] + self.blocks[:-1]

    def draw(self):
        draw(self.blocks, WHITE)

def available_food_check(pos):
    if snake:
        if pos in snake.blocks:
            return False
    if game_map[pos] == WALL:
        return False
    dead = 0
    for direction in Directions:
        temp = vector_sum(pos, direction)
        if game_map[temp] == WALL:
            dead += 1
        if snake and temp in snake.blocks:
            dead += 1
    if dead <= 2:
        return True
    else:
        return False

title_font = pygame.font.Font(None, 60)
font = pygame.font.Font(None, 24)
title = title_font.render('Snake Game', True, WHITE)
display_helps = [font.render('Wall', True, WHITE),
                font.render('Food', True, WHITE),
                font.render('Snake', True, WHITE)]
control_helps = [font.render('Press [W or K_UP] to move up', True, WHITE),
                font.render('Press [S or K_DOWN] to move down', True, WHITE),
                font.render('Press [D or K_RIGHT] to move right', True, WHITE),
                font.render('Press [A or K_LEFT] to move left', True, WHITE),
                font.render('Press [ESC] to pause', True, WHITE)]
start_help = font.render('Press [ENTER] to start', True, WHITE)
gameover = title_font.render('GAME OVER', True, WHITE)

screen = pygame.display.set_mode((720, 720))
pygame.display.set_caption('Snake Game Demo')
game_map = Map()

stage = 0       #0 for beginning; 1 for gaming; 2 for end
snake = None
food = None
head = None
pause = False
            
screen.fill(BLACK)
screen.blit(title, (360-title.get_width()/2, 150))
for i in range(len(control_helps)):
    screen.blit(control_helps[i], (100, 264+48*i-control_helps[i].get_height()/2))
display_colors = [GRAY, GREEN, WHITE]
for i in range(len(display_helps)):
    pygame.draw.rect(screen, display_colors[i], (501, 266+80*i, 28, 28))
    screen.blit(display_helps[i], (560, 280+80*i-display_helps[i].get_height()/2))
screen.blit(start_help, (360-start_help.get_width()/2, 560))
pygame.display.flip()

t = 0

while True:
    if stage == 1 and not food:
        available_choices = list(filter(available_food_check, [(i, j) for i in range(24) for j in range(24)]))
        food = random.choice(available_choices)
        game_map[food] = FOOD
        draw(food, GREEN)
        
    
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

        if event.type == KEYDOWN:
            key = event.key
        
            if stage == 1:
                if not pause:
                    if key == K_RIGHT or key == K_d:
                        head = Directions[0]
                    elif key == K_UP or key == K_w:
                        head = Directions[1]
                    elif key == K_LEFT or key == K_a:
                        head = Directions[2]
                    elif key == K_DOWN or key == K_s:
                        head = Directions[3]
                if key == K_ESCAPE:
                    pause = not pause

            if stage == 0:
                if key == K_RETURN:
                    game_map.clear()
                    screen.fill(BLACK)
                    snake = Snake()
                    snake.draw()
                    for i in range(24):
                        for j in range(24):
                            if game_map[i, j] == WALL:
                                draw((i, j), GRAY)
                    pygame.display.flip()
                    stage = 1
            
    if stage == 1:
        if pause:
            continue
        if not snake.move(head):
            head = None
            snake.draw()
            pygame.display.flip()
            clock.tick(1.7)
    if stage == 2:
        screen.blit(gameover, (360-gameover.get_width()/2, 240))
        screen.blit(start_help, (360-start_help.get_width()/2, 480))
        pygame.display.flip()
        food = None
        stage = 0

