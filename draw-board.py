#!/usr/bin/env python3

import sys
import re

pat_next = re.compile(r'\(\s*NEXT\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_blocked = re.compile(r'\(\s*BLOCKED\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_at = re.compile(r'\(\s*at\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_num = re.compile(r'[0-9]+')

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

    s = ';; '
    for i in range(num_cols):
        s += '+'
        if board[0][i] in blocked['north']:
            s += 'xx'
        else:
            s += '--'
    s += '+\n'
    for row in board:
        s += ';; '
        if row[0] in blocked['west']:
            s += 'x'
        else:
            s += '|'
        for cell in row:
            assert(cell not in at or cell not in goal_at)
            if cell in at:
                m = pat_num.search(at[cell])
                s += 'R' + m.group(0)
            elif cell in goal_at:
                m = pat_num.search(goal_at[cell])
                s += 'G' + m.group(0)
            else:
                s += '  '
            if cell in blocked['east']:
                s += 'x'
            else:
                s += '|'
        s += '\n'

        s += ';; '
        for cell in row:
            s += '+'
            if cell in blocked['south']:
                s += 'xx'
            else:
                s += '--'
        s += '+\n'

    print(s)


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
    if fn == '-':
        fin = sys.stdin
    else:
        fin = open(fn, 'r')

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
        print('''
Draws a board with placements of all robots and the goal in ascii art
''')
        sys.exit(-1)
    sys.exit(main(sys.argv[1]))
