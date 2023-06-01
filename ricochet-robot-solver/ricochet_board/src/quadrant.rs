//! Create a [`Game`](super::Game) from quadrants.
//!
//! These quadrants are the same as the ones used to build the physical board.

use draw_a_box::{find_character, Weight};
use std::fmt;

use crate::draw::{FIELD_DRAW_HEIGHT, FIELD_DRAW_WIDTH};
use crate::{Field, Game, PositionEncoding, Round, Symbol, Target, TARGETS};

/// The side length of the standard physical board.
pub const STANDARD_BOARD_SIZE: PositionEncoding = 16;

/// The side length of a quadrant.
const QUADRANT_SIZE: PositionEncoding = STANDARD_BOARD_SIZE / 2 + 1;

/// All possible orientations of a quadrant.
pub const ORIENTATIONS: [Orientation; 4] = [
    Orientation::UpperLeft,
    Orientation::UpperRight,
    Orientation::BottomRight,
    Orientation::BottomLeft,
];

/// Number of unique boards that can be assembled from the standard board quadrants.
///
/// The board can always be rotated in a way that a red quadrant would be in the upper left. So
/// there are three possible values, after that choose one of the remaining nine quadrants and so
/// forth until we have a complete board.
pub const DISTINCT_STANDARD_BOARDS: usize = 3 * 9 * 6 * 3;

/// Number of unique rounds that can be assembled from the standard board quadrants.
pub const DISTINCT_STANDARD_ROUNDS: usize = DISTINCT_STANDARD_BOARDS * 17;

/// The orientation of a quadrant.
#[derive(Copy, Clone, Debug, PartialEq)]
pub enum Orientation {
    /// Indicates a quadrant rotated so it fits in the upper left.
    UpperLeft,
    /// Indicates a quadrant rotated so it fits in the upper right.
    UpperRight,
    /// Indicates a quadrant rotated so it fits in the bottom right.
    BottomRight,
    /// Indicates a quadrant rotated so it fits in the bottom left.
    BottomLeft,
}

impl Orientation {
    /// Returns the number of clockwise rotations needed to rotate a quadrant to `orient`.
    pub fn right_rotations_to(self, orient: Orientation) -> usize {
        let all = [
            Orientation::UpperLeft,
            Orientation::UpperRight,
            Orientation::BottomRight,
            Orientation::BottomLeft,
        ];
        let self_pos = all.iter().position(|o| o == &self).unwrap() as isize;
        let orient_pos = all.iter().position(|o| o == &orient).unwrap() as isize;
        (orient_pos - self_pos + all.len() as isize) as usize % all.len()
    }
}

impl fmt::Display for Orientation {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        write!(
            fmt,
            "{}",
            match self {
                Orientation::UpperLeft => "upper left",
                Orientation::UpperRight => "upper right",
                Orientation::BottomRight => "bottom right",
                Orientation::BottomLeft => "bottom left",
            }
        )
    }
}

/// The color of a quadrant which is given by the physical counterpart.
#[derive(Copy, Clone, Debug, Eq, PartialEq, Hash)]
pub enum QuadColor {
    /// Indicates a green quadrant.
    Green,
    /// Indicates a red quadrant.
    Red,
    /// Indicates a blue quadrant.
    Blue,
    /// Indicates a yellow quadrant.
    Yellow,
}

impl fmt::Display for QuadColor {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        write!(
            fmt,
            "{}",
            match self {
                QuadColor::Green => r#""green"(g)"#,
                QuadColor::Red => r#""red"(r)"#,
                QuadColor::Blue => r#""blue"(b)"#,
                QuadColor::Yellow => r#""yellow"(y)"#,
            }
        )
    }
}

/// The directions a [`Field`](super::Field) stores walls for.
#[derive(Copy, Clone, Debug, PartialEq)]
pub enum WallDirection {
    /// Indicates a wall at the bottom of a field.
    Down,
    /// Indicates a wall to the right of a field.
    Right,
}

