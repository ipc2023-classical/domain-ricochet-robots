# Ricochet Robots PDDL Domain

It is a domain based on the board game Ricochet Robots
https://boardgamegeek.com/boardgame/51/ricochet-robots

## Tools
 - The script `draw-board.sh` takes a pddl problem file and draw the board
   in ASCII.
 - The script `asp-to-pddl.py` reads an ASP problem file (from `asp-2015`
   directory) from stdin and writes the corresponding PDDL encoding to stdout.
 - The script `asp-solve-with-clingo.sh` takes an ASP problem file (from
   `asp-2015` directory) and runs clingo ASP solver.
