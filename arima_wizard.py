from __future__ import annotations

from PySide6 import QtWidgets

from design.arimawizard_ui import Ui_ArimaWizard


class ArimaWizard(QtWidgets.QWizard):
    def __init__(
        self,
        parent=None,
        *,
        p: int = 1,
        d: int = 1,
        q: int = 1,
        train_percent: int = 80,
    ):
        super().__init__(parent)

        self.ui = Ui_ArimaWizard()
        self.ui.setupUi(self)

        self.setWindowTitle("Ручная настройка модели ARIMA")
        self.setOption(QtWidgets.QWizard.NoBackButtonOnStartPage, True)

        page = self.page(0)
        if page is not None:
            page.setTitle("Параметры ARIMA")
            page.setSubTitle(
                "Укажите порядок AR, порядок дифференцирования, порядок MA "
                "и процент обучающей выборки."
            )

        self.ui.arimaWizardSpinBoxAR.setRange(0, 10)
        self.ui.arimaWizardSpinBoxI.setRange(0, 3)
        self.ui.arimaWizardSpinBoxMA.setRange(0, 10)
        self.ui.arimaWizardSpinBoxTrainPercent.setRange(50, 95)

        self.ui.arimaWizardSpinBoxAR.setValue(int(p))
        self.ui.arimaWizardSpinBoxI.setValue(int(d))
        self.ui.arimaWizardSpinBoxMA.setValue(int(q))
        self.ui.arimaWizardSpinBoxTrainPercent.setValue(int(train_percent))

    def validateCurrentPage(self) -> bool:
        p = self.ui.arimaWizardSpinBoxAR.value()
        d = self.ui.arimaWizardSpinBoxI.value()
        q = self.ui.arimaWizardSpinBoxMA.value()

        if p == 0 and d == 0 and q == 0:
            QtWidgets.QMessageBox.warning(
                self,
                "Некорректные параметры",
                "Нельзя одновременно задать p=0, d=0 и q=0.",
            )
            return False
        return True

    def result_params(self) -> dict:
        p = self.ui.arimaWizardSpinBoxAR.value()
        d = self.ui.arimaWizardSpinBoxI.value()
        q = self.ui.arimaWizardSpinBoxMA.value()
        train_percent = self.ui.arimaWizardSpinBoxTrainPercent.value()

        return {
            "mode": "manual",
            "p": int(p),
            "d": int(d),
            "q": int(q),
            "train_percent": int(train_percent),
            "summary": f"ARIMA({p}, {d}, {q}), train={train_percent}%",
        }