impl WallDirection {
    /// Changes the direction of a wall when rotating a quadrant.
    fn rotate(self) -> Self {
        match self {
            WallDirection::Down => WallDirection::Right,
            WallDirection::Right => WallDirection::Down,
        }
    }
}

/// A quadrant representing a quarter of the ricochet board.
///
/// The physical board is built from four 8x8 pieces. Each of these pieces is assigned a color and
/// can be rotated in four different ways.
#[derive(Clone, Debug, PartialEq)]
pub struct BoardQuadrant {
    orientation: Orientation,
    color: QuadColor,
    walls: Vec<((isize, isize), WallDirection)>,
    targets: Vec<((isize, isize), Target)>,
}

impl BoardQuadrant {
    /// Returns the color of the quadrant.
    pub fn color(&self) -> QuadColor {
        self.color
    }

    /// Returns the orientation of the quadrant.
    pub fn orientation(&self) -> Orientation {
        self.orientation
    }

    /// Returns the walls on the quadrant.
    pub fn walls(&self) -> &Vec<((isize, isize), WallDirection)> {
        &self.walls
    }

    /// Returns the targets on the quadrant.
    pub fn targets(&self) -> &Vec<((isize, isize), Target)> {
        &self.targets
    }

    /// Rotates the quadrant clockwise.
    pub fn rotate_right(&mut self) {
        self.orientation = match self.orientation {
            Orientation::UpperLeft => Orientation::UpperRight,
            Orientation::UpperRight => Orientation::BottomRight,
            Orientation::BottomRight => Orientation::BottomLeft,
            Orientation::BottomLeft => Orientation::UpperLeft,
        };

        self.walls = self
            .walls
            .iter()
            .map(|&((c, r), dir)| match dir {
                WallDirection::Right => (
                    ((STANDARD_BOARD_SIZE / 2) as isize - r - 1, c),
                    dir.rotate(),
                ),
                WallDirection::Down => (
                    ((STANDARD_BOARD_SIZE / 2 - 1) as isize - r - 1, c),
                    dir.rotate(),
                ),
            })
            .collect();

        self.targets = self
            .targets
            .iter()
            .map(|&((c, r), t)| (((STANDARD_BOARD_SIZE / 2) as isize - r - 1, c), t))
            .collect();
    }

    /// Rotates the quadrant to the given orientation.
    pub fn rotate_to(&mut self, orient: Orientation) {
        for _ in 0..self.orientation.right_rotations_to(orient) {
            self.rotate_right();
        }
    }

    /// Creates a default quadrant of `color` in the upper left with no walls or targets.
    fn default_quadrant(color: QuadColor) -> Self {
        BoardQuadrant {
            orientation: Orientation::UpperLeft,
            color,
            walls: Vec::new(),
            targets: Vec::new(),
        }
    }

    /// Sets multiple walls in the given direction.
    fn set_walls(mut self, dir: WallDirection, walls: Vec<(isize, isize)>) -> Self {
        for (c, r) in walls {
            self.walls.push(((c, r), dir));
        }
        self
    }

    /// Adds `target` at `pos` to the quadrant.
    fn set_target(mut self, pos: (isize, isize), target: Target) -> Self {
        self.targets.push((pos, target));
        self
    }
}

