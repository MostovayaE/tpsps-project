# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'csvwizard.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpinBox, QStackedWidget, QVBoxLayout,
    QWidget, QWizard, QWizardPage)

class Ui_CSVWizard(object):
    def setupUi(self, CSVWizard):
        if not CSVWizard.objectName():
            CSVWizard.setObjectName(u"CSVWizard")
        CSVWizard.resize(400, 526)
        self.PageColumns = QWizardPage()
        self.PageColumns.setObjectName(u"PageColumns")
        self.verticalLayout = QVBoxLayout(self.PageColumns)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.PageColumns)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.comboBoxTimeCol = QComboBox(self.PageColumns)
        self.comboBoxTimeCol.setObjectName(u"comboBoxTimeCol")

        self.verticalLayout.addWidget(self.comboBoxTimeCol)

        self.label_2 = QLabel(self.PageColumns)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.comboBoxValCol = QComboBox(self.PageColumns)
        self.comboBoxValCol.setObjectName(u"comboBoxValCol")

        self.verticalLayout.addWidget(self.comboBoxValCol)

        CSVWizard.addPage(self.PageColumns)
        self.PageDateFormat = QWizardPage()
        self.PageDateFormat.setObjectName(u"PageDateFormat")
        self.horizontalLayout = QHBoxLayout(self.PageDateFormat)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelDateFormat = QLabel(self.PageDateFormat)
        self.labelDateFormat.setObjectName(u"labelDateFormat")

        self.horizontalLayout.addWidget(self.labelDateFormat)

        CSVWizard.addPage(self.PageDateFormat)
        self.PageFreq = QWizardPage()
        self.PageFreq.setObjectName(u"PageFreq")
        self.verticalLayout_2 = QVBoxLayout(self.PageFreq)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_3 = QLabel(self.PageFreq)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_2.addWidget(self.label_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_4 = QLabel(self.PageFreq)
        self.label_4.setObjectName(u"label_4")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.label_4)

        self.spinBoxFreq = QSpinBox(self.PageFreq)
        self.spinBoxFreq.setObjectName(u"spinBoxFreq")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinBoxFreq.sizePolicy().hasHeightForWidth())
        self.spinBoxFreq.setSizePolicy(sizePolicy1)
        self.spinBoxFreq.setMinimum(1)

        self.horizontalLayout_2.addWidget(self.spinBoxFreq)

        self.comboBoxFreq = QComboBox(self.PageFreq)
        self.comboBoxFreq.setObjectName(u"comboBoxFreq")

        self.horizontalLayout_2.addWidget(self.comboBoxFreq)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.stackAnchor = QStackedWidget(self.PageFreq)
        self.stackAnchor.setObjectName(u"stackAnchor")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.stackAnchor.sizePolicy().hasHeightForWidth())
        self.stackAnchor.setSizePolicy(sizePolicy2)
        self.pageAnchorNone = QWidget()
        self.pageAnchorNone.setObjectName(u"pageAnchorNone")
        self.stackAnchor.addWidget(self.pageAnchorNone)
        self.pageAnchorMonth = QWidget()
        self.pageAnchorMonth.setObjectName(u"pageAnchorMonth")
        self.horizontalLayout_4 = QHBoxLayout(self.pageAnchorMonth)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.comboAnchorMonth = QComboBox(self.pageAnchorMonth)
        self.comboAnchorMonth.setObjectName(u"comboAnchorMonth")

        self.horizontalLayout_4.addWidget(self.comboAnchorMonth)

        self.stackAnchor.addWidget(self.pageAnchorMonth)
        self.pageAnchorDay = QWidget()
        self.pageAnchorDay.setObjectName(u"pageAnchorDay")
        self.horizontalLayout_3 = QHBoxLayout(self.pageAnchorDay)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.comboAnchorDay = QComboBox(self.pageAnchorDay)
        self.comboAnchorDay.setObjectName(u"comboAnchorDay")

        self.horizontalLayout_3.addWidget(self.comboAnchorDay)

        self.stackAnchor.addWidget(self.pageAnchorDay)

        self.verticalLayout_2.addWidget(self.stackAnchor)

        self.labelFreqError = QLabel(self.PageFreq)
        self.labelFreqError.setObjectName(u"labelFreqError")

        self.verticalLayout_2.addWidget(self.labelFreqError)

        self.labelFreqPreview = QLabel(self.PageFreq)
        self.labelFreqPreview.setObjectName(u"labelFreqPreview")

        self.verticalLayout_2.addWidget(self.labelFreqPreview)

        CSVWizard.addPage(self.PageFreq)
        self.PageDupClearing = QWizardPage()
        self.PageDupClearing.setObjectName(u"PageDupClearing")
        self.verticalLayout_3 = QVBoxLayout(self.PageDupClearing)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.labelDupClearing = QLabel(self.PageDupClearing)
        self.labelDupClearing.setObjectName(u"labelDupClearing")

        self.verticalLayout_3.addWidget(self.labelDupClearing)

        CSVWizard.addPage(self.PageDupClearing)
        self.PageAlignByFreq = QWizardPage()
        self.PageAlignByFreq.setObjectName(u"PageAlignByFreq")
        self.verticalLayout_4 = QVBoxLayout(self.PageAlignByFreq)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.labelAlignByFreq = QLabel(self.PageAlignByFreq)
        self.labelAlignByFreq.setObjectName(u"labelAlignByFreq")

        self.verticalLayout_4.addWidget(self.labelAlignByFreq)

        CSVWizard.addPage(self.PageAlignByFreq)
        self.PageFixOutliers = QWizardPage()
        self.PageFixOutliers.setObjectName(u"PageFixOutliers")
        self.horizontalLayout_5 = QHBoxLayout(self.PageFixOutliers)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.labelFixOutliers = QLabel(self.PageFixOutliers)
        self.labelFixOutliers.setObjectName(u"labelFixOutliers")

        self.horizontalLayout_5.addWidget(self.labelFixOutliers)

        CSVWizard.addPage(self.PageFixOutliers)

        self.retranslateUi(CSVWizard)

        self.stackAnchor.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(CSVWizard)
    # setupUi

    def retranslateUi(self, CSVWizard):
        CSVWizard.setWindowTitle(QCoreApplication.translate("CSVWizard", u"\u041e\u0431\u0440\u0430\u0431\u043e\u0442\u043a\u0430 CSV", None))
        self.label.setText(QCoreApplication.translate("CSVWizard", u"\u041a\u043e\u043b\u043e\u043d\u043a\u0430 \u0432\u0440\u0435\u043c\u0435\u043d\u0438", None))
        self.label_2.setText(QCoreApplication.translate("CSVWizard", u"\u041a\u043e\u043b\u043e\u043d\u043a\u0430 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0439", None))
        self.labelDateFormat.setText(QCoreApplication.translate("CSVWizard", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("CSVWizard", u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u0443\u044e \u0447\u0430\u0441\u0442\u043e\u0442\u0443:", None))
        self.label_4.setText(QCoreApplication.translate("CSVWizard", u"\u041a\u0430\u0436\u0434\u044b\u0439", None))
        self.labelFreqError.setText(QCoreApplication.translate("CSVWizard", u"TextLabel", None))
        self.labelFreqPreview.setText(QCoreApplication.translate("CSVWizard", u"TextLabel", None))
        self.labelDupClearing.setText(QCoreApplication.translate("CSVWizard", u"DupClearing", None))
        self.labelAlignByFreq.setText(QCoreApplication.translate("CSVWizard", u"AlignByFreq", None))
        self.labelFixOutliers.setText(QCoreApplication.translate("CSVWizard", u"FixOutliers", None))
    # retranslateUi

