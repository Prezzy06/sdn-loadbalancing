from __future__ import annotations

from typing import Dict, List, Optional
from controllers.odl_client import ODLClient
from utils.flow_installer import FlowInstaller


class ODLFlowInstaller(FlowInstaller):
    def __init__(self, client: Optional[ODLClient] = None) -> None:
        self.client = client or ODLClient()

    def install_path_flow(
        self,
        path: List[str],
        in_port: Optional[int],
        match: Dict,
        cookie: int,
        idle_timeout: int = 30,
        hard_timeout: int = 300,
        priority: int = 100,
    ) -> None:
        # Placeholder: transform to ODL flow JSON and push across nodes in path
        # Real implementation would enumerate segments and set output ports per hop.
        pass