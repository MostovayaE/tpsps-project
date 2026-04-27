# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'etswizard.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QHBoxLayout,
    QLabel, QLayout, QSizePolicy, QSpinBox,
    QVBoxLayout, QWidget, QWizard, QWizardPage)

class Ui_EtsWizard(object):
    def setupUi(self, EtsWizard):
        if not EtsWizard.objectName():
            EtsWizard.setObjectName(u"EtsWizard")
        EtsWizard.resize(590, 1156)
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

        self.label_5 = QLabel(self.arimaWizardMainPage)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_5)

        self.label = QLabel(self.arimaWizardMainPage)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.label)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.etsWizardComboBoxTrendType = QComboBox(self.arimaWizardMainPage)
        self.etsWizardComboBoxTrendType.addItem("")
        self.etsWizardComboBoxTrendType.addItem("")
        self.etsWizardComboBoxTrendType.addItem("")
        self.etsWizardComboBoxTrendType.setObjectName(u"etsWizardComboBoxTrendType")

        self.verticalLayout_2.addWidget(self.etsWizardComboBoxTrendType)

        self.etsWizardComboBoxSeasonType = QComboBox(self.arimaWizardMainPage)
        self.etsWizardComboBoxSeasonType.addItem("")
        self.etsWizardComboBoxSeasonType.addItem("")
        self.etsWizardComboBoxSeasonType.addItem("")
        self.etsWizardComboBoxSeasonType.setObjectName(u"etsWizardComboBoxSeasonType")

        self.verticalLayout_2.addWidget(self.etsWizardComboBoxSeasonType)

        self.etsWizardSpinBoxSeasonLength = QSpinBox(self.arimaWizardMainPage)
        self.etsWizardSpinBoxSeasonLength.setObjectName(u"etsWizardSpinBoxSeasonLength")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.etsWizardSpinBoxSeasonLength.sizePolicy().hasHeightForWidth())
        self.etsWizardSpinBoxSeasonLength.setSizePolicy(sizePolicy2)
        self.etsWizardSpinBoxSeasonLength.setMinimum(1)
        self.etsWizardSpinBoxSeasonLength.setMaximum(100)

        self.verticalLayout_2.addWidget(self.etsWizardSpinBoxSeasonLength)

        self.etsWizardFadingTrendCheckBox = QCheckBox(self.arimaWizardMainPage)
        self.etsWizardFadingTrendCheckBox.setObjectName(u"etsWizardFadingTrendCheckBox")

        self.verticalLayout_2.addWidget(self.etsWizardFadingTrendCheckBox)

        self.etsWizardSpinBoxTestSplit = QSpinBox(self.arimaWizardMainPage)
        self.etsWizardSpinBoxTestSplit.setObjectName(u"etsWizardSpinBoxTestSplit")
        sizePolicy2.setHeightForWidth(self.etsWizardSpinBoxTestSplit.sizePolicy().hasHeightForWidth())
        self.etsWizardSpinBoxTestSplit.setSizePolicy(sizePolicy2)

        self.verticalLayout_2.addWidget(self.etsWizardSpinBoxTestSplit)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        EtsWizard.addPage(self.arimaWizardMainPage)

        self.retranslateUi(EtsWizard)

        QMetaObject.connectSlotsByName(EtsWizard)
    # setupUi

    def retranslateUi(self, EtsWizard):
        EtsWizard.setWindowTitle(QCoreApplication.translate("EtsWizard", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0430 ETS", None))
        self.label_4.setText(QCoreApplication.translate("EtsWizard", u"\u0422\u0438\u043f \u0442\u0440\u0435\u043d\u0434\u0430", None))
        self.label_2.setText(QCoreApplication.translate("EtsWizard", u"\u0422\u0438\u043f \u0441\u0435\u0437\u043e\u043d\u043d\u043e\u0441\u0442\u0438", None))
        self.label_3.setText(QCoreApplication.translate("EtsWizard", u"\u0414\u043b\u0438\u043d\u0430 \u0441\u0435\u0437\u043e\u043d\u0430", None))
        self.label_5.setText(QCoreApplication.translate("EtsWizard", u"\u0417\u0430\u0442\u0443\u0445\u0430\u044e\u0449\u0438\u0439 \u0442\u0440\u0435\u043d\u0434", None))
        self.label.setText(QCoreApplication.translate("EtsWizard", u"\u041f\u0440\u043e\u0446\u0435\u043d\u0442 \u043e\u0431\u0443\u0447\u0430\u044e\u0449\u0435\u0439 \u0432\u044b\u0431\u043e\u0440\u043a\u0438", None))
        self.etsWizardComboBoxTrendType.setItemText(0, QCoreApplication.translate("EtsWizard", u"\u041d\u0435\u0442", None))
        self.etsWizardComboBoxTrendType.setItemText(1, QCoreApplication.translate("EtsWizard", u"\u0410\u0434\u0434\u0438\u0442\u0438\u0432\u043d\u044b\u0439", None))
        self.etsWizardComboBoxTrendType.setItemText(2, QCoreApplication.translate("EtsWizard", u"\u041c\u0443\u043b\u044c\u0442\u0438\u043f\u043b\u0438\u043a\u0430\u0442\u0438\u0432\u043d\u044b\u0439", None))

        self.etsWizardComboBoxSeasonType.setItemText(0, QCoreApplication.translate("EtsWizard", u"\u041d\u0435\u0442", None))
        self.etsWizardComboBoxSeasonType.setItemText(1, QCoreApplication.translate("EtsWizard", u"\u0410\u0434\u0434\u0438\u0442\u0438\u0432\u043d\u0430\u044f", None))
        self.etsWizardComboBoxSeasonType.setItemText(2, QCoreApplication.translate("EtsWizard", u"\u041c\u0443\u043b\u044c\u0442\u0438\u043f\u043b\u0438\u043a\u0430\u0442\u0438\u0432\u043d\u0430\u044f", None))

        self.etsWizardFadingTrendCheckBox.setText("")
    # retranslateUi