impl fmt::Display for BoardQuadrant {
    fn fmt(&self, fmt: &mut fmt::Formatter) -> fmt::Result {
        let size = QUADRANT_SIZE as usize;
        let mut print = vec![vec![Field::default(); size]; size];

        for ((c, r), d) in &self.walls {
            let field = &mut print[(c + 1) as usize][(r + 1) as usize];
            match d {
                WallDirection::Down => field.down = true,
                WallDirection::Right => field.right = true,
            }
        }

        let (mut canvas, mut weights) = crate::draw::create_board_string_vec(&print);
        let mut output = String::new();

        // Remove the first column and first row and smoothen the now outer boarder.
        for row in FIELD_DRAW_HEIGHT..canvas[0].len() {
            for col in FIELD_DRAW_WIDTH..canvas.len() {
                if row == FIELD_DRAW_HEIGHT && col % FIELD_DRAW_WIDTH == 0 {
                    let w = &mut weights[col][row];
                    w[0] = Weight::Empty;
                    canvas[col][row] = find_character(Weight::Empty, w[1], w[2], w[3]);
                }
                if col == FIELD_DRAW_WIDTH && row % FIELD_DRAW_HEIGHT == 0 {
                    let w = &weights[col][row];
                    canvas[col][row] = find_character(w[0], w[1], w[2], Weight::Empty);
                }
                output.push_str(canvas[col][row]);
            }
            output.push('\n');
        }

        write!(fmt, "{}", output)
    }
}

/// Creates a `Round` from a `seed` between 0 and [8262](DISTINCT_STANDARD_ROUNDS).
///
/// The actual seed used is the given `seed` mod `DISTINCT_STANDARD_ROUNDS` to ensure its in the
/// correct range. The target is chosen with `num_to_target(seed % TARGETS.len())`, the game with
/// `game_from_seed(seed / target_count)`.
pub fn round_from_seed(seed: usize) -> Round {
    let seed = seed % DISTINCT_STANDARD_ROUNDS;
    let target_count = TARGETS.len();
    let game = game_from_seed(seed / target_count);
    let target = num_to_target(seed % target_count);
    Round::new(
        game.board().clone(),
        target,
        *game
            .targets()
            .get(&target)
            .expect("could not find a target in a `Game`"),
    )
}

/// Creates a `Game` from a seed between 0 and [486](DISTINCT_STANDARD_BOARDS).
///
/// The actual seed used is the given `seed` mod `DISTINCT_STANDARD_BOARDS` to ensure its in the
/// correct range.
pub fn game_from_seed(seed: usize) -> Game {
    let seed = seed % DISTINCT_STANDARD_BOARDS;
    let mut indices = Vec::new();
    let mut div_mod = |i: usize, div: usize| {
        indices.push(i % div);
        i / div
    };

    let mut div = seed;
    for denom in &[3, 9, 6, 3] {
        div = div_mod(div, *denom);
    }

    let quadrants = gen_quadrants();
    let mut chosen_quads = Vec::with_capacity(4);

    // Choose a red quadrant for the upper left piece.
    chosen_quads.push(quadrants[indices[0]].clone());

    for &idx in &indices[1..] {
        let next_quad = quadrants
            .iter()
            .filter(|&quad| !chosen_quads.iter().any(|ct| ct.color() == quad.color()))
            .nth(idx)
            .unwrap()
            .clone();
        chosen_quads.push(next_quad);
    }

    chosen_quads
        .iter_mut()
        .zip(ORIENTATIONS.iter())
        .for_each(|(quad, orient)| quad.rotate_to(*orient));
    Game::from_quadrants(&chosen_quads)
}

/// Create a target from an integer between 0 and 16 inclusive.
///
/// There are four targets per color
/// 0 to 3 are the red targets. 4 to 7 are the blue targets, followed by four green, four yellow and finally one spiral.
/// The symbols are chosen with [num_to_target_symbol].
fn num_to_target(n: usize) -> Target {
    match n {
        0..=3 => Target::Red(num_to_target_symbol(n % 4)),
        4..=7 => Target::Blue(num_to_target_symbol(n % 4)),
        8..=11 => Target::Green(num_to_target_symbol(n % 4)),
        12..=15 => Target::Yellow(num_to_target_symbol(n % 4)),
        16 => Target::Spiral,
        _ => panic!(),
    }
}

