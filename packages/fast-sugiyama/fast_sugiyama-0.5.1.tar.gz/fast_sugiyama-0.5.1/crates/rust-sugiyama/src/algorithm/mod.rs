//! The implementation roughly follows sugiyamas algorithm for creating
//! a layered graph layout.
//!
//! Usually Sugiyamas algorithm consists of 4 Phases:
//! 1. Remove Cycles
//! 2. Assign each vertex to a rank/layer
//! 3. Reorder vertices in each rank to reduce crossings
//! 4. Calculate the final coordinates.
//!
//! Currently, phase 2 to 4 are implemented, Cycle removal might be added at
//! a later time.
//!
//! The whole algorithm roughly follows the 1993 paper "A technique for drawing
//! directed graphs" by Gansner et al. It can be found
//! [here](https://ieeexplore.ieee.org/document/221135).
//!
//! See the submodules for each phase for more details on the implementation
//! and references used.
use std::collections::{BTreeMap, HashMap, HashSet};

use log::{debug, info};
use petgraph::stable_graph::{EdgeIndex, NodeIndex, StableDiGraph};
use petgraph::visit::{EdgeRef, IntoEdgeReferences};

use crate::configure::{
    COORD_CALC_LOG_TARGET, CYCLE_LOG_TARGET, Config, CrossingMinimization, INIT_LOG_TARGET,
    LAYOUT_LOG_TARGET, RankingType,
};
use crate::{Layout, Layouts, util::weakly_connected_components};
use p0_cycle_removal as p0;
use p1_layering as p1;
use p2_reduce_crossings as p2;
use p3_calculate_coordinates as p3;

use p3::VDir;

mod p0_cycle_removal;
mod p1_layering;
mod p2_reduce_crossings;
mod p3_calculate_coordinates;

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Vertex {
    pub id: usize,
    size: (f64, f64),
    rank: i32,
    pos: usize,
    low: u32,
    lim: u32,
    parent: Option<NodeIndex>,
    is_tree_vertex: bool,
    pub is_dummy: bool,
    root: NodeIndex,
    align: NodeIndex,
    shift: f64,
    sink: NodeIndex,
    block_max_vertex_width: f64,
}

impl Vertex {
    pub fn new(id: usize, size: (f64, f64)) -> Self {
        Self {
            id,
            size,
            ..Default::default()
        }
    }
}

