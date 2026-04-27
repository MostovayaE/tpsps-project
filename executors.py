from __future__ import annotations

import logging
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, Protocol

_logger = logging.getLogger(__name__)

_FORBIDDEN_ROOTS: tuple[Path, ...] = (
    Path("C:/Windows"),
    Path("C:/Windows/System32"),
    Path("/etc"),
    Path("/usr"),
    Path("/bin"),
    Path("/sbin"),
    Path("/boot"),
)

def _validate_export_path(raw: str) -> Path:
    p = Path(raw).resolve()

    for forbidden in _FORBIDDEN_ROOTS:
        try:
            p.relative_to(forbidden.resolve())
            raise RuntimeError(
                f"Export CSV: запись в системную директорию запрещена: {p}"
            )
        except ValueError:
            pass
    return p

import numpy as np
import pandas as pd
from PySide6 import QtWidgets

from context import PipelineContext
from csvwizard import Wizard
from technical.report_channel import ReportChannel
from technical.plots import GraphPlots
from technical.arima_executor import ArimaExecutor
from technical.sarima_executor import SarimaExecutor
from technical.ets_executor import EtsExecutor
from technical.ensemble_executor import EnsembleExecutor
from technical.ensemble_by_errors_executor import EnsembleByErrorsExecutor

class NodeExecutor(Protocol):
    def run(
        self, node, inputs: Dict[str, Any], report: ReportChannel
    ) -> Dict[str, Any]: ...

def _parse_int(node, prop_name: str, default: int) -> int:
    raw = (node.get_property(prop_name) or "").strip()
    try:
        return int(raw)
    except Exception:
        return default

def _parse_str(node, prop_name: str, default: str) -> str:
    raw = (node.get_property(prop_name) or "").strip()
    return raw or default

class StartCsvExecutor:
    def run(
        self, node, inputs: Dict[str, Any], report: ReportChannel
    ) -> Dict[str, Any]:
        csv_path = (node.get_property("csv_path") or "").strip()
        if not csv_path:
            raise RuntimeError("START: не задан csv_path")

        p = Path(csv_path)
        if not p.exists():
            raise RuntimeError(f"START: CSV файл не найден: {p}")

        df = pd.read_csv(p)
        if df.empty:
            raise RuntimeError("START: CSV пустой")

        if callable(getattr(report, "wizard_opener", None)):
            ctx = report.wizard_opener(df, report)
            if ctx is None:
                raise RuntimeError("Отменено пользователем")
        else:
            w = Wizard(df, report=report)
            if w.exec() != QtWidgets.QDialog.Accepted:
                raise RuntimeError("Отменено пользователем")
            ctx = w.result_context()

        report.add_text(
            f"Загружено строк: {len(ctx.df)}\n"
            f"time_col: {ctx.time_col}\n"
            f"value_col: {ctx.value_col}\n"
            f"freq: {ctx.freq}",
            title="Загрузка данных",
        )

        return {"ctx": ctx}

class SimpleSeriesPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        fig = GraphPlots.time_series(ctx)
        report.add_figure(fig, title="Временной ряд")
        return {"ctx": ctx}

class ACFPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        lags = _parse_int(node, "lags", 40)
        fig = GraphPlots.acf(ctx, lags=lags)
        report.add_figure(fig, title=f"ACF (lags={lags})")
        return {"ctx": ctx}

class PACFPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        lags = _parse_int(node, "lags", 40)
        fig = GraphPlots.pacf(ctx, lags=lags)
        report.add_figure(fig, title=f"PACF (lags={lags})")
        return {"ctx": ctx}

class RollingStatsPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        window = _parse_int(node, "window", 12)
        fig = GraphPlots.rolling_stats(ctx, window=window)
        report.add_figure(fig, title=f"Скользящие статистики (window={window})")
        return {"ctx": ctx}

class DifferencePlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        order = _parse_int(node, "order", 1)
        fig = GraphPlots.difference(ctx, order=order)
        report.add_figure(fig, title=f"Разность порядка {order}")
        return {"ctx": ctx}

class SeasonalDifferencePlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        seasonal_period = _parse_int(node, "seasonal_period", 12)
        fig = GraphPlots.seasonal_difference(ctx, seasonal_period=seasonal_period)
        report.add_figure(fig, title=f"Сезонная разность (lag={seasonal_period})")
        return {"ctx": ctx}

class DecompositionPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        period = _parse_int(node, "period", 12)
        model = _parse_str(node, "model", "additive")
        fig = GraphPlots.decomposition(ctx, period=period, model=model)
        report.add_figure(fig, title=f"Decomposition ({model}, period={period})")
        return {"ctx": ctx}

class HistogramPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        bins = _parse_int(node, "bins", 30)
        fig = GraphPlots.histogram(ctx, bins=bins)
        report.add_figure(fig, title=f"Гистограмма (bins={bins})")
        return {"ctx": ctx}

class QQPlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        fig = GraphPlots.qq(ctx)
        report.add_figure(fig, title="Q-Q plot")
        return {"ctx": ctx}

class SeasonalProfilePlotExecutor:
    def run(self, node, inputs, report):
        ctx = inputs["ctx"]
        fig = GraphPlots.seasonal_profile(ctx)
        report.add_figure(fig, title="Сезонный профиль")
        return {"ctx": ctx}

class OutlierCleaningExecutor:
    def run(
        self, node, inputs: Dict[str, Any], report: ReportChannel
    ) -> Dict[str, Any]:
        from technical.clearing import Clearing

        ctx: PipelineContext = inputs["ctx"]

        raw_threshold = (node.get_property("threshold") or "3.5").strip()
        try:
            threshold = float(raw_threshold)
            if threshold <= 0:
                raise ValueError
        except ValueError:
            threshold = 3.5

        fill_policy = (node.get_property("fill_policy") or "time").strip()
        if fill_policy not in ("time", "ffill", "bfill", "const", "none"):
            fill_policy = "time"

        raw_fill_value = (node.get_property("fill_value") or "0.0").strip()
        try:
            fill_value = float(raw_fill_value)
        except ValueError:
            fill_value = 0.0

        log_lines: list[str] = []
        clearing = Clearing(log_func=log_lines.append)

        new_ctx = clearing.detect_and_fix_outliers(
            ctx,
            threshold=threshold,
            fill_policy=fill_policy,
            fill_value=fill_value,
        )

        report.add_text(
            "\n".join(log_lines),
            title="Очистка выбросов",
        )

        return {"ctx": new_ctx}

class ExportCsvExecutor:
    def run(
        self, node, inputs: Dict[str, Any], report: ReportChannel
    ) -> Dict[str, Any]:
        ctx: PipelineContext = inputs["ctx"]
        export_path = (node.get_property("export_path") or "").strip()
        if not export_path:
            raise RuntimeError("Export CSV: не задан путь для выгрузки.")

        p = _validate_export_path(export_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        ctx.df.to_csv(p, index=False)

        report.add_text(
            f"Данные экспортированы в: {p}\nСтрок: {len(ctx.df)}, столбцов: {len(ctx.df.columns)}",
            title="Экспорт CSV",
        )

        return {"ctx": ctx}

EXECUTORS = {
    "pipeline.start.StartCsvNode": StartCsvExecutor(),
    "pipeline.plot.SimpleSeriesPlotNode": SimpleSeriesPlotExecutor(),
    "pipeline.plot.ACFPlotNode": ACFPlotExecutor(),
    "pipeline.plot.PACFPlotNode": PACFPlotExecutor(),
    "pipeline.plot.RollingStatsPlotNode": RollingStatsPlotExecutor(),
    "pipeline.plot.DifferencePlotNode": DifferencePlotExecutor(),
    "pipeline.plot.SeasonalDifferencePlotNode": SeasonalDifferencePlotExecutor(),
    "pipeline.plot.DecompositionPlotNode": DecompositionPlotExecutor(),
    "pipeline.plot.HistogramPlotNode": HistogramPlotExecutor(),
    "pipeline.plot.QQPlotNode": QQPlotExecutor(),
    "pipeline.plot.SeasonalProfilePlotNode": SeasonalProfilePlotExecutor(),
    "pipeline.model.ArimaModelNode": ArimaExecutor(),
    "pipeline.model.SarimaModelNode": SarimaExecutor(),
    "pipeline.model.EtsModelNode": EtsExecutor(),
    "pipeline.ensemble.EnsembleModelNode": EnsembleExecutor(),
    "pipeline.ensemble.EnsembleByErrorsModelNode": EnsembleByErrorsExecutor(),
    "pipeline.transform.OutlierCleaningNode": OutlierCleaningExecutor(),
    "pipeline.export.ExportCsvNode": ExportCsvExecutor(),
}
