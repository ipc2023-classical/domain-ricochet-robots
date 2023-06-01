use std::collections::HashSet;
use text_io::{read, try_scan};
use std::env;

use ricochet_board::{
    quadrant, Game, PositionEncoding, Robot, RobotPositions, Round, Symbol, Target, Position, Board, draw_board
};
use std::collections::{BTreeMap};
use ricochet_solver::{IdaStar, Solver};

fn main() {

    let args: Vec<String> = env::args().collect();

    let size_string: String = read!("{}\n");
    let size = size_string.parse::<u16>().unwrap();

    let mut board = Board::new_empty(size).wall_enclosure();
    let walls = board.get_mut_walls();

    // walls
    loop {
        let line: String = read!("{}\n");
        let parts: Vec<&str> = line.split(' ').collect();

        if parts.len() == 1 {
            break;
        }

        let row = parts[0].parse::<usize>().unwrap();
        let col = parts[1].parse::<usize>().unwrap();
        let dir = parts[2];

        if dir == "d" {
            walls[row][col].down = true;
        }
        if dir == "r" {
            walls[row][col].right = true;
        }
    }

    if args.len() > 3 && &args[3] == "-v"{
        println!("{}",draw_board(board.get_walls()));
    }

    // targets
    let mut targets = BTreeMap::new();

    let targte_string: String = read!("{}\n");
    let parts: Vec<&str> = targte_string.split(' ').collect();

    let row = parts[0].parse::<u16>().unwrap();
    let col = parts[1].parse::<u16>().unwrap();
    let target_color = parts[2];

    let mut target = Target::Red(Symbol::Triangle);

    match target_color {
        "r" => target = Target::Red(Symbol::Triangle),
        "b" => target = Target::Blue(Symbol::Triangle),
        "g" => target = Target::Green(Symbol::Triangle),
        "y" => target = Target::Yellow(Symbol::Triangle),
        &_ => panic!("Color does not exists")
    };

    targets.insert(target, Position::new(row, col));

    let game = Game::new(board, targets);
    
    // init robot positions
    let mut positions = [(0, 0); 4];

    for i in 0..4 {
        let input: String = read!("{}\n");
        let parts: Vec<&str> = input.split(' ').collect();

        let row = parts[0].parse::<u16>().unwrap();
        let col = parts[1].parse::<u16>().unwrap();

        positions[i] = (row, col);
    }

    // position order: r b g y
    let robopos = RobotPositions::from_tuples(&positions);
    
    
    let target_position = game
        .get_target_position(&target)
        .expect("Failed to find the position of the target on the board");
    let round = Round::new(game.board().clone(), target, target_position);

    let path = IdaStar::new().solve(&round, robopos);
    println!("{}", path.len());
    
    if args.len() > 3 && &args[3] == "-v"{
        let movements = path.movements();
        for (move_n, (robot, dir)) in movements.iter().enumerate() {
            println!(" {:>2}  {:<8}{:<6}", move_n + 1, robot, dir);
        }
    }
}