impl Default for Vertex {
    fn default() -> Self {
        Self {
            id: 0,
            size: (0.0, 0.0),
            rank: 0,
            pos: 0,
            low: 0,
            lim: 0,
            parent: None,
            is_tree_vertex: false,
            is_dummy: false,
            root: 0.into(),
            align: 0.into(),
            shift: f64::INFINITY,
            sink: 0.into(),
            block_max_vertex_width: 0.0,
        }
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Edge {
    weight: i32,
    cut_value: Option<i32>,
    is_tree_edge: bool,
    has_type_1_conflict: bool,
    reversed: bool,
}

impl Default for Edge {
    fn default() -> Self {
        Self {
            weight: 1,
            cut_value: None,
            is_tree_edge: false,
            has_type_1_conflict: false,
            reversed: false,
        }
    }
}

pub(super) fn start(graph: &StableDiGraph<Vertex, Edge>, config: &Config) -> Layouts<usize> {
    let dummy_id_offset = graph
        .node_indices()
        .fold(0usize, |max, n| max.max(n.index()));

    weakly_connected_components(graph)
        .into_iter()
        .map(|mut g| {
            init_graph(&mut g);
            let (positions, w, h, edges) = build_layout(&mut g, config, dummy_id_offset);
            if config.check_layout {
                assert!(layout_is_valid(&positions))
            }

            (positions, w, h, edges)
        })
        .collect()
}

fn init_graph(graph: &mut StableDiGraph<Vertex, Edge>) {
    info!(
        target: INIT_LOG_TARGET,
        "Initializing graphs vertex weights"
    );
    for id in graph.node_indices().collect::<Vec<_>>() {
        graph[id].id = id.index();
        graph[id].root = id;
        graph[id].align = id;
        graph[id].sink = id;
    }
}

fn build_layout(
    graph: &mut StableDiGraph<Vertex, Edge>,
    config: &Config,
    dummy_id_offset: usize,
) -> Layout<usize> {
    info!(target: LAYOUT_LOG_TARGET, "Start building layout");
    info!(target: LAYOUT_LOG_TARGET, "Configuration is: {:?}", config);

    // Treat the vertex spacing as just additional padding in each node. Each node will then take
    // 50% of the "responsibility" of the vertex spacing. This does however mean that dummy vertices
    // will have a gap of 50% of the vertex spacing between them and the next and previous vertex.
    for vertex in graph.node_weights_mut() {
        vertex.size.0 += config.vertex_spacing;
        vertex.size.1 += config.vertex_spacing;
    }

    // we store the edges that where reversed in the graph itself for later correction.
    let _ = execute_phase_0(graph);

    execute_phase_1(graph, config.minimum_length as i32, config.ranking_type);

    let layers = execute_phase_2(
        graph,
        config.minimum_length as i32,
        (config.dummy_vertices || config.dummy_size > 0.0).then_some(config.dummy_size),
        config.c_minimization,
        config.transpose,
        dummy_id_offset,
    );

    let layout = execute_phase_3(graph, layers, config.dummy_vertices);
    debug!(target: LAYOUT_LOG_TARGET, "Coordinates: {:?}\nwidth: {}, height:{}",
        layout.0,
        layout.1,
        layout.2
    );
    layout
}

fn execute_phase_0(graph: &mut StableDiGraph<Vertex, Edge>) -> Vec<EdgeIndex> {
    info!(target: LAYOUT_LOG_TARGET, "Executing phase 0: Cycle Removal");
    p0::remove_cycles(graph)
}

/// Assign each vertex a rank
fn execute_phase_1(
    graph: &mut StableDiGraph<Vertex, Edge>,
    minimum_length: i32,
    ranking_type: RankingType,
) {
    info!(target: LAYOUT_LOG_TARGET, "Executing phase 1: Ranking");
    p1::rank(graph, minimum_length, ranking_type);
}

/// Reorder vertices in ranks to reduce crossings. If `dummy_size` is [Some],
/// dummies will be passed along to the next phase.
fn execute_phase_2(
    graph: &mut StableDiGraph<Vertex, Edge>,
    minimum_length: i32,
    dummy_size: Option<f64>,
    crossing_minimization: CrossingMinimization,
    transpose: bool,
    dummy_id_offset: usize,
) -> Vec<Vec<NodeIndex>> {
    info!(target: LAYOUT_LOG_TARGET, "Executing phase 2: Crossing Reduction");

    p2::insert_dummy_vertices(
        graph,
        minimum_length,
        dummy_size.unwrap_or(0.0),
        dummy_id_offset,
    );
    let mut order = p2::ordering(graph, crossing_minimization, transpose);
    if dummy_size.is_none() {
        p2::remove_dummy_vertices(graph, &mut order);
    }
    order
}

/// calculate the final coordinates for each vertex, after the graph was layered and crossings where minimized.
fn execute_phase_3(
    graph: &mut StableDiGraph<Vertex, Edge>,
    mut layers: Vec<Vec<NodeIndex>>,
    dummy_vertices: bool,
) -> Layout<usize> {
    info!(target: LAYOUT_LOG_TARGET, "Executing phase 3: Coordinate Calculation");

    let mut layouts = p3::create_layouts(graph, &mut layers);
    reset_edge_directions(graph);

    p3::align_to_smallest_width_layout(&mut layouts);

    debug!(target: LAYOUT_LOG_TARGET, "Debug 4 layouts: {:?}", layouts
        .iter()
        .map(|layout| {
            layout
                .iter()
                .filter(|(v, _)| !graph[**v].is_dummy)
                .map(|(v, x)| (graph[*v].id, (*x, graph[*v].rank as f64)))
                .collect::<Vec<_>>()
        })
        .collect::<Vec<_>>());

    let mut x_coordinates = p3::calculate_relative_coords(layouts);
    // determine the smallest x-coordinate
    let (xmin, xmax) = x_coordinates
        .iter()
        .fold((f64::INFINITY, f64::NEG_INFINITY), |(min, max), (_, x)| {
            (min.min(*x), max.max(*x))
        });
    let width = (xmax - xmin).max(1.0);

    // shift all coordinates so the minimum coordinate is 0
    for (_, c) in &mut x_coordinates {
        *c -= xmin;
    }

    // Find max y size in each rank. Use a BTreeMap so iteration through the map
    // is ordered.
    let mut rank_to_max_height = BTreeMap::<i32, f64>::new();
    for vertex in graph.node_weights() {
        let max = rank_to_max_height.entry(vertex.rank).or_default();
        *max = max.max(vertex.size.1);
    }

    // Stack up each rank to assign it an offset. The gap between each rank and the next is half the
    // height of the current rank, plus half the height of the next rank.
    let mut rank_to_y_offset = HashMap::new();
    let mut current_rank_top_offset = *rank_to_max_height.iter().next().unwrap().1 * -0.5;
    for (rank, max_height) in rank_to_max_height {
        // The center of the rank is the middle of the max height plus the top of the rank.
        rank_to_y_offset.insert(rank, current_rank_top_offset + max_height * 0.5);
        // Shift by the height of the rank. The height of a rank already includes the vertex
        // spacing.
        current_rank_top_offset += max_height;
    }

    // since vertices all share ranks, this is faster than taking the max y coordinate.
    let height = rank_to_y_offset
        .values()
        .fold(f64::NEG_INFINITY, |acc, y| acc.max(*y))
        .max(1.0);

    // format to (usize, (x, y)), width, height, Some(edge_list) || None
    (
        x_coordinates
            .into_iter()
            .filter(|(v, _)| dummy_vertices || !graph[*v].is_dummy)
            // calculate y coordinate
            .map(|(v, x)| {
                (
                    graph[v].id,
                    (
                        x,
                        // flip y by default to match `dot` program convention with
                        // directions trending downward
                        *rank_to_y_offset.get(&graph[v].rank).unwrap() * -1.0 + height,
                    ),
                )
            })
            .collect::<Vec<_>>(),
        width,
        height,
        dummy_vertices.then_some(edge_list(graph)),
    )
}

fn edge_list(graph: &StableDiGraph<Vertex, Edge>) -> Vec<(usize, usize)> {
    graph
        .edge_references()
        .map(|e| (graph[e.source()].id, graph[e.target()].id))
        .collect::<Vec<_>>()
}

fn reset_edge_directions(graph: &mut StableDiGraph<Vertex, Edge>) {
    for edge in graph.edge_indices().collect::<Vec<_>>() {
        let mut w = graph[edge];
        if w.reversed
            && let Some((tail, head)) = graph.edge_endpoints(edge)
        {
            // add new edge in correct direction
            w.reversed = false;
            let _ = graph.add_edge(head, tail, w);
            // remove the reversed edge
            graph.remove_edge(edge);
        }
    }
}

fn slack(graph: &StableDiGraph<Vertex, Edge>, edge: EdgeIndex, minimum_length: i32) -> i32 {
    let (tail, head) = graph.edge_endpoints(edge).unwrap();
    graph[head].rank - graph[tail].rank - minimum_length
}

fn has_duplicates<T: Eq + std::hash::Hash>(vec: &[T]) -> bool {
    let mut seen = HashSet::new();
    for item in vec {
        let is_new = seen.insert(item);
        if !is_new {
            return true; // Found a duplicate
        }
    }
    false // No duplicates found
}

fn layout_is_valid(layout: &[(usize, (f64, f64))]) -> bool {
    let rank_scale = 2_i64.pow(31) as f64; // make space to pack x & y into an i64
    let xs = layout
        .iter()
        .map(|(_s, (x, y))| (y * rank_scale + x * 100.0).round() as i64)
        .collect::<Vec<_>>();

    !has_duplicates(&xs)
}

#[allow(dead_code)]
fn print_to_console(
    dir: VDir,
    graph: &StableDiGraph<Vertex, Edge>,
    layers: &[Vec<NodeIndex>],
    mut coordinates: HashMap<NodeIndex, isize>,
    vertex_spacing: usize,
) {
    let min = *coordinates.values().min().unwrap();
    let str_width = 4;
    coordinates
        .values_mut()
        .for_each(|v| *v = str_width * (*v - min) / vertex_spacing as isize);
    let width = *coordinates.values().max().unwrap() as usize;

    for line in layers {
        let mut v_line = vec!['-'; width + str_width as usize];
        let mut a_line = vec![' '; width + str_width as usize];
        for v in line {
            let pos = *coordinates.get(v).unwrap() as usize;
            if graph[*v].root != *v {
                a_line[pos] = if dir == VDir::Up { 'v' } else { '^' };
            }
            for (i, c) in v.index().to_string().chars().enumerate() {
                v_line[pos + i] = c;
            }
        }
        match dir {
            VDir::Up => {
                println!("{}", v_line.into_iter().collect::<String>());
                println!("{}", a_line.into_iter().collect::<String>());
            }
            VDir::Down => {
                println!("{}", a_line.into_iter().collect::<String>());
                println!("{}", v_line.into_iter().collect::<String>());
            }
        }
    }
    println!();
}

#[test]
fn is_valid_layout() {
    // this graph failed to create a valid layout
    // in versions <= 0.3
    let edges = [
        (2, 1),
        (3, 1),
        (7, 4),
        (8, 7),
        (9, 2),
        (10, 1),
        (4, 2),
        (6, 1),
        (11, 4),
        (5, 4),
        (12, 1),
    ];

    let graph = StableDiGraph::from_edges(edges);

    let layouts = start(&graph, &Config::default());

    for (positions, _, _, _) in layouts {
        assert!(layout_is_valid(&positions));
    }
}
