**This is a copy of [Lireer/ricochet-robot-solver](https://github.com/Lireer/ricochet-robot-solver)**
with few modifications made by Rebecca Eifler <eifler@cs.uni-saarland.de> allowing to feed the solver
with the definition of the problem to its standard input.

# Ricochet Robots Solver

**Based on the work of: [Lireer/ricochet-robot-solver](https://github.com/Lireer/ricochet-robot-solver)**

A collection of crates for solving the board game [ricochet robots](https://en.wikipedia.org/wiki/Ricochet_Robot).

Ricochet Robots is a puzzle game played on a 16x16 grid board.
The player can move robots of four different colors and tries to move a robots to a target of the same color with as few moves as possible.
Robots can only move in straight lines until they hit an obstacle, a wall or another robot.
Any robot can be moved at any point.
The player to find the shortest path gets a token.
After every target on the board has been visited the player with the most tokens wins.

## Project structure

This project is split into multiple parts to make management of the codebase easier and more modular:

### Board

The base which everything builds upon is in `ricochet_board`.
It contains the implementation of the board and game logic. Besides that anything related to creating boards is also located there, whether it's putting board quadrants of the physical board together or even randomly generating boards of any size.

### Solvers

Multiple solvers have been implemented to find optimal solutions.

Given a board, a target and the robots start positions any move of a robot can be seen as moving along an axis in an undirected graph to another state. This means path finding algorithms can be used to traverse this graph to find the shortest path to a state with the main robot on the target.

So far these algorithms have been implemented and optimized for riochet robots (sorted by fastest to slowest):

| Algorithm               | Finds the shortest path? |
| ----------------------- | ------------------------ |
| A\*                     | yes                      |
| Iterative deepening A\* | yes                      |
| Breadth-first search    | yes                      |
| Monte Carlo tree search | no                       |

## Building from source

Building from source requires a stable rust compiler which can be installed using [rustup](https://rustup.rs/).
If no python interop is needed, the rust code can be compiled with `cargo build --release` or run with `cargo run --release`.

## Documentation

The documentation is besides the code and can be easily viewed by running `cargo doc --open`, to view the documenation of private code add `--document-private-items`.

## Contributing

Any code to be included in the project has to be formatted with **rustfmt** and checked with **clippy**.
Make sure no tests are failing and run the benchmarks with and without your changes if the solvers were changed to see possible performance regressions.
