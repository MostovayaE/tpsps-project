# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'warnings.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_WarningsFrame(object):
    def setupUi(self, WarningsFrame):
        if not WarningsFrame.objectName():
            WarningsFrame.setObjectName(u"WarningsFrame")
        WarningsFrame.resize(472, 574)
        self.verticalLayout = QVBoxLayout(WarningsFrame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollAreaWarnings = QScrollArea(WarningsFrame)
        self.scrollAreaWarnings.setObjectName(u"scrollAreaWarnings")
        self.scrollAreaWarnings.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 452, 554))
        self.scrollAreaWarnings.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollAreaWarnings)


        self.retranslateUi(WarningsFrame)

        QMetaObject.connectSlotsByName(WarningsFrame)
    # setupUi

    def retranslateUi(self, WarningsFrame):
        WarningsFrame.setWindowTitle(QCoreApplication.translate("WarningsFrame", u"Frame", None))
    # retranslateUi

