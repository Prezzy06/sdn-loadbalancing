from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import random
import networkx as nx


Node = str
EdgePath = List[Node]


@dataclass
class PathSelection:
    path: EdgePath
    weight: float


class PathFinder:
    """Compute shortest paths (by hop count) and perform weighted selection among ECMP paths.

    The graph is expected to be an undirected simple graph representing the L2/L3 fabric.
    We assume each edge has unit weight for hop-count minimization. For fat-tree, this aligns with
    latency minimization in a homogeneous fabric.
    """

    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph

    def all_shortest_paths(self, src: Node, dst: Node) -> List[EdgePath]:
        if src not in self.graph or dst not in self.graph:
            raise ValueError("Source or destination not in graph")
        if src == dst:
            return [[src]]
        # Hop-count shortest paths
        paths = list(nx.all_shortest_paths(self.graph, source=src, target=dst, weight=None))
        return [list(p) for p in paths]

    def shortest_path_length(self, src: Node, dst: Node) -> int:
        return int(nx.shortest_path_length(self.graph, source=src, target=dst, weight=None))

    def select_path_weighted(
        self,
        src: Node,
        dst: Node,
        path_weights: Optional[Dict[Tuple[Node, ...], float]] = None,
        rng: Optional[random.Random] = None,
    ) -> PathSelection:
        """Select a path among equal-cost shortest paths using weights.

        - path_weights: mapping from path (as tuple of nodes) to weight representing desirability.
          Higher weight => higher selection probability. If None, uniform among ECMP.
        - rng: optional Random for deterministic testing.
        """
        if rng is None:
            rng = random

        paths = self.all_shortest_paths(src, dst)
        if not paths:
            raise RuntimeError("No path found")

        if path_weights is None:
            # Uniform ECMP
            choice = rng.choice(paths)
            return PathSelection(path=choice, weight=1.0)

        # Filter weights to only those ECMP candidates
        weights: List[float] = []
        normalized_paths: List[EdgePath] = []
        for p in paths:
            t = tuple(p)
            w = path_weights.get(t, 0.0)
            weights.append(max(0.0, float(w)))
            normalized_paths.append(p)

        total = sum(weights)
        if total <= 0.0:
            # Fallback to uniform if all zero
            choice = rng.choice(normalized_paths)
            return PathSelection(path=choice, weight=0.0)

        # Weighted random choice
        r = rng.random() * total
        acc = 0.0
        for p, w in zip(normalized_paths, weights):
            acc += w
            if r <= acc:
                return PathSelection(path=p, weight=w)
        # Numerical edge case fallback
        return PathSelection(path=normalized_paths[-1], weight=weights[-1])

    @staticmethod
    def invert_loads_to_weights(
        paths: Iterable[EdgePath],
        edge_load_func: callable,
        epsilon: float = 1e-6,
    ) -> Dict[Tuple[Node, ...], float]:
        """Compute path weights inversely proportional to average edge load.

        - edge_load_func(u, v) -> utilization in [0, 1]
        - weight for path p is 1 / (epsilon + avg_load(p)) so less loaded gets higher weight
        """
        weights: Dict[Tuple[Node, ...], float] = {}
        for p in paths:
            if len(p) <= 1:
                avg = 0.0
            else:
                loads: List[float] = []
                for u, v in zip(p[:-1], p[1:]):
                    # Graph may be undirected; ensure canonical order
                    if edge_load_func(u, v) is not None:
                        loads.append(float(edge_load_func(u, v)))
                avg = sum(loads) / len(loads) if loads else 0.0
            weights[tuple(p)] = 1.0 / (epsilon + max(0.0, avg))
        return weights