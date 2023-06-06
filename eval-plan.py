#!/usr/bin/env python3

import sys
import re
import copy
from pprint import pprint

pat_next = re.compile(r'\(\s*next\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_blocked = re.compile(r'\(\s*blocked\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_at = re.compile(r'\(\s*at\s+([a-zA-Z0-9_-]+)\s+([a-zA-Z0-9_-]+)\s*\)')
pat_num = re.compile(r'[0-9]+')

PDDL_PLAN = []

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

def boardAsStr(board, blocked, at, goal_at):
    num_rows = len(board)
    num_cols = len(board[0])

    s = ''
    for i in range(num_cols):
        s += '+'
        if board[0][i] in blocked['north']:
            s += 'x'
        else:
            s += '-'
    s += '+\n'
    for row in board:
        if row[0] in blocked['west']:
            s += 'x'
        else:
            s += '|'
        for cell in row:
            if cell in at and cell in goal_at:
                m = pat_num.search(at[cell])
                rob = m.group(0)
                m = pat_num.search(goal_at[cell])
                g = m.group(0)

                if rob == g:
                    s += chr(ord('A') + int(m.group(0)) - 1)
                else:
                    s += rob

            elif cell in at:
                m = pat_num.search(at[cell])
                s += m.group(0)

            elif cell in goal_at:
                m = pat_num.search(goal_at[cell])
                s += chr(ord('a') + int(m.group(0)) - 1)

            else:
                s += ' '
            if cell in blocked['east']:
                s += 'x'
            else:
                s += '|'
        s += '\n'

        for cell in row:
            s += '+'
            if cell in blocked['south']:
                s += 'x'
            else:
                s += '-'
        s += '+\n'

    return s

def spliceBoards(b1, b2, text = ''):
    b1 = b1.split('\n')
    b2 = b2.split('\n')
    text = text.split('\n')
    gapsize = max([len(x) for x in text])
    assert(len(b1) == len(b2))

    s = ''
    texti = 0
    for li in range(len(b1)):
        s += b1[li]
        s += '    '
        if texti < len(text):
            s += text[texti]
            for _ in range(gapsize - len(text[texti])):
                s += ' '
            texti += 1
        else:
            for _ in range(gapsize):
                s += ' '
        s += '    '
        s += b2[li]
        s += '\n'
    return s


def printBoard(board, blocked, at, goal_at):
    print(boardAsStr(board, blocked, at, goal_at))


def cellCoord(board, cell):
    for r, row in enumerate(board):
        for c, cl in enumerate(row):
            if cell == cl:
                return r, c
    return None

def applyStep(board, blocked, at, goal_at, step):
    robot_at = { v : k for k, v in at.items() }
    robot = step[0]
    direction = step[1]

    text = f'GO {robot} {direction}\n'
    global PDDL_PLAN
    PDDL_PLAN += [f'(go {robot} {direction})']
    stopped = False
    while robot_at[robot] not in blocked[direction]:
        r, c = cellCoord(board, robot_at[robot])
        text += f'Step {robot} {r} {c} {direction}\n'
        rfrom = r
        cfrom = c
        if direction == 'south':
            r += 1
        elif direction == 'north':
            r -= 1
        elif direction == 'west':
            c -= 1
        elif direction == 'east':
            c += 1
        if board[r][c] in robot_at.values():
            stopped = True
            PDDL_PLAN += [f'(stop-at-robot {robot} cell-{cfrom+1}-{rfrom+1} cell-{c+1}-{r+1} {direction})']
            break
        PDDL_PLAN += [f'(step {robot} cell-{cfrom+1}-{rfrom+1} cell-{c+1}-{r+1} {direction})']
        robot_at[robot] = board[r][c]
    if not stopped:
        PDDL_PLAN += [f'(stop-at-barrier {robot} cell-{c+1}-{r+1} {direction})']

    b1 = boardAsStr(board, blocked, at, goal_at)
    at = { v : k for k, v in robot_at.items() }
    b2 = boardAsStr(board, blocked, at, goal_at)
    b = spliceBoards(b1, b2, text)
    print(b)
    return at

def main(fn, planfn):
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

    if planfn == '-':
        fin = sys.stdin
    else:
        fin = open(planfn, 'r')
    plan = []
    for line in fin:
        if line.startswith('(go '):
            s = line.split()
            robot = s[1]
            direction = s[2].strip(')')
            plan += [(robot, direction)]

    cells = set(cells.keys())
    board = createBoard(cells, cell)
    printBoard(board, blocked, at, goal_at)
    for step in plan:
        at = applyStep(board, blocked, at, goal_at, step)

    goal_position = list(goal_at.keys())[0]
    if goal_position not in at:
        print('PLAN FAILED: Goal position wasn not reached.')
        return -1

    if goal_at[goal_position] != at[goal_position]:
        print('PLAN FAILED: Goal position was not reached by the right robot.')
        return -1
    return 0

if __name__ == '__main__':
    if len(sys.argv) not in [3, 4]:
        print('Usage: {0} problem.pddl problem.plan [full.plan]'.format(sys.argv[0]))
        print('''
This script evaluates the skeleton of the plan "problem.plan". Skeleton
means that it reads only (go ...) action. However, if full.plan is
specified, then it reconstructs and prints out the full plan.
''')

        sys.exit(-1)

    ret = main(sys.argv[1], sys.argv[2])
    if ret == 0 and len(sys.argv) == 4:
        with open(sys.argv[3], 'w') as fout:
            for line in PDDL_PLAN:
                print(line, file = fout)
    sys.exit(ret)
