from __future__ import annotations

import base64
import json
from typing import Any, Dict, Optional
import requests


class ODLClient:
    def __init__(
        self,
        base_url: str = "https://localhost:8443/restconf",
        username: str = "admin",
        password: str = "admin",
        verify_ssl: bool = False,
        timeout: int = 10,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.session.timeout = timeout
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.session.headers.update({
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_topology(self) -> Dict[str, Any]:
        url = f"{self.base_url}/operational/network-topology:network-topology"
        r = self.session.get(url)
        r.raise_for_status()
        return r.json()

    def push_flow(self, node_id: str, table_id: int, flow_id: str, flow_body: Dict[str, Any]) -> None:
        url = (
            f"{self.base_url}/config/opendaylight-inventory:nodes/node/{node_id}/"
            f"table/{table_id}/flow/{flow_id}"
        )
        r = self.session.put(url, data=json.dumps({"flow": [flow_body]}))
        r.raise_for_status()

    def delete_flow(self, node_id: str, table_id: int, flow_id: str) -> None:
        url = (
            f"{self.base_url}/config/opendaylight-inventory:nodes/node/{node_id}/"
            f"table/{table_id}/flow/{flow_id}"
        )
        r = self.session.delete(url)
        r.raise_for_status()