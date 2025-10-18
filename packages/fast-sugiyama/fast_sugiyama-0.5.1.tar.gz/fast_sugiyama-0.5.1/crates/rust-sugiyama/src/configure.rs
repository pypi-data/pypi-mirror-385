use std::env;

use log::error;
use petgraph::stable_graph::StableDiGraph;

// Default values for configuration
pub const MINIMUM_LENGTH_DEFAULT: u32 = 1;
pub const VERTEX_SPACING_DEFAULT: f64 = 10.0;
pub const DUMMY_VERTICES_DEFAULT: bool = true;
pub const RANKING_TYPE_DEFAULT: RankingType = RankingType::MinimizeEdgeLength;
pub const C_MINIMIZATION_DEFAULT: CrossingMinimization = CrossingMinimization::Barycenter;
pub const TRANSPOSE_DEFAULT: bool = true;
pub const DUMMY_SIZE_DEFAULT: f64 = 1.0;
pub const CHECK_LAYOUT_DEFAULT: bool = true;

const ENV_MINIMUM_LENGTH: &str = "RUST_GRAPH_MIN_LEN";
const ENV_VERTEX_SPACING: &str = "RUST_GRAPH_V_SPACING";
const ENV_DUMMY_VERTICES: &str = "RUST_GRAPH_DUMMIES";
const ENV_RANKING_TYPE: &str = "RUST_GRAPH_R_TYPE";
const ENV_CROSSING_MINIMIZATION: &str = "RUST_GRAPH_CROSS_MIN";
const ENV_TRANSPOSE: &str = "RUST_GRAPH_TRANSPOSE";
const ENV_DUMMY_SIZE: &str = "RUST_GRAPH_DUMMY_SIZE";
const ENV_CHECK_LAYOUT: &str = "RUST_GRAPH_CHECK_VALID";

pub(crate) const INIT_LOG_TARGET: &str = "rust-sugiyama.initialization";
pub(crate) const LAYOUT_LOG_TARGET: &str = "rust-sugiyama.layouting";
pub(crate) const COORD_CALC_LOG_TARGET: &str = "rust-sugiyama.coordinate_calculation";
pub(crate) const CROSSING_LOG_TARGET: &str = "rust-sugiyama.crossing_reduction";
pub(crate) const RANKING_LOG_TARGET: &str = "rust-sugiyama.ranking";
pub(crate) const LOW_LIM_LOG_TARGET: &str = "rust-sugiyama.low_lim";
pub(crate) const CUT_VAL_LOG_TARGET: &str = "rust-sugiyama.cut_values";
pub(crate) const CYCLE_LOG_TARGET: &str = "rust-sugiyama.cycle_removal";

pub trait IntoCoordinates {}

impl<V, E> IntoCoordinates for StableDiGraph<V, E> {}
impl IntoCoordinates for &[(u32, u32)] {}
impl IntoCoordinates for (&[u32], &[(u32, u32)]) {}

macro_rules! read_env {
    ($field:expr, $cb:tt, $env:ident) => {
        #[allow(unused_parens)]
        match env::var($env).map($cb) {
            Ok(Ok(v)) => $field = v,
            Ok(Err(e)) => {
                error!(target: INIT_LOG_TARGET, "{e}");
            }
            _ => (),
        }
    };
}

/// Used to configure parameters of the graph layout.
#[derive(Clone, Copy, Debug)]
pub struct Config {
    /// Length between layers.
    pub minimum_length: u32,
    /// The minimum spacing between vertices on the same layer and between
    /// layers.
    pub vertex_spacing: f64,
    /// Whether to include dummy vertices when calculating the layout.
    pub dummy_vertices: bool,
    /// How much space a dummy should take up, as a multiplier of the
    /// [`Self::vertex_spacing`].
    pub dummy_size: f64,
    /// Defines how vertices are placed vertically.
    pub ranking_type: RankingType,
    /// Which heuristic to use when minimizing edge crossings.
    pub c_minimization: CrossingMinimization,
    /// Whether to attempt to further reduce crossings by swapping vertices in a
    /// layer. This may increase runtime significantly.
    pub transpose: bool,
    /// Whether to check that the layout is valid i.e., no duplicated coordinates.
    pub check_layout: bool,
    /// Whether to encode/decode the edges in the `from_edges` function in case of
    /// sparse u32 values. StableGraphs are very expensive to create and operate on
    /// when the indices are not compact. This is not intended to be public, but
    /// its a performance switch for users who have pre-compacted their edge indices.
    pub encode_edges: bool,
}

