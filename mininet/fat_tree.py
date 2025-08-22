#!/usr/bin/env python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI


class FatTreeTopo(Topo):
    def build(self, k=4):
        # Basic k-ary fat-tree with OVS switches
        core = []
        agg = []
        edge = []
        hosts = []

        pods = k
        core_count = (k // 2) ** 2

        for i in range(core_count):
            core.append(self.addSwitch(f"c{i+1}"))

        for p in range(pods):
            agg_layer = []
            edge_layer = []
            for a in range(k // 2):
                s = self.addSwitch(f"a{p+1}_{a+1}")
                agg_layer.append(s)
            for e in range(k // 2):
                s = self.addSwitch(f"e{p+1}_{e+1}")
                edge_layer.append(s)
            agg.append(agg_layer)
            edge.append(edge_layer)

            # Connect aggregation to edge within pod
            for a_s in agg_layer:
                for e_s in edge_layer:
                    self.addLink(a_s, e_s)

            # Add hosts per edge
            for e_idx, e_s in enumerate(edge_layer):
                for h in range(k // 2):
                    h_id = self.addHost(f"h{p+1}_{e_idx+1}_{h+1}")
                    hosts.append(h_id)
                    self.addLink(h_id, e_s)

        # Connect aggregation to core
        core_idx = 0
        for p in range(pods):
            for a_s in agg[p]:
                for _ in range(k // 2):
                    self.addLink(a_s, core[core_idx % len(core)])
                    core_idx += 1


def run(k=4, controller_ip="127.0.0.1", controller_port=6653):
    topo = FatTreeTopo(k=k)
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=True,
        controller=lambda name: RemoteController(name, ip=controller_ip, port=controller_port),
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True,
    )
    net.start()
    print("Fat-tree started. Try: pingall, iperf3 between hosts.")
    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    run()