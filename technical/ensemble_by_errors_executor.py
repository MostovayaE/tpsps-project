from __future__ import annotations

import math
from dataclasses import replace
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


def _weighted_ensemble_plot(
    series_list: list[pd.Series],
    ensemble: pd.Series,
    labels: list[str],
    metric: str,
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
        label=f"Ансамбль (1/{metric.upper()})",
        color="black",
    )
    ax.set_title(
        f"Ансамблирование по ошибкам ({metric.upper()}): взвешенное усреднение",
        fontsize=_TITLE_FS,
        pad=4,
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


class EnsembleByErrorsExecutor:
    def run(self, node, inputs: Dict[str, Any], report) -> Dict[str, Any]:
        ctxes: list[tuple[str, PipelineContext]] = []
        for port in ("ctx1", "ctx2", "ctx3"):
            val = inputs.get(port)
            if val is not None:
                ctxes.append((port, val))

        if len(ctxes) < 2:
            raise RuntimeError(
                "Ensemble by Errors: необходимо подключить минимум 2 входных ctx."
            )

        raw_metric = node.get_property("metric")
        metric = (raw_metric or "mae").strip().lower()
        if metric not in ("mae", "mape", "rmse"):
            metric = "mae"

        errors: list[float] = []
        for port, ctx in ctxes:
            val = getattr(ctx, metric, None)
            if val is None or (
                isinstance(val, float) and (math.isnan(val) or math.isinf(val))
            ):
                raise RuntimeError(
                    f"Ensemble by Errors: модель на входе «{port}» не содержит корректную метрику "
                    f"{metric.upper()} (значение: {val}). Убедитесь, что все подключённые узлы — модели "
                    f"(ARIMA/SARIMA/ETS), которые уже выполнились и имеют конечное значение ошибки."
                )
            if float(val) < 0.0:
                raise RuntimeError(
                    f"Ensemble by Errors: метрика {metric.upper()} на входе «{port}» "
                    f"отрицательная ({val:.4f}). Ожидается неотрицательная ошибка."
                )
            errors.append(float(val))

        inv = [1.0 / e if e > 0.0 else math.inf for e in errors]

        if any(math.isinf(w) for w in inv):
            n_perfect = sum(1 for w in inv if math.isinf(w))
            weights = [1.0 / n_perfect if math.isinf(w) else 0.0 for w in inv]
        else:
            total = sum(inv)
            weights = [w / total for w in inv]

        base_ctx = ctxes[0][1]
        series_list = [_series_from_ctx(ctx) for _, ctx in ctxes]

        combined = pd.concat(series_list, axis=1)
        w_arr = np.array(weights)

        numerator = combined.mul(w_arr, axis=1).sum(axis=1, min_count=1)
        denominator = combined.notna().mul(w_arr, axis=1).sum(axis=1)
        ensemble = (numerator / denominator).dropna()
        ensemble.name = base_ctx.value_col

        out_df = pd.DataFrame(
            {
                base_ctx.time_col: ensemble.index,
                base_ctx.value_col: ensemble.values,
            }
        )
        out_ctx = _ctx_with_df(base_ctx, out_df)

        labels = [
            f"{ctx.model_name if ctx.model_name else f'Модель {i + 1} ({port})'} (вес {weights[i]:.2f})"
            for i, (port, ctx) in enumerate(ctxes)
        ]

        report.add_figure(
            _weighted_ensemble_plot(series_list, ensemble, labels, metric),
            title="Взвешенное ансамблирование прогнозов",
        )

        report.add_text(
            "\n".join(
                [
                    f"Количество моделей: {len(ctxes)}",
                    f"Метрика для весов: {metric.upper()}",
                    f"Метод: обратное взвешивание (вес = 1/ошибка)",
                    f"Точек в ансамбле: {len(ensemble)}",
                    f"Временной диапазон: {ensemble.index[0]} — {ensemble.index[-1]}",
                ]
            ),
            title="Сводка ансамбля по ошибкам",
        )

        table_rows = [
            ["Метрика для весов", metric.upper()],
            ["Метод", "Обратное взвешивание"],
        ]
        for i, (port, ctx) in enumerate(ctxes):
            model_label = (
                ctx.model_name if ctx.model_name else f"Модель {i + 1} ({port})"
            )
            table_rows.append([f"{model_label} — {metric.upper()}", f"{errors[i]:.4f}"])
            table_rows.append([f"{model_label} — вес", f"{weights[i]:.4f}"])
        table_rows += [
            ["Точек в результате", str(len(ensemble))],
            ["Min значение", f"{float(ensemble.min()):.4f}"],
            ["Max значение", f"{float(ensemble.max()):.4f}"],
            ["Среднее значение", f"{float(ensemble.mean()):.4f}"],
        ]

        report.add_table(
            headers=["Параметр", "Значение"],
            rows=table_rows,
            title="Параметры взвешенного ансамбля",
        )

        preview_rows = [
            [str(ts), f"{val:.4f}"]
            for ts, val in list(ensemble.items())[: min(10, len(ensemble))]
        ]
        report.add_table(
            headers=["Дата / время", "Ансамбль"],
            rows=preview_rows,
            title="Первые точки ансамблированного прогноза",
        )

        return {"ctx": out_ctx}
