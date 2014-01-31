#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import time
import sys
import os

from itertools import product


os.environ['SDL_VIDEO_WINDOW_POS'] = '300, 30'

class Cell(object):

    def __init__(self, spawn_point, node, cycle):
        self.spawn_point = spawn_point
        self.node = node
        self.created = time.ctime()
        self.generations = 1
        self.cycle_created = cycle 
    
    def __str__(self):
        return ('Node:%s Spawn Position:%s Created:%s Cycle:%s Generations:%s' 
                % (self.node, self.spawn_point, self.created, 
                   self.cycle_created, self.generations))
    
    def __repr__(self):
        return '%s <Node> [%s]' % (self, str(self.node))


class Board(object):

    def __init__(self):
        self.board = pygame.display.set_mode((900, 720))
        self.board.fill((255, 255, 255))
        self.board.fill((0, 0, 0), (720, 0, 1, 720))
        self.board.fill((92, 117, 94), (0, 0, 720, 720))
        self.board.fill((156, 159, 132), (721, 0, 179, 720))
        self.start = pygame.image.load('images/start.png')
        self.stop = pygame.image.load('images/stop.png')
        self.grid = pygame.image.load('images/grid.png')
        self.state = pygame.image.load('images/state.png')
        self.clear = pygame.image.load('images/clear.png')
        self.cycle = False
        self.cycle_count = 1
        self.life_stage = 17
        self.nodes = list(product(xrange(0, 720, 10), xrange(0, 720, 10)))
        self.fill_node = lambda x: x - (x % 10)
        self.find_neighbors = lambda n, p: (n[0] + p[0], n[1] + p[1])
        self.neighbors = [[0, 10], [10, 0], [10, 10], [-10, 0], 
                          [0, -10], [-10, -10], [10, -10], [-10, 10]]
        self.living_cells = dict()

    @property
    def update(self):
        self.board.fill((255, 255, 255))
        self.board.fill((0, 0, 0), (720, 0, 1, 720))
        self.board.fill((92, 117, 94), (0, 0, 720, 720))
        self.board.fill((156, 159, 132), (721, 0, 179, 720))
        self.start_rect = self.board.blit(self.start, (760, 300))
        self.stop_rect = self.board.blit(self.stop, (760, 350))
        self.state_rect = self.board.blit(self.state,(760, 450))
        self.clear_rect = self.board.blit(self.clear, (760, 500))
        for cell in self.living_cells:
            generation = self.living_cells[cell].generations
            x, y = self.living_cells[cell].node
            self.board.fill(self.cell_stage(generation), (x, y, 10, 10)) 
        self.board.blit(self.grid, (0, 0))
        pygame.display.flip()

    def cell_stage(self, generation):
        STAGE = generation * self.life_stage
        R, G, B = (0, 255, 0)
        while STAGE:
            STAGE -= self.life_stage
            if not ~G & B and R < G:
                R += self.life_stage
            elif not ~R & B and G > B:
                G -= self.life_stage
            elif not ~R & G and B < R:
                B += self.life_stage
            elif not ~R & G & ~B and R > G:
                R -= self.life_stage
            else:
                STAGE = 0
        return (R, G, B)

    def create_cell(self):
        cell_position = pygame.mouse.get_pos()
        node = tuple(map(self.fill_node, cell_position))
        if node in self.nodes and not self.living_cells.get(node):
            new_cell = Cell(cell_position, node, self.cycle_count)
            self.living_cells[node] = new_cell
            print new_cell

    def destroy_cell(self):               
        cell_position = pygame.mouse.get_pos()
        node = tuple(map(self.fill_node, cell_position))
        if self.living_cells.get(node):
            del self.living_cells[node]

    def calculate_cell_state(self):
        # Any live cell with fewer than two live neighbours dies, as if caused by under-population.
        # Any live cell with two or three live neighbours lives on to the next generation.
        # Any live cell with more than three live neighbours dies, as if by overcrowding.
        # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.        
        born_cells = dict()
        died_cells = list()
        for node in self.nodes:
            all_neighbors = [self.find_neighbors(node, p) 
                             for p in self.neighbors]
            live_neighbors = [n for n in all_neighbors if n in self.living_cells]
            if self.living_cells.get(node) and len(live_neighbors) not in (2, 3):
                died_cells.append(node)
            elif len(live_neighbors) == 3 and node not in self.living_cells:
                new_cell = Cell(node, node, self.cycle_count)
                born_cells[node] = new_cell
        for cell in died_cells:
            del self.living_cells[cell]
        self.living_cells.update(born_cells)

    def next_cell_generation(self):
        for cell in self.living_cells:
            self.living_cells[cell].generations += 1
        
    def clear(self):
        self.living_cells = dict()

    def state(self):
        print '    === Grid State :: Cycle %d ===' % self.cycle_count
        for cell in self.living_cells:
            print self.living_cells[cell]


class Conway(Board):

    def __init__(self):
        pygame.init()
        super(Conway, self).__init__()
        self.L_MOUSEBUTTON_DOWN = False
        self.R_MOUSEBUTTON_DOWN = False

    def life_loop(self):
        while True:
            if not self.cycle:
                if self.L_MOUSEBUTTON_DOWN:
                    self.create_cell()
                elif self.R_MOUSEBUTTON_DOWN:
                    self.destroy_cell()
                for event in pygame.event.get():
                    if (event.type == pygame.KEYDOWN and 
                        event.key == pygame.K_ESCAPE):
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        if self.start_rect.collidepoint(pos):
                            self.cycle = True
                        elif self.clear_rect.collidepoint(pos):
                            self.clear()
                        elif self.state_rect.collidepoint(pos):
                            self.state()
                        elif event.button == 1:
                            self.L_MOUSEBUTTON_DOWN = True
                        elif event.button == 3:
                            self.R_MOUSEBUTTON_DOWN = True
                    elif (event.type == pygame.MOUSEBUTTONUP and
                          event.button == 1):
                        self.L_MOUSEBUTTON_DOWN = False
                    elif (event.type == pygame.MOUSEBUTTONUP and
                          event.button == 3):
                        self.R_MOUSEBUTTON_DOWN = False
            else:
                pos = pygame.mouse.get_pos()
                for event in pygame.event.get():
                    if (event.type == pygame.KEYDOWN and
                        event.key == pygame.K_ESCAPE):
                        sys.exit()
                    elif (event.type == pygame.MOUSEBUTTONDOWN and
                          self.stop_rect.collidepoint(pos)):
                        self.cycle = False
                self.cycle_count += 1
                self.next_cell_generation()
                self.calculate_cell_state()
                time.sleep(1)
            self.update


if __name__ == '__main__':
    conway = Conway()
    conway.life_loop()