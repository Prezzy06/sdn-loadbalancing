from __future__ import annotations

import hashlib
from typing import Dict, List, Tuple

from utils.path_finder import EdgePath


def _hash_key(key_bytes: bytes) -> int:
    return int.from_bytes(hashlib.sha256(key_bytes).digest()[:8], "big", signed=False)


def build_weighted_slots(
    paths: List[EdgePath],
    weights: Dict[Tuple[str, ...], float],
    total_slots: int = 1000,
) -> List[EdgePath]:
    # Normalize weights and build a slot table deterministically
    items = []
    for p in paths:
        t = tuple(p)
        w = max(0.0, float(weights.get(t, 0.0)))
        items.append((t, w))
    if not items:
        return []
    total_weight = sum(w for _, w in items)
    if total_weight <= 0.0:
        # Fallback uniform
        per = max(1, total_slots // len(items))
        table: List[EdgePath] = []
        for t, _ in items:
            table.extend([list(t)] * per)
        # Pad/truncate
        while len(table) < total_slots:
            table.append(list(items[-1][0]))
        return table[:total_slots]

    table: List[EdgePath] = []
    for t, w in items:
        slots = max(1, int(round((w / total_weight) * total_slots)))
        table.extend([list(t)] * slots)
    if len(table) < total_slots:
        table.extend([table[-1]] * (total_slots - len(table)))
    return table[:total_slots]


def select_path_for_key(
    key_bytes: bytes,
    slot_table: List[EdgePath],
) -> EdgePath:
    if not slot_table:
        raise ValueError("Empty slot table")
    idx = _hash_key(key_bytes) % len(slot_table)
    return slot_table[idx]