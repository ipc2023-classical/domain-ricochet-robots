#!/usr/bin/env python3

import sys
import re

pat_next = re.compile(r'\(\s*next\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_blocked = re.compile(r'\(\s*blocked\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_at = re.compile(r'\(\s*at\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_num = re.compile(r'[0-9]+')

robot_num_to_color = {'1': 'r', '2': 'b', '3': 'g', '4': 'y'}

def boardRow(start, cell):
    row = [start]
    cur = start
    while cur in cell['east']:
        assert(len(cell['east'][cur].keys()) == 1)
        nx = list(cell['east'][cur].keys())[0]
        row += [nx]
        cur = nx
    return row

def createBoard(cells, cell):
    west = cells - set(cell['west'].keys())
    northwest = west - set(cell['north'].keys())
    assert(len(northwest) == 1)

    cur = list(northwest)[0]
    board = [boardRow(cur, cell)]
    while cur in cell['south']:
        assert(len(cell['south'][cur].keys()) == 1)
        nx = list(cell['south'][cur].keys())[0]
        board += [boardRow(nx, cell)]
        cur = nx

    return board

def printBoard(board, blocked, at, goal_at):
    num_rows = len(board)
    num_cols = len(board[0])
    
    assert num_rows == num_cols , "Board needs to be a square!"
    
    print(num_rows);

    for x in range(num_cols):
        for y in range(num_rows):
            if board[x][y] in blocked['south']:
                print(str(y) + ' ' + str(x) + ' d')
            if board[x][y] in blocked['east']:
                print(str(y) + ' ' + str(x) + ' r')
                
    print("T")
    for cell, robot in goal_at.items():
        target_coordinates = cell.split('-')[1:]
        robot_id = robot.replace('robot-','')
        x = int(target_coordinates[0]) - 1
        y = int(target_coordinates[1]) - 1
        print(str(x) + ' ' + str(y) + ' ' + robot_num_to_color[robot_id])
    
    for cell, robot in at.items():
        target_coordinates = cell.split('-')[1:]
        robot_id = robot.replace('robot-','')
        x = int(target_coordinates[0]) - 1
        y = int(target_coordinates[1]) - 1
        print(str(x) + ' ' + str(y) + ' ' + robot_num_to_color[robot_id])


def main(fn):
    cells = {}
    cell = {
        'south' : {},
        'north' : {},
        'east' : {},
        'west' : {},
    }
    blocked = {
        'south' : {},
        'north' : {},
        'east' : {},
        'west' : {},
    }
    at = {}
    goal_at = {}
    with open(fn, 'r') as fin:
        in_init = False
        in_goal = False
        for line in fin:
            if '(:init' in line:
                in_init = True
                in_goal = False
            if '(:goal' in line:
                in_init = False
                in_goal = True

            if in_goal:
                m = pat_at.search(line)
                if m is not None:
                    r = m.group(1)
                    c = m.group(2)
                    goal_at[c] = r

            if not in_init:
                continue

            m = pat_next.search(line)
            if m is not None:
                fr = m.group(1)
                to = m.group(2)
                dr = m.group(3)

                if fr not in cell[dr]:
                    cell[dr][fr] = {}
                assert(to not in cell[dr][fr])
                cell[dr][fr][to] = True
                cells[fr] = True
                cells[to] = True

            m = pat_blocked.search(line)
            if m is not None:
                c = m.group(1)
                dr = m.group(2)
                blocked[dr][c] = True

            m = pat_at.search(line)
            if m is not None:
                r = m.group(1)
                c = m.group(2)
                at[c] = r

    cells = set(cells.keys())
    board = createBoard(cells, cell)
    printBoard(board, blocked, at, goal_at)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: {0} problem.pddl'.format(sys.argv[0]))
        sys.exit(-1)
    sys.exit(main(sys.argv[1]))
    
    
# cat ../domain-ricochet-robots/board/test2.board | cargo run --release ricli -p -v
