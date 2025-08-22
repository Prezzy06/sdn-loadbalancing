from __future__ import annotations

# Ryu imports are only available at runtime inside Ryu env
from typing import Dict, Tuple, Optional, List
import time
import random

try:
    from ryu.base import app_manager
    from ryu.controller import ofp_event
    from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
    from ryu.controller.handler import set_ev_cls
    from ryu.ofproto import ofproto_v1_3
    from ryu.lib.packet import packet
    from ryu.lib.packet import ethernet
    from ryu.lib.packet import ether_types
except Exception:  # pragma: no cover - allow import in test env without Ryu
    app_manager = object  # type: ignore
    ofproto_v1_3 = object  # type: ignore
    def set_ev_cls(*args, **kwargs):  # type: ignore
        def deco(f):
            return f
        return deco

from utils.topology import TopologyManager
from utils.path_finder import PathFinder
from utils.load_monitor import LoadMonitor


class MultipathLoadBalancer(app_manager.RyuApp):  # type: ignore
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]  # type: ignore

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)  # type: ignore
        self.topo = TopologyManager()
        self.path_finder: Optional[PathFinder] = None
        self.load_monitor = LoadMonitor(poll_interval_sec=20)
        self.random = random.Random(42)
        self.last_rebalance_ts = 0.0
        self.rebalance_interval = 20

    def _ensure_path_finder(self) -> None:
        if self.path_finder is None:
            self.path_finder = PathFinder(self.topo.get_graph())

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)  # type: ignore
    def switch_features_handler(self, ev) -> None:  # type: ignore
        # Install table-miss or default rules as needed
        pass

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)  # type: ignore
    def _packet_in_handler(self, ev) -> None:  # type: ignore
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        in_port = msg.match["in_port"]

        # For POC: simplistic behavior—drop broadcast flood in favor of path install
        # In a full implementation, ARP/NDP handling is added here.

        # Placeholder: determine src/dst attachment switches and compute paths
        # src_sw, dst_sw = ... discover via topology events/host tracker
        # For now, skip if we cannot resolve
        return

    def compute_weights_and_select(self, src: str, dst: str) -> Optional[List[str]]:
        self._ensure_path_finder()
        assert self.path_finder is not None
        paths = self.path_finder.all_shortest_paths(src, dst)
        if not paths:
            return None

        def edge_load(u: str, v: str) -> float:
            return self.load_monitor.get_utilization(u, v)

        weights = self.path_finder.invert_loads_to_weights(paths, edge_load)
        sel = self.path_finder.select_path_weighted(src, dst, path_weights=weights, rng=self.random)
        return sel.path