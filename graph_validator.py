from __future__ import annotations

from dataclasses import dataclass
from typing import List

from graph_links import GraphLinks, Edge

@dataclass
class Warning:
    severity: str
    message: str
    node_name: str = ""

def _safe_int(node, name: str, default: int) -> int:
    raw = node.get_property(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(raw)
    except Exception:
        return default

def _safe_str(node, name: str, default: str) -> str:
    raw = node.get_property(name)
    if raw is None or str(raw).strip() == "":
        return default
    return str(raw).strip()

_MODEL_TYPES = {
    "pipeline.model.ArimaModelNode",
    "pipeline.model.SarimaModelNode",
    "pipeline.model.EtsModelNode",
}

_ENSEMBLE_TYPES = {
    "pipeline.ensemble.EnsembleModelNode",
    "pipeline.ensemble.EnsembleByErrorsModelNode",
}

_SEASONAL_MODELS = {
    "pipeline.model.SarimaModelNode",
    "pipeline.model.EtsModelNode",
}

def _validate_node(n, edges_to, node_by_id) -> List[Warning]:
    warnings: List[Warning] = []
    incoming = edges_to.get(n.id, [])

    if n.type_ != "pipeline.start.StartCsvNode" and not incoming:
        warnings.append(
            Warning(
                "warning",
                f"Узел «{n.name()}» не имеет входных соединений — он не получит данных.",
                node_name=n.name(),
            )
        )

    if n.type_ == "pipeline.model.SarimaModelNode":
        s = _safe_int(n, "s", 12)
        if s < 2:
            warnings.append(
                Warning(
                    "error",
                    f"SARIMA «{n.name()}»: длина сезона s={s} некорректна (минимум 2).",
                    node_name=n.name(),
                )
            )

    if n.type_ == "pipeline.model.EtsModelNode":
        seasonal = _safe_str(n, "seasonal", "none")
        season_length = _safe_int(n, "season_length", 12)
        if seasonal != "none" and season_length < 2:
            warnings.append(
                Warning(
                    "error",
                    f"ETS «{n.name()}»: сезонность включена, но длина сезона = {season_length} (минимум 2).",
                    node_name=n.name(),
                )
            )

    if n.type_ in _MODEL_TYPES:
        fh = _safe_int(n, "forecast_horizon", 12)
        if fh < 1:
            warnings.append(
                Warning(
                    "warning",
                    f"«{n.name()}»: горизонт прогноза = {fh}. Будет использован размер тестовой выборки.",
                    node_name=n.name(),
                )
            )

    if n.type_ in _ENSEMBLE_TYPES:
        connected_ports = {e.dst_port for e in incoming}
        n_connected = len(connected_ports)
        if n_connected < 2:
            warnings.append(
                Warning(
                    "error",
                    f"Ансамбль «{n.name()}»: подключено {n_connected} вход(ов), необходимо минимум 2.",
                    node_name=n.name(),
                )
            )

    if n.type_ in _ENSEMBLE_TYPES:
        src_models = []
        for e in incoming:
            src_node = node_by_id.get(e.src_node_id)
            if src_node:
                src_models.append((src_node, e.src_port))

        for src_node, src_port in src_models:
            if src_node.type_ in _ENSEMBLE_TYPES:
                warnings.append(
                    Warning(
                        "warning",
                        f"Ансамбль «{n.name()}» получает вход от другого ансамбля «{src_node.name()}» — "
                        f"это может дать неинтерпретируемый результат.",
                        node_name=n.name(),
                    )
                )

        horizons = {}
        for src_node, src_port in src_models:
            if src_node.type_ in _MODEL_TYPES:
                fh = _safe_int(src_node, "forecast_horizon", 12)
                horizons[src_node.name()] = fh
        if len(set(horizons.values())) > 1:
            details = ", ".join(f"{name}={h}" for name, h in horizons.items())
            warnings.append(
                Warning(
                    "warning",
                    f"Ансамбль «{n.name()}»: подключённые модели имеют разный горизонт прогноза ({details}). "
                    f"Длина результирующих рядов может различаться.",
                    node_name=n.name(),
                )
            )

    if n.type_ in _MODEL_TYPES:
        for e in incoming:
            src_node = node_by_id.get(e.src_node_id)
            if src_node and src_node.type_ in _MODEL_TYPES and e.src_port == "forecast":
                warnings.append(
                    Warning(
                        "warning",
                        f"Модель «{n.name()}» получает вход от forecast-порта модели «{src_node.name()}» — "
                        f"это построение прогноза на основании прогноза, результат может быть ненадёжным.",
                        node_name=n.name(),
                    )
                )

    if n.type_ == "pipeline.model.ArimaModelNode":
        mode = _safe_str(n, "mode", "auto")
        if mode == "manual":
            p = _safe_int(n, "p", 1)
            d = _safe_int(n, "d", 1)
            q = _safe_int(n, "q", 1)
            if p == 0 and d == 0 and q == 0:
                warnings.append(
                    Warning(
                        "error",
                        f"ARIMA «{n.name()}»: все параметры p=d=q=0, модель вырождена.",
                        node_name=n.name(),
                    )
                )

    if n.type_ == "pipeline.model.SarimaModelNode":
        mode = _safe_str(n, "mode", "auto")
        if mode == "manual":
            vals = [_safe_int(n, k, 1) for k in ("p", "d", "q", "P", "D", "Q")]
            if all(v == 0 for v in vals):
                warnings.append(
                    Warning(
                        "error",
                        f"SARIMA «{n.name()}»: все параметры (p,d,q,P,D,Q) = 0, модель вырождена.",
                        node_name=n.name(),
                    )
                )

    if n.type_ == "pipeline.model.EtsModelNode":
        mode = _safe_str(n, "mode", "auto")
        if mode == "manual":
            trend = _safe_str(n, "trend", "none")
            damped = _safe_str(n, "damped_trend", "false").lower() in (
                "true",
                "1",
                "yes",
            )
            if trend == "none" and damped:
                warnings.append(
                    Warning(
                        "warning",
                        f"ETS «{n.name()}»: затухающий тренд включён, но тренд не задан. Параметр будет проигнорирован.",
                        node_name=n.name(),
                    )
                )

    if n.type_ == "pipeline.ensemble.EnsembleByErrorsModelNode":
        metric = _safe_str(n, "metric", "mae").lower()
        if metric not in ("mae", "mape", "rmse"):
            warnings.append(
                Warning(
                    "warning",
                    f"Ансамбль по ошибкам «{n.name()}»: неизвестная метрика «{metric}», будет использована MAE.",
                    node_name=n.name(),
                )
            )

    if n.type_ == "pipeline.ensemble.EnsembleByErrorsModelNode":
        for e in incoming:
            src_node = node_by_id.get(e.src_node_id)
            if src_node and src_node.type_ not in _MODEL_TYPES:
                warnings.append(
                    Warning(
                        "warning",
                        f"Ансамбль по ошибкам «{n.name()}»: вход «{e.dst_port}» подключён к "
                        f"«{src_node.name()}» — это не модель, метрики ошибок могут отсутствовать.",
                        node_name=n.name(),
                    )
                )

    return warnings

def validate_graph(graph) -> List[Warning]:
    warnings: List[Warning] = []

    links = GraphLinks(graph)
    nodes = links.nodes()
    edges = links.edges()

    if not nodes:
        warnings.append(Warning("error", "Граф пуст — нет ни одного узла."))
        return warnings

    node_by_id = {n.id: n for n in nodes}

    edges_to: dict[str, list[Edge]] = {}
    for e in edges:
        edges_to.setdefault(e.dst_node_id, []).append(e)

    start_nodes = [n for n in nodes if n.type_ == "pipeline.start.StartCsvNode"]
    if not start_nodes:
        warnings.append(
            Warning("error", "В графе нет стартового узла START: Load CSV.")
        )
    if len(start_nodes) > 1:
        warnings.append(
            Warning(
                "error",
                f"В графе {len(start_nodes)} стартовых узлов. Допускается только один — удалите лишние.",
            )
        )

    try:
        ordered = links.toposort_by_position()
    except RuntimeError:
        warnings.append(
            Warning(
                "error",
                "В графе обнаружен цикл — выполнение невозможно.",
            )
        )
        return warnings

    for n in ordered:
        warnings.extend(_validate_node(n, edges_to, node_by_id))

    return warnings
