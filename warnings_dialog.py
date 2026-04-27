from __future__ import annotations

from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from design.warnings_ui import Ui_WarningsFrame
from graph_validator import Warning

class WarningsDialog(QtWidgets.QDialog):

    def __init__(self, warnings: List[Warning], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Проверка графа перед запуском")
        self.resize(540, 420)
        self.setMinimumSize(400, 300)

        self._warnings = warnings
        self._has_errors = any(w.severity == "error" for w in warnings)

        self._build_ui()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        n_err = sum(1 for w in self._warnings if w.severity == "error")
        n_warn = sum(1 for w in self._warnings if w.severity == "warning")

        header = QtWidgets.QLabel()
        parts = []
        if n_err:
            parts.append(f"<b style='color:#c0392b;'>Ошибок: {n_err}</b>")
        if n_warn:
            parts.append(f"<b style='color:#e67e22;'>Предупреждений: {n_warn}</b>")
        header.setText("  |  ".join(parts))
        header.setTextFormat(QtCore.Qt.RichText)
        main_layout.addWidget(header)

        frame = QtWidgets.QFrame()
        ui = Ui_WarningsFrame()
        ui.setupUi(frame)

        scroll_layout = QtWidgets.QVBoxLayout(ui.scrollAreaWidgetContents)
        scroll_layout.setContentsMargins(6, 6, 6, 6)
        scroll_layout.setSpacing(6)

        for w in self._warnings:
            card = self._make_card(w)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()

        main_layout.addWidget(frame, stretch=1)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        self._btn_run = QtWidgets.QPushButton("Всё равно запустить")
        self._btn_run.setEnabled(not self._has_errors)
        if self._has_errors:
            self._btn_run.setToolTip(
                "Невозможно запустить — исправьте ошибки (красные)."
            )
        self._btn_run.clicked.connect(self.accept)

        btn_cancel = QtWidgets.QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self._btn_run)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

    @staticmethod
    def _make_card(w: Warning) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setFrameShape(QtWidgets.QFrame.StyledPanel)

        if w.severity == "error":
            icon_text = "X"
            color = "#c0392b"
            bg = "#fdecea"
        else:
            icon_text = "!"
            color = "#e67e22"
            bg = "#fef9e7"

        card.setStyleSheet(
            f"QFrame {{ background: {bg}; border: 1px solid {color}; border-radius: 4px; }}"
        )

        layout = QtWidgets.QHBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)

        icon_label = QtWidgets.QLabel(icon_text)
        icon_label.setFixedWidth(24)
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setStyleSheet(
            f"font-weight: bold; font-size: 14px; color: {color}; border: none; background: transparent;"
        )
        layout.addWidget(icon_label)

        text_label = QtWidgets.QLabel(w.message)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(text_label, stretch=1)

        return card
