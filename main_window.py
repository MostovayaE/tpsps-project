from __future__ import annotations

import logging

from PySide6 import QtCore, QtGui, QtWidgets

_logger = logging.getLogger(__name__)
from NodeGraphQt import NodeGraph
from NodeGraphQt.constants import ViewerEnum

from design.design import Ui_MainWindow
from loading_dialog import LoadingDialog
from nodes import (
    StartCsvNode,
    SimpleSeriesPlotNode,
    ACFPlotNode,
    PACFPlotNode,
    RollingStatsPlotNode,
    DifferencePlotNode,
    SeasonalDifferencePlotNode,
    DecompositionPlotNode,
    HistogramPlotNode,
    QQPlotNode,
    SeasonalProfilePlotNode,
    ArimaModelNode,
    SarimaModelNode,
    EtsModelNode,
    EnsembleModelNode,
    EnsembleByErrorsModelNode,
    OutlierCleaningNode,
    ExportCsvNode,
)
from FinalDialog import FinalDialog
from graph_validator import validate_graph
from warnings_dialog import WarningsDialog
from technical.report_channel import ReportChannel

class _GraphRunThread(QtCore.QThread):

    error_occurred = QtCore.Signal(str)
    ready_for_loading = QtCore.Signal()
    _request_wizard = QtCore.Signal(object, object)

    def __init__(self, graph, report, parent=None):
        super().__init__(parent)
        self._graph = graph
        self._report = report
        self._wizard_result = None

        self._request_wizard.connect(
            self._open_wizard_on_main_thread,
            QtCore.Qt.BlockingQueuedConnection,
        )

    @QtCore.Slot(object, object)
    def _open_wizard_on_main_thread(self, df, report):
        from csvwizard import Wizard

        w = Wizard(df, report=report)
        if w.exec() == QtWidgets.QDialog.Accepted:
            self._wizard_result = w.result_context()
        else:
            self._wizard_result = None

    def _wizard_opener(self, df, report):
        self._wizard_result = None
        self._request_wizard.emit(df, report)
        self.ready_for_loading.emit()
        return self._wizard_result

    def run(self):
        from runner import GraphRunner

        self._report.enable_buffering()
        self._report.wizard_opener = self._wizard_opener
        try:
            GraphRunner(self._graph, report=self._report).run_all()
        except Exception as exc:
            self.error_occurred.emit(str(exc))

NODE_CATALOG = [
    ("График: Временной ряд", "pipeline.plot.SimpleSeriesPlotNode", "Графики"),
    ("График: ACF", "pipeline.plot.ACFPlotNode", "Графики"),
    ("График: PACF", "pipeline.plot.PACFPlotNode", "Графики"),
    ("График: Скользящие статистики", "pipeline.plot.RollingStatsPlotNode", "Графики"),
    ("График: Разность", "pipeline.plot.DifferencePlotNode", "Графики"),
    (
        "График: Сезонная разность",
        "pipeline.plot.SeasonalDifferencePlotNode",
        "Графики",
    ),
    ("График: Декомпозиция", "pipeline.plot.DecompositionPlotNode", "Графики"),
    ("График: Гистограмма", "pipeline.plot.HistogramPlotNode", "Графики"),
    ("График: Q-Q", "pipeline.plot.QQPlotNode", "Графики"),
    ("График: Сезонный профиль", "pipeline.plot.SeasonalProfilePlotNode", "Графики"),
    ("Очистка выбросов", "pipeline.transform.OutlierCleaningNode", "Очистка"),
    ("Модель: ARIMA", "pipeline.model.ArimaModelNode", "Модели"),
    ("Модель: SARIMA", "pipeline.model.SarimaModelNode", "Модели"),
    ("Модель: ETS", "pipeline.model.EtsModelNode", "Модели"),
    ("Простой ансамбль", "pipeline.ensemble.EnsembleModelNode", "Ансамбль"),
    ("Ансамбль по ошибкам", "pipeline.ensemble.EnsembleByErrorsModelNode", "Ансамбль"),
    ("Экспорт CSV", "pipeline.export.ExportCsvNode", "Экспорт"),
]

