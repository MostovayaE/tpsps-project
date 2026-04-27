# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'final_dialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QScrollArea,
    QSizePolicy, QWidget)

class Ui_FinalDialog(object):
    def setupUi(self, FinalDialog):
        if not FinalDialog.objectName():
            FinalDialog.setObjectName(u"FinalDialog")
        FinalDialog.resize(652, 704)
        self.horizontalLayout = QHBoxLayout(FinalDialog)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.scrollArea = QScrollArea(FinalDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 632, 684))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.horizontalLayout.addWidget(self.scrollArea)


        self.retranslateUi(FinalDialog)

        QMetaObject.connectSlotsByName(FinalDialog)
    # setupUi

    def retranslateUi(self, FinalDialog):
        FinalDialog.setWindowTitle(QCoreApplication.translate("FinalDialog", u"Dialog", None))
    # retranslateUi

