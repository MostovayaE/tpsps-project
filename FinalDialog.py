from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from design.final_dialog_ui import Ui_FinalDialog
from technical.report_channel import (
    ReportDocument,
    ReportFigureItem,
    ReportTableItem,
    ReportTextItem,
)
from technical.reportlab_pdf_exporter import ReportLabPdfExporter


class ScrollableFigureCanvas(FigureCanvasQTAgg):
    def wheelEvent(self, event: QtGui.QWheelEvent):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QtWidgets.QAbstractScrollArea):
                sb = parent.verticalScrollBar()
                step = sb.singleStep() or 20
                delta = event.angleDelta().y()
                sb.setValue(sb.value() - (delta // 120) * step)
                event.accept()
                return
            parent = parent.parent()
        super().wheelEvent(event)


class FinalDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_FinalDialog()
        self.ui.setupUi(self)

        self.setWindowTitle("Результаты пайплайна")
        self.resize(900, 750)
        self.setModal(False)

        self.ui.scrollArea.setWidgetResizable(True)
        contents = self.ui.scrollAreaWidgetContents

        layout = contents.layout()
        if layout is None:
            layout = QtWidgets.QVBoxLayout(contents)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        self._content_layout = layout
        self._content_layout.addStretch(1)

        self._document = ReportDocument()
        self._pdf_exporter = ReportLabPdfExporter()

        root_layout = self.layout()
        root_layout.removeWidget(self.ui.scrollArea)

        wrapper = QtWidgets.QVBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)
        wrapper.addWidget(self.ui.scrollArea, stretch=1)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch(1)

        self._btn_export = QtWidgets.QPushButton("📄 Экспорт в PDF")
        self._btn_export.setFixedHeight(36)
        self._btn_export.setMinimumWidth(180)
        self._btn_export.clicked.connect(self._export_pdf)
        btn_row.addWidget(self._btn_export)

        wrapper.addLayout(btn_row)
        root_layout.addLayout(wrapper)

    def closeEvent(self, event: QtGui.QCloseEvent):
        self.hide()
        event.ignore()

    @property
    def document(self) -> ReportDocument:
        return self._document

    def set_document(self, document: ReportDocument) -> None:
        self._document = document
        self._rebuild_ui()

    def clear(self) -> None:
        self._document = ReportDocument(
            title=self._document.title, subtitle=self._document.subtitle
        )
        self._clear_ui()

    def add_text(self, text: str, *, title: str | None = None) -> None:
        item = ReportTextItem(title=title, text=text)
        self._document.items.append(item)
        self._append_text_item(item)

    def add_figure(
        self,
        fig: Figure,
        *,
        title: str | None = None,
        caption: str | None = None,
    ) -> None:
        item = ReportFigureItem(title=title, figure=fig, caption=caption)
        self._document.items.append(item)
        self._append_figure_item(item)

    def add_table(self, headers, rows, *, title=None) -> None:
        item = ReportTableItem(
            title=title,
            headers=[str(h) for h in headers],
            rows=[[str(v) for v in row] for row in rows],
        )
        self._document.items.append(item)
        self._append_table_item(item)

    def _clear_ui(self) -> None:
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _rebuild_ui(self) -> None:
        self._clear_ui()
        for item in self._document.items:
            if isinstance(item, ReportTextItem):
                self._append_text_item(item)
            elif isinstance(item, ReportTableItem):
                self._append_table_item(item)
            elif isinstance(item, ReportFigureItem):
                self._append_figure_item(item)

    def _insert_block_widget(
        self,
        widget: QtWidgets.QWidget,
        *,
        title: str | None = None,
    ) -> None:
        if title:
            box = QtWidgets.QGroupBox(title)
            box_layout = QtWidgets.QVBoxLayout(box)
            box_layout.setContentsMargins(10, 10, 10, 10)
            box_layout.addWidget(widget)
            self._content_layout.insertWidget(self._content_layout.count() - 1, box)
        else:
            self._content_layout.insertWidget(self._content_layout.count() - 1, widget)

    def _append_text_item(self, item: ReportTextItem) -> None:
        browser = QtWidgets.QTextBrowser()
        browser.setPlainText(item.text)
        browser.setReadOnly(True)
        browser.setOpenExternalLinks(False)
        browser.setMinimumHeight(160)
        browser.setFrameShape(QtWidgets.QFrame.NoFrame)
        browser.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)
        browser.setStyleSheet(
            "QTextBrowser {"
            "  font-family: Consolas, 'Courier New', monospace;"
            "  font-size: 12pt;"
            "  background: transparent;"
            "}"
        )
        self._insert_block_widget(browser, title=item.title)

    def _append_table_item(self, item: ReportTableItem) -> None:
        table = QtWidgets.QTableWidget()
        table.setRowCount(len(item.rows))
        table.setColumnCount(len(item.headers))
        table.setHorizontalHeaderLabels(item.headers)

        for i, row in enumerate(item.rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))

        table.resizeColumnsToContents()
        table.setMinimumHeight(min(80 + len(item.rows) * 34, 500))
        table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)

        self._insert_block_widget(table, title=item.title)

    def _append_figure_item(self, item: ReportFigureItem) -> None:
        wrapper = QtWidgets.QWidget()
        wrapper_layout = QtWidgets.QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(8)

        canvas = ScrollableFigureCanvas(item.figure)
        canvas.setMinimumHeight(320)
        wrapper_layout.addWidget(canvas)

        if item.caption:
            caption = QtWidgets.QLabel(item.caption)
            caption.setWordWrap(True)
            caption.setStyleSheet(
                "QLabel { color: #4B5563; font-size: 10pt; padding-top: 2px; }"
            )
            wrapper_layout.addWidget(caption)

        self._insert_block_widget(wrapper, title=item.title)

    def _export_pdf(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт как PDF",
            "report.pdf",
            "PDF файлы (*.pdf)",
        )
        if not path:
            return

        try:
            self._pdf_exporter.export(self._document, path)
        except ModuleNotFoundError as exc:
            if exc.name == "reportlab":
                QtWidgets.QMessageBox.warning(
                    self,
                    "ReportLab не найден",
                    "Для экспорта в PDF требуется пакет reportlab.\n\n"
                    "Установи его в окружение проекта:\n"
                    "pip install reportlab",
                )
                return
            raise
        except Exception as exc:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка экспорта", f"Не удалось сохранить PDF:\n{exc}"
            )
            return

        QtWidgets.QMessageBox.information(self, "Экспорт", f"Отчёт сохранён:\n{path}")