NODE_FIELDS = {
    "pipeline.start.StartCsvNode": [
        {"name": "csv_path", "label": "Путь к CSV", "type": "file"},
    ],
    "pipeline.plot.ACFPlotNode": [
        {
            "name": "lags",
            "label": "Количество лагов",
            "type": "int",
            "default": 40,
            "min": 1,
            "max": 500,
        },
    ],
    "pipeline.plot.PACFPlotNode": [
        {
            "name": "lags",
            "label": "Количество лагов",
            "type": "int",
            "default": 40,
            "min": 1,
            "max": 500,
        },
    ],
    "pipeline.plot.RollingStatsPlotNode": [
        {
            "name": "window",
            "label": "Окно",
            "type": "int",
            "default": 12,
            "min": 1,
            "max": 500,
        },
    ],
    "pipeline.plot.DifferencePlotNode": [
        {
            "name": "order",
            "label": "Порядок разности",
            "type": "int",
            "default": 1,
            "min": 1,
            "max": 10,
        },
    ],
    "pipeline.plot.SeasonalDifferencePlotNode": [
        {
            "name": "seasonal_period",
            "label": "Сезонный период",
            "type": "int",
            "default": 12,
            "min": 1,
            "max": 500,
        },
    ],
    "pipeline.plot.DecompositionPlotNode": [
        {
            "name": "period",
            "label": "Период",
            "type": "int",
            "default": 12,
            "min": 1,
            "max": 500,
        },
        {
            "name": "model",
            "label": "Модель",
            "type": "choice",
            "choices": ["additive", "multiplicative"],
            "default": "additive",
        },
    ],
    "pipeline.plot.HistogramPlotNode": [
        {
            "name": "bins",
            "label": "Количество bins",
            "type": "int",
            "default": 30,
            "min": 2,
            "max": 500,
        },
    ],
    "pipeline.plot.SimpleSeriesPlotNode": [],
    "pipeline.plot.QQPlotNode": [],
    "pipeline.plot.SeasonalProfilePlotNode": [],
    "pipeline.ensemble.EnsembleModelNode": [],
    "pipeline.export.ExportCsvNode": [
        {"name": "export_path", "label": "Путь выгрузки", "type": "save_file"},
    ],
    "pipeline.ensemble.EnsembleByErrorsModelNode": [
        {
            "name": "metric",
            "label": "Метрика ошибки",
            "type": "choice",
            "choices": [("MAE", "mae"), ("MAPE", "mape"), ("RMSE", "rmse")],
            "default": "mae",
        },
    ],
    "pipeline.model.ArimaModelNode": [
        {
            "name": "mode",
            "label": "Режим настройки",
            "type": "choice",
            "choices": [("Авто", "auto"), ("Ручной", "manual")],
            "default": "auto",
        },
        {
            "name": "p",
            "label": "Порядок AR (p)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 10,
        },
        {
            "name": "d",
            "label": "Дифференцирование (d)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 3,
        },
        {
            "name": "q",
            "label": "Порядок MA (q)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 10,
        },
        {
            "name": "train_percent",
            "label": "Обучающая выборка, %",
            "type": "int",
            "default": 80,
            "min": 50,
            "max": 95,
        },
        {
            "name": "forecast_horizon",
            "label": "Горизонт прогноза (шагов)",
            "type": "int",
            "default": 12,
            "min": 1,
            "max": 9999,
        },
    ],
    "pipeline.model.SarimaModelNode": [
        {
            "name": "mode",
            "label": "Режим настройки",
            "type": "choice",
            "choices": [("Авто", "auto"), ("Ручной", "manual")],
            "default": "auto",
        },
        {
            "name": "p",
            "label": "Порядок AR (p)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 10,
        },
        {
            "name": "d",
            "label": "Дифференцирование (d)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 3,
        },
        {
            "name": "q",
            "label": "Порядок MA (q)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 10,
        },
        {
            "name": "P",
            "label": "Сезонный AR (P)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 10,
        },
        {
            "name": "D",
            "label": "Сезонное дифф. (D)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 2,
        },
        {
            "name": "Q",
            "label": "Сезонный MA (Q)",
            "type": "int",
            "default": 1,
            "min": 0,
            "max": 10,
        },
        {
            "name": "s",
            "label": "Длина сезона (s)",
            "type": "int",
            "default": 12,
            "min": 2,
            "max": 366,
        },
        {
            "name": "train_percent",
            "label": "Обучающая выборка, %",
            "type": "int",
            "default": 80,
            "min": 50,
            "max": 95,
        },
        {
            "name": "forecast_horizon",
            "label": "Горизонт прогноза (шагов)",
            "type": "int",
            "default": 12,
            "min": 1,
            "max": 9999,
        },
    ],
    "pipeline.model.EtsModelNode": [
        {
            "name": "mode",
            "label": "Режим настройки",
            "type": "choice",
            "choices": [("Авто", "auto"), ("Ручной", "manual")],
            "default": "auto",
        },
        {
            "name": "trend",
            "label": "Тип тренда",
            "type": "choice",
            "choices": [
                ("Нет", "none"),
                ("Аддитивный", "add"),
                ("Мультипликативный", "mul"),
            ],
            "default": "none",
        },
        {
            "name": "seasonal",
            "label": "Тип сезонности",
            "type": "choice",
            "choices": [
                ("Нет", "none"),
                ("Аддитивная", "add"),
                ("Мультипликативная", "mul"),
            ],
            "default": "none",
        },
        {
            "name": "season_length",
            "label": "Длина сезона",
            "type": "int",
            "default": 12,
            "min": 2,
            "max": 366,
        },
        {
            "name": "damped_trend",
            "label": "Затухающий тренд",
            "type": "choice",
            "choices": [("Нет", "false"), ("Да", "true")],
            "default": "false",
        },
        {
            "name": "train_percent",
            "label": "Обучающая выборка, %",
            "type": "int",
            "default": 80,
            "min": 50,
            "max": 95,
        },
        {
            "name": "forecast_horizon",
            "label": "Горизонт прогноза (шагов)",
            "type": "int",
            "default": 12,
            "min": 1,
            "max": 9999,
        },
    ],
    "pipeline.transform.OutlierCleaningNode": [
        {
            "name": "threshold",
            "label": "Порог MAD (чувствительность)",
            "type": "float",
            "default": 3.5,
            "min": 0.1,
            "max": 20.0,
            "step": 0.1,
        },
        {
            "name": "fill_policy",
            "label": "Заполнение удалённых выбросов",
            "type": "choice",
            "choices": [
                ("Интерполяция по времени", "time"),
                ("Forward fill", "ffill"),
                ("Backward fill", "bfill"),
                ("Константа", "const"),
                ("Не заполнять (NaN)", "none"),
            ],
            "default": "time",
        },
        {
            "name": "fill_value",
            "label": "Константа заполнения (для 'const')",
            "type": "float",
            "default": 0.0,
            "min": -1e9,
            "max": 1e9,
            "step": 1.0,
        },
    ],
}

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.graph = NodeGraph()
        self._report_dialog = FinalDialog(parent=self)
        self._run_thread: _GraphRunThread | None = None

        self._last_selected_node_id = None
        self._node_create_counter = 0
        self._updating_inspector = False
        self._inspector_editors: dict[str, QtWidgets.QWidget] = {}
        self._pan_keys_held: set[int] = set()

        self._configure_graph_view()
        self._configure_docks()
        self._register_nodes()
        self._mount_graph_widget()
        self._build_left_panel()
        self._build_right_panel()
        self._build_toolbar()
        self._bind_shortcuts()

        self.graph.create_node("pipeline.start.StartCsvNode", pos=[0, 0])

        self._selection_timer = QtCore.QTimer(self)
        self._selection_timer.timeout.connect(self._refresh_inspector_from_selection)
        self._selection_timer.start(200)

        self._pan_timer = QtCore.QTimer(self)
        self._pan_timer.setInterval(16)
        self._pan_timer.timeout.connect(self._tick_pan)

        QtCore.QTimer.singleShot(0, self._apply_initial_sizes)

    _PAN_ARROW_DELTA = {
        QtCore.Qt.Key_Left: (-12, 0),
        QtCore.Qt.Key_Right: (12, 0),
        QtCore.Qt.Key_Up: (0, -12),
        QtCore.Qt.Key_Down: (0, 12),
    }

    _PAN_SCAN_DELTA = {
        17: (0, -12),
        30: (-12, 0),
        31: (0, 12),
        32: (12, 0),
    }

    def _configure_graph_view(self):
        self.graph.set_background_color(0x0B, 0x3D, 0x2E)
        self.graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_LINES.value)
        self.graph.set_grid_color(0x1A, 0x66, 0x4E)

        self.graph.widget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.graph.widget.setFocus()
        self.graph.viewer().installEventFilter(self)

    def _configure_docks(self):
        self.ui.dockLeft.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.ui.dockRight.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)

        self.ui.dockLeft.setMinimumWidth(260)
        self.ui.dockLeft.setMaximumWidth(340)

        self.ui.dockRight.setMinimumWidth(300)
        self.ui.dockRight.setMaximumWidth(420)

        self.ui.dockLeft.show()
        self.ui.dockRight.show()

        self.ui.nodeHostWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )

    def _apply_initial_sizes(self):
        try:
            self.resizeDocks([self.ui.dockLeft], [260], QtCore.Qt.Horizontal)
            self.resizeDocks([self.ui.dockRight], [320], QtCore.Qt.Horizontal)
        except Exception:
            _logger.warning(
                "Не удалось установить начальные размеры панелей", exc_info=True
            )

    def _register_nodes(self):
        self.graph.register_node(StartCsvNode)
        self.graph.register_node(SimpleSeriesPlotNode)
        self.graph.register_node(ACFPlotNode)
        self.graph.register_node(PACFPlotNode)
        self.graph.register_node(RollingStatsPlotNode)
        self.graph.register_node(DifferencePlotNode)
        self.graph.register_node(SeasonalDifferencePlotNode)
        self.graph.register_node(DecompositionPlotNode)
        self.graph.register_node(HistogramPlotNode)
        self.graph.register_node(QQPlotNode)
        self.graph.register_node(SeasonalProfilePlotNode)
        self.graph.register_node(ArimaModelNode)
        self.graph.register_node(SarimaModelNode)
        self.graph.register_node(EtsModelNode)
        self.graph.register_node(EnsembleModelNode)
        self.graph.register_node(EnsembleByErrorsModelNode)
        self.graph.register_node(OutlierCleaningNode)
        self.graph.register_node(ExportCsvNode)

    def _mount_graph_widget(self):
        host_layout = self.ui.nodeHostWidgetLayout
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(0)
        host_layout.addWidget(self.graph.widget)

    def _pan_id_for_event(self, event):
        key = event.key()
        if key in self._PAN_ARROW_DELTA:
            return key
        scan = event.nativeScanCode()
        if scan in self._PAN_SCAN_DELTA:
            return ("sc", scan)
        return None

    def _pan_delta(self, pan_id):
        if isinstance(pan_id, tuple):
            return self._PAN_SCAN_DELTA[pan_id[1]]
        return self._PAN_ARROW_DELTA[pan_id]

    def eventFilter(self, obj, event):
        if obj is self.graph.viewer():
            t = event.type()
            if t == QtCore.QEvent.KeyPress and not event.isAutoRepeat():
                pan_id = self._pan_id_for_event(event)
                if pan_id is not None:
                    self._pan_keys_held.add(pan_id)
                    if not self._pan_timer.isActive():
                        self._pan_timer.start()
                    return True
            elif t == QtCore.QEvent.KeyRelease and not event.isAutoRepeat():
                pan_id = self._pan_id_for_event(event)
                if pan_id is not None:
                    self._pan_keys_held.discard(pan_id)
                    if not self._pan_keys_held:
                        self._pan_timer.stop()
                    return True
            elif t in (QtCore.QEvent.FocusOut, QtCore.QEvent.WindowDeactivate):
                self._pan_keys_held.clear()
                self._pan_timer.stop()
        return super().eventFilter(obj, event)

    def _tick_pan(self):
        if not self._pan_keys_held:
            self._pan_timer.stop()
            return
        dx, dy = 0, 0
        for pan_id in self._pan_keys_held:
            kx, ky = self._pan_delta(pan_id)
            dx += kx
            dy += ky
        self.graph.viewer()._set_viewer_pan(dx, dy)

    def _build_left_panel(self):
        layout = self.ui.dockLeftWidgetLayout
        self._clear_layout(layout)

        title = QtWidgets.QLabel("Узлы")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")

        self.node_search_edit = QtWidgets.QLineEdit()
        self.node_search_edit.setPlaceholderText("Поиск узла...")
        self.node_search_edit.textChanged.connect(self._filter_node_list)

        self.node_list_widget = QtWidgets.QListWidget()
        self.node_list_widget.itemDoubleClicked.connect(self._add_node_from_item)

        self.add_node_btn = QtWidgets.QPushButton("Добавить выбранный узел")
        self.add_node_btn.clicked.connect(self._add_selected_node_from_palette)

        hint = QtWidgets.QLabel(
            "Двойной клик по узлу — добавить на поле.\n"
            "Delete — удалить выделенные узлы.\n"
            "F — показать весь граф, Ctrl+0 — сбросить масштаб."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #555; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(self.node_search_edit)
        layout.addWidget(self.node_list_widget, stretch=1)
        layout.addWidget(self.add_node_btn)
        layout.addWidget(hint)

        self._populate_node_list()

    def _populate_node_list(self):
        self.node_list_widget.clear()

        current_group = None
        for display_name, node_type, group in NODE_CATALOG:
            if group != current_group:
                header = QtWidgets.QListWidgetItem(group)
                header.setFlags(QtCore.Qt.NoItemFlags)
                header.setForeground(QtGui.QBrush(QtGui.QColor("#1A66A0")))
                self.node_list_widget.addItem(header)
                current_group = group

            item = QtWidgets.QListWidgetItem(f"  {display_name}")
            item.setData(QtCore.Qt.UserRole, node_type)
            item.setData(QtCore.Qt.UserRole + 1, display_name.lower())
            self.node_list_widget.addItem(item)

    def _filter_node_list(self):
        text = self.node_search_edit.text().strip().lower()

        for i in range(self.node_list_widget.count()):
            item = self.node_list_widget.item(i)
            node_type = item.data(QtCore.Qt.UserRole)
            search_blob = item.data(QtCore.Qt.UserRole + 1)

            if node_type is None:
                item.setHidden(False)
                continue

            item.setHidden(bool(text) and text not in search_blob)

        for i in range(self.node_list_widget.count()):
            item = self.node_list_widget.item(i)
            if item.data(QtCore.Qt.UserRole) is not None:
                continue

            has_visible_children = False
            j = i + 1
            while j < self.node_list_widget.count():
                nxt = self.node_list_widget.item(j)
                if nxt.data(QtCore.Qt.UserRole) is None:
                    break
                if not nxt.isHidden():
                    has_visible_children = True
                    break
                j += 1

            item.setHidden(not has_visible_children)

    def _add_selected_node_from_palette(self):
        item = self.node_list_widget.currentItem()
        if item is None:
            return
        self._add_node_from_item(item)

    def _add_node_from_item(self, item: QtWidgets.QListWidgetItem):
        node_type = item.data(QtCore.Qt.UserRole)
        if not node_type:
            return

        x = 120 + self._node_create_counter * 40
        y = 80 + self._node_create_counter * 20
        self._node_create_counter += 1

        self.graph.create_node(node_type, pos=[x, y])
        self.focus_graph()

    def _build_right_panel(self):
        layout = self.ui.dockRightWidgetLayout
        self._clear_layout(layout)

        title = QtWidgets.QLabel("Параметры узла")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")

        self.inspector_name_label = QtWidgets.QLabel("Ничего не выбрано")
        self.inspector_name_label.setWordWrap(True)
        self.inspector_name_label.setStyleSheet("font-size: 13px; color: #333;")

        self.inspector_scroll = QtWidgets.QScrollArea()
        self.inspector_scroll.setWidgetResizable(True)

        self.inspector_container = QtWidgets.QWidget()
        self.inspector_form_layout = QtWidgets.QFormLayout(self.inspector_container)
        self.inspector_form_layout.setContentsMargins(8, 8, 8, 8)
        self.inspector_form_layout.setSpacing(12)

        self.inspector_scroll.setWidget(self.inspector_container)

        self.delete_selected_btn = QtWidgets.QPushButton("Удалить выбранные узлы")
        self.delete_selected_btn.clicked.connect(self.delete_selected_nodes)

        self.focus_btn = QtWidgets.QPushButton("Вернуться к графу")
        self.focus_btn.clicked.connect(self.focus_graph)

        hint = QtWidgets.QLabel(
            "Здесь показываются только прикладные параметры выделенного узла.\n"
            "Служебные свойства NodeGraphQt скрыты."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #555; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(self.inspector_name_label)
        layout.addWidget(self.inspector_scroll, stretch=1)
        layout.addWidget(self.delete_selected_btn)
        layout.addWidget(self.focus_btn)
        layout.addWidget(hint)

    def _refresh_inspector_from_selection(self):
        selected = self.graph.selected_nodes()
        if len(selected) != 1:
            if self._last_selected_node_id is not None:
                self._last_selected_node_id = None
                self.inspector_name_label.setText("Ничего не выбрано")
                self._rebuild_inspector_form(None)
            return

        node = selected[0]
        if node.id == self._last_selected_node_id:
            return

        self._last_selected_node_id = node.id
        self.inspector_name_label.setText(node.NODE_NAME)
        self._rebuild_inspector_form(node)

    def _rebuild_inspector_form(self, node):
        self._clear_form_layout(self.inspector_form_layout)
        self._inspector_editors.clear()

        if node is None:
            empty = QtWidgets.QLabel("Выберите один узел на поле графа.")
            empty.setWordWrap(True)
            self.inspector_form_layout.addRow(empty)
            return

        fields = NODE_FIELDS.get(node.type_, [])
        if not fields:
            empty = QtWidgets.QLabel("У этого узла нет редактируемых параметров.")
            empty.setWordWrap(True)
            self.inspector_form_layout.addRow(empty)
            return

        self._updating_inspector = True
        try:
            for spec in fields:
                editor = self._build_editor_for_field(node, spec)
                self._inspector_editors[spec["name"]] = editor
                self.inspector_form_layout.addRow(spec["label"], editor)
        finally:
            self._updating_inspector = False

        if node.type_ in self._AUTO_LOCKED_FIELDS:
            self._setup_mode_binding(node)

    def _build_editor_for_field(self, node, spec: dict) -> QtWidgets.QWidget:
        field_name = spec["name"]
        field_type = spec["type"]

        current_value = node.get_property(field_name)
        if current_value is None:
            current_value = spec.get("default", "")

        if field_type in ("line", "file", "save_file"):
            container = QtWidgets.QWidget()
            row = QtWidgets.QHBoxLayout(container)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(4)

            line = QtWidgets.QLineEdit(str(current_value))
            line.editingFinished.connect(
                lambda n=node, e=line, key=field_name: self._set_node_property(
                    n, key, e.text()
                )
            )
            row.addWidget(line, stretch=1)

            if field_type == "file":
                btn = QtWidgets.QPushButton("...")
                btn.setFixedWidth(32)
                btn.setToolTip("Выбрать файл")

                def _browse(checked=False, n=node, e=line, key=field_name):
                    path, _ = QtWidgets.QFileDialog.getOpenFileName(
                        self,
                        "Выберите CSV-файл",
                        e.text(),
                        "CSV файлы (*.csv);;Все файлы (*)",
                    )
                    if path:
                        e.setText(path)
                        self._set_node_property(n, key, path)

                btn.clicked.connect(_browse)
                row.addWidget(btn)

            if field_type == "save_file":
                btn = QtWidgets.QPushButton("...")
                btn.setFixedWidth(32)
                btn.setToolTip("Выбрать путь для сохранения")

                def _browse_save(checked=False, n=node, e=line, key=field_name):
                    path, _ = QtWidgets.QFileDialog.getSaveFileName(
                        self,
                        "Сохранить CSV-файл",
                        e.text(),
                        "CSV файлы (*.csv);;Все файлы (*)",
                    )
                    if path:
                        e.setText(path)
                        self._set_node_property(n, key, path)

                btn.clicked.connect(_browse_save)
                row.addWidget(btn)

            return container

        if field_type == "int":
            w = QtWidgets.QSpinBox()
            w.setMinimum(spec.get("min", -999999))
            w.setMaximum(spec.get("max", 999999))
            try:
                w.setValue(int(current_value))
            except Exception:
                w.setValue(int(spec.get("default", 0)))
            w.valueChanged.connect(
                lambda val, n=node, key=field_name: self._set_node_property(
                    n, key, str(val)
                )
            )
            return w

        if field_type == "float":
            w = QtWidgets.QDoubleSpinBox()
            w.setMinimum(spec.get("min", -1e9))
            w.setMaximum(spec.get("max", 1e9))
            w.setSingleStep(spec.get("step", 0.1))
            w.setDecimals(4)
            try:
                w.setValue(float(current_value))
            except Exception:
                w.setValue(float(spec.get("default", 0.0)))
            w.valueChanged.connect(
                lambda val, n=node, key=field_name: self._set_node_property(
                    n, key, str(val)
                )
            )
            return w

        if field_type == "choice":
            w = QtWidgets.QComboBox()
            choices = spec.get("choices", [])
            for ch in choices:
                if isinstance(ch, (list, tuple)):
                    w.addItem(ch[0], ch[1])
                else:
                    w.addItem(ch, ch)

            idx = w.findData(str(current_value))
            if idx < 0:
                idx = w.findData(spec.get("default"))
            if idx >= 0:
                w.setCurrentIndex(idx)

            w.currentIndexChanged.connect(
                lambda _i, n=node, e=w, key=field_name: self._set_node_property(
                    n, key, e.currentData()
                )
            )
            return w

        fallback = QtWidgets.QLineEdit(str(current_value))
        fallback.editingFinished.connect(
            lambda n=node, e=fallback, key=field_name: self._set_node_property(
                n, key, e.text()
            )
        )
        return fallback

    _AUTO_LOCKED_FIELDS = {
        "pipeline.model.EtsModelNode": (
            "trend",
            "seasonal",
            "season_length",
            "damped_trend",
            "train_percent",
        ),
        "pipeline.model.ArimaModelNode": ("p", "d", "q", "train_percent"),
        "pipeline.model.SarimaModelNode": (
            "p",
            "d",
            "q",
            "P",
            "D",
            "Q",
            "s",
            "train_percent",
        ),
    }

    def _setup_mode_binding(self, node) -> None:
        mode_editor = self._inspector_editors.get("mode")
        if mode_editor is None:
            return
        self._update_auto_param_state(
            node.type_, str(node.get_property("mode") or "auto")
        )
        mode_editor.currentIndexChanged.connect(
            lambda _i, e=mode_editor, nt=node.type_: self._update_auto_param_state(
                nt, e.currentData()
            )
        )

    def _update_auto_param_state(self, node_type: str, mode_value: str) -> None:
        is_manual = mode_value == "manual"
        for name in self._AUTO_LOCKED_FIELDS.get(node_type, ()):
            editor = self._inspector_editors.get(name)
            if editor is not None:
                editor.setEnabled(is_manual)

    def _set_node_property(self, node, key: str, value):
        if self._updating_inspector:
            return
        try:
            node.set_property(key, value)
        except Exception:
            _logger.warning(
                "Не удалось установить свойство узла: key=%r value=%r",
                key,
                value,
                exc_info=True,
            )

    def _build_toolbar(self):
        tb = self.addToolBar("Конвейер")
        tb.setMovable(False)

        self._act_run = QtGui.QAction("Запустить граф", self)
        self._act_run.triggered.connect(self.run_graph)
        tb.addAction(self._act_run)

        tb.addSeparator()

        act_save = QtGui.QAction("Сохранить граф", self)
        act_save.setToolTip("Сохранить граф (Ctrl+S)")
        act_save.triggered.connect(self.save_graph)
        tb.addAction(act_save)

        act_open = QtGui.QAction("Открыть граф", self)
        act_open.setToolTip("Открыть граф (Ctrl+O)")
        act_open.triggered.connect(self.load_graph)
        tb.addAction(act_open)

        tb.addSeparator()

        act_delete = QtGui.QAction("Удалить выделенные", self)
        act_delete.triggered.connect(self.delete_selected_nodes)
        tb.addAction(act_delete)

        act_fit = QtGui.QAction("Показать весь граф", self)
        act_fit.setToolTip("Вписать все узлы графа в видимую область (F)")
        act_fit.triggered.connect(self.fit_graph_view)
        tb.addAction(act_fit)

        act_reset_zoom = QtGui.QAction("Сбросить масштаб", self)
        act_reset_zoom.triggered.connect(self.reset_graph_zoom)
        tb.addAction(act_reset_zoom)

    def _bind_shortcuts(self):
        act_delete = QtGui.QAction(self)
        act_delete.setShortcut(QtGui.QKeySequence.Delete)
        act_delete.triggered.connect(self.delete_selected_nodes)
        self.addAction(act_delete)

        act_fit = QtGui.QAction(self)
        act_fit.setShortcut(QtGui.QKeySequence("F"))
        act_fit.triggered.connect(self.fit_graph_view)
        self.addAction(act_fit)

        act_reset_zoom = QtGui.QAction(self)
        act_reset_zoom.setShortcut(QtGui.QKeySequence("Ctrl+0"))
        act_reset_zoom.triggered.connect(self.reset_graph_zoom)
        self.addAction(act_reset_zoom)

        act_focus = QtGui.QAction(self)
        act_focus.setShortcut(QtGui.QKeySequence("Ctrl+G"))
        act_focus.triggered.connect(self.focus_graph)
        self.addAction(act_focus)

        act_save = QtGui.QAction(self)
        act_save.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_graph)
        self.addAction(act_save)

        act_open = QtGui.QAction(self)
        act_open.setShortcut(QtGui.QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self.load_graph)
        self.addAction(act_open)

    def focus_graph(self):
        self.graph.widget.setFocus()
        self.graph.widget.activateWindow()

    def delete_selected_nodes(self):
        viewer = self.graph.viewer()
        selected_pipes = viewer.selected_pipes()
        if selected_pipes:
            ports = [[p.input_port, p.output_port] for p in selected_pipes]
            self.graph._on_connection_sliced(ports)

        selected = self.graph.selected_nodes()
        for node in selected:
            if node.type_ == "pipeline.start.StartCsvNode":
                continue
            self.graph.delete_node(node)

        self.focus_graph()

    def fit_graph_view(self):
        viewer = self.graph.viewer()
        try:
            scene = viewer.scene()
            rect = scene.itemsBoundingRect()
            if not rect.isEmpty():
                margin = 40
                rect = rect.adjusted(-margin, -margin, margin, margin)
                viewer.fitInView(rect, QtCore.Qt.KeepAspectRatio)
        except Exception:
            _logger.warning(
                "fit_graph_view: не удалось вписать граф в область", exc_info=True
            )
            try:
                viewer.reset_zoom()
            except Exception:
                _logger.warning(
                    "fit_graph_view: fallback reset_zoom тоже не сработал",
                    exc_info=True,
                )
        self.focus_graph()

    def reset_graph_zoom(self):
        viewer = self.graph.viewer()
        try:
            viewer.reset_zoom()
        except Exception:
            _logger.warning(
                "reset_graph_zoom: не удалось сбросить масштаб", exc_info=True
            )
        self.focus_graph()

    def save_graph(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Сохранить граф",
            "",
            "Граф (*.json);;Все файлы (*)",
        )
        if not path:
            return
        try:
            self.graph.save_session(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка сохранения", str(e))

    def load_graph(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Открыть граф",
            "",
            "Граф (*.json);;Все файлы (*)",
        )
        if not path:
            return

        backup = self.graph.serialize_session()

        try:
            self.graph.load_session(path)
            loaded_nodes = list(self.graph.all_nodes())
            if not loaded_nodes:
                raise ValueError("Файл не содержит ни одного узла графа.")

        except Exception as e:
            try:
                self.graph.deserialize_session(backup)
            except Exception:
                self.graph.clear_session()
                self.graph.create_node("pipeline.start.StartCsvNode", pos=[0, 0])

            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка загрузки",
                f"Не удалось загрузить граф:\n{e}\n\nПредыдущий граф восстановлен.",
            )
            return

        self._last_selected_node_id = None
        self._node_create_counter = len(loaded_nodes)
        self._rebuild_inspector_form(None)
        self.inspector_name_label.setText("Ничего не выбрано")

    def run_graph(self):
        graph_warnings = validate_graph(self.graph)
        if graph_warnings:
            dlg = WarningsDialog(graph_warnings, parent=self)
            if dlg.exec() != QtWidgets.QDialog.Accepted:
                return

        if self._run_thread is not None and self._run_thread.isRunning():
            return

        report = ReportChannel()
        self._report_dialog.clear()

        loading = LoadingDialog(self)
        self._run_thread = _GraphRunThread(self.graph, report, parent=self)

        self._act_run.setEnabled(False)

        def on_ready_for_loading():
            loading.show()

        def on_finished():
            loading.close()
            self._act_run.setEnabled(True)

            try:
                report.flush()
                self._report_dialog.set_document(report.document)
                self._report_dialog.show()
                self._report_dialog.raise_()
                self._report_dialog.activateWindow()
            finally:
                self._run_thread = None

        def on_error(msg: str):
            loading.close()
            self._act_run.setEnabled(True)
            self._run_thread = None
            QtWidgets.QMessageBox.critical(self, "Ошибка выполнения", msg)

        self._run_thread.ready_for_loading.connect(on_ready_for_loading)
        self._run_thread.finished.connect(on_finished)
        self._run_thread.error_occurred.connect(on_error)
        self._run_thread.start()

    @staticmethod
    def _clear_layout(layout: QtWidgets.QLayout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            child_layout = item.layout()
            if w is not None:
                w.deleteLater()
            elif child_layout is not None:
                MainWindow._clear_layout(child_layout)

    @staticmethod
    def _clear_form_layout(layout: QtWidgets.QFormLayout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            child_layout = item.layout()
            if w is not None:
                w.deleteLater()
            elif child_layout is not None:
                MainWindow._clear_layout(child_layout)
