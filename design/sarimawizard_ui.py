# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sarimawizard.ui'
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

class Ui_SarimaWizard(object):
    def setupUi(self, SarimaWizard):
        if not SarimaWizard.objectName():
            SarimaWizard.setObjectName(u"SarimaWizard")
        SarimaWizard.resize(590, 1156)
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

        self.label_5 = QLabel(self.arimaWizardMainPage)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_5)

        self.label_6 = QLabel(self.arimaWizardMainPage)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_6)

        self.label_7 = QLabel(self.arimaWizardMainPage)
        self.label_7.setObjectName(u"label_7")
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_7)

        self.label_8 = QLabel(self.arimaWizardMainPage)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_8)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.sarimaWizardSpinBoxAR = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxAR.setObjectName(u"sarimaWizardSpinBoxAR")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxAR.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxAR.setSizePolicy(sizePolicy2)
        self.sarimaWizardSpinBoxAR.setMaximum(10)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxAR)

        self.sarimaWizardSpinBoxI = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxI.setObjectName(u"sarimaWizardSpinBoxI")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxI.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxI.setSizePolicy(sizePolicy2)
        self.sarimaWizardSpinBoxI.setMaximum(3)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxI)

        self.sarimaWizardSpinBoxMA = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxMA.setObjectName(u"sarimaWizardSpinBoxMA")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxMA.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxMA.setSizePolicy(sizePolicy2)
        self.sarimaWizardSpinBoxMA.setMaximum(10)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxMA)

        self.sarimaWizardSpinBoxTrainPercent = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxTrainPercent.setObjectName(u"sarimaWizardSpinBoxTrainPercent")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxTrainPercent.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxTrainPercent.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxTrainPercent)

        self.sarimaWizardSpinBoxP = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxP.setObjectName(u"sarimaWizardSpinBoxP")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxP.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxP.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxP)

        self.sarimaWizardSpinBoxD = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxD.setObjectName(u"sarimaWizardSpinBoxD")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxD.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxD.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxD)

        self.sarimaWizardSpinBoxQ = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxQ.setObjectName(u"sarimaWizardSpinBoxQ")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxQ.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxQ.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxQ)

        self.sarimaWizardSpinBoxS = QSpinBox(self.arimaWizardMainPage)
        self.sarimaWizardSpinBoxS.setObjectName(u"sarimaWizardSpinBoxS")
        sizePolicy2.setHeightForWidth(self.sarimaWizardSpinBoxS.sizePolicy().hasHeightForWidth())
        self.sarimaWizardSpinBoxS.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.sarimaWizardSpinBoxS)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        SarimaWizard.addPage(self.arimaWizardMainPage)

        self.retranslateUi(SarimaWizard)

        QMetaObject.connectSlotsByName(SarimaWizard)
    # setupUi

    def retranslateUi(self, SarimaWizard):
        SarimaWizard.setWindowTitle(QCoreApplication.translate("SarimaWizard", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 ARIMA", None))
        self.label_4.setText(QCoreApplication.translate("SarimaWizard", u"\u041f\u043e\u0440\u044f\u0434\u043e\u043a AR", None))
        self.label_2.setText(QCoreApplication.translate("SarimaWizard", u"\u041f\u043e\u0440\u044f\u0434\u043e\u043a \u0434\u0438\u0444\u0444\u0435\u0440\u0435\u043d\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f", None))
        self.label_3.setText(QCoreApplication.translate("SarimaWizard", u"\u041f\u043e\u0440\u044f\u0434\u043e\u043a MA", None))
        self.label.setText(QCoreApplication.translate("SarimaWizard", u"\u041f\u0440\u043e\u0446\u0435\u043d\u0442 \u043e\u0431\u0443\u0447\u0430\u044e\u0449\u0435\u0439 \u0432\u044b\u0431\u043e\u0440\u043a\u0438", None))
        self.label_5.setText(QCoreApplication.translate("SarimaWizard", u"P", None))
        self.label_6.setText(QCoreApplication.translate("SarimaWizard", u"D", None))
        self.label_7.setText(QCoreApplication.translate("SarimaWizard", u"Q", None))
        self.label_8.setText(QCoreApplication.translate("SarimaWizard", u"S", None))
    # retranslateUi

