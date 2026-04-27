# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arimawizard.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLayout,
    QSizePolicy, QSpinBox, QVBoxLayout, QWidget,
    QWizard, QWizardPage)

class Ui_ArimaWizard(object):
    def setupUi(self, ArimaWizard):
        if not ArimaWizard.objectName():
            ArimaWizard.setObjectName(u"ArimaWizard")
        ArimaWizard.resize(590, 498)
        self.arimaWizardMainPage = QWizardPage()
        self.arimaWizardMainPage.setObjectName(u"arimaWizardMainPage")
        self.horizontalLayout = QHBoxLayout(self.arimaWizardMainPage)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.label_4 = QLabel(self.arimaWizardMainPage)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.label_4)

        self.label_2 = QLabel(self.arimaWizardMainPage)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.label_2)

        self.label_3 = QLabel(self.arimaWizardMainPage)
        self.label_3.setObjectName(u"label_3")
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.label_3)

        self.label = QLabel(self.arimaWizardMainPage)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.label)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.arimaWizardSpinBoxAR = QSpinBox(self.arimaWizardMainPage)
        self.arimaWizardSpinBoxAR.setObjectName(u"arimaWizardSpinBoxAR")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.arimaWizardSpinBoxAR.sizePolicy().hasHeightForWidth())
        self.arimaWizardSpinBoxAR.setSizePolicy(sizePolicy1)
        self.arimaWizardSpinBoxAR.setMaximum(10)

        self.verticalLayout_2.addWidget(self.arimaWizardSpinBoxAR)

        self.arimaWizardSpinBoxI = QSpinBox(self.arimaWizardMainPage)
        self.arimaWizardSpinBoxI.setObjectName(u"arimaWizardSpinBoxI")
        sizePolicy1.setHeightForWidth(self.arimaWizardSpinBoxI.sizePolicy().hasHeightForWidth())
        self.arimaWizardSpinBoxI.setSizePolicy(sizePolicy1)
        self.arimaWizardSpinBoxI.setMaximum(3)

        self.verticalLayout_2.addWidget(self.arimaWizardSpinBoxI)

        self.arimaWizardSpinBoxMA = QSpinBox(self.arimaWizardMainPage)
        self.arimaWizardSpinBoxMA.setObjectName(u"arimaWizardSpinBoxMA")
        sizePolicy1.setHeightForWidth(self.arimaWizardSpinBoxMA.sizePolicy().hasHeightForWidth())
        self.arimaWizardSpinBoxMA.setSizePolicy(sizePolicy1)
        self.arimaWizardSpinBoxMA.setMaximum(10)

        self.verticalLayout_2.addWidget(self.arimaWizardSpinBoxMA)

        self.arimaWizardSpinBoxTrainPercent = QSpinBox(self.arimaWizardMainPage)
        self.arimaWizardSpinBoxTrainPercent.setObjectName(u"arimaWizardSpinBoxTrainPercent")
        sizePolicy1.setHeightForWidth(self.arimaWizardSpinBoxTrainPercent.sizePolicy().hasHeightForWidth())
        self.arimaWizardSpinBoxTrainPercent.setSizePolicy(sizePolicy1)

        self.verticalLayout_2.addWidget(self.arimaWizardSpinBoxTrainPercent)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        ArimaWizard.addPage(self.arimaWizardMainPage)

        self.retranslateUi(ArimaWizard)

        QMetaObject.connectSlotsByName(ArimaWizard)
    # setupUi

    def retranslateUi(self, ArimaWizard):
        ArimaWizard.setWindowTitle(QCoreApplication.translate("ArimaWizard", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 ARIMA", None))
        self.label_4.setText(QCoreApplication.translate("ArimaWizard", u"\u041f\u043e\u0440\u044f\u0434\u043e\u043a AR", None))
        self.label_2.setText(QCoreApplication.translate("ArimaWizard", u"\u041f\u043e\u0440\u044f\u0434\u043e\u043a \u0434\u0438\u0444\u0444\u0435\u0440\u0435\u043d\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f", None))
        self.label_3.setText(QCoreApplication.translate("ArimaWizard", u"\u041f\u043e\u0440\u044f\u0434\u043e\u043a MA", None))
        self.label.setText(QCoreApplication.translate("ArimaWizard", u"\u041f\u0440\u043e\u0446\u0435\u043d\u0442 \u043e\u0431\u0443\u0447\u0430\u044e\u0449\u0435\u0439 \u0432\u044b\u0431\u043e\u0440\u043a\u0438", None))
    # retranslateUi

