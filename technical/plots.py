from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.gofplots import qqplot

from context import PipelineContext

_TITLE_FS = 9
_LABEL_FS = 8
_TICK_FS = 7
_LEGEND_FS = 7


def _style_ax(
    ax, *, xlabel: str = "", ylabel: str = "", title: str = "", rotate_x: bool = True
) -> None:
    if title:
        ax.set_title(title, fontsize=_TITLE_FS, pad=4)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=_LABEL_FS)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=_LABEL_FS)
    ax.tick_params(axis="both", labelsize=_TICK_FS)
    if rotate_x:
        ax.tick_params(axis="x", rotation=45)


class GraphPlots:
    @staticmethod
    def _series(ctx: PipelineContext) -> pd.Series:
        df = ctx.df.copy()
        x = pd.to_datetime(df[ctx.time_col], errors="coerce")
        y = pd.to_numeric(df[ctx.value_col], errors="coerce")
        s = pd.Series(y.values, index=x).dropna().sort_index()
        return s

    @staticmethod
    def time_series(ctx: PipelineContext) -> Figure:
        s = GraphPlots._series(ctx)

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.plot(s.index, s.values, linewidth=1.2)
        ax.grid(True, linestyle="--", alpha=0.5)
        _style_ax(
            ax,
            xlabel=ctx.time_col,
            ylabel=ctx.value_col,
            title=f"{ctx.value_col} по времени",
        )
        return fig

    @staticmethod
    def acf(ctx: PipelineContext, lags: int = 40) -> Figure:
        s = GraphPlots._series(ctx)

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        plot_acf(s, lags=lags, ax=ax, zero=False)
        _style_ax(ax, title=f"ACF ({ctx.value_col})", rotate_x=False)
        return fig

    @staticmethod
    def pacf(ctx: PipelineContext, lags: int = 40) -> Figure:
        s = GraphPlots._series(ctx)

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        plot_pacf(s, lags=lags, ax=ax, zero=False, method="ywm")
        _style_ax(ax, title=f"PACF ({ctx.value_col})", rotate_x=False)
        return fig

    @staticmethod
    def rolling_stats(ctx: PipelineContext, window: int = 12) -> Figure:
        s = GraphPlots._series(ctx)
        roll_mean = s.rolling(window=window).mean()
        roll_std = s.rolling(window=window).std()

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.plot(s.index, s.values, label="Ряд", linewidth=1.0)
        ax.plot(roll_mean.index, roll_mean.values, label=f"MA({window})", linewidth=1.4)
        ax.plot(roll_std.index, roll_std.values, label=f"STD({window})", linewidth=1.2)
        ax.legend(fontsize=_LEGEND_FS, handlelength=1.5)
        ax.grid(True, linestyle="--", alpha=0.5)
        _style_ax(ax, title=f"Скользящие статистики (window={window})")
        return fig

    @staticmethod
    def difference(ctx: PipelineContext, order: int = 1) -> Figure:
        s = GraphPlots._series(ctx)
        d = s.diff(order).dropna()

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.plot(d.index, d.values, linewidth=1.0)
        ax.grid(True, linestyle="--", alpha=0.5)
        _style_ax(ax, title=f"Разность порядка {order}")
        return fig

    @staticmethod
    def seasonal_difference(ctx: PipelineContext, seasonal_period: int = 12) -> Figure:
        s = GraphPlots._series(ctx)
        d = s.diff(seasonal_period).dropna()

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.plot(d.index, d.values, linewidth=1.0)
        ax.grid(True, linestyle="--", alpha=0.5)
        _style_ax(ax, title=f"Сезонная разность, lag={seasonal_period}")
        return fig

    @staticmethod
    def decomposition(
        ctx: PipelineContext, period: int = 12, model: str = "additive"
    ) -> Figure:
        s = GraphPlots._series(ctx)
        result = seasonal_decompose(
            s, model=model, period=period, extrapolate_trend="freq"
        )

        fig = Figure(figsize=(9, 10), tight_layout=True)
        axes = [fig.add_subplot(4, 1, i + 1) for i in range(4)]

        axes[0].plot(result.observed.index, result.observed.values)
        axes[1].plot(result.trend.index, result.trend.values)
        axes[2].plot(result.seasonal.index, result.seasonal.values)
        axes[3].plot(result.resid.index, result.resid.values)

        sub_titles = ["Observed", "Trend", "Seasonal", "Residual"]
        for ax, t in zip(axes, sub_titles):
            _style_ax(ax, title=t)
            ax.grid(True, linestyle="--", alpha=0.4)

        fig.suptitle(
            f"Seasonal decomposition ({model}, period={period})",
            fontsize=_TITLE_FS,
            y=1.01,
        )
        return fig

    @staticmethod
    def histogram(ctx: PipelineContext, bins: int = 30) -> Figure:
        s = GraphPlots._series(ctx)

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.hist(s.values, bins=bins)
        ax.grid(True, linestyle="--", alpha=0.4)
        _style_ax(
            ax,
            xlabel=ctx.value_col,
            ylabel="Частота",
            title="Гистограмма значений",
            rotate_x=False,
        )
        return fig

    @staticmethod
    def qq(ctx: PipelineContext) -> Figure:
        s = GraphPlots._series(ctx)

        fig = Figure(figsize=(6, 6.5), tight_layout=True)
        ax = fig.add_subplot(111)
        qqplot(s.values, line="s", ax=ax)
        _style_ax(ax, title="Q-Q plot", rotate_x=False)
        return fig

    @staticmethod
    def seasonal_profile(ctx: PipelineContext) -> Figure:
        s = GraphPlots._series(ctx)
        idx = s.index

        if ctx.freq and ("M" in ctx.freq or "Q" in ctx.freq or "Y" in ctx.freq):
            groups = idx.month
            xlabel = "Месяц"
        elif ctx.freq and "W" in ctx.freq:
            groups = idx.dayofweek
            xlabel = "День недели"
        elif ctx.freq and ("h" in ctx.freq or "min" in ctx.freq or "s" in ctx.freq):
            groups = idx.hour
            xlabel = "Час"
        else:
            groups = idx.month
            xlabel = "Месяц"

        grouped = pd.DataFrame({"x": groups, "y": s.values}).groupby("x")["y"].mean()

        fig = Figure(figsize=(9, 5.5), tight_layout=True)
        ax = fig.add_subplot(111)
        ax.plot(grouped.index, grouped.values, marker="o")
        ax.grid(True, linestyle="--", alpha=0.4)
        _style_ax(
            ax,
            xlabel=xlabel,
            ylabel=ctx.value_col,
            title="Средний сезонный профиль",
            rotate_x=False,
        )
        return fig
