import pygame
import random
from pygame.locals import *
pygame.init()

font = pygame.font.Font(None, 20)

screen = pygame.display.set_mode((160, 160))
screen.fill((0, 0, 0, 0))

class Block():
    def __init__(self, x, y):
        self.value = 0
        self.x = x*40
        self.y = y*40

    def set_value(self, value):
        self.value = value
        block = pygame.surface.Surface((40, 40))
        block.fill((0, 0, 0))
        pygame.draw.rect(block, (0, 255, 0), (1, 1, 38, 38), 1)
        if self.value:
            text = font.render(str(value), True, (0, 255, 0))
            block.blit(text, (20-text.get_width()/2, 20-text.get_height()/2))
        self.block = block.copy()

    def draw(self):
        screen.blit(self.block, (self.x, self.y))


blocks = []
for y in range(4):
    temp = []
    for x in range(4):
        block = Block(x, y)
        block.set_value(0)
        temp.append(block)
    blocks.append(temp)

for block in random.sample([blocks[i][j] for i in range(4) for j in range(4)], 2):
    block.set_value(2)
    

for row in blocks:
    for block in row:
        block.draw()
pygame.display.flip()
direction = 0   #0 for stop;1 for right;2 for down;3 for left; 4 for up 

def get_sequence(index, direction):
    if direction % 2 == 1:
        temp = [blocks[index][j].value for j in range(4)]
    else:
        temp = [blocks[i][index].value for i in range(4)]
    return temp if direction > 2 else list(reversed(temp))

def set_sequence(index, direction, sequence):
    if direction % 2 == 1:
        path = [(index, j) for j in range(4)]
    else:
        path = [(i, index) for i in range(4)]
    if direction <= 2:
        path.reverse()
    for p in range(4):
        blocks[path[p][0]][path[p][1]].set_value(sequence[p])

def move(sequence):
    sequence = list(filter(lambda x:x, sequence))
    n = len(sequence)
    sequence += [0]*(4-n)
    i = 0
    res = []
    while i < n:
        if i < 3 and sequence[i] == sequence[i+1]:
            res.append(sequence[i]*2)
            i += 2
        else:
            res.append(sequence[i])
            i += 1
    res += [0]*(4-len(res))
    return res
            

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                direction = 1
            elif event.key == K_DOWN:
                direction = 2
            elif event.key == K_LEFT:
                direction = 3
            elif event.key == K_UP:
                direction = 4

    if direction:
        for index in range(4):
            sequence = get_sequence(index, direction)
            sequence = move(sequence)
            set_sequence(index, direction, sequence)

        if 2048 in [blocks[i][j].value for i in range(4) for j in range(4)]:
            end = font.render('GAME OVER: YOU WIN!', True, (0, 255, 0))
            screen.fill((0, 0, 0))
            screen.blit(end, (80-end.get_width()/2, 80-end.get_height()/2))
            pygame.display.flip()
            while True:
                for event in pygame.event.wait():
                    if event.type == QUIT:
                        exit()
        temp = list(filter(lambda x:not x.value, [blocks[i][j]for i in range(4) for j in range(4)]))
        if temp:
            block = random.choice(temp)
            block.set_value(random.choices([2, 4], weights=[5, 1])[0])
        else:
            over = font.render('GAME OVER: YOU LOSE!', True, (0, 255, 0))
            leave = font.render('[Enter] to try again', True, (0, 255, 0))
            screen.fill((0, 0, 0))
            screen.blit(over, (80-over.get_width()/2, 70-over.get_height()/2))
            screen.blit(leave, (80-leave.get_width()/2, 110-leave.get_height()/2))
            pygame.display.flip()
            while True:
                on = False
                for event in pygame.event.get():
                    if event.type == QUIT:
                        exit()
                    if event.type == KEYDOWN:
                        if event.key == K_RETURN:
                            blocks = []
                            for y in range(4):
                                temp = []
                                for x in range(4):
                                    block = Block(x, y)
                                    block.set_value(0)
                                    temp.append(block)
                                blocks.append(temp)

                            for block in random.sample([blocks[i][j] for i in range(4) for j in range(4)], 2):
                                block.set_value(2)
                            on = True
                if on:
                    break
        screen.fill((0, 0, 0))
        for row in blocks:
            for block in row:
                block.draw()
        pygame.display.flip()
        direction = 0
