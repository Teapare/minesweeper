import pygame
import random
  # please do not touch anything, thank you
import sys
cell_s = 70
v_group = pygame.sprite.Group()
screen = pygame.display.set_mode((700, 700))
numbers = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight'}
images = {
    'one': pygame.transform.scale(pygame.image.load('one.png'), 
                                  (cell_s, cell_s)),
    'two': pygame.transform.scale(pygame.image.load('two.png'),
                                  (cell_s, cell_s)),
    'three': pygame.transform.scale(pygame.image.load('three.png'), 
                                    (cell_s, cell_s)),
    'four': pygame.transform.scale(pygame.image.load('four.png'), 
                                   (cell_s, cell_s)),
    'five': pygame.transform.scale(pygame.image.load('five.png'),
                                   (cell_s, cell_s)),
    'six': pygame.transform.scale(pygame.image.load('six.png'),
                                  (cell_s, cell_s)),
    'seven': pygame.transform.scale(pygame.image.load('seven.png'),
                                    (cell_s, cell_s)),
    'eight': pygame.transform.scale(pygame.image.load('eight.png'),
                                    (cell_s, cell_s)),
    'closed': pygame.transform.scale(pygame.image.load('closed.png'), 
                                     (cell_s, cell_s)),
    'empty': pygame.transform.scale(pygame.image.load('empty.png'),
                                    (cell_s, cell_s)),
    'flagged': pygame.transform.scale(pygame.image.load('flag.png'), 
                                      (cell_s, cell_s)),
    'mined': pygame.transform.scale(pygame.image.load('mine.png'), 
                                    (cell_s, cell_s))
}
class Cell:
    def __repr__(self):
        return 'Cell ({}, {})'.format(*self._f_pos)
    def __init__(self, cell_size, f_pos, r_pos, cell_type='closed', cell_open_type='empty'):
        self._size = cell_size  #  literally the size of the cell
        self._f_pos = f_pos  # where the cell is located at the field (field_position)
        self._r_pos = r_pos  # where the cell is located in the pygame window (real_position)
        if cell_type in images:
            self._type = cell_type
        else:
            self._type = 'closed'
        self._opened = False if cell_type == 'closed' or cell_type == 'flagged'\
            else True
        self._opened_type = cell_open_type  # what the cell will look once it's been uncovered

    def size(self):
        return self._size
    
    def opened(self):
        return self._opened

    def type(self):
        return self._type
    
    def op_type(self):
        return self._opened_type
    
    def set_op_type(self, new_op_type):
        if new_op_type in images:
            self._opened_type = new_op_type
            if self._opened:
                self._type = self._opened_type

    def set_type(self, new_type):
        if new_type in images:
            self._type = new_type
        self._opened = self._type != 'closed' and self._type != 'flagged'

    def f_pos(self):
        return self._f_pos

    def r_pos(self):
        return self._r_pos

    def draw(self, screen):
        screen.blit(images[self._type], self._r_pos)
        
