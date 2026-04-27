# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'design.ui'
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QHBoxLayout, QMainWindow,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.nodeHostWidget = QWidget(self.centralwidget)
        self.nodeHostWidget.setObjectName(u"nodeHostWidget")
        sizePolicy.setHeightForWidth(self.nodeHostWidget.sizePolicy().hasHeightForWidth())
        self.nodeHostWidget.setSizePolicy(sizePolicy)
        self.horizontalLayout_3 = QHBoxLayout(self.nodeHostWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.nodeHostWidgetLayout = QVBoxLayout()
        self.nodeHostWidgetLayout.setObjectName(u"nodeHostWidgetLayout")

        self.horizontalLayout_3.addLayout(self.nodeHostWidgetLayout)


        self.horizontalLayout.addWidget(self.nodeHostWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.dockRight = QDockWidget(MainWindow)
        self.dockRight.setObjectName(u"dockRight")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.dockRight.sizePolicy().hasHeightForWidth())
        self.dockRight.setSizePolicy(sizePolicy1)
        self.dockRight.setMaximumSize(QSize(10000, 524287))
        self.dockRightWidget = QWidget()
        self.dockRightWidget.setObjectName(u"dockRightWidget")
        self.verticalLayout_3 = QVBoxLayout(self.dockRightWidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.dockRightWidgetLayout = QVBoxLayout()
        self.dockRightWidgetLayout.setObjectName(u"dockRightWidgetLayout")

        self.verticalLayout_3.addLayout(self.dockRightWidgetLayout)

        self.dockRight.setWidget(self.dockRightWidget)
        MainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockRight)
        self.dockLeft = QDockWidget(MainWindow)
        self.dockLeft.setObjectName(u"dockLeft")
        sizePolicy1.setHeightForWidth(self.dockLeft.sizePolicy().hasHeightForWidth())
        self.dockLeft.setSizePolicy(sizePolicy1)
        self.dockLeft.setMaximumSize(QSize(10000, 524287))
        self.dockLeftWidget = QWidget()
        self.dockLeftWidget.setObjectName(u"dockLeftWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.dockLeftWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.dockLeftWidgetLayout = QVBoxLayout()
        self.dockLeftWidgetLayout.setObjectName(u"dockLeftWidgetLayout")

        self.horizontalLayout_2.addLayout(self.dockLeftWidgetLayout)

        self.dockLeft.setWidget(self.dockLeftWidget)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockLeft)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
    # retranslateUi

