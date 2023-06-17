#!/usr/bin/env python3

import os
import sys
import re
import random
import subprocess

TOPDIR = os.path.dirname(os.path.realpath(__file__))
DRAW_BOARD = os.path.join(TOPDIR, 'draw-board.py')
SOLVER = os.path.join(TOPDIR, 'solve-pddl.py')

pat_dim = re.compile(r'^dim\(([0-9]+)\)\.$')
pat_barrier = re.compile(r'^barrier\(([0-9]+), *([0-9]+), *(south|north|east|west)\)\.$')
pat_length = re.compile(r'^length\(([0-9]+)\)\.$')
pat_pos = re.compile(r'^pos\(([a-zA-Z_]+), *([0-9]+), *([0-9]+)\)\.$')
pat_target = re.compile(r'^target\(([a-zA-Z_]+), *([0-9]+), *([0-9]+)\)\.$')

def main(fnin, fnout, fnplan):
    asp = open(fnin, 'r').read()
    asp = asp.split('\n')
    asp = [x.strip() for x in asp]
    asp = [x for x in asp if len(x) > 0]

    dim = 0
    for line in asp:
        m = pat_dim.match(line)
        if m is not None:
            dim = max(dim, int(m.group(1)))

    directions = ['west', 'east', 'north', 'south']

    cells = []
    for x in range(1, dim + 1):
        for y in range(1, dim + 1):
            cells += [f'cell-{x}-{y}']

    next_cell = []
    for x in range(1, dim + 1):
        for y in range(1, dim):
            next_cell += ['(NEXT cell-{0}-{1} cell-{0}-{2} south)'.format(x, y, y + 1)]
    for x in range(1, dim + 1):
        for y in range(dim, 1, -1):
            next_cell += ['(NEXT cell-{0}-{1} cell-{0}-{2} north)'.format(x, y, y - 1)]
    for y in range(1, dim + 1):
        for x in range(1, dim):
            next_cell += ['(NEXT cell-{1}-{0} cell-{2}-{0} east)'.format(y, x, x + 1)]
    for y in range(1, dim + 1):
        for x in range(dim, 1, -1):
            next_cell += ['(NEXT cell-{1}-{0} cell-{2}-{0} west)'.format(y, x, x - 1)]

    blocked = []
    for x in range(1, dim + 1):
        blocked += ['(BLOCKED cell-{0}-1 north)'.format(x)]
        blocked += ['(BLOCKED cell-{0}-{1} south)'.format(x, dim)]
    for y in range(1, dim + 1):
        blocked += ['(BLOCKED cell-1-{0} west)'.format(y)]
        blocked += ['(BLOCKED cell-{1}-{0} east)'.format(y, dim)]
    for line in asp:
        m = pat_barrier.match(line)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            direction = m.group(3)
            blocked += [f'(BLOCKED cell-{x}-{y} {direction})']

            if direction == 'east':
                direction = 'west'
                x += 1
            elif direction == 'west':
                direction = 'east'
                x -= 1
            elif direction == 'north':
                direction = 'south'
                y -= 1
            elif direction == 'south':
                direction = 'north'
                y += 1

            assert(x > 0 and x <= dim)
            assert(y > 0 and y <= dim)
            blocked += [f'(BLOCKED cell-{x}-{y} {direction})']

    robot_idx = {
        'red' : 1,
        'blue' : 2,
        'green' : 3,
        'yellow' : 4,
    }
    robots = []
    at = []
    occupied = []
    robot_map = {}
    robot_at = []
    for line in asp:
        m = pat_pos.match(line)
        if m is not None:
            idx = robot_idx[m.group(1)]
            robot = 'robot-{0}'.format(idx)
            robot_map[m.group(1)] = robot
            robots += [robot]
            robot_at += ['(at {0} cell-{1}-{2}) ;; {3}' \
                            .format(robot, m.group(2), m.group(3), m.group(1))]
            occupied += [(int(m.group(2)), int(m.group(3)))]
    at += sorted(robot_at)

    free = []
    for x in range(1, dim + 1):
        for y in range(1, dim + 1):
            if (x, y) not in occupied:
                free += [f'(free cell-{x}-{y})']

    goal = []
    for line in asp:
        m = pat_target.match(line)
        if m is not None:
            rob = robot_map[m.group(1)]
            goal += ['(at {0} cell-{1}-{2})' \
                        .format(rob, m.group(2), m.group(3))]
    length = None
    for line in asp:
        m = pat_length.match(line)
        if m is not None:
            length = int(m.group(1))

    cells = ' '.join(cells)
    robots = ' '.join(robots)
    directions = ' '.join(directions)
    next_cell = '\n    '.join(next_cell)
    blocked = '\n    '.join(blocked)
    free = '\n    '.join(free)
    at = '\n    '.join(at)
    goal = '\n        '.join(goal)

    rand = int(1000000 * random.random())
    out = f'''(define (problem ricochet-robots-{dim}x{dim}-{length}-{rand})
(:domain ricochet-robots)

(:objects
    {cells} - cell
    {robots} - robot
    {directions} - direction
)

(:init
    {next_cell}

    {blocked}

    {free}

    {at}

    (nothing-is-moving)

    (= (total-cost) 0)
    (= (go-cost) 1)
    (= (step-cost) 0)
    (= (stop-cost) 0)
)
(:goal
    (and
        {goal}
        (nothing-is-moving)
    )
)
(:metric minimize (total-cost))
)

'''

    fname = fnin.split('/')[-1]
    header = f';; Generated from file {fname} from the ASP competition 2015\n'

    cmd = ['python3', DRAW_BOARD, '-']
    proc = subprocess.run(cmd, input = out, encoding = 'ascii',
                          capture_output = True)
    header += ';;\n'
    header += proc.stdout

    out = header + out
    with open(fnout, 'w') as fout:
        fout.write(out)

    ret = os.system(f'python3 {SOLVER} {fnout} {fnplan}')
    if ret != 0:
        return -1
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: {0} problem.asp problem.pddl problem.plan'.format(sys.argv[0]))
        print('''
This script translates the ASP problems into PDDL problem file.
It also calls the solver solve-pddl.py and puts the (optimal) plan into the plan file.
''')
        sys.exit(-1)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
