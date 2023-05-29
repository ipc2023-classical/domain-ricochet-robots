#!/usr/bin/env python3

import sys
import re
import random

pat_dim = re.compile(r'^dim\(([0-9]+)\)\.$')
pat_barrier = re.compile(r'^barrier\(([0-9]+), *([0-9]+), *(south|north|east|west)\)\.$')
pat_length = re.compile(r'^length\(([0-9]+)\)\.$')
pat_pos = re.compile(r'^pos\(([a-zA-Z_]+), *([0-9]+), *([0-9]+)\)\.$')
pat_target = re.compile(r'^target\(([a-zA-Z_]+), *([0-9]+), *([0-9]+)\)\.$')

def main():
    asp = sys.stdin.read()
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
            next_cell += ['(next cell-{0}-{1} cell-{0}-{2} south)'.format(x, y, y + 1)]
    for x in range(1, dim + 1):
        for y in range(dim, 1, -1):
            next_cell += ['(next cell-{0}-{1} cell-{0}-{2} north)'.format(x, y, y - 1)]
    for y in range(1, dim + 1):
        for x in range(1, dim):
            next_cell += ['(next cell-{1}-{0} cell-{2}-{0} east)'.format(y, x, x + 1)]
    for y in range(1, dim + 1):
        for x in range(dim, 1, -1):
            next_cell += ['(next cell-{1}-{0} cell-{2}-{0} west)'.format(y, x, x - 1)]

    blocked = []
    for x in range(1, dim + 1):
        blocked += ['(blocked cell-{0}-1 north)'.format(x)]
        blocked += ['(blocked cell-{0}-{1} south)'.format(x, dim)]
    for y in range(1, dim + 1):
        blocked += ['(blocked cell-1-{0} west)'.format(y)]
        blocked += ['(blocked cell-{1}-{0} east)'.format(y, dim)]
    for line in asp:
        m = pat_barrier.match(line)
        if m is not None:
            x = int(m.group(1))
            y = int(m.group(2))
            direction = m.group(3)
            blocked += [f'(blocked cell-{x}-{y} {direction})']

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
            blocked += [f'(blocked cell-{x}-{y} {direction})']

    robots = []
    at = []
    occupied = []
    robot_map = {}
    for line in asp:
        m = pat_pos.match(line)
        if m is not None:
            idx = len(robots) + 1
            robot = 'robot-{0}'.format(idx)
            robot_map[m.group(1)] = robot
            robots += [robot]
            at += ['(at {0} cell-{1}-{2}) ;; {3}' \
                        .format(robot, m.group(2), m.group(3), m.group(1))]
            occupied += [(int(m.group(2)), int(m.group(3)))]

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
    print(out)

    return 0

if __name__ == '__main__':
    sys.exit(main())
