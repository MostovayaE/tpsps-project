from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass(frozen=True)
class Edge:
    src_node_id: str
    src_port: str
    dst_node_id: str
    dst_port: str

class GraphLinks:

    def __init__(self, graph):
        self.graph = graph

    def nodes(self):
        return list(self.graph.all_nodes())

    def edges(self) -> List[Edge]:
        nodes = self.nodes()
        edges: List[Edge] = []

        for node in nodes:
            for dst_name, in_port in node.inputs().items():
                for out_port in in_port.connected_ports():
                    src_node = out_port.node()
                    edges.append(
                        Edge(
                            src_node_id=src_node.id,
                            src_port=out_port.name(),
                            dst_node_id=node.id,
                            dst_port=dst_name,
                        )
                    )

        return edges

    def toposort(self) -> List:
        nodes = self.nodes()
        edges = self.edges()

        node_by_id = {n.id: n for n in nodes}
        deps: Dict[str, Set[str]] = {n.id: set() for n in nodes}
        outs: Dict[str, Set[str]] = {n.id: set() for n in nodes}

        for e in edges:
            deps[e.dst_node_id].add(e.src_node_id)
            outs[e.src_node_id].add(e.dst_node_id)

        ready = [nid for nid in deps if not deps[nid]]
        order = []

        while ready:
            nid = ready.pop()
            order.append(node_by_id[nid])
            for m in list(outs[nid]):
                deps[m].discard(nid)
                if not deps[m]:
                    ready.append(m)

        if len(order) != len(nodes):
            raise RuntimeError(
                "В графе есть цикл или неразрешимые зависимости (DAG нарушен)."
            )

        return order

    def toposort_by_position(self) -> List:
        nodes = self.nodes()
        edges = self.edges()

        node_by_id = {n.id: n for n in nodes}
        deps: Dict[str, Set[str]] = {n.id: set() for n in nodes}
        outs: Dict[str, Set[str]] = {n.id: set() for n in nodes}

        for e in edges:
            deps[e.dst_node_id].add(e.src_node_id)
            outs[e.src_node_id].add(e.dst_node_id)

        def _y(nid: str) -> float:
            node = node_by_id.get(nid)
            if node is None:
                return 0.0
            try:
                return node.y_pos()
            except Exception:
                return 0.0

        ready_roots = sorted(
            [nid for nid in deps if not deps[nid]],
            key=_y,
        )

        order: List = []
        visited: Set[str] = set()

        def _process_branch(start_nid: str):
            stack = [start_nid]
            while stack:
                nid = stack.pop()
                if nid in visited:
                    continue
                if deps[nid]:
                    continue
                visited.add(nid)
                order.append(node_by_id[nid])

                newly_ready = []
                for m in outs[nid]:
                    deps[m].discard(nid)
                    if not deps[m] and m not in visited:
                        newly_ready.append(m)

                newly_ready.sort(key=_y, reverse=True)
                stack.extend(newly_ready)

        for root_nid in ready_roots:
            if root_nid not in visited:
                _process_branch(root_nid)

        remaining = sorted(
            [nid for nid in node_by_id if nid not in visited and not deps[nid]],
            key=_y,
        )
        while remaining:
            for nid in remaining:
                _process_branch(nid)
            remaining = sorted(
                [nid for nid in node_by_id if nid not in visited and not deps[nid]],
                key=_y,
            )

        if len(order) != len(nodes):
            raise RuntimeError(
                "В графе есть цикл или неразрешимые зависимости (DAG нарушен)."
            )

        return order

    def collect_inputs(self, node, edges: List[Edge], artifacts: Dict[str, Dict]):
        inputs = {}
        for e in edges:
            if e.dst_node_id != node.id:
                continue
            src_out = artifacts.get(e.src_node_id)
            if src_out is None:
                raise RuntimeError(
                    f"Узел {node.name()} получает данные от не выполненного узла."
                )
            inputs[e.dst_port] = src_out.get(e.src_port)
        return inputs
