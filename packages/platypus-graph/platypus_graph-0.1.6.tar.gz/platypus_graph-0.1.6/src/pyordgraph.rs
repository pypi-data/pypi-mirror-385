use fxhash::{FxHashSet, FxHashMap};

use graphbench::algorithms::LinearGraphAlgorithms;
use pyo3::prelude::*;

use std::collections::HashSet;

use graphbench::ordgraph::*;
use graphbench::graph::*;
use graphbench::graph::IntegerColouring;
use graphbench::iterators::*;

use crate::ducktype::*;
use crate::vmap::PyVMap;
use crate::pygraph::PyEditGraph;


/// A data structure representing a graph with a linear ordering on its vertex set.
///
///
#[pyclass(name="OrdGraph",module="platypus")]
pub struct PyOrdGraph {
    pub(crate) G: OrdGraph
}

#[pymethods]
impl PyOrdGraph {

    /// Returns the number of vertices in the graph.
    #[pyo3(text_signature="($self,/)")]
    pub fn num_vertices(&self) -> PyResult<usize> {
        Ok(self.G.num_vertices())
    }

    /// Constructs an ordered graph from `graph` by computing a degeneracy
    /// ordering.
    #[staticmethod]
    #[pyo3(text_signature="(graph,/)")]
    pub fn by_degeneracy(graph: &PyEditGraph ) -> PyResult<PyOrdGraph> {
        Ok(PyOrdGraph{G: OrdGraph::by_degeneracy(&graph.G)})
    }

    /// Constructs an ordered graph from `graph` using `order`.
    #[staticmethod]
    #[pyo3(text_signature="(graph, order,/)")]
    pub fn with_ordering(graph: &PyEditGraph, obj:&Bound<'_,PyAny>) -> PyResult<PyOrdGraph> {
        let order = to_vertex_list(obj)?;
        Ok(PyOrdGraph{G: OrdGraph::with_ordering(&graph.G, order.iter())})
    }

    /// Returns the ordering of this graph.
    #[pyo3(text_signature="($self,/)")]
    pub fn order(&self) -> PyResult<Vec<Vertex>> {
        Ok(self.G.vertices().cloned().collect())
    }

    fn __len__(&self) -> PyResult<usize> {
        Ok(self.G.num_vertices())
    }

