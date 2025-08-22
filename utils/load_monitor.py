from __future__ import annotations

import time
from typing import Dict, Tuple, Optional, Callable


Edge = Tuple[str, str]


class LoadMonitor:
    """Caches link utilization using a provided stats fetcher.

    The fetcher must return a mapping {(u, v): (tx_bytes, rx_bytes, ts_seconds)} for each observed
    link direction or aggregate direction. Utilization is computed assuming symmetric capacity and
    returns a value in [0, 1].
    """

    def __init__(
        self,
        capacity_bps: int = 1_000_000_000,
        poll_interval_sec: int = 20,
        stats_fetcher: Optional[Callable[[], Dict[Edge, Tuple[int, int, float]]]] = None,
    ) -> None:
        self.capacity_bps = capacity_bps
        self.poll_interval_sec = poll_interval_sec
        self.stats_fetcher = stats_fetcher
        self.prev_bytes: Dict[Edge, Tuple[int, int, float]] = {}
        self.utilization_cache: Dict[Edge, float] = {}
        self.last_poll_ts: float = 0.0

    def _compute_utilization(
        self, prev: Tuple[int, int, float], curr: Tuple[int, int, float]
    ) -> float:
        prev_tx, prev_rx, prev_ts = prev
        tx, rx, ts = curr
        dt = max(1e-6, ts - prev_ts)
        dbytes = max(0, (tx + rx) - (prev_tx + prev_rx))
        bits_per_sec = (dbytes * 8.0) / dt
        return max(0.0, min(1.0, bits_per_sec / self.capacity_bps))

    def poll_once(self) -> None:
        if self.stats_fetcher is None:
            return
        raw = self.stats_fetcher()
        now = time.time()
        for edge, (tx, rx, ts) in raw.items():
            curr = (tx, rx, ts or now)
            if edge in self.prev_bytes:
                util = self._compute_utilization(self.prev_bytes[edge], curr)
                # Store symmetric for undirected graph convenience
                u, v = edge
                self.utilization_cache[(u, v)] = util
                self.utilization_cache[(v, u)] = util
            self.prev_bytes[edge] = curr
        self.last_poll_ts = now

    def get_utilization(self, u: str, v: str) -> float:
        return self.utilization_cache.get((u, v), 0.0)