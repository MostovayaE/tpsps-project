from __future__ import annotations

from dataclasses import replace
from math import sqrt
from typing import Any, Dict

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from context import PipelineContext


def _ctx_with_df(ctx: PipelineContext, df: pd.DataFrame) -> PipelineContext:
    return replace(ctx, df=df)


def _series_from_ctx(ctx: PipelineContext) -> pd.Series:
    df = ctx.df.copy()
    x = pd.to_datetime(df[ctx.time_col], errors="coerce")
    y = pd.to_numeric(df[ctx.value_col], errors="coerce")
    return pd.Series(y.values, index=x).dropna().sort_index()


_TITLE_FS = 9
_LABEL_FS = 8
_TICK_FS = 7
_LEGEND_FS = 7


def _ensemble_plot(
    series_list: list[pd.Series], ensemble: pd.Series, labels: list[str]
) -> Figure:
    fig = Figure(figsize=(10, 7.0))
    ax = fig.add_subplot(111)
    fig.subplots_adjust(left=0.08, right=0.97, top=0.93, bottom=0.28)

    for s, label in zip(series_list, labels):
        ax.plot(
            s.index, s.values, linewidth=1.1, linestyle="--", alpha=0.7, label=label
        )
    ax.plot(
        ensemble.index,
        ensemble.values,
        linewidth=2.0,
        label="Ансамбль (среднее)",
        color="black",
    )

    ax.set_title(
        "Простое ансамблирование: усреднение прогнозов", fontsize=_TITLE_FS, pad=4
    )
    ax.set_xlabel("Время", fontsize=_LABEL_FS)
    ax.set_ylabel("Значение", fontsize=_LABEL_FS)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.tick_params(axis="both", labelsize=_TICK_FS)
    ax.tick_params(axis="x", rotation=45)

    handles, leg_labels = ax.get_legend_handles_labels()
    fig.legend(
        handles,
        leg_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncols=2,
        fontsize=_LEGEND_FS,
        handlelength=1.5,
        frameon=True,
        framealpha=0.9,
    )
    return fig


class EnsembleExecutor:
    def run(self, node, inputs: Dict[str, Any], report) -> Dict[str, Any]:
        ctxes: list[tuple[str, PipelineContext]] = []
        for port in ("ctx1", "ctx2", "ctx3"):
            val = inputs.get(port)
            if val is not None:
                ctxes.append((port, val))

        if len(ctxes) < 2:
            raise RuntimeError(
                "Simple Ensemble: необходимо подключить минимум 2 входных ctx."
            )

        base_ctx = ctxes[0][1]

        series_list = [_series_from_ctx(ctx) for _, ctx in ctxes]
        labels = [
            ctx.model_name if ctx.model_name else f"Модель {i + 1} ({port})"
            for i, (port, ctx) in enumerate(ctxes)
        ]

        combined = pd.concat(series_list, axis=1)
        ensemble = combined.mean(axis=1).dropna()
        ensemble.name = base_ctx.value_col

        out_df = pd.DataFrame(
            {
                base_ctx.time_col: ensemble.index,
                base_ctx.value_col: ensemble.values,
            }
        )
        out_ctx = _ctx_with_df(base_ctx, out_df)

        report.add_figure(
            _ensemble_plot(series_list, ensemble, labels),
            title="Ансамблирование прогнозов",
        )

        report.add_text(
            "\n".join(
                [
                    f"Количество моделей: {len(ctxes)}",
                    f"Метод: простое усреднение",
                    f"Точек в ансамбле: {len(ensemble)}",
                    f"Временной диапазон: {ensemble.index[0]} — {ensemble.index[-1]}",
                ]
            ),
            title="Сводка ансамбля",
        )

        report.add_table(
            headers=["Параметр", "Значение"],
            rows=[
                ["Количество моделей", str(len(ctxes))],
                ["Метод ансамблирования", "Простое усреднение"],
                ["Точек в результате", str(len(ensemble))],
                ["Min значение", f"{float(ensemble.min()):.4f}"],
                ["Max значение", f"{float(ensemble.max()):.4f}"],
                ["Среднее значение", f"{float(ensemble.mean()):.4f}"],
            ],
            title="Параметры ансамбля",
        )

        preview_rows = [
            [str(ts), f"{val:.4f}"] for ts, val in list(ensemble.items())[:10]
        ]
        report.add_table(
            headers=["Дата / время", "Ансамбль"],
            rows=preview_rows,
            title="Первые точки ансамблированного прогноза",
        )

        return {"ctx": out_ctx}
