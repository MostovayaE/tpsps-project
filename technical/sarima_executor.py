from __future__ import annotations

from dataclasses import replace
from math import sqrt
from typing import Dict, Any

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from pandas.tseries.frequencies import to_offset
from statsmodels.tsa.statespace.sarimax import SARIMAX

from context import PipelineContext


def _ctx_with_df(ctx: PipelineContext, df: pd.DataFrame) -> PipelineContext:
    return replace(ctx, df=df)


def _series_from_ctx(ctx: PipelineContext) -> pd.Series:
    df = ctx.df.copy()
    x = pd.to_datetime(df[ctx.time_col], errors="coerce")
    y = pd.to_numeric(df[ctx.value_col], errors="coerce")
    return pd.Series(y.values, index=x).dropna().sort_index()


def _safe_int_property(node, name: str, default: int) -> int:
    raw = node.get_property(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(raw)
    except Exception:
        return default


def _safe_str_property(node, name: str, default: str) -> str:
    raw = node.get_property(name)
    if raw is None or str(raw).strip() == "":
        return default
    return str(raw).strip()


def _mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    return float(np.mean(np.abs(y_true - y_pred)))


def _rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    return float(sqrt(np.mean((y_true - y_pred) ** 2)))


def _mape(y_true: pd.Series, y_pred: pd.Series) -> float:
    mask = y_true != 0
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)


def _future_index(
    last_timestamp: pd.Timestamp, freq: str, periods: int
) -> pd.DatetimeIndex:
    offset = to_offset(freq)
    start = last_timestamp + offset
    return pd.date_range(start=start, periods=periods, freq=freq)


_TITLE_FS = 9
_LABEL_FS = 8
_TICK_FS = 7
_LEGEND_FS = 7


def _train_test_plot(train, test, pred_test, title: str) -> Figure:
    fig = Figure(figsize=(9, 5.5), tight_layout=True)
    ax = fig.add_subplot(111)
    ax.plot(train.index, train.values, label="Обучающая выборка", linewidth=1.2)
    ax.plot(test.index, test.values, label="Фактические значения теста", linewidth=1.2)
    ax.plot(
        pred_test.index,
        pred_test.values,
        label="Прогноз модели на тесте",
        linewidth=1.4,
    )
    ax.set_title(title, fontsize=_TITLE_FS, pad=4)
    ax.set_xlabel("Время", fontsize=_LABEL_FS)
    ax.set_ylabel("Значение", fontsize=_LABEL_FS)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=_LEGEND_FS, handlelength=1.5)
    ax.tick_params(axis="both", labelsize=_TICK_FS)
    ax.tick_params(axis="x", rotation=45)
    return fig


def _forecast_plot(history, future_forecast, title: str) -> Figure:
    fig = Figure(figsize=(9, 5.5), tight_layout=True)
    ax = fig.add_subplot(111)
    ax.plot(history.index, history.values, label="Исторический ряд", linewidth=1.2)
    ax.plot(
        future_forecast.index,
        future_forecast.values,
        label="Будущий прогноз",
        linewidth=1.6,
    )
    ax.set_title(title, fontsize=_TITLE_FS, pad=4)
    ax.set_xlabel("Время", fontsize=_LABEL_FS)
    ax.set_ylabel("Значение", fontsize=_LABEL_FS)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(fontsize=_LEGEND_FS, handlelength=1.5)
    ax.tick_params(axis="both", labelsize=_TICK_FS)
    ax.tick_params(axis="x", rotation=45)
    return fig


