from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from executors import EXECUTORS
from graph_links import GraphLinks
from technical.report_channel import ReportChannel


@dataclass(frozen=True)
class RunResult:
    artifacts: Dict[str, Dict[str, Any]]
    start_ctx: Optional[Any] = None


class GraphRunner:
    def __init__(self, graph, report: Optional[ReportChannel] = None):
        self.graph = graph
        self.links = GraphLinks(graph)
        self.report = report or ReportChannel()

    def run_all(self) -> RunResult:
        nodes = self.links.nodes()
        edges = self.links.edges()
        order = self.links.toposort_by_position()

        artifacts: Dict[str, Dict[str, Any]] = {}

        for node in order:
            inputs = self.links.collect_inputs(node, edges, artifacts)
            executor = EXECUTORS.get(node.type_)
            if executor is None:
                raise RuntimeError(f"Нет executor для узла типа: {node.type_}")

            outputs = executor.run(node, inputs, self.report) or {}
            artifacts[node.id] = outputs

        start_ctx = None
        for node in nodes:
            if node.type_ == "pipeline.start.StartCsvNode":
                start_ctx = artifacts.get(node.id, {}).get("ctx")
                break

        return RunResult(artifacts=artifacts, start_ctx=start_ctx)
