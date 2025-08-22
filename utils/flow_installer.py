from __future__ import annotations

from typing import Dict, List, Optional, Tuple


class FlowInstaller:
    """Abstracts pushing flows to devices. Implementations: RyuOpenFlowInstaller, ODLInstaller."""

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
        raise NotImplementedError


class RyuOpenFlowInstaller(FlowInstaller):
    def __init__(self, app) -> None:
        self.app = app

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
        # Placeholder: implemented in controllers/ryu_app.py where OFP libs are available
        # This class serves as an injectable dependency.
        pass