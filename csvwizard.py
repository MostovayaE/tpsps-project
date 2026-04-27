from contextlib import contextmanager

from PySide6 import QtCore, QtWidgets
from design.csvwizard_ui import Ui_CSVWizard
from technical.clearing import Clearing
from technical.report_channel import ReportChannel
from context import PipelineContext
import pandas as pd

class LogBuffer:

    def __init__(self):
        self._lines: list[str] = []

    def __call__(self, msg: str):
        self._lines.append(str(msg))

    def clear(self):
        self._lines.clear()

    def text(self) -> str:
        return "\n".join(self._lines)

class WizardLogger:
    def __init__(self):
        self.buffer = LogBuffer()

    @contextmanager
    def capture_to_label(self, label: QtWidgets.QLabel, *, header: str = ""):
        self.buffer.clear()
        try:
            yield self.buffer
        finally:
            out = self.buffer.text().strip()
            if header:
                out = (header.strip() + "\n" + out).strip() if out else header.strip()
            label.setText(out)
            self.buffer.clear()

class Wizard(QtWidgets.QWizard):
    def __init__(self, df: pd.DataFrame, report: ReportChannel | None = None):
        super().__init__()
        self._freq_page_valid = None
        self._freq_page_current_freq = None
        self.ui = Ui_CSVWizard()
        self.ui.setupUi(self)

        self.df = df
        self.report = report or ReportChannel()
        self.logger = WizardLogger()
        self.clearing = Clearing(log_func=self.logger.buffer)

        self.ctx = PipelineContext(
            df=pd.DataFrame(), time_col="", value_col="", freq=""
        )

        self.time_col = ""
        self.value_col = ""
        self.dup_clearing_page_init = False
        self.align_by_freq_page_init = False
        self._dateformat_page_built = False

        for _pid in self.pageIds():
            _page = self.page(_pid)
            if _page is not None and _page.objectName() == "PageFixOutliers":
                self.removePage(_pid)
                break

        cols = [str(c) for c in df.columns]
        self.ui.comboBoxTimeCol.clear()
        self.ui.comboBoxValCol.clear()
        self.ui.comboBoxTimeCol.addItems(cols)
        self.ui.comboBoxValCol.addItems(cols)

        self.currentIdChanged.connect(self.on_page_changed)

    def on_page_changed(self, page_id: int):
        name = self.currentPage().objectName()

        if name == "PageDateFormat":
            self._init_dateformat_page()
        elif name == "PageFreq":
            self._init_freq_page()
        elif name == "PageDupClearing":
            self._init_dup_clearing_page()
        elif name == "PageAlignByFreq":
            self._init_align_by_freq_page()

    def validateCurrentPage(self) -> bool:
        name = self.currentPage().objectName()

        if name == "PageColumns":
            return self._validate_columns_page()
        if name == "PageDateFormat":
            return self._validate_dateformat_page()
        if name == "PageFreq":
            return self._validate_freq_page()

        return True

    def _validate_columns_page(self) -> bool:
        time_col = self.ui.comboBoxTimeCol.currentText().strip()
        value_col = self.ui.comboBoxValCol.currentText().strip()

        if not time_col or not value_col:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите обе колонки.")
            return False
        if time_col == value_col:
            QtWidgets.QMessageBox.warning(
                self, "Ошибка", "Колонки времени и значения должны различаться."
            )
            return False

        self.time_col = time_col
        self.value_col = value_col
        self.ctx.time_col = time_col
        self.ctx.value_col = value_col
        return True

    def _init_dateformat_page(self):
        if not self.time_col:
            self.ui.labelDateFormat.setText(
                "Сначала выберите колонку времени на предыдущем шаге."
            )
            return

        if not self._dateformat_page_built:
            self._build_dateformat_ui()
            self._dateformat_page_built = True

        raw = self.df[self.time_col].astype(str)
        samples = raw.head(6).tolist()
        self._label_raw_samples.setText("    ".join(samples))

        best_idx = 0
        best_pct = 0.0
        for i, (_label, code, _hint) in enumerate(self._DATE_PRESETS):
            if not code:
                try:
                    p = pd.to_datetime(raw, errors="coerce")
                except Exception:
                    continue
            else:
                try:
                    p = pd.to_datetime(raw, format=code, errors="coerce")
                except Exception:
                    continue
            pct = p.notna().mean() if len(p) else 0.0
            if pct > best_pct:
                best_pct = pct
                best_idx = i

        self._combo_datefmt.blockSignals(True)
        self._combo_datefmt.setCurrentIndex(best_idx)
        self._combo_datefmt.blockSignals(False)

        self._try_parse_dates()

    _DATE_PRESETS = [
        ("Авто-определение", "", ""),
        ("2023", "%Y", "Только год"),
        ("2023-06", "%Y-%m", "Год и месяц"),
        ("31.12.2023", "%d.%m.%Y", "День.Месяц.Год"),
        ("12/31/2023", "%m/%d/%Y", "Месяц/День/Год"),
        ("2023-12-31", "%Y-%m-%d", "Год-Месяц-День"),
        ("31.12.2023 14:30", "%d.%m.%Y %H:%M", "День.Месяц.Год Час:Мин"),
        ("2023-12-31 14:30:00", "%Y-%m-%d %H:%M:%S", "Год-Месяц-День Час:Мин:Сек"),
    ]

    def _build_dateformat_ui(self):
        page = self.ui.PageDateFormat

        old_layout = page.layout()
        if old_layout is not None:
            old_layout.removeWidget(self.ui.labelDateFormat)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(12, 12, 12, 12)
        vbox.setSpacing(10)

        raw_group = QtWidgets.QGroupBox("Ваши данные (первые значения колонки)")
        raw_lay = QtWidgets.QVBoxLayout(raw_group)
        self._label_raw_samples = QtWidgets.QLabel("")
        self._label_raw_samples.setWordWrap(True)
        self._label_raw_samples.setStyleSheet(
            "font-family: Consolas, monospace; padding: 4px;"
        )
        raw_lay.addWidget(self._label_raw_samples)
        vbox.addWidget(raw_group)

        fmt_group = QtWidgets.QGroupBox("Формат даты")
        fmt_lay = QtWidgets.QVBoxLayout(fmt_group)

        self._combo_datefmt = QtWidgets.QComboBox()
        for label, code, _hint in self._DATE_PRESETS:
            display = label if not _hint else f"{_hint}  —  {label}"
            self._combo_datefmt.addItem(display, code)
        self._combo_datefmt.addItem("Свой формат...", "__custom__")
        fmt_lay.addWidget(self._combo_datefmt)

        custom_frame = QtWidgets.QFrame()
        custom_lay = QtWidgets.QHBoxLayout(custom_frame)
        custom_lay.setContentsMargins(0, 0, 0, 0)
        self._edit_custom_fmt = QtWidgets.QLineEdit()
        self._edit_custom_fmt.setPlaceholderText(
            "Введите формат, например: %d/%m/%Y %H:%M"
        )
        self._edit_custom_fmt.setEnabled(False)
        self._btn_apply_custom = QtWidgets.QPushButton("Применить")
        self._btn_apply_custom.setEnabled(False)
        self._btn_apply_custom.clicked.connect(self._try_parse_dates)
        custom_lay.addWidget(self._edit_custom_fmt, stretch=1)
        custom_lay.addWidget(self._btn_apply_custom)
        fmt_lay.addWidget(custom_frame)

        hint = QtWidgets.QLabel(
            "<small>"
            "<b>%Y</b> — год (2023) &nbsp; "
            "<b>%m</b> — месяц (01–12) &nbsp; "
            "<b>%d</b> — день (01–31) &nbsp; "
            "<b>%H</b> — час &nbsp; "
            "<b>%M</b> — мин &nbsp; "
            "<b>%S</b> — сек"
            "</small>"
        )
        hint.setTextFormat(QtCore.Qt.RichText)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666;")
        fmt_lay.addWidget(hint)

        vbox.addWidget(fmt_group)

        result_group = QtWidgets.QGroupBox("Результат распознавания")
        result_lay = QtWidgets.QVBoxLayout(result_group)

        self._label_parse_status = QtWidgets.QLabel("")
        self._label_parse_status.setStyleSheet("font-weight: bold; padding: 2px;")
        result_lay.addWidget(self._label_parse_status)

        self._table_preview = QtWidgets.QTableWidget()
        self._table_preview.setColumnCount(2)
        self._table_preview.setHorizontalHeaderLabels(
            ["Исходное значение", "Распознанная дата"]
        )
        self._table_preview.horizontalHeader().setStretchLastSection(True)
        self._table_preview.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch
        )
        self._table_preview.verticalHeader().setVisible(False)
        self._table_preview.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self._table_preview.setMaximumHeight(180)
        result_lay.addWidget(self._table_preview)

        self.ui.labelDateFormat.setVisible(False)
        result_lay.addWidget(self.ui.labelDateFormat)

        vbox.addWidget(result_group)
        vbox.addStretch(1)

        self._combo_datefmt.currentIndexChanged.connect(self._on_datefmt_changed)

        if old_layout is not None:
            QtWidgets.QWidget().setLayout(old_layout)
        page.setLayout(vbox)

    def _on_datefmt_changed(self):
        is_custom = self._combo_datefmt.currentData() == "__custom__"
        self._edit_custom_fmt.setEnabled(is_custom)
        self._btn_apply_custom.setEnabled(is_custom)
        if not is_custom:
            self._try_parse_dates()

    def _get_date_format(self) -> str | None:
        data = self._combo_datefmt.currentData()
        if data == "":
            return None
        if data == "__custom__":
            custom = self._edit_custom_fmt.text().strip()
            return custom if custom else None
        return data

    def _try_parse_dates(self):
        self.ctx.df = self.df.copy()
        fmt = self._get_date_format()

        col = self.ctx.df[self.time_col]
        raw_values = col.astype(str)

        if fmt:
            parsed = pd.to_datetime(raw_values, format=fmt, errors="coerce")
            method = fmt
        else:
            parsed = pd.to_datetime(col, errors="coerce")
            method = "авто"

        self.ctx.df[self.time_col] = parsed

        n_total = len(parsed)
        n_ok = int(parsed.notna().sum())
        n_fail = n_total - n_ok
        pct = n_ok / n_total if n_total else 0.0

        if pct >= 0.95:
            color = "#2e7d32"
            icon = "OK"
        elif pct >= 0.5:
            color = "#e65100"
            icon = "!!"
        else:
            color = "#c62828"
            icon = "XX"

        status = f"{icon}  Распознано {n_ok} из {n_total} ({pct:.0%})"
        if n_fail:
            status += f"  |  Не распознано: {n_fail}"
        if method != "авто":
            status += f"  |  Формат: {method}"

        self._label_parse_status.setText(status)
        self._label_parse_status.setStyleSheet(
            f"font-weight: bold; color: {color}; padding: 2px;"
        )

        show_idx = list(range(min(5, n_total)))
        fail_idx = parsed.index[parsed.isna()].tolist()
        for fi in fail_idx[:3]:
            pos = parsed.index.get_loc(fi)
            if pos not in show_idx:
                show_idx.append(pos)
        show_idx = show_idx[:8]

        self._table_preview.setRowCount(len(show_idx))
        for row, idx in enumerate(show_idx):
            raw_item = QtWidgets.QTableWidgetItem(str(raw_values.iloc[idx]))
            self._table_preview.setItem(row, 0, raw_item)

            if pd.notna(parsed.iloc[idx]):
                result_text = str(parsed.iloc[idx])
                result_item = QtWidgets.QTableWidgetItem(result_text)
            else:
                result_item = QtWidgets.QTableWidgetItem("-- не распознано --")
                result_item.setForeground(QtWidgets.QColor("#c62828"))
            self._table_preview.setItem(row, 1, result_item)

        self.ui.labelDateFormat.setText(
            f"Метод: {method}\nРаспознано: {n_ok} из {n_total} ({pct:.0%})"
        )

    def _validate_dateformat_page(self) -> bool:
        if self.ctx.df.empty:
            return False

        parsed = self.ctx.df[self.time_col]
        ok_ratio = parsed.notna().mean() if len(parsed) else 0.0

        if ok_ratio < 0.5:
            QtWidgets.QMessageBox.warning(
                self,
                "Ошибка",
                f"Распознано только {ok_ratio:.0%} дат.\n"
                "Попробуйте выбрать другой формат.",
            )
            return False

        return True

    def _init_freq_page(self):
        cb = self.ui.comboBoxFreq
        cb.blockSignals(True)
        try:
            cb.clear()

            cb.addItem("Секунда", "s")
            cb.addItem("Минута", "min")
            cb.addItem("Час", "h")
            cb.insertSeparator(cb.count())

            cb.addItem("День", "D")
            cb.addItem("Рабочий день (пн–пт)", "B")
            cb.addItem("Неделя", "W")
            cb.insertSeparator(cb.count())

            cb.addItem("Месяц (начало месяца)", "MS")
            cb.addItem("Месяц (конец месяца)", "ME")
            cb.insertSeparator(cb.count())

            cb.addItem("Квартал (начало квартала)", "QS")
            cb.addItem("Квартал (конец квартала)", "QE")
            cb.insertSeparator(cb.count())

            cb.addItem("Год (начало года)", "YS")
            cb.addItem("Год (конец года)", "YE")

        finally:
            cb.blockSignals(False)

        self.ui.spinBoxFreq.setRange(1, 999)
        self.ui.spinBoxFreq.setValue(1)

        day_cb = self.ui.comboAnchorDay
        day_cb.clear()
        day_cb.addItem("Понедельник", "MON")
        day_cb.addItem("Вторник", "TUE")
        day_cb.addItem("Среда", "WED")
        day_cb.addItem("Четверг", "THU")
        day_cb.addItem("Пятница", "FRI")
        day_cb.addItem("Суббота", "SAT")
        day_cb.addItem("Воскресенье", "SUN")
        idx_mon = day_cb.findData("MON")
        if idx_mon >= 0:
            day_cb.setCurrentIndex(idx_mon)

        month_cb = self.ui.comboAnchorMonth
        month_cb.clear()
        month_cb.addItem("Январь", "JAN")
        month_cb.addItem("Февраль", "FEB")
        month_cb.addItem("Март", "MAR")
        month_cb.addItem("Апрель", "APR")
        month_cb.addItem("Май", "MAY")
        month_cb.addItem("Июнь", "JUN")
        month_cb.addItem("Июль", "JUL")
        month_cb.addItem("Август", "AUG")
        month_cb.addItem("Сентябрь", "SEP")
        month_cb.addItem("Октябрь", "OCT")
        month_cb.addItem("Ноябрь", "NOV")
        month_cb.addItem("Декабрь", "DEC")
        idx_dec = month_cb.findData("DEC")
        if idx_dec >= 0:
            month_cb.setCurrentIndex(idx_dec)

        self.ui.stackAnchor.setCurrentWidget(self.ui.pageAnchorNone)

        self.ui.comboBoxFreq.currentIndexChanged.connect(self.on_freq_changed)
        self.ui.spinBoxFreq.valueChanged.connect(self.on_freq_changed)
        self.ui.comboAnchorDay.currentIndexChanged.connect(self.on_freq_changed)
        self.ui.comboAnchorMonth.currentIndexChanged.connect(self.on_freq_changed)

        self.on_freq_changed()

    def on_freq_changed(self):
        base = self.ui.comboBoxFreq.currentData()
        n = int(self.ui.spinBoxFreq.value())

        if base == "W":
            self.ui.stackAnchor.setCurrentWidget(self.ui.pageAnchorDay)
            anchor = "-" + (self.ui.comboAnchorDay.currentData() or "")
        elif base in ("Q", "QS", "A", "YS"):
            self.ui.stackAnchor.setCurrentWidget(self.ui.pageAnchorMonth)
            anchor = "-" + (self.ui.comboAnchorMonth.currentData() or "")
        else:
            self.ui.stackAnchor.setCurrentWidget(self.ui.pageAnchorNone)
            anchor = ""

        freq = f"{base}{anchor}"
        if n != 1:
            freq = f"{n}{freq}"

        self.ui.labelFreqPreview.setText(f"Итоговая частота: {freq}")

        try:
            pd.tseries.frequencies.to_offset(freq)
            self.ui.labelFreqError.setText("")
            self._freq_page_current_freq = freq
            self._freq_page_valid = True
        except Exception as e:
            self.ui.labelFreqError.setText(
                f"Некорректная частота: {freq}\n{type(e).__name__}: {e}"
            )
            self._freq_page_current_freq = None
            self._freq_page_valid = False

    def _validate_freq_page(self) -> bool:
        if not getattr(self, "_freq_page_valid", False) or not getattr(
            self, "_freq_page_current_freq", None
        ):
            QtWidgets.QMessageBox.warning(
                self, "Ошибка", "Выбрана некорректная частота. Исправьте значение."
            )
            return False

        self.ctx.freq = self._freq_page_current_freq
        return True

    def _init_dup_clearing_page(self):
        if not self.dup_clearing_page_init:
            with self.logger.capture_to_label(
                self.ui.labelDupClearing, header="Очистка дублей:"
            ):
                self.ctx = self.clearing.dup_clearing(self.ctx)
            self.dup_clearing_page_init = True

            self.report.add_text(
                self.ui.labelDupClearing.text(),
                title="Очистка дубликатов",
            )
            return True
        else:
            return True

    def _init_align_by_freq_page(self):
        if not self.align_by_freq_page_init:
            with self.logger.capture_to_label(
                self.ui.labelAlignByFreq, header="Выравнивание временной сетки:"
            ):
                self.ctx = self.clearing.align_by_freq_and_log_missing(self.ctx)
            self.align_by_freq_page_init = True

            self.report.add_text(
                self.ui.labelAlignByFreq.text(),
                title="Выравнивание по частоте",
            )
            return True
        else:
            return True

    def result_context(self) -> PipelineContext:
        self.ctx = self.clearing.align_by_freq_and_log_missing(self.ctx)
        return self.ctx
