### Architecture Overview

- Topology discovery via Ryu events or OpenDaylight REST.
- Graph built in `TopologyManager` (NetworkX Graph)
- Dijkstra shortest paths (hop-count) via `PathFinder`
- `LoadMonitor` polls link stats and computes utilization in [0,1]
- Weights derived as inverse of average path load
- Selection uses weighted random for traffic spreading + flow hashing for consistency

### Balancing Details
- Hash 5-tuple to choose a path deterministically per flow
- Periodically recompute weights; when imbalance >20% or utilization >70%, rebalance
- Batch flow mods to minimize churn

### Failure Handling
- On link down or switch down, recompute affected paths
- Expire stale flows with timeouts; proactively remove when topology changes