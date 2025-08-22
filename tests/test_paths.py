import networkx as nx
from utils.path_finder import PathFinder


def line_graph(n):
    g = nx.Graph()
    for i in range(n):
        g.add_node(str(i))
    for i in range(n - 1):
        g.add_edge(str(i), str(i + 1))
    return g


def test_all_shortest_paths_square():
    # 0 - 1
    # |   |
    # 3 - 2
    g = nx.Graph()
    g.add_edges_from([("0", "1"), ("1", "2"), ("2", "3"), ("3", "0")])
    pf = PathFinder(g)
    paths = pf.all_shortest_paths("0", "2")
    assert sorted(paths) == sorted([["0", "1", "2"], ["0", "3", "2"]])


def test_weighted_selection_prefers_less_loaded():
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "D"), ("A", "C"), ("C", "D")])
    pf = PathFinder(g)
    paths = pf.all_shortest_paths("A", "D")

    def edge_load(u, v):
        # Path A-B-D has higher load (0.9), A-C-D low (0.1)
        if {u, v} == {"A", "B"} or {u, v} == {"B", "D"}:
            return 0.9
        if {u, v} == {"A", "C"} or {u, v} == {"C", "D"}:
            return 0.1
        return 0.0

    weights = pf.invert_loads_to_weights(paths, edge_load)
    # Heavily skewed toward A-C-D
    w_abd = weights[tuple(["A", "B", "D"])]; w_acd = weights[tuple(["A", "C", "D"])]
    assert w_acd > w_abd

    rng = __import__("random").Random(1)
    counts = {"ABD": 0, "ACD": 0}
    for _ in range(2000):
        sel = pf.select_path_weighted("A", "D", path_weights=weights, rng=rng)
        if sel.path == ["A", "B", "D"]:
            counts["ABD"] += 1
        else:
            counts["ACD"] += 1
    assert counts["ACD"] > counts["ABD"]


def test_shortest_path_length_line():
    g = line_graph(5)
    pf = PathFinder(g)
    assert pf.shortest_path_length("0", "4") == 4