class Field:
    def __init__(self, size, cell_size):
        self.size = size
        self.cell_size = cell_size
        self.matrix = [[Cell(cell_size, 
                             (col, row), 
                             (col * cell_size, row * cell_size))
                        for row in range(size)] for col in range(size)]

    def render(self):
        for ri, row in enumerate(self.matrix):
            for ci, elem in enumerate(row):
                elem.draw(screen)

    def get_click(self, pos):
        if pos[0] > self.size * self.cell_size:
            return None
        if pos[1] > self.size * self.cell_size:
            return None
        return pos[0] // self.cell_size, pos[1] // self.cell_size

    def on_click(self, pos, ignore_flag=False):
        if pos is None:
            return False
        if self.matrix[pos[0]][pos[1]].type() == 'closed' or ignore_flag:
            self.matrix[pos[0]][pos[1]].set_type(self.matrix[pos[0]][pos[1]].op_type())
            if self.matrix[pos[0]][pos[1]].op_type() == 'empty':
                for n in self.neighbours(pos):
                    self.on_click(n.f_pos())
            return self.matrix[pos[0]][pos[1]].op_type() == 'mined'

    def all_uncovered(self):
        global running
        if any(map(lambda x: any(map(lambda y: y.opened() is False, x)), self.matrix)):
            return False
        #if any(map(lambda x: any(map(lambda y: y[0] == 0, x)), self.matrix)): 
        return True

    def check_cell(self):
        pass
    
    def switch_flag(self, pos):
        if pos is None:
            return None
        if self.matrix[pos[0]][pos[1]].opened() == True:
            return None
        if self.matrix[pos[0]][pos[1]].type() == 'flagged':
            self.matrix[pos[0]][pos[1]].set_type('closed')
            return None
        self.matrix[pos[0]][pos[1]].set_type('flagged')
    
    def neighbours(self, pos):
        if pos is None:
            return None
        x, y = pos
        neighbours = []
        xlist = [x_ for x_ in [x - 1, x, x + 1] if 0 <= x_ < self.size]
        ylist = [y_ for y_ in [y - 1, y, y + 1] if 0 <= y_ < self.size]
        for col in xlist:
            for el in ylist:
                if pos != (col, el):
                    neighbours.append(self.matrix[col][el])
        return neighbours

    def switch_mine(self, pos):
        if pos is None:
            return None
        if self.matrix[pos[0]][pos[1]].op_type() == 'empty':
            self.matrix[pos[0]][pos[1]].set_op_type('mined')
            return None
        self.matrix[pos[0]][pos[1]].set_op_type('empty')
    
    def init_cells(self, mines:int=0, immune:tuple=None):
        if mines >= self.size ** 2:
            for col in self.matrix:
                for cell in col:
                    if cell.f_pos() != immune:
                        cell.set_op_type('mined')
        in_a_row = 0
        while mines > 0:
            global numbers
            for col in self.matrix:
                for cell in col:
                    if cell.op_type() == 'mined' or cell.f_pos() == immune or any(map(lambda n: n is cell, self.neighbours(immune))):
                        in_a_row = 0
                        continue
                    if random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]) == 1:
                        mines -= 1
                        cell.set_op_type('mined')
                        in_a_row += 1
                        if mines <= 0:
                            break
                    if mines <= 0:
                        break
                if mines <= 0:
                    break
            for col in self.matrix:
                for cell in col:
                    if cell.op_type() == 'mined':
                        continue
                    mn = [c for c in self.neighbours(cell.f_pos()) if c.op_type() == 'mined']
                    if mn:
                        cell.set_op_type(numbers[len(mn)])
    
    def uncover_all(self):
        for col in self.matrix:
            for cell in col:
                cell.set_type(cell.op_type())
    
    def check_win(self):
        win = True
        for col in self.matrix:
            for cell in col:
                if cell.op_type() == 'mined' and cell.type() != 'flagged':
                    win = False
                    break
                if cell.op_type() != 'mined' and cell.opened() is False:
                    win = False
                    break
            if win is False:
                break
        return win


class Victory(pygame.sprite.Sprite):
    def __init__(self):
        super(Victory, self).__init__(v_group)
        self.images = [pygame.transform.scale(pygame.image.load('ppclap1.gif'), (600, 600)),
                       pygame.transform.scale(pygame.image.load('ppclap2.gif'), (600, 600))]
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = 50
        self.index = 0
        self.frame_change_time = 0
    
    def update(self, t):
        self.frame_change_time += t
        if self.frame_change_time > 90:
            self.frame_change_time %= 90
            self.index = (self.index + 1) % 2
            self.image = self.images[self.index]
            
    
def main():
    running = True
    paused = False
    victory = False
    pygame.init()
    field = Field(10, cell_s)
    first_click = True
    timer = pygame.time.Clock()
    while running:
        if paused:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                running = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        field.switch_flag(field.get_click(event.pos))
                    elif event.button == 1:
                        if first_click:
                            field.init_cells(30, field.get_click(event.pos))
                            paused = field.on_click(field.get_click(event.pos), True)
                            first_click = False
                        else:
                            paused = field.on_click(field.get_click(event.pos))
                        if paused:
                            field.uncover_all()
                        if field.all_uncovered():
                            paused = True
                    elif event.button == 2:
                        field.switch_mine(field.get_click(event.pos))
                    if field.check_win():
                        victory = True
                        print('You win')
                        Victory()
        screen.fill('white')
        field.render()
        t = timer.tick(30)
        if victory:
            v_group.update(t) 
            v_group.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()

main()
