from utils.consistent_selector import build_weighted_slots, select_path_for_key


def test_weighted_slots_distribution():
    paths = [["A", "B", "D"], ["A", "C", "D"]]
    weights = {tuple(paths[0]): 1.0, tuple(paths[1]): 9.0}
    table = build_weighted_slots(paths, weights, total_slots=1000)
    abd = sum(1 for p in table if p == paths[0])
    acd = sum(1 for p in table if p == paths[1])
    # Approximately 10% vs 90%
    assert 60 < abd < 140
    assert 860 < acd < 940


def test_consistent_mapping_same_key():
    paths = [["A", "B", "D"], ["A", "C", "D"]]
    weights = {tuple(paths[0]): 1.0, tuple(paths[1]): 1.0}
    table = build_weighted_slots(paths, weights, total_slots=10)
    key = b"flow-1"
    s1 = select_path_for_key(key, table)
    s2 = select_path_for_key(key, table)
    assert s1 == s2