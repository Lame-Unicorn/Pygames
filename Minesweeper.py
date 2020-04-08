import pygame
from pygame.locals import *
import random
pygame.init()

Directions = [(1, 0), (0, 1), (-1, 0), (0, -1),
              (1, 1), (-1, 1), (-1, -1), (1, -1)]

def vector_sum(vector_x, vector_y, sub=False):
    if type(vector_x) != tuple or type(vector_y) != tuple:
        raise TypeError('unsupported operand type(s) for +: \'{}\' and \'{}\''.format(type(vector_x),type(vector_y)))
    if len(vector_x) != len(vector_y):
        raise Exception('different dimensions')
    return tuple(vector_x[i]-vector_y[i]if sub else vector_x[i]+vector_y[i] for i in range(len(vector_x)))

#color sets
BLACK = (0, 0, 0)
DEEPGRAY = (60, 60, 60)
LIGHTGRAY = (160, 160, 160)
LIGHTLIGHTGRAY = (220, 220, 220)
WHITE = (255, 255, 255)
NUMBERCOLORS = [None,
               (85, 85, 225),
               (0, 128, 0),
               (128, 0, 0),
               (0, 0, 128),
               (96, 0, 0),
               (0, 128, 128),
               (64, 0, 0),
               (64, 0, 0)]

#text settlements:
title_font = pygame.font.Font(None, 64)
font = pygame.font.Font(None, 24)
tiny_font = pygame.font.Font(None, 12)
title = title_font.render(u'MINE SWEEPER', 1, WHITE)
texts = [((font.render(u'Difficulty:Easy', 1, WHITE), font.render(u'Map:9*9', 1, WHITE)),
            (font.render(u'Difficulty:Easy', 1, (0, 0, 0)), font.render(u'Map:9*9', 1, BLACK))),
           ((font.render(u'Difficulty:Medium', 1, WHITE), font.render(u'Map:16*16', 1, WHITE)),
            (font.render(u'Difficulty:Medium', 1, BLACK), font.render(u'Map:16*16', 1, BLACK))),
           ((font.render(u'Difficulty:Hard', 1, WHITE), font.render(u'Map:16*30', 1, WHITE)),
            (font.render(u'Difficulty:Hard', 1, BLACK), font.render(u'Map:16*30', 1, BLACK)))]