    fn __str__(&self) -> PyResult<String> {
        self.__repr__()
    }

    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("OrdGraph (n={},m={})]", self.G.num_vertices(), self.G.num_edges() ))
    }

    /// Returns the number of edges in the graph.
    #[pyo3(text_signature="($self,/)")]
    pub fn num_edges(&self) -> PyResult<usize> {
        Ok(self.G.num_edges())
    }

    /// Returns whether vertices `u` and `v` are connected by an edge.
    #[pyo3(text_signature="($self,u,v,/)")]
    pub fn adjacent(&self, u:Vertex, v:Vertex) -> PyResult<bool> {
        Ok(self.G.adjacent(&u, &v))
    }

    /// Returns the number of edges incident to `u` in the graph.
    #[pyo3(text_signature="($self,u,/)")]
    pub fn degree(&self, u:Vertex) -> PyResult<u32> {
        Ok(self.G.degree(&u))
    }

    /// Returns the number of neighbours of `u` that
    /// appear before `u` in the ordering.
    #[pyo3(text_signature="($self,u,/)")]
    pub fn left_degree(&self, u:Vertex) -> PyResult<u32> {
        Ok(self.G.left_degree(&u))
    }


    /// Returns the number of neighbours of `u` that
    /// appear after `u` in the ordering.
    #[pyo3(text_signature="($self,u,/)")]
    pub fn right_degree(&self, u:Vertex) -> PyResult<u32> {
        Ok(self.G.right_degree(&u))
    }


    /// Returns the degrees of all vertices in the graph as a [`VMap`].
    #[pyo3(text_signature="($self,/)")]
    pub fn degrees(&self) -> PyResult<PyVMap> {
        Ok(PyVMap::new_int(self.G.degrees()))
    }


    /// Returns the left-degrees of all vertices in the graph as a [`VMap`].
    #[pyo3(text_signature="($self,/)")]
    pub fn left_degrees(&self) -> PyResult<PyVMap> {
        Ok(PyVMap::new_int(self.G.left_degrees()))
    }


    /// Returns the right-degrees of all vertices in the graph as a [`VMap`].
    #[pyo3(text_signature="($self,/)")]
    pub fn right_degrees(&self) -> PyResult<PyVMap> {
        Ok(PyVMap::new_int(self.G.right_degrees()))
    }

    /// Returns whether the vertex `u` is contained in the graph.
    #[pyo3(text_signature="($self,u,/)")]
    pub fn contains(&mut self, u:Vertex) -> PyResult<bool> {
        Ok(self.G.contains(&u))
    }

    /// Returns the vertices of this graph as a set.
    #[pyo3(text_signature="($self,/)")]
    pub fn vertices(&self) -> PyResult<VertexSet> {
        Ok(self.G.vertices().cloned().collect())
    }

    /// Returns the edges of this graph as a list.
    #[pyo3(text_signature="($self,/)")]
    pub fn edges(&self) -> PyResult<Vec<Edge>> {
        Ok(self.G.edges().collect())
    }


    /// Returns the neigbhours of the vertex `u`.
    #[pyo3(text_signature="($self, u,/)")]
    pub fn neighbours(&self, u:Vertex) -> PyResult<VertexSet> {
        Ok(self.G.neighbours(&u).cloned().collect())
    }

    /// Returns the neighbours of `u` that
    /// appear before `u` in the ordering.
    #[pyo3(text_signature="($self,u,/)")]
    pub fn left_neighbours(&self, u:Vertex) -> PyResult<Vec<Vertex>> {
        Ok(self.G.left_neighbours(&u))
    }

    /// Returns the joint neighbourhood of a collection `vertices`,
    /// that is, all vertices that have a neighbour in `vertices`
    /// but are not themselves contained in it.
    #[pyo3(text_signature="($self, vertices,/)")]
    pub fn neighbourhood(&self, vertices:&Bound<'_,PyAny>) -> PyResult<VertexSet> {
        let vertices = to_vertex_list(vertices)?;
        Ok(self.G.neighbourhood(vertices.iter()))
    }

    /// Returns the joint closed neighbourhood of a collection `vertices`,
    /// that is, all vertices that have at least one neighbour `vertices`
    /// or are themselves contained in it.
    #[pyo3(text_signature="($self, vertices,/)")]
    pub fn closed_neighbourhood(&self, vertices:&Bound<'_,PyAny>) -> PyResult<VertexSet> {
        let vertices = to_vertex_list(vertices)?;
        Ok(self.G.closed_neighbourhood(vertices.iter()))
    }

    /// Returns all vertices that have distance at most `r` to `u`.
    #[pyo3(text_signature="($self, u, r,/)")]
    pub fn r_neighbours(&self, u:Vertex, r:usize) -> PyResult<VertexSet> {
        Ok(self.G.r_neighbours(&u, r))
    }


    /// Returns all vertices that have distance at most `r` to some vertex
    /// in the provided collection.
    #[pyo3(text_signature="($self, vertices, r,/)")]
    pub fn r_neighbourhood(&self, vertices:&Bound<'_,PyAny>, r:usize) -> PyResult<VertexSet> {
        let vertices = to_vertex_list(vertices)?;
        Ok(self.G.r_neighbourhood(vertices.iter(), r))
    }

    //
    //  Ordgraph specific methods
    //

    /// Swaps the positions of `u` and `v` in the ordering.
    #[pyo3(text_signature="($self, u, v,/)")]
    pub fn swap(&mut self, u:Vertex, v:Vertex) -> PyResult<()> {
        self.G.swap(&u,&v);
        Ok(())
    }

    /// Computes all strongly $r$-reachable vertices to $u$.
    ///
    /// A vertex $v$ is strongly $r$-reachable from $u$ if there exists a $u$-$v$-path in the graph
    /// of length at most $r$ where $v$ is the only vertex of the path that comes before $u$ in the
    /// ordering.
    ///
    /// Returns a `VMap` with all vertices that are strongly $r$-reachable
    /// from $u$. For each member $v$ in the map the corresponding values represents
    /// the distance $d \\leq r$ at which $v$ is strongly reachable from $u$.
    #[pyo3(text_signature="($self, u, r,/)")]
    pub fn sreach_set(&self, u:Vertex, r:u32) -> PyResult<PyVMap> {
        let sreach = self.G.sreach_set(&u, r);
        Ok(PyVMap::new_int(sreach))
    }

    /// Computes all weakly $r$-reachable sets as a map..
    ///
    /// A vertex $v$ is weakly $r$-rechable from $u$ if there exists a $u$-$v$-path in the graph
    /// of length at most $r$ whose leftmost vertex is $v$. In particular, $v$ must be left of
    /// $u$ in the ordering.
    ///
    /// Returns a `VMap` for each vertex. For a vertex $u$ the corresponding `VMap`
    /// contains all vertices that are weakly $r$-reachable from $u$. For each member $v$
    /// in this `VMap` the corresponding values represents the distance $d \\leq r$ at
    /// which $v$ is weakly reachable from $u$.
    ///
    /// If the sizes of the weakly $r$-reachable sets are bounded by a constant the computation
    /// takes $O(|G|)$ time.
    #[pyo3(text_signature="($self, r,/)")]
    pub fn wreach_sets(&self, r:u32) -> PyResult<VertexMap<PyVMap>> {
        let wreach_map = self.G.wreach_sets(r);
        let res = wreach_map.into_iter().map(|(u,wreach)| (u, PyVMap::new_int(wreach)) ).collect();
        Ok(res)
    }

    /// Returns for each vertex the size of its weakly $r$-reachable set.
    #[pyo3(text_signature="($self, r,/)")]
    pub fn wreach_sizes(&self, r:u32) -> PyResult<PyVMap> {
        Ok(PyVMap::new_int(self.G.wreach_sizes(r)))
    }

    /// Computes all strongly $r$-reachable sets as a map.
    ///
    /// A vertex $v$ is strongly $r$-rechable from $u$ if there exists a $u$-$v$-path in the graph
    /// of length at most $r$ whose inner vertices come all after $u$. In particular, $v$ must be left of
    /// $u$ in the ordering.
    ///
    /// Returns a `VMap` for each vertex. For a vertex $u$ the corresponding `VMap`
    /// contains all vertices that are strongly $r$-reachable from $u$. For each member $v$
    /// in this `VMap` the corresponding values represents the distance $d \\leq r$ at
    /// which $v$ is strongly reachable from $u$.
    ///
    /// If the sizes of the strongly $r$-reachable sets are bounded by a constant the computation
    /// takes $O(|G|)$ time.
    #[pyo3(text_signature="($self, r,/)")]
    pub fn sreach_sets(&self, r:u32) -> PyResult<VertexMap<PyVMap>> {
        let sreach_map = self.G.sreach_sets(r);
        let res = sreach_map.into_iter().map(|(u,sreach)| (u, PyVMap::new_int(sreach)) ).collect();
        Ok(res)
    }

    /// Returns for each vertex the size of its strongly $r$-reachable set.
    #[pyo3(text_signature="($self, r,/)")]
    pub fn sreach_sizes(&self, r:u32) -> PyResult<PyVMap> {
        Ok(PyVMap::new_int(self.G.sreach_sizes(r)))
    }

    /// Computes an approximate $r$-dominating set of the underlying graph,
    /// where $r$ is the provided `radius`. An $r$-dominating set of a graph $G$ is a set of
    /// vertices $D \subseteq V(G)$ such that every vertex of $G$ has at least one vertex in $D$
    /// with distance $\leq r$. In other words, the closed $r$-neighbourhood $N^r[D]$ cover the
    /// whole graph.
    ///
    /// The approximation ratio is a function of the weak-colouring number of this ordered graph.
    /// See \[Dvořák13\] for the algorithm.
    ///
    /// > \[Dvořák13\]
    /// Dvořák, Z. (2013). Constant-factor approximation of the domination number in sparse graphs. *European Journal of Combinatorics*, 34(5), 833-840.
    pub fn domset(&self, r:u32) -> PyResult<VertexSet> {
        let (domset, _dist, _) =  self.G.domset(r, false);
        Ok(domset)
    }


    /// Computes an approximate $r$-dominating set for the provided target set `target`.
    /// An $r$-dominating set for a vertex set $T$ in a graph $G$ is a vertex set $D \subseteq V(G)$ such
    /// that every vertex in $T$ has at least one vertex in $D$ with distance $\leq r$. In other words, the
    /// closed $r$-neighbourhood $N^r[D]$ covers the set $T$.
    pub fn domset_for(&self, r:u32, target:&Bound<'_,PyAny>) -> PyResult<VertexSet> {
        let target = to_vertex_list(target)?;
        let (domset, _dist, _) =  self.G.domset_with_target(r, false, target);
        Ok(domset)
    }

    /// Computes a vertex colouring of the vertices in `target` such that every pair of
    /// vertices with the same colour has distance at least `d` to each other.
    /// The number of colour classes depends on the weak-colouring number of this ordered graph.
    fn scattered_colouring(&self, d:u32, target:&Bound<'_,PyAny>) -> PyResult<PyVMap> {
        let target = to_vertex_list(target)?;
        let colouring =  self.G.scattered_colouring(d, target);
        let colouring_map:VertexColouring<u32> = VertexColouring::from_sets(colouring);

        Ok(PyVMap::new_int(colouring_map.as_map()))
    }
}

// impl AttemptCast for PyOrdGraph {
//     fn try_cast<F, R>(obj: &Bound<'_,PyAny>, f: F) -> Option<R>
//     where F: FnOnce(&Self) -> R,
//     {
//         if let Ok(py_cell) = obj.downcast::<PyCell<Self>>() {
//             let map:&Self = &*(py_cell.borrow());
//             Some(f(map))
//         } else {
//             None
//         }
//     }
// }
