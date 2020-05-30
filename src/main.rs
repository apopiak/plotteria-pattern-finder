use std::collections::HashMap;

use itertools::Itertools;

type Solution = Vec<(i32, i32, i32)>;
type Graph = HashMap<(i32, i32, i32), Vec<(i32, i32, i32)>>;

const DIMENSION: u32 = 3;

fn generate_graph(depth: i32) -> Graph {
    let mut graph = HashMap::new();
    let edges = (0..depth)
        .cartesian_product(0..depth)
        .cartesian_product(0..depth);

    for (i, j, k) in edges.map(|((i, j), k)| (i, j, k)) {
        graph.insert(
            (i, j, k),
            (0..depth)
                .filter_map(|n| {
                    if !(i == j && j == k && n == i) {
                        Some((j, k, n))
                    } else {
                        None
                    }
                })
                .collect::<Vec<(i32, i32, i32)>>(),
        );
    }
    graph
}

#[derive(Debug)]
enum Validity {
    Yes,
    No,
    Maybe,
}

impl Validity {
    fn valid(&self) -> bool {
        match self {
            Validity::No => false,
            _ => true,
        }
    }
}

fn is_solution_valid(solution: &Solution, depth: i32) -> Validity {
    let triples = (1..depth).map(|x| (x, x, x));
    if solution.len() < 3 {
        return Validity::Maybe;
    }
    let mut indices: Vec<Option<usize>> = triples
        .map(|t| solution[2..].iter().position(|a| a == &t))
        .collect();
    let mut findings = vec![Some(0usize)];
    findings.append(&mut indices);
    let mut index = findings.len() - 1;
    for (i, maybe_val) in findings.iter().enumerate().rev() {
        if maybe_val.is_some() {
            index = i;
            break;
        }
    }
    let positions = &findings[0..index + 1];

    let chunk_size = (depth.pow(DIMENSION) / depth) as usize;
    let pattern: Vec<_> = (0..(depth as usize)).map(|x| x * chunk_size).collect();
    for (a, b) in positions.iter().zip(pattern.clone()) {
        if a != &Some(b) {
            return Validity::No;
        }
    }
    if pattern.len() > positions.len() {
        if solution.len() + DIMENSION as usize - 1 > pattern[positions.len()] + 4 {
            Validity::No
        } else {
            Validity::Maybe
        }
    } else {
        Validity::Yes
    }
}

use lazy_static::lazy_static;
use std::sync::Mutex;

lazy_static! {
    static ref SOLUTION_COUNT: Mutex<Box<usize>> = Mutex::new(Box::new(0));
}

fn find_hamilton_bf<F>(visited: &Solution, graph: &Graph, is_valid: &F) -> Vec<Solution>
where
    F: Fn(&Solution) -> Validity,
{
    let mut solutions = vec![];
    if visited.len() >= graph.values().count() {
        if is_valid(visited).valid() {
            let _ = SOLUTION_COUNT.lock().map(|mut s| {
                **s += 1;
                // println!("solution count: {}\r", s);
                if **s > 20_000 {
                    std::process::exit(0);
                }
            });
            return vec![visited.to_vec()];
        }
    } else if !is_valid(visited).valid() {
        return vec![];
    }
    let current = visited[visited.len() - 1];
    for next in &graph[&current] {
        if !visited.contains(next) {
            let mut visit = visited.clone();
            visit.push(*next);
            solutions.append(&mut find_hamilton_bf(&visit, graph, is_valid));
        }
    }
    solutions
}

fn main() {
    let depth = 4;
    let graph = generate_graph(depth);
    let visited = vec![(0, 0, 0)];
    let solutions = find_hamilton_bf(&visited, &graph, &|x| is_solution_valid(x, depth));
    println!("solutions: {:?}", solutions.len());
}
