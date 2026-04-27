from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Callable, Optional, Literal

from context import PipelineContext

FillPolicy = Literal["none", "time", "ffill", "bfill", "const"]

class Clearing:
    def __init__(self, log_func: Optional[Callable[[str], None]] = None):
        self.log = log_func or (lambda msg: print(msg))

    @staticmethod
    def normalize_freq(freq: Optional[str]) -> Optional[str]:
        if not freq:
            return freq

        f = str(freq).strip()

        repl = {
            "BAS": "BYS",
            "BMS": "BMS",
            "BM": "BME",
            "BA": "BYE",
            "AS": "YS",
            "A": "YE",
            "Y": "YE",
            "Q": "QE",
            "M": "ME",
            "H": "h",
            "T": "min",
            "S": "s",
            "L": "ms",
            "U": "us",
            "N": "ns",
        }

        parts = f.split("-", 1)
        head = parts[0]
        tail = "-" + parts[1] if len(parts) == 2 else ""

        for old, new in repl.items():
            if head == old:
                head = new
                break
            elif head.endswith(old) and head[: -len(old)].isdigit():
                head = head[: -len(old)] + new
                break

        return head + tail

    def dup_clearing(self, ctx: PipelineContext) -> PipelineContext:
        if ctx is None or ctx.df is None or ctx.df.empty:
            self.log("dup_clearing: нет данных.")
            return ctx

        time_col = ctx.time_col
        value_col = ctx.value_col

        if not time_col or not value_col:
            raise ValueError("dup_clearing: в ctx не заданы time_col/value_col.")

        df = ctx.df.copy()

        if time_col not in df.columns:
            raise ValueError(f"dup_clearing: колонка времени '{time_col}' не найдена.")
        if value_col not in df.columns:
            raise ValueError(
                f"dup_clearing: колонка значения '{value_col}' не найдена."
            )

        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

        before_rows = len(df)
        df = df.dropna(subset=[time_col])
        removed_bad_time = before_rows - len(df)
        if removed_bad_time > 0:
            self.log(
                f"dup_clearing: удалено строк с некорректным временем: {removed_bad_time}"
            )

        dup_info = df.groupby(time_col)[value_col].agg(count="count", mean="mean")
        dup_info = dup_info[dup_info["count"] > 1]

        if dup_info.empty:
            self.log("dup_clearing: дубликатов по времени не обнаружено.")
            df = df.sort_values(time_col).reset_index(drop=True)
            return PipelineContext(
                df=df, freq=ctx.freq, time_col=time_col, value_col=value_col
            )

        self.log(
            "dup_clearing: найдены дубликаты по времени (будут схлопнуты в среднее значение)."
        )
        self.log(dup_info.reset_index().head(20).to_string(index=False))
        if len(dup_info) > 20:
            self.log("... (показаны первые 20)")

        before_rows = len(df)
        df_collapsed = (
            df.groupby(time_col, as_index=False)[value_col]
            .mean()
            .sort_values(time_col)
            .reset_index(drop=True)
        )
        after_rows = len(df_collapsed)

        self.log(
            f"dup_clearing: схлопнули дубли: было строк {before_rows}, стало {after_rows}."
        )
        self.log("")

        return PipelineContext(
            df=df_collapsed, freq=ctx.freq, time_col=time_col, value_col=value_col
        )

    def align_by_freq_and_log_missing(
        self,
        ctx: PipelineContext,
        *,
        fill_policy: FillPolicy = "time",
        fill_edges: bool = True,
        fill_value: Optional[float] = None,
        preview_limit: int = 10,
    ) -> PipelineContext:
        if ctx is None or ctx.df is None or ctx.df.empty:
            self.log("align_by_freq: нет данных.")
            return ctx

        if not ctx.time_col or not ctx.value_col:
            raise ValueError("align_by_freq: в ctx не заданы time_col/value_col.")

        if not ctx.freq:
            self.log("align_by_freq: ctx.freq не задан — выравнивание не выполняется.")
            return ctx

        time_col = ctx.time_col
        value_col = ctx.value_col
        freq = (
            self.normalize_freq(ctx.freq)
            if hasattr(self, "normalize_freq")
            else str(ctx.freq)
        )

        df_work = ctx.df.copy()

        if time_col not in df_work.columns:
            raise ValueError(f"align_by_freq: колонка времени '{time_col}' не найдена.")
        if value_col not in df_work.columns:
            raise ValueError(
                f"align_by_freq: колонка значения '{value_col}' не найдена."
            )

        try:
            pd.tseries.frequencies.to_offset(freq)
        except Exception as e:
            raise ValueError(
                f"align_by_freq: некорректная частота '{freq}': {e}"
            ) from e

        df_work[time_col] = pd.to_datetime(df_work[time_col], errors="coerce")
        before_rows = len(df_work)
        df_work = df_work.dropna(subset=[time_col])
        removed = before_rows - len(df_work)
        if removed:
            self.log(f"align_by_freq: удалено строк с некорректным временем: {removed}")

        df_work = df_work.sort_values(time_col).set_index(time_col)
        times = df_work.index

        if times.empty:
            self.log(
                "align_by_freq: после приведения времени не осталось валидных точек."
            )
            empty_df = pd.DataFrame(columns=[time_col, value_col])
            return PipelineContext(
                df=empty_df, freq=freq, time_col=time_col, value_col=value_col
            )

        self.log(f"align_by_freq: используем частоту для выравнивания: {freq}.")

        start = times.min()
        end = times.max()
        full_index = pd.date_range(start=start, end=end, freq=freq)

        missing = full_index.difference(times)
        if missing.empty:
            self.log("align_by_freq: пропусков по времени не обнаружено.")
        else:
            n_missing = len(missing)
            self.log(
                f"align_by_freq: найдено {n_missing} пропусков во временной шкале."
            )
            preview = missing[:preview_limit]
            lines = "\n".join(str(ts) for ts in preview)
            self.log(
                "Пропущенные метки (preview):\n"
                + lines
                + ("\n..." if n_missing > preview_limit else "")
            )

        df_regular = df_work.reindex(full_index)

        nan_before_fill = int(df_regular[value_col].isna().sum())
        self.log(f"align_by_freq: NaN после reindex (до заполнения): {nan_before_fill}")

        s = df_regular[value_col]

        if fill_policy == "none":
            self.log("align_by_freq: fill_policy=none — NaN оставлены как есть.")
        elif fill_policy == "time":
            s_filled = s.interpolate(method="time")
            if fill_edges:
                s_filled = s_filled.ffill().bfill()
            df_regular[value_col] = s_filled
            self.log(
                f"align_by_freq: заполнение NaN интерполяцией по времени (edges={'on' if fill_edges else 'off'})."
            )
        elif fill_policy == "ffill":
            df_regular[value_col] = s.ffill()
            self.log("align_by_freq: заполнение NaN ffill().")
        elif fill_policy == "bfill":
            df_regular[value_col] = s.bfill()
            self.log("align_by_freq: заполнение NaN bfill().")
        elif fill_policy == "const":
            if fill_value is None:
                raise ValueError(
                    "align_by_freq: fill_policy='const' требует fill_value."
                )
            df_regular[value_col] = s.fillna(fill_value)
            self.log(f"align_by_freq: заполнение NaN константой {fill_value}.")
        else:
            raise ValueError(f"align_by_freq: неизвестный fill_policy='{fill_policy}'")

        nan_after_fill = int(df_regular[value_col].isna().sum())
        self.log(f"align_by_freq: NaN после заполнения: {nan_after_fill}")

        if fill_policy != "none" and nan_before_fill > 0:
            before_mask = df_regular.index.isin(full_index)
            missing_mask = df_regular.index.isin(missing)

            filled_now = missing_mask & df_regular[value_col].notna()
            filled_cnt = int(filled_now.sum())
            self.log(f"align_by_freq: заполнено пропусков по времени: {filled_cnt}")

            if filled_cnt:
                ex_idx = df_regular.index[filled_now][:preview_limit]
                lines = [f"{t} : NaN → {df_regular.at[t, value_col]}" for t in ex_idx]
                self.log(
                    "Примеры заполненных пропусков:\n"
                    + "\n".join(lines)
                    + ("\\n..." if filled_cnt > preview_limit else "")
                )

        self.log("")

        out_df = df_regular.reset_index().rename(columns={"index": time_col})

        return PipelineContext(
            df=out_df, freq=freq, time_col=time_col, value_col=value_col
        )

    def detect_target_freq(self, times: pd.DatetimeIndex) -> Optional[str]:
        times = pd.DatetimeIndex(times).sort_values().unique()
        if len(times) < 3:
            self.log(
                "detect_target_freq: слишком мало точек для определения частоты (нужно ≥ 3)."
            )
            return None

        inferred = pd.infer_freq(times)
        if inferred is not None:
            inferred = self.normalize_freq(inferred)
            self.log(
                f"detect_target_freq: pd.infer_freq определил частоту: {inferred}."
            )
            return inferred

        self.log(
            "detect_target_freq: pd.infer_freq не смог однозначно определить частоту. Пробуем паттерны и дельты."
        )

        years = times.to_period("Y")
        max_per_year = years.value_counts().max()

        md = pd.Series(list(zip(times.month, times.day)))
        md_mode = md.mode().iloc[0]
        md_share = (md == md_mode).mean()
        md_month, md_day = md_mode
        unique_months = pd.Series(times.month).nunique()

        if max_per_year == 1 and md_share >= 0.8 and unique_months == 1:
            self.log(
                f"detect_target_freq: годовой паттерн на {md_day:02d}.{md_month:02d}."
            )
            if md_month == 1 and md_day == 1:
                return "YS"
            else:
                return "YE"

        months = times.to_period("M")
        max_per_month = months.value_counts().max()

        days = pd.Series(times.day)
        day_mode = days.mode().iloc[0]
        share_day_mode = (days == day_mode).mean()
        months_nunique = pd.Series(times.month).nunique()

        if max_per_month == 1 and share_day_mode >= 0.8 and months_nunique >= 6:
            self.log(f"detect_target_freq: месячный паттерн на {day_mode}-е число.")
            if day_mode == 1:
                return "MS"
            else:
                return "ME"

        deltas = times.to_series().diff().dropna()
        if deltas.empty:
            self.log("detect_target_freq: не удалось вычислить дельты.")
            return None

        delta_counts = deltas.value_counts()
        main_delta = delta_counts.index[0]
        share_delta = float(delta_counts.iloc[0]) / float(len(deltas))

        self.log(
            f"detect_target_freq: самая частая дельта: {main_delta} ({share_delta:.1%})."
        )

        if share_delta >= 0.7:
            days = main_delta / pd.Timedelta(days=1)
            if 320 <= days <= 400:
                return "YS"
            return main_delta

        self.log("detect_target_freq: надёжно определить частоту не удалось.")
        return None

    @staticmethod
    def _fill_series(s: pd.Series, fill_policy: str, fill_value: float) -> pd.Series:
        if fill_policy == "none":
            return s
        elif fill_policy == "time":
            return s.interpolate(method="time").ffill().bfill()
        elif fill_policy == "ffill":
            return s.ffill().bfill()
        elif fill_policy == "bfill":
            return s.bfill().ffill()
        elif fill_policy == "const":
            return s.fillna(fill_value)
        return s.interpolate(method="time").ffill().bfill()

    def detect_and_fix_outliers(
        self,
        ctx: PipelineContext,
        threshold: float = 3.5,
        fill_policy: str = "time",
        fill_value: float = 0.0,
    ) -> PipelineContext:
        if ctx is None or ctx.df is None or ctx.df.empty:
            self.log("detect_and_fix_outliers: нет данных.")
            return ctx

        time_col = ctx.time_col
        value_col = ctx.value_col
        freq = self.normalize_freq(ctx.freq)

        df = ctx.df.copy()

        if time_col not in df.columns:
            raise ValueError(
                f"detect_and_fix_outliers: колонка времени '{time_col}' не найдена."
            )
        if value_col not in df.columns:
            raise ValueError(
                f"detect_and_fix_outliers: колонка значения '{value_col}' не найдена."
            )

        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
        before = len(df)
        df = df.dropna(subset=[time_col])
        removed = before - len(df)
        if removed:
            self.log(
                f"detect_and_fix_outliers: удалено строк с некорректным временем: {removed}"
            )

        df = df.sort_values(time_col).set_index(time_col)

        s_orig = pd.to_numeric(df[value_col], errors="coerce")

        n_points = int(s_orig.notna().sum())
        if n_points < 5:
            self.log(
                f"detect_and_fix_outliers: недостаточно данных для выбросов (не-NaN точек: {n_points})."
            )

            s_filled = self._fill_series(s_orig, fill_policy, fill_value)
            df[value_col] = s_filled

            nan_after = int(pd.isna(s_filled).sum())
            self.log(f"detect_and_fix_outliers: NaN после fill = {nan_after}.")
            return PipelineContext(
                df=df.reset_index(), freq=freq, time_col=time_col, value_col=value_col
            )

        window = self._choose_outlier_window(freq, n_points)
        window = max(3, min(window, n_points))
        min_periods = max(3, window // 2)

        self.log(
            f"detect_and_fix_outliers: rolling median+MAD "
            f"(freq={freq}, window={window}, min_periods={min_periods}, threshold={threshold})"
        )

        median = s_orig.rolling(
            window=window, center=True, min_periods=min_periods
        ).median()
        abs_dev = (s_orig - median).abs()
        mad = abs_dev.rolling(
            window=window, center=True, min_periods=min_periods
        ).median()

        mad_scaled = mad * 1.4826
        mad_scaled_safe = mad_scaled.where(mad_scaled != 0, np.nan)
        deviation_score = abs_dev / (mad_scaled_safe + 1e-12)

        outliers_mask = (deviation_score > threshold) & s_orig.notna()
        n_outliers = int(outliers_mask.sum())

        if n_outliers == 0:
            self.log(
                f"detect_and_fix_outliers: выбросов не найдено. Заполняем пропуски (policy={fill_policy})."
            )
            s_filled = self._fill_series(s_orig, fill_policy, fill_value)
            df[value_col] = s_filled
            nan_after = int(pd.isna(s_filled).sum())
            self.log(f"detect_and_fix_outliers: NaN после fill = {nan_after}.")
            return PipelineContext(
                df=df.reset_index(), freq=freq, time_col=time_col, value_col=value_col
            )

        self.log(f"detect_and_fix_outliers: найдено выбросов: {n_outliers}.")

        preview_limit = 10
        outliers_idx = deviation_score.index[outliers_mask]
        self.log(f"Примеры выбросов (первые {min(preview_limit, n_outliers)}):")
        lines = []
        for t in outliers_idx[:preview_limit]:
            lines.append(
                f"{t} : value={s_orig.loc[t]} score={deviation_score.loc[t]:.2f}"
            )
        self.log("\n".join(lines))
        if n_outliers > preview_limit:
            self.log("...")

        s_clean = s_orig.copy()
        s_clean[outliers_mask] = np.nan

        s_filled = self._fill_series(s_clean, fill_policy, fill_value)

        nan_before = int(pd.isna(s_orig).sum())
        nan_after = int(pd.isna(s_filled).sum())
        self.log(
            f"detect_and_fix_outliers: NaN было={nan_before}, стало={nan_after} (fill_policy={fill_policy})."
        )

        self.log(
            f"Примеры заменённых значений (первые {min(preview_limit, n_outliers)}):"
        )
        lines = []
        for t in outliers_idx[:preview_limit]:
            lines.append(f"{t} : {s_orig.loc[t]} → {s_filled.loc[t]}")
        self.log("\n".join(lines))
        if n_outliers > preview_limit:
            self.log("...")

        df[value_col] = s_filled
        self.log(f"detect_and_fix_outliers: исправлено значений: {n_outliers}.")
        self.log("")

        return PipelineContext(
            df=df.reset_index(), freq=freq, time_col=time_col, value_col=value_col
        )

    def _choose_outlier_window(self, freq, n_points: int) -> int:
        default_window = max(3, min(25, n_points // 10 or 3))

        if freq is None or n_points < 10:
            return default_window

        if isinstance(freq, pd.Timedelta):
            total_sec = freq.total_seconds()
            day_sec = 24 * 3600
            if total_sec <= 0:
                return default_window
            if total_sec < day_sec:
                steps_per_day = int(round(day_sec / total_sec))
                return max(3, min(steps_per_day, n_points // 5 or steps_per_day))
            if day_sec < total_sec <= 31 * day_sec:
                steps_per_month = int(round(30 * day_sec / total_sec))
                return max(3, min(steps_per_month, n_points // 3 or steps_per_month))
            return default_window

        if isinstance(freq, str):
            f = self.normalize_freq(freq)

            if (
                "min" in f
                or f.endswith("s")
                or f.endswith("ms")
                or f.endswith("us")
                or f.endswith("ns")
                or f.endswith("h")
            ):
                return min(24, max(3, n_points // 50 or 3))
            if f.startswith("W"):
                return min(8, max(3, n_points // 10 or 3))
            if f.endswith("D"):
                return max(7, min(31, n_points // 2))
            if "MS" in f or "ME" in f:
                return min(12, n_points)
            if "QS" in f or "QE" in f:
                return min(4, n_points)
            if "YS" in f or "YE" in f:
                return min(5, n_points)

            return default_window

        return default_window
