from __future__ import annotations
import math
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

class RainbowCatWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0.0
        self._hue = 0.0
        self._orbit_angle = 0.0

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
        self.setFixedSize(200, 200)

    def _tick(self):
        self._angle = (self._angle + 5.0) % 360.0
        self._hue = (self._hue + 0.009) % 1.0
        self._orbit_angle = (self._orbit_angle + 4.0) % 360.0
        self.update()

    def _c(self, offset: float, s: float = 0.88, v: float = 1.0) -> QtGui.QColor:
        return QtGui.QColor.fromHsvF((self._hue + offset) % 1.0, s, v)

    def paintEvent(self, _event):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)

        cx, cy = self.width() / 2, self.height() / 2

        p.setPen(Qt.NoPen)
        for i in range(8):
            a = math.radians(self._orbit_angle + i * 45)
            sx = cx + 82 * math.cos(a)
            sy = cy + 82 * math.sin(a)
            r = 4 + 2 * math.sin(math.radians(self._orbit_angle * 3 + i * 60))
            p.setBrush(self._c(i / 8))
            p.drawEllipse(QtCore.QPointF(sx, sy), r, r)

        p.translate(cx, cy)
        p.rotate(self._angle)

        scale = min(self.width(), self.height()) / 260.0
        p.scale(scale, scale)
        p.setPen(Qt.NoPen)

        tail_pen = QtGui.QPen(self._c(0.62), 7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        p.setPen(tail_pen)
        p.setBrush(Qt.NoBrush)
        tail = QtGui.QPainterPath()
        tail.moveTo(28, 36)
        tail.cubicTo(62, 28, 72, -8, 46, -46)
        p.drawPath(tail)
        p.setPen(Qt.NoPen)

        p.setBrush(self._c(0.0))
        p.drawEllipse(QtCore.QRectF(-30, 10, 60, 50))

        p.setBrush(self._c(0.15))
        p.drawEllipse(QtCore.QRectF(-30, -50, 60, 60))

        p.setBrush(self._c(0.30))
        p.drawPolygon(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(-30, -38),
                    QtCore.QPointF(-48, -78),
                    QtCore.QPointF(-8, -68),
                ]
            )
        )
        p.drawPolygon(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(30, -38),
                    QtCore.QPointF(48, -78),
                    QtCore.QPointF(8, -68),
                ]
            )
        )

        p.setBrush(self._c(0.38, s=0.45))
        p.drawPolygon(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(-28, -42),
                    QtCore.QPointF(-42, -70),
                    QtCore.QPointF(-12, -63),
                ]
            )
        )
        p.drawPolygon(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(28, -42),
                    QtCore.QPointF(42, -70),
                    QtCore.QPointF(12, -63),
                ]
            )
        )

        p.setBrush(QtGui.QColor(240, 245, 255))
        p.drawEllipse(QtCore.QRectF(-23, -36, 15, 17))
        p.drawEllipse(QtCore.QRectF(8, -36, 15, 17))

        p.setBrush(QtGui.QColor(15, 8, 25))
        p.drawEllipse(QtCore.QRectF(-20, -33, 8, 12))
        p.drawEllipse(QtCore.QRectF(12, -33, 8, 12))

        p.setBrush(QtGui.QColor(255, 255, 255, 210))
        p.drawEllipse(QtCore.QRectF(-19, -32, 4, 4))
        p.drawEllipse(QtCore.QRectF(13, -32, 4, 4))

        p.setBrush(self._c(0.50, s=0.65))
        p.drawPolygon(
            QtGui.QPolygonF(
                [
                    QtCore.QPointF(-5, -16),
                    QtCore.QPointF(5, -16),
                    QtCore.QPointF(0, -11),
                ]
            )
        )

        mouth_pen = QtGui.QPen(QtGui.QColor(70, 35, 35), 2, Qt.SolidLine, Qt.RoundCap)
        p.setPen(mouth_pen)
        p.setBrush(Qt.NoBrush)
        lm = QtGui.QPainterPath()
        lm.moveTo(0, -11)
        lm.quadTo(-7, -5, -11, -1)
        rm = QtGui.QPainterPath()
        rm.moveTo(0, -11)
        rm.quadTo(7, -5, 11, -1)
        p.drawPath(lm)
        p.drawPath(rm)

        w_pen = QtGui.QPen(
            QtGui.QColor(210, 210, 250, 190), 1.5, Qt.SolidLine, Qt.RoundCap
        )
        p.setPen(w_pen)
        for dy, lx, rx in [(-14, -38, 38), (-12, -38, 38), (-10, -36, 36)]:
            p.drawLine(QtCore.QPointF(-5, dy), QtCore.QPointF(lx, dy - 1))
            p.drawLine(QtCore.QPointF(5, dy), QtCore.QPointF(rx, dy - 1))

        p.end()

class LoadingDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выполнение графа")
        self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedSize(300, 310)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 16, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        cat = RainbowCatWidget(self)
        layout.addWidget(cat, alignment=Qt.AlignCenter)

        self._label = QtWidgets.QLabel("Выполняется")
        self._label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label)

        self._dots = 0
        self._dots_timer = QtCore.QTimer(self)
        self._dots_timer.timeout.connect(self._tick_dots)
        self._dots_timer.start(500)

        self.setStyleSheet("""
            LoadingDialog {
                background-color: #0d0d20;
                border: 2px solid #4a2080;
            }
            QLabel {
                color: #d8c8ff;
                font-size: 15px;
                font-weight: 600;
                background: transparent;
            }
        """)

    def _tick_dots(self):
        self._dots = (self._dots + 1) % 4
        self._label.setText("Выполняется" + "." * self._dots)

    def set_status(self, text: str):
        self._dots_timer.stop()
        self._label.setText(text)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)
