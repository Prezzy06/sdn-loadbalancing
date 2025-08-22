from __future__ import annotations

from typing import Dict, Iterable, Tuple
import networkx as nx


class TopologyManager:
    """Maintains a NetworkX graph of the fabric and provides update hooks."""

    def __init__(self) -> None:
        self.graph = nx.Graph()

    def add_switch(self, dpid: str) -> None:
        self.graph.add_node(dpid, type="switch")

    def add_host(self, host_id: str, attached_switch: str) -> None:
        self.graph.add_node(host_id, type="host")
        self.graph.add_edge(host_id, attached_switch)

    def add_link(self, a: str, b: str, capacity_bps: int = 1_000_000_000) -> None:
        self.graph.add_edge(a, b, capacity_bps=capacity_bps)

    def remove_node(self, node_id: str) -> None:
        if node_id in self.graph:
            self.graph.remove_node(node_id)

    def remove_link(self, a: str, b: str) -> None:
        if self.graph.has_edge(a, b):
            self.graph.remove_edge(a, b)

    def get_graph(self) -> nx.Graph:
        return self.graph