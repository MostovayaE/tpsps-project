from NodeGraphQt import BaseNode


class StartCsvNode(BaseNode):
    __identifier__ = "pipeline.start"
    NODE_NAME = "СТАРТ: Загрузка CSV"

    def __init__(self):
        super().__init__()
        self.add_output("ctx")
        self.add_text_input("csv_path", text="")


class SimpleSeriesPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Временной ряд"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")


class ACFPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: ACF"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("lags", text="40")


class PACFPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: PACF"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("lags", text="40")


class RollingStatsPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Скользящие статистики"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("window", text="12")


class DifferencePlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Разность"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("order", text="1")


class SeasonalDifferencePlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Сезонная разность"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("seasonal_period", text="12")


class DecompositionPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Декомпозиция"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("period", text="12")
        self.add_text_input("model", text="additive")


class HistogramPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Гистограмма"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.add_text_input("bins", text="30")


class QQPlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Q-Q"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")


class SeasonalProfilePlotNode(BaseNode):
    __identifier__ = "pipeline.plot"
    NODE_NAME = "График: Сезонный профиль"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")


class ArimaModelNode(BaseNode):
    __identifier__ = "pipeline.model"
    NODE_NAME = "Модель: ARIMA"

    def __init__(self):
        super().__init__()

        self.add_input("ctx")
        self.add_output("forecast")
        self.add_output("combined")

        self.create_property("mode", "auto")
        self.create_property("p", "1")
        self.create_property("d", "1")
        self.create_property("q", "1")
        self.create_property("train_percent", "80")
        self.create_property("forecast_horizon", "12")
        self.create_property("summary", "ARIMA auto")


class SarimaModelNode(BaseNode):
    __identifier__ = "pipeline.model"
    NODE_NAME = "Модель: SARIMA"

    def __init__(self):
        super().__init__()

        self.add_input("ctx")
        self.add_output("forecast")
        self.add_output("combined")

        self.create_property("mode", "auto")
        self.create_property("p", "1")
        self.create_property("d", "1")
        self.create_property("q", "1")
        self.create_property("P", "1")
        self.create_property("D", "1")
        self.create_property("Q", "1")
        self.create_property("s", "12")
        self.create_property("train_percent", "80")
        self.create_property("forecast_horizon", "12")
        self.create_property("summary", "SARIMA auto")


class EtsModelNode(BaseNode):
    __identifier__ = "pipeline.model"
    NODE_NAME = "Модель: ETS"

    def __init__(self):
        super().__init__()

        self.add_input("ctx")
        self.add_output("forecast")
        self.add_output("combined")

        self.create_property("mode", "auto")
        self.create_property("trend", "none")
        self.create_property("seasonal", "none")
        self.create_property("season_length", "12")
        self.create_property("damped_trend", "false")
        self.create_property("train_percent", "80")
        self.create_property("forecast_horizon", "12")
        self.create_property("summary", "ETS auto")


class EnsembleModelNode(BaseNode):
    __identifier__ = "pipeline.ensemble"
    NODE_NAME = "Модель: Простой ансамбль"

    def __init__(self):
        super().__init__()

        self.add_input("ctx1")
        self.add_input("ctx2")
        self.add_input("ctx3")
        self.add_output("ctx")


class ExportCsvNode(BaseNode):
    __identifier__ = "pipeline.export"
    NODE_NAME = "Экспорт CSV"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.create_property("export_path", "")


class EnsembleByErrorsModelNode(BaseNode):
    __identifier__ = "pipeline.ensemble"
    NODE_NAME = "Модель: Ансамбль по ошибкам"

    def __init__(self):
        super().__init__()

        self.add_input("ctx1")
        self.add_input("ctx2")
        self.add_input("ctx3")
        self.add_output("ctx")

        self.create_property("metric", "mae")


class OutlierCleaningNode(BaseNode):
    __identifier__ = "pipeline.transform"
    NODE_NAME = "Очистка выбросов"

    def __init__(self):
        super().__init__()
        self.add_input("ctx")
        self.add_output("ctx")
        self.create_property("threshold", "3.5")
        self.create_property("fill_policy", "time")
        self.create_property("fill_value", "0.0")