/// Creates a symbol from an integer between 0 and 3 inclusive.
///
/// The ordering is `Circle`, `Triangle`, `Square`, and `Hexagon`.
fn num_to_target_symbol(n: usize) -> Symbol {
    match n {
        0 => Symbol::Circle,
        1 => Symbol::Triangle,
        2 => Symbol::Square,
        3 => Symbol::Hexagon,
        _ => panic!(),
    }
}

/// Creates a vec containing all known quadrants.
///
/// There are three quadrants for each color and the vec contains them in the order red, blue, green, yellow.
pub fn gen_quadrants() -> Vec<BoardQuadrant> {
    vec![
        // Add red boards
        BoardQuadrant::default_quadrant(QuadColor::Red)
            .set_walls(
                WallDirection::Down,
                vec![(0, 5), (1, 3), (3, 6), (4, 0), (5, 4)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 3), (1, 0), (3, 6), (4, 1), (4, 5)],
            )
            .set_target((1, 3), Target::Red(Symbol::Triangle))
            .set_target((3, 6), Target::Blue(Symbol::Hexagon))
            .set_target((4, 1), Target::Green(Symbol::Circle))
            .set_target((5, 5), Target::Yellow(Symbol::Square)),
        BoardQuadrant::default_quadrant(QuadColor::Red)
            .set_walls(
                WallDirection::Down,
                vec![(0, 5), (1, 1), (2, 4), (6, 1), (7, 4)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 1), (2, 4), (3, 0), (6, 2), (6, 5)],
            )
            .set_target((1, 1), Target::Red(Symbol::Triangle))
            .set_target((2, 4), Target::Blue(Symbol::Hexagon))
            .set_target((6, 2), Target::Green(Symbol::Circle))
            .set_target((7, 5), Target::Yellow(Symbol::Square)),
        BoardQuadrant::default_quadrant(QuadColor::Red)
            .set_walls(
                WallDirection::Down,
                vec![(0, 4), (1, 5), (2, 3), (5, 2), (7, 5)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 6), (2, 4), (3, 0), (5, 2), (6, 5)],
            )
            .set_target((1, 6), Target::Yellow(Symbol::Square))
            .set_target((2, 4), Target::Green(Symbol::Circle))
            .set_target((5, 2), Target::Blue(Symbol::Hexagon))
            .set_target((7, 5), Target::Red(Symbol::Triangle)),
        // Add blue boards
        BoardQuadrant::default_quadrant(QuadColor::Blue)
            .set_walls(
                WallDirection::Down,
                vec![(0, 3), (2, 3), (3, 1), (4, 5), (5, 3)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(2, 2), (2, 4), (4, 3), (4, 5), (5, 0)],
            )
            .set_target((2, 4), Target::Red(Symbol::Square))
            .set_target((3, 2), Target::Yellow(Symbol::Circle))
            .set_target((4, 5), Target::Green(Symbol::Hexagon))
            .set_target((5, 3), Target::Blue(Symbol::Triangle)),
        BoardQuadrant::default_quadrant(QuadColor::Blue)
            .set_walls(
                WallDirection::Down,
                vec![(0, 3), (1, 2), (2, 5), (5, 1), (6, 3)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 2), (2, 6), (3, 0), (5, 1), (5, 4)],
            )
            .set_target((1, 2), Target::Red(Symbol::Square))
            .set_target((2, 6), Target::Blue(Symbol::Triangle))
            .set_target((5, 1), Target::Green(Symbol::Hexagon))
            .set_target((6, 4), Target::Yellow(Symbol::Circle)),
        BoardQuadrant::default_quadrant(QuadColor::Blue)
            .set_walls(
                WallDirection::Down,
                vec![(0, 4), (1, 6), (2, 0), (4, 4), (6, 3)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(1, 1), (1, 6), (4, 0), (4, 5), (5, 3)],
            )
            .set_target((1, 6), Target::Green(Symbol::Hexagon))
            .set_target((2, 1), Target::Yellow(Symbol::Circle))
            .set_target((4, 5), Target::Red(Symbol::Square))
            .set_target((6, 3), Target::Blue(Symbol::Triangle)),
        // Add green boards
        BoardQuadrant::default_quadrant(QuadColor::Green)
            .set_walls(
                WallDirection::Down,
                vec![(0, 6), (1, 4), (3, 0), (4, 5), (6, 3)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 4), (1, 0), (2, 1), (4, 6), (6, 3)],
            )
            .set_target((1, 4), Target::Red(Symbol::Circle))
            .set_target((3, 1), Target::Green(Symbol::Triangle))
            .set_target((4, 6), Target::Blue(Symbol::Square))
            .set_target((6, 3), Target::Yellow(Symbol::Hexagon)),
        BoardQuadrant::default_quadrant(QuadColor::Green)
            .set_walls(
                WallDirection::Down,
                vec![(0, 5), (1, 1), (3, 6), (4, 0), (6, 3)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(1, 0), (1, 2), (2, 6), (3, 1), (6, 3)],
            )
            .set_target((1, 2), Target::Green(Symbol::Triangle))
            .set_target((3, 6), Target::Blue(Symbol::Square))
            .set_target((4, 1), Target::Red(Symbol::Circle))
            .set_target((6, 3), Target::Yellow(Symbol::Hexagon)),
        BoardQuadrant::default_quadrant(QuadColor::Green)
            .set_walls(
                WallDirection::Down,
                vec![(0, 5), (1, 1), (3, 6), (6, 1), (6, 4)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 2), (2, 6), (4, 0), (6, 1), (6, 5)],
            )
            .set_target((1, 2), Target::Green(Symbol::Triangle))
            .set_target((3, 6), Target::Red(Symbol::Circle))
            .set_target((6, 1), Target::Yellow(Symbol::Hexagon))
            .set_target((6, 5), Target::Blue(Symbol::Square)),
        // Add yellow boards
        BoardQuadrant::default_quadrant(QuadColor::Yellow)
            .set_walls(
                WallDirection::Down,
                vec![(0, 3), (1, 5), (3, 4), (5, 1), (6, 4), (7, 2)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(1, 6), (2, 0), (3, 4), (4, 1), (5, 5), (7, 2)],
            )
            .set_target((1, 6), Target::Yellow(Symbol::Triangle))
            .set_target((3, 4), Target::Red(Symbol::Hexagon))
            .set_target((5, 1), Target::Blue(Symbol::Circle))
            .set_target((6, 5), Target::Green(Symbol::Square))
            .set_target((7, 2), Target::Spiral),
        BoardQuadrant::default_quadrant(QuadColor::Yellow)
            .set_walls(
                WallDirection::Down,
                vec![(0, 4), (1, 3), (2, 1), (3, 7), (5, 5), (6, 3)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(0, 3), (2, 1), (3, 7), (4, 0), (5, 4), (5, 6)],
            )
            .set_target((1, 3), Target::Green(Symbol::Square))
            .set_target((3, 1), Target::Red(Symbol::Hexagon))
            .set_target((3, 7), Target::Spiral)
            .set_target((5, 6), Target::Blue(Symbol::Circle))
            .set_target((6, 4), Target::Yellow(Symbol::Triangle)),
        BoardQuadrant::default_quadrant(QuadColor::Yellow)
            .set_walls(
                WallDirection::Down,
                vec![(0, 6), (1, 2), (2, 5), (5, 3), (6, 1), (7, 5)],
            )
            .set_walls(
                WallDirection::Right,
                vec![(1, 3), (2, 5), (3, 0), (4, 4), (5, 1), (7, 5)],
            )
            .set_target((1, 3), Target::Yellow(Symbol::Triangle))
            .set_target((2, 5), Target::Red(Symbol::Hexagon))
            .set_target((5, 4), Target::Green(Symbol::Square))
            .set_target((6, 1), Target::Blue(Symbol::Circle))
            .set_target((7, 5), Target::Spiral),
    ]
}