class SarimaExecutor:
    def run(self, node, inputs: Dict[str, Any], report) -> Dict[str, Any]:
        ctx: PipelineContext = inputs["ctx"]
        series = _series_from_ctx(ctx)

        if len(series) < 24:
            raise RuntimeError("SARIMA: для модели желательно хотя бы 24 наблюдения.")
        if not ctx.freq:
            raise RuntimeError("SARIMA: в контексте не задана частота ряда.")

        mode = _safe_str_property(node, "mode", "auto").lower()
        p = _safe_int_property(node, "p", 1)
        d = _safe_int_property(node, "d", 1)
        q = _safe_int_property(node, "q", 1)
        P = _safe_int_property(node, "P", 1)
        D = _safe_int_property(node, "D", 1)
        Q = _safe_int_property(node, "Q", 1)
        s = _safe_int_property(node, "s", 12)
        train_percent = _safe_int_property(node, "train_percent", 80)

        if mode == "manual":
            node.set_property(
                "summary",
                f"SARIMA({p},{d},{q})x({P},{D},{Q},{s}), train={train_percent}%",
            )
        else:
            best_spec = None
            best_aic = None

            auto_train_size = int(round(len(series) * train_percent / 100.0))
            auto_train_size = max(12, min(auto_train_size, len(series) - 1))
            train_auto = series.iloc[:auto_train_size]

            for pp in range(0, 3):
                for dd in range(0, 2):
                    for qq in range(0, 3):
                        for PP in range(0, 2):
                            for DD in range(0, 2):
                                for QQ in range(0, 2):
                                    if pp == dd == qq == PP == DD == QQ == 0:
                                        continue
                                    try:
                                        result = SARIMAX(
                                            train_auto,
                                            order=(pp, dd, qq),
                                            seasonal_order=(PP, DD, QQ, s),
                                            enforce_stationarity=False,
                                            enforce_invertibility=False,
                                        ).fit(disp=False)
                                        aic = float(result.aic)
                                        if best_aic is None or aic < best_aic:
                                            best_aic = aic
                                            best_spec = (pp, dd, qq, PP, DD, QQ)
                                    except Exception:
                                        continue

            if best_spec is None:
                raise RuntimeError(
                    "SARIMA: не удалось автоматически подобрать параметры."
                )

            p, d, q, P, D, Q = best_spec

            node.set_property("mode", "auto")
            node.set_property("p", str(p))
            node.set_property("d", str(d))
            node.set_property("q", str(q))
            node.set_property("P", str(P))
            node.set_property("D", str(D))
            node.set_property("Q", str(Q))
            node.set_property("s", str(s))
            node.set_property("train_percent", str(train_percent))
            node.set_property("summary", f"SARIMA({p},{d},{q})x({P},{D},{Q},{s}), auto")

        train_size = int(round(len(series) * train_percent / 100.0))
        train_size = max(12, min(train_size, len(series) - 1))

        train = series.iloc[:train_size]
        test = series.iloc[train_size:]

        result_train = SARIMAX(
            train,
            order=(p, d, q),
            seasonal_order=(P, D, Q, s),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)

        _forecast_raw = result_train.forecast(steps=len(test))
        pred_test = pd.Series(_forecast_raw.values, index=test.index)

        mae = _mae(test, pred_test)
        rmse = _rmse(test, pred_test)
        mape = _mape(test, pred_test)

        result_full = SARIMAX(
            series,
            order=(p, d, q),
            seasonal_order=(P, D, Q, s),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)

        forecast_horizon = _safe_int_property(node, "forecast_horizon", len(test))
        if forecast_horizon < 1:
            forecast_horizon = len(test)
        future_values = result_full.forecast(steps=forecast_horizon)
        future_idx = _future_index(series.index[-1], ctx.freq, forecast_horizon)
        future_forecast = pd.Series(future_values.values, index=future_idx)

        forecast_df = pd.DataFrame(
            {
                ctx.time_col: future_forecast.index,
                ctx.value_col: future_forecast.values,
            }
        )

        history_df = pd.DataFrame(
            {
                ctx.time_col: series.index,
                ctx.value_col: series.values,
            }
        )

        combined_df = pd.concat([history_df, forecast_df], ignore_index=True)

        _model_name = f"SARIMA({p},{d},{q})x({P},{D},{Q},{s})"
        forecast_ctx = replace(
            _ctx_with_df(ctx, forecast_df),
            mae=mae,
            mape=mape,
            rmse=rmse,
            model_name=_model_name,
            test_actual=test,
            test_predicted=pred_test,
        )
        combined_ctx = replace(
            _ctx_with_df(ctx, combined_df),
            mae=mae,
            mape=mape,
            rmse=rmse,
            model_name=_model_name,
            test_actual=test,
            test_predicted=pred_test,
        )

        report.add_figure(
            _train_test_plot(
                train,
                test,
                pred_test,
                f"SARIMA({p},{d},{q})x({P},{D},{Q},{s}): качество на train/test split",
            ),
            title="Проверка модели на отложенной выборке",
        )
        report.add_figure(
            _forecast_plot(
                series,
                future_forecast,
                f"SARIMA({p},{d},{q})x({P},{D},{Q},{s}): будущий прогноз",
            ),
            title="Будущий прогноз модели SARIMA",
        )

        report.add_text(
            "\n".join(
                [
                    f"Режим настройки: {'ручной' if mode == 'manual' else 'автоматический'}",
                    f"Выбранная модель: SARIMA({p},{d},{q})x({P},{D},{Q},{s})",
                    f"Частота ряда: {ctx.freq}",
                    f"Размер ряда: {len(series)} наблюдений",
                    f"Обучающая выборка: {len(train)} наблюдений ({train_percent}%)",
                    f"Тестовая выборка: {len(test)} наблюдений ({100 - train_percent}%)",
                    f"Горизонт будущего прогноза: {forecast_horizon} точек",
                    f"AIC финальной модели: {getattr(result_full, 'aic', float('nan')):.3f}",
                    f"BIC финальной модели: {getattr(result_full, 'bic', float('nan')):.3f}",
                ]
            ),
            title="Параметры и сводка по модели SARIMA",
        )

        report.add_table(
            headers=["Параметр", "Значение"],
            rows=[
                ["Режим настройки", "ручной" if mode == "manual" else "автоматический"],
                ["AR (p)", str(p)],
                ["Дифференцирование (d)", str(d)],
                ["MA (q)", str(q)],
                ["Сезонный AR (P)", str(P)],
                ["Сезонное дифференцирование (D)", str(D)],
                ["Сезонный MA (Q)", str(Q)],
                ["Длина сезона (s)", str(s)],
                ["Итоговая модель", f"SARIMA({p},{d},{q})x({P},{D},{Q},{s})"],
                ["Частота ряда", str(ctx.freq)],
                ["Обучающая выборка, %", str(train_percent)],
                ["Тестовая выборка, %", str(100 - train_percent)],
                ["Горизонт прогноза", str(forecast_horizon)],
                ["AIC", f"{getattr(result_full, 'aic', float('nan')):.3f}"],
                ["BIC", f"{getattr(result_full, 'bic', float('nan')):.3f}"],
            ],
            title="Параметры модели SARIMA",
        )

        report.add_table(
            headers=["Метрика", "Значение"],
            rows=[
                ["MAE (средняя абсолютная ошибка)", f"{mae:.4f}"],
                ["RMSE (корень из средней квадратичной ошибки)", f"{rmse:.4f}"],
                [
                    "MAPE (средняя абсолютная процентная ошибка), %",
                    f"{mape:.2f}" if np.isfinite(mape) else "не вычисляется",
                ],
            ],
            title="Метрики качества на тестовой выборке",
        )

        preview_rows = [
            [str(ts), f"{val:.4f}"] for ts, val in list(future_forecast.items())[:10]
        ]
        report.add_table(
            headers=["Дата / время", "Прогноз"],
            rows=preview_rows,
            title="Первые точки будущего прогноза",
        )

        return {
            "forecast": forecast_ctx,
            "combined": combined_ctx,
        }
