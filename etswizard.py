from __future__ import annotations

from PySide6 import QtWidgets
from PySide6.QtWidgets import QComboBox, QLabel

from design.etswizard_ui import Ui_EtsWizard

_TREND_VALUES = [None, "add", "mul"]
_SEASON_VALUES = [None, "add", "mul"]


class EtsWizard(QtWidgets.QWizard):
    def __init__(
        self,
        parent=None,
        *,
        mode: str = "auto",
        trend: str = "none",
        seasonal: str = "none",
        season_length: int = 12,
        damped_trend: bool = False,
        train_percent: int = 80,
    ):
        super().__init__(parent)

        self.ui = Ui_EtsWizard()
        self.ui.setupUi(self)

        self.setWindowTitle("Настройка ETS")
        self.setOption(QtWidgets.QWizard.NoBackButtonOnStartPage, True)

        page = self.page(0)
        if page is not None:
            page.setTitle("Параметры ETS")
            page.setSubTitle(
                "Выберите режим настройки. В режиме «Авто» параметры тренда и "
                "сезонности подбираются автоматически по AIC."
            )

        self._mode_label = QLabel("Режим")
        self.ui.verticalLayout.insertWidget(0, self._mode_label)

        self._mode_combo = QComboBox()
        self._mode_combo.addItem("Авто")
        self._mode_combo.addItem("Ручной")
        self.ui.verticalLayout_2.insertWidget(0, self._mode_combo)

        self.ui.etsWizardSpinBoxSeasonLength.setRange(2, 366)
        self.ui.etsWizardSpinBoxTestSplit.setRange(50, 95)

        trend_idx = {"none": 0, "add": 1, "mul": 2}.get(trend, 0)
        self.ui.etsWizardComboBoxTrendType.setCurrentIndex(trend_idx)

        seasonal_idx = {"none": 0, "add": 1, "mul": 2}.get(seasonal, 0)
        self.ui.etsWizardComboBoxSeasonType.setCurrentIndex(seasonal_idx)

        self.ui.etsWizardSpinBoxSeasonLength.setValue(int(season_length))
        self.ui.etsWizardFadingTrendCheckBox.setChecked(bool(damped_trend))
        self.ui.etsWizardSpinBoxTestSplit.setValue(int(train_percent))

        mode_idx = 1 if mode == "manual" else 0
        self._mode_combo.setCurrentIndex(mode_idx)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self._on_mode_changed(mode_idx)

    def _on_mode_changed(self, index: int) -> None:
        is_manual = index == 1
        self.ui.etsWizardComboBoxTrendType.setEnabled(is_manual)
        self.ui.etsWizardComboBoxSeasonType.setEnabled(is_manual)
        self.ui.etsWizardSpinBoxSeasonLength.setEnabled(is_manual)
        self.ui.etsWizardFadingTrendCheckBox.setEnabled(is_manual)

    def _trend_value(self) -> str | None:
        return _TREND_VALUES[self.ui.etsWizardComboBoxTrendType.currentIndex()]

    def _seasonal_value(self) -> str | None:
        return _SEASON_VALUES[self.ui.etsWizardComboBoxSeasonType.currentIndex()]

    def validateCurrentPage(self) -> bool:
        if self._mode_combo.currentIndex() == 0:
            return True

        trend = self._trend_value()
        damped = self.ui.etsWizardFadingTrendCheckBox.isChecked()

        if damped and trend is None:
            QtWidgets.QMessageBox.warning(
                self,
                "Некорректные параметры",
                "Затухающий тренд применим только при наличии тренда "
                "(Аддитивный или Мультипликативный).",
            )
            return False

        return True

    def result_params(self) -> dict:
        is_auto = self._mode_combo.currentIndex() == 0
        train_percent = self.ui.etsWizardSpinBoxTestSplit.value()
        season_length = self.ui.etsWizardSpinBoxSeasonLength.value()

        if is_auto:
            return {
                "mode": "auto",
                "trend": "none",
                "seasonal": "none",
                "season_length": season_length,
                "damped_trend": False,
                "train_percent": train_percent,
                "summary": f"ETS auto, train={train_percent}%",
            }

        trend = self._trend_value()
        seasonal = self._seasonal_value()
        damped = self.ui.etsWizardFadingTrendCheckBox.isChecked()

        trend_str = "none" if trend is None else trend
        seasonal_str = "none" if seasonal is None else seasonal

        summary = (
            f"ETS(trend={trend_str}, seasonal={seasonal_str}, "
            f"s={season_length}, damped={damped}), train={train_percent}%"
        )

        return {
            "mode": "manual",
            "trend": trend_str,
            "seasonal": seasonal_str,
            "season_length": season_length,
            "damped_trend": damped,
            "train_percent": train_percent,
            "summary": summary,
        }