impl Config {
    /// Read in configuration values from environment variables.
    ///
    /// Envs that can be set include:
    ///
    /// | ENV | values | default | description |
    /// | --- | ------ | ------- | ----------- |
    /// | RUST_GRAPH_MIN_LEN      | integer, > 0         | 1          | minimum edge length between layers |
    /// | RUST_GRAPH_V_SPACING    | integer, > 0         | 10         | minimum spacing between vertices on the same layer |
    /// | RUST_GRAPH_DUMMIES      | y \| n               | y          | if dummy vertices are included in the final layout |
    /// | RUST_GRAPH_R_TYPE       | original \| minimize \| up \| down | minimize   | defines how vertices are placed vertically |
    /// | RUST_GRAPH_CROSS_MIN    | barycenter \| median | barycenter | which heuristic to use for crossing reduction |
    /// | RUST_GRAPH_TRANSPOSE    | y \| n               | y          | if transpose function is used to further try to reduce crossings (may increase runtime significantly for large graphs) |
    /// | RUST_GRAPH_DUMMY_SIZE   | float, 1 >= v > 0    | 1.0        | size of dummy vertices in final layout, if dummy vertices are included. this will squish the graph horizontally |
    /// | RUST_GRAPH_CHECK_LAYOUT | y \| n               | y          | check if the layout is valid |
    pub fn new_from_env() -> Self {
        let mut config = Self::default();

        let parse_bool = |x: String| match x.as_str() {
            "y" => Ok(true),
            "n" => Ok(false),
            v => Err(format!("Invalid argument for dummy vertex env: {v}")),
        };

        read_env!(
            config.minimum_length,
            (|x| x.parse::<u32>()),
            ENV_MINIMUM_LENGTH
        );

        read_env!(
            config.c_minimization,
            (TryFrom::try_from),
            ENV_CROSSING_MINIMIZATION
        );

        read_env!(config.ranking_type, (TryFrom::try_from), ENV_RANKING_TYPE);

        read_env!(
            config.vertex_spacing,
            (|x| x.parse::<f64>()),
            ENV_VERTEX_SPACING
        );

        read_env!(config.dummy_vertices, parse_bool, ENV_DUMMY_VERTICES);

        read_env!(config.dummy_size, (|x| x.parse::<f64>()), ENV_DUMMY_SIZE);

        read_env!(config.transpose, parse_bool, ENV_TRANSPOSE);

        read_env!(config.check_layout, parse_bool, ENV_CHECK_LAYOUT);

        config
    }
}

impl Default for Config {
    fn default() -> Self {
        Self {
            minimum_length: MINIMUM_LENGTH_DEFAULT,
            vertex_spacing: VERTEX_SPACING_DEFAULT,
            dummy_vertices: DUMMY_VERTICES_DEFAULT,
            ranking_type: RANKING_TYPE_DEFAULT,
            c_minimization: C_MINIMIZATION_DEFAULT,
            transpose: TRANSPOSE_DEFAULT,
            dummy_size: DUMMY_SIZE_DEFAULT,
            check_layout: CHECK_LAYOUT_DEFAULT,
            encode_edges: true,
        }
    }
}

/// Defines the Ranking type, i.e. how vertices are placed on each layer.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RankingType {
    /// First moves vertices as far up as possible, and then as low as possible
    Original,
    /// Tries to minimize edge lengths across layers
    MinimizeEdgeLength,
    /// Move vertices as far up as possible
    Up,
    /// Move vertices as far down as possible
    Down,
}

impl TryFrom<String> for RankingType {
    type Error = String;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        match value.as_str() {
            "original" => Ok(Self::Original),
            "minimize" => Ok(Self::MinimizeEdgeLength),
            "up" => Ok(Self::Up),
            "down" => Ok(Self::Down),
            s => Err(format!("invalid value for ranking type: {s}")),
        }
    }
}

impl From<RankingType> for &'static str {
    fn from(value: RankingType) -> Self {
        match value {
            RankingType::Up => "up",
            RankingType::Down => "down",
            RankingType::Original => "original",
            RankingType::MinimizeEdgeLength => "minimize",
        }
    }
}

/// Defines the heuristic used for crossing minimization.
/// During crossing minimization, the vertices of one layer are
/// ordered, so they're as close to neighboring vertices as possible.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CrossingMinimization {
    /// Calculates the average of the positions of adjacent neighbors
    Barycenter,
    /// Calculates the weighted median of the positions of adjacent neighbors
    Median,
}

impl TryFrom<String> for CrossingMinimization {
    type Error = String;

    fn try_from(value: String) -> Result<Self, Self::Error> {
        match value.as_str() {
            "barycenter" => Ok(Self::Barycenter),
            "median" => Ok(Self::Median),
            s => Err(format!("invalid value for crossing minimization: {s}")),
        }
    }
}

impl From<CrossingMinimization> for &'static str {
    fn from(value: CrossingMinimization) -> Self {
        match value {
            CrossingMinimization::Median => "median",
            CrossingMinimization::Barycenter => "barycenter",
        }
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use std::env;
    use std::sync::Mutex;

    static ENV_MUTEX: Mutex<()> = Mutex::new(());

    #[test]
    fn from_env_all_valid() {
        let _guard = ENV_MUTEX.lock().unwrap(); // Acquire lock
        unsafe {
            env::set_var(ENV_MINIMUM_LENGTH, "5");
            env::set_var(ENV_DUMMY_VERTICES, "y");
            env::set_var(ENV_DUMMY_SIZE, "0.1");
            env::set_var(ENV_RANKING_TYPE, "up");
            env::set_var(ENV_CROSSING_MINIMIZATION, "median");
            env::set_var(ENV_TRANSPOSE, "n");
            env::set_var(ENV_VERTEX_SPACING, "20");
            env::set_var(ENV_CHECK_LAYOUT, "y");
        }
        let cfg = Config::new_from_env();
        assert_eq!(cfg.minimum_length, 5);
        assert!(cfg.dummy_vertices);
        assert_eq!(cfg.dummy_size, 0.1);
        assert_eq!(cfg.ranking_type, RankingType::Up);
        assert_eq!(cfg.c_minimization, CrossingMinimization::Median);
        assert!(!cfg.transpose);
        assert_eq!(cfg.vertex_spacing, 20.0);
        assert!(cfg.check_layout);
    }

    #[test]
    fn from_env_invalid_value() {
        let _guard = ENV_MUTEX.lock().unwrap(); // Acquire lock
        unsafe {
            env::set_var(ENV_CROSSING_MINIMIZATION, "flubbeldiflap");
            env::set_var(ENV_VERTEX_SPACING, "1bleh0");
        }
        let cfg = Config::new_from_env();
        let default = Config::default();
        assert_eq!(default.c_minimization, cfg.c_minimization);
        assert_eq!(default.vertex_spacing, cfg.vertex_spacing);
    }
}
