#!/usr/bin/env python3

import os
import sys
import random

TOPDIR = os.path.dirname(os.path.realpath(__file__))
PYTHON = 'python3'
ASP_TO_PDDL = os.path.join(TOPDIR, 'asp-to-pddl.py')

def genRandASP(size, num_barriers):
    s = ''

    barriers = set()
    while True:
        if len(barriers) == num_barriers:
            break

        x = random.randint(1, size)
        y = random.randint(1, size)
        dir = random.choice(['north', 'south', 'east', 'west'])
        if dir == 'south':
            other = (x, y + 1, 'north')
        elif dir == 'north':
            other = (x, y - 1, 'south')
        elif dir == 'west':
            other = (x - 1, y, 'east')
        elif dir == 'east':
            other = (x + 1, y, 'west')
        if dir == 'south' and y == size:
            continue
        if dir == 'north' and y == 1:
            continue
        if dir == 'east' and x == size:
            continue
        if dir == 'west' and x == 1:
            continue
        if (x, y, dir) not in barriers and other not in barriers:
            barriers.add((x, y, dir))
            s += f'barrier({x},{y},{dir}).\n'

    for i in range(1, size + 1):
        s += f'dim({i}).\n'

    robot_pos = set()
    for rob in ['red', 'blue', 'green', 'yellow']:
        while True:
            x = random.randint(1, size)
            y = random.randint(1, size)
            if (x, y) not in robot_pos:
                robot_pos.add((x, y))
                s += f'pos({rob},{x},{y}).\n'
                break

    rob = random.choice(['red', 'blue', 'green', 'yellow'])
    x = random.randint(1, size)
    y = random.randint(1, size)
    s += f'target({rob},{x},{y}).\n'
    return s

#def main(board_size, num_moves, fnpddl, fnplan):
#    for _ in range(50):
#        num_barriers = random.randint(5, 5 + board_size**2 // 3)
#        print(f'size: {board_size}, barriers: {num_barriers} :: {num_moves}')
#        asp = genRandASP(board_size, num_barriers)
#        tmpfn = f'generate-{os.getpid()}.asp'
#        with open(tmpfn, 'w') as fout:
#            fout.write(asp)
#        cmd = f'{ASP_TO_PDDL} {tmpfn} {fnpddl} {fnplan}'
#        ret = os.system(cmd)
#        if os.system(cmd) != 0:
#            os.unlink(tmpfn)
#            continue
#        os.unlink(tmpfn)
#        plan_cost = int(open(fnplan, 'r').readline().strip().split()[-1])
#        print(f'    plan cost: {plan_cost}')
#        if plan_cost == num_moves:
#            print(f'FOUND {board_size} {num_moves}')
#            return 0
#    os.unlink(fnpddl)
#    os.unlink(fnplan)
#    return -1

def main(min_board_size, max_board_size, max_steps):
    fnasp = f'generate-{os.getpid()}.asp'
    fnpddl = f'generate-{os.getpid()}.pddl'
    fnplan = f'generate-{os.getpid()}.plan'
    for _ in range(max_steps):
        board_size = random.randint(min_board_size, max_board_size)
        num_barriers = random.randint(5, 5 + board_size**2 // 3)
        print(f'size: {board_size}, barriers: {num_barriers}', file = sys.stderr, end = '')
        sys.stderr.flush()

        asp = genRandASP(board_size, num_barriers)
        with open(fnasp, 'w') as fout:
            fout.write(asp)

        cmd = f'{ASP_TO_PDDL} {fnasp} {fnpddl} {fnplan}'
        ret = os.system(cmd)
        if os.system(cmd) == 0:
            plan_cost = int(open(fnplan, 'r').readline().strip().split()[-1])
            print(f' --> cost: {plan_cost}', file = sys.stderr, end = '')
            sys.stderr.flush()

            fn = 'p-{0:02d}-{1:02d}'.format(board_size, plan_cost)
            if plan_cost > 0 and not os.path.isfile(fn + '.pddl'):
                os.system(f'cp {fnpddl} {fn}.pddl')
                os.system(f'cp {fnplan} {fn}.plan')
                print(f' ADD {fn}.pddl {fn}.plan', file = sys.stderr)
            else:
                print(' IGN ', file = sys.stderr)
        else:
            print(' FAILED', file = sys.stderr)
        sys.stderr.flush()

        if os.path.isfile(fnasp):
            os.unlink(fnasp)
        if os.path.isfile(fnpddl):
            os.unlink(fnpddl)
        if os.path.isfile(fnplan):
            os.unlink(fnplan)
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} min-board-size max-board-size max-steps', file = sys.stderr)
        print('''
This script generates random instances.
It makes {max-steps} steps. In each step, it generates a square NxN board
where N is chosen randomly between {min-board-size} and {max-board-size}.
Then it places between 5 and 5 + N^2 / 3 barriers inside the board.
The resulting files are named p-{N}-{optimal-cost}.*

This script relies on asp-to-pddl.py.
''', file = sys.stderr)
        sys.exit(-1)
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))

#    if len(sys.argv) != 5:
#        print(f'Usage: {sys.argv[0]} board-size num-moves out.pddl out.plan', file = sys.stderr)
#        sys.exit(-1)
#    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4]))
