from __future__ import annotations

from PySide6 import QtWidgets

from design.sarimawizard_ui import Ui_SarimaWizard

class SarimaWizard(QtWidgets.QWizard):

    def __init__(
        self,
        parent=None,
        *,
        p: int = 1,
        d: int = 1,
        q: int = 1,
        P: int = 1,
        D: int = 1,
        Q: int = 1,
        s: int = 12,
        train_percent: int = 80,
    ):
        super().__init__(parent)

        self.ui = Ui_SarimaWizard()
        self.ui.setupUi(self)

        self.setWindowTitle("Ручная настройка модели SARIMA")
        self.setOption(QtWidgets.QWizard.NoBackButtonOnStartPage, True)

        page = self.page(0)
        if page is not None:
            page.setTitle("Параметры SARIMA")
            page.setSubTitle(
                "Укажите не сезонные параметры (p, d, q), "
                "сезонные параметры (P, D, Q, s) "
                "и долю обучающей выборки."
            )

        self.ui.sarimaWizardSpinBoxAR.setRange(0, 10)
        self.ui.sarimaWizardSpinBoxI.setRange(0, 3)
        self.ui.sarimaWizardSpinBoxMA.setRange(0, 10)

        self.ui.sarimaWizardSpinBoxTrainPercent.setRange(50, 95)

        self.ui.sarimaWizardSpinBoxP.setRange(0, 10)
        self.ui.sarimaWizardSpinBoxD.setRange(0, 2)
        self.ui.sarimaWizardSpinBoxQ.setRange(0, 10)
        self.ui.sarimaWizardSpinBoxS.setRange(2, 366)

        self.ui.sarimaWizardSpinBoxAR.setValue(int(p))
        self.ui.sarimaWizardSpinBoxI.setValue(int(d))
        self.ui.sarimaWizardSpinBoxMA.setValue(int(q))
        self.ui.sarimaWizardSpinBoxTrainPercent.setValue(int(train_percent))

        self.ui.sarimaWizardSpinBoxP.setValue(int(P))
        self.ui.sarimaWizardSpinBoxD.setValue(int(D))
        self.ui.sarimaWizardSpinBoxQ.setValue(int(Q))
        self.ui.sarimaWizardSpinBoxS.setValue(int(s))

    def validateCurrentPage(self) -> bool:
        p = self.ui.sarimaWizardSpinBoxAR.value()
        d = self.ui.sarimaWizardSpinBoxI.value()
        q = self.ui.sarimaWizardSpinBoxMA.value()

        P = self.ui.sarimaWizardSpinBoxP.value()
        D = self.ui.sarimaWizardSpinBoxD.value()
        Q = self.ui.sarimaWizardSpinBoxQ.value()
        s = self.ui.sarimaWizardSpinBoxS.value()

        train_percent = self.ui.sarimaWizardSpinBoxTrainPercent.value()

        if p == 0 and d == 0 and q == 0 and P == 0 and D == 0 and Q == 0:
            QtWidgets.QMessageBox.warning(
                self,
                "Некорректные параметры",
                "Нельзя одновременно занулить все параметры модели.",
            )
            return False

        if s < 2:
            QtWidgets.QMessageBox.warning(
                self,
                "Некорректная сезонность",
                "Длина сезона s должна быть не меньше 2.",
            )
            return False

        if train_percent < 50 or train_percent > 95:
            QtWidgets.QMessageBox.warning(
                self,
                "Некорректное разделение выборки",
                "Процент обучающей выборки должен быть в диапазоне 50–95.",
            )
            return False

        return True

    def result_params(self) -> dict:
        p = self.ui.sarimaWizardSpinBoxAR.value()
        d = self.ui.sarimaWizardSpinBoxI.value()
        q = self.ui.sarimaWizardSpinBoxMA.value()

        P = self.ui.sarimaWizardSpinBoxP.value()
        D = self.ui.sarimaWizardSpinBoxD.value()
        Q = self.ui.sarimaWizardSpinBoxQ.value()
        s = self.ui.sarimaWizardSpinBoxS.value()

        train_percent = self.ui.sarimaWizardSpinBoxTrainPercent.value()

        return {
            "mode": "manual",
            "p": int(p),
            "d": int(d),
            "q": int(q),
            "P": int(P),
            "D": int(D),
            "Q": int(Q),
            "s": int(s),
            "train_percent": int(train_percent),
            "summary": f"SARIMA({p}, {d}, {q})x({P}, {D}, {Q}, {s}), train={train_percent}%",
        }