choices = []
choice_bg = pygame.surface.Surface((400, 70))
for text in texts:
    choice_bg.fill(BLACK)
    choice_bg.blit(text[0][0], (50, 35-text[0][0].get_height()//2))
    choice_bg.blit(text[0][1], (250, 35-text[0][1].get_height()//2))
    a = choice_bg.copy()
    choice_bg.fill(WHITE)
    choice_bg.blit(text[1][0], (50, 35-text[1][0].get_height()//2))
    choice_bg.blit(text[1][1], (250, 35-text[1][1].get_height()//2))
    b = choice_bg.copy()
    choices.append((a, b))   
start_helps = [font.render(u'Press the direction key to choose', 1, WHITE),
              font.render(u'Press [ENTER] to confirm', 1, WHITE)]
game_win = title_font.render(u'You Win!', 1, WHITE)

#marks set:
block_bg = pygame.surface.Surface((16, 16))
block_bg.fill(DEEPGRAY)
pygame.draw.rect(block_bg, LIGHTLIGHTGRAY, (0, 0, 16, 16), 1)
unshowed_img = block_bg.copy()
show_part = block_bg.subsurface((1, 1, 14, 14))
show_part.fill(LIGHTGRAY)
empty_img = block_bg.copy()
number_marks = []
for i in range(9):
    temp = empty_img.copy()
    if i:
        text = font.render(str(i), 1, NUMBERCOLORS[i])
        temp.blit(text, (8-text.get_width()//2, 8-text.get_height()//2))
    number_marks.append(temp)
pygame.draw.ellipse(empty_img, WHITE, (1, 1, 14, 14))
bomber_img = empty_img
marks = [unshowed_img]
bomber_mark = font.render(u'!', 1, WHITE)
temp = unshowed_img.copy()
temp.blit(bomber_mark, (8-bomber_mark.get_width()//2, 8-bomber_mark.get_height()//2))
marks.append(temp.copy())
question_mark = font.render(u'?', 1, WHITE)
temp = unshowed_img.copy()
temp.blit(question_mark, (8-question_mark.get_width()//2, 8-question_mark.get_height()//2))
marks.append(temp.copy())


EMPTY = 0
#the state of Block
BOMB = -1
#the marks of Block
SUSPECTED = 1
MARK = 2
#the display of Block
SHOW = 1

#(map size, screen size, number of bombers)
game_difficulty_set = [((9, 9), (144, 144), 10),
                       ((16, 16), (256, 256), 40),
                       ((30, 16), (320, 256), 99)]


class Block():
    def __init__(self, x, y):
        self.pos = x, y
        self.inside = EMPTY
        self.mark = EMPTY
        self.display = EMPTY
    
    def button_1_tap(self):
        if not self.display:
            global stage
            width, height = game_map.size
            self.display = SHOW
            if self.inside == BOMB:
                stage = 2
                for i in range(width):
                    for j in range(height):
                        if game_map.map[i][j].inside == BOMB:
                            temp = game_map.map[i][j]
                            game_map.screen.blit(bomber_img, temp.pos)
                pygame.display.flip()
                return
            game_map.screen.blit(number_marks[self.inside], self.pos)
            pygame.display.flip()
            for i in range(width):
                for j in range(height):
                    if not game_map.map[i][j].display and game_map.map[i][j].inside != BOMB:
                        return
            stage = 3
    
    def button_3_tap(self):
        if not self.display:
            self.mark = (self.mark+1)%3
            game_map.screen.blit(marks[self.mark], self.pos)
            pygame.display.flip()

class Group():
    def __init__(self, difficulty):
        self.size = game_difficulty_set[difficulty][0]
        self.screen = pygame.display.set_mode(game_difficulty_set[difficulty][1])
        self.map = []
        width, height = self.size
        for i in range(width):
            self.map.append([])
            for j in range(height):
                self.map[i].append(Block(16*i, 16*(game_difficulty_set[difficulty][0][1]-j-1)))
        n_bombers = game_difficulty_set[difficulty][2]
        poss = [(i, j)for i in range(width) for j in range(height)]
        bombers = random.choices(poss, k=n_bombers)
        for (x, y) in bombers:
            self.map[x][y].inside = BOMB
        for (x, y) in poss:
            if self.map[x][y].inside == EMPTY:
                counter = 0
                for direction in Directions:
                    temp_x, temp_y = vector_sum((x, y), direction)
                    if temp_x < 0 or temp_x >= width or temp_y < 0 or temp_y >= height:
                        continue
                    if self.map[temp_x][temp_y].inside == BOMB:
                        counter += 1
                self.map[x][y].inside = counter
        for (x, y) in poss:
            self.screen.blit(unshowed_img, self.map[x][y].pos)
        pygame.display.flip()
        

    def bloom(self, pos):
        record = [pos]
        def dfs(pos):
            for direction in Directions:
                temp_pos = vector_sum(pos, direction)
                if temp_pos in record:
                    continue
                if temp_pos[0] < 0 or temp_pos[0] >= self.size[0] or temp_pos[1] < 0 or temp_pos[1] >= self.size[1]:
                    continue
                elif self.map[temp_pos[0]][temp_pos[1]].inside == EMPTY:
                    self.map[temp_pos[0]][temp_pos[1]].button_1_tap()
                    record.append(temp_pos)
                    dfs(temp_pos)
                elif self.map[temp_pos[0]][temp_pos[1]].inside in range(1, 9) and not self.map[temp_pos[0]][temp_pos[1]].display:
                    self.map[temp_pos[0]][temp_pos[1]].button_1_tap()
                    record.append(temp_pos)
        dfs(pos)
        
    
    def button_1_tap(self, pos):
        width, height = self.size
        for i in range(width):
            for j in range(height):
                x, y = self.map[i][j].pos
                if pos[0] >= x and pos[0] < x+16 and pos[1] >= y and pos[1] < y+16:
                    self.map[i][j].button_1_tap()
                    print('Block (%d, %d) is called by button 1'%(i, j))
                    if self.map[i][j].inside == EMPTY:
                        self.bloom((i, j))

    def button_3_tap(self, pos):
        width, height = self.size
        for i in range(width):
            for j in range(height):
                x, y = self.map[i][j].pos
                if pos[0] >= x and pos[0] < x+16 and pos[1] >= y and pos[1] < y+16:
                    self.map[i][j].button_3_tap()
                    return

#beginning set:
screen = pygame.display.set_mode((720, 400))
screen.blit(title, (360-title.get_width()//2, 40))
for i in range(3):
    screen.blit(choices[i][0], (160, 100+i*75))
for i in range(2):
    screen.blit(start_helps[i], (360-start_helps[i].get_width()//2, 340+30*i))
pygame.display.flip()

stage = 0
chosen = -1

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

        if stage == 0:
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    if chosen == -1:
                        chosen = 0
                        screen.blit(choices[0][1], (160, 100))
                        pygame.display.flip()
                    else:
                        screen.blit(choices[chosen][0], (160, 100+75*chosen))
                        chosen -= 1
                        chosen %= 3
                        screen.blit(choices[chosen][1], (160, 100+75*chosen))
                        pygame.display.flip()
                if event.key == K_DOWN:
                    if chosen == -1:
                        chosen = 0
                        screen.blit(choices[0][1], (160, 100))
                        pygame.display.flip()
                    else:
                        screen.blit(choices[chosen][0], (160, 100+75*chosen))
                        chosen += 1
                        chosen %= 3
                        screen.blit(choices[chosen][1], (160, 100+75*chosen))
                        pygame.display.flip()
                if event.key == K_RETURN:
                    if chosen != -1:
                        game_map = Group(chosen)
                        stage = 1
                    
        if stage == 1:
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    game_map.button_1_tap(event.pos)
                if event.button == 3:
                    game_map.button_3_tap(event.pos)

        if stage == 2:
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    game_map = Group(chosen)
                    stage = 1
                    

        if stage == 3:
            screen = pygame.display.set_mode((320, 320))
            screen.fill(BLACK)
            screen.blit(game_win, (160-game_win.get_width()//2, 160-game_win.get_height()//2))
            pygame.display.flip()
            stage = 2
