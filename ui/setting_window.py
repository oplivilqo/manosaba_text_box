# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_setting_windowtbKpGg.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialogButtonBox, QFormLayout, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QSizePolicy, QSlider,
    QSpacerItem, QTabWidget, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_SettingWindow(object):
    def setupUi(self, SettingWindow):
        if not SettingWindow.objectName():
            SettingWindow.setObjectName(u"SettingWindow")
        SettingWindow.resize(523, 698)
        SettingWindow.setMinimumSize(QSize(0, 150))
        self.verticalLayout = QVBoxLayout(SettingWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(SettingWindow)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setDocumentMode(False)
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.verticalLayout_3 = QVBoxLayout(self.tab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.scrollArea = QScrollArea(self.tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 477, 596))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_pasteCfg = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_pasteCfg.setObjectName(u"groupBox_pasteCfg")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_pasteCfg.sizePolicy().hasHeightForWidth())
        self.groupBox_pasteCfg.setSizePolicy(sizePolicy)
        self.groupBox_pasteCfg.setMinimumSize(QSize(0, 160))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_pasteCfg)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(20, -1, 20, 15)
        self.widget = QWidget(self.groupBox_pasteCfg)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.label_pasteModeSelect = QLabel(self.widget)
        self.label_pasteModeSelect.setObjectName(u"label_pasteModeSelect")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_pasteModeSelect.sizePolicy().hasHeightForWidth())
        self.label_pasteModeSelect.setSizePolicy(sizePolicy1)
        self.label_pasteModeSelect.setMinimumSize(QSize(80, 30))

        self.horizontalLayout.addWidget(self.label_pasteModeSelect)

        self.comboBox_pasteModeSelect = QComboBox(self.widget)
        self.comboBox_pasteModeSelect.setObjectName(u"comboBox_pasteModeSelect")
        self.comboBox_pasteModeSelect.setMinimumSize(QSize(0, 30))

        self.horizontalLayout.addWidget(self.comboBox_pasteModeSelect)


        self.verticalLayout_2.addWidget(self.widget)

        self.label_info1 = QLabel(self.groupBox_pasteCfg)
        self.label_info1.setObjectName(u"label_info1")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_info1.sizePolicy().hasHeightForWidth())
        self.label_info1.setSizePolicy(sizePolicy2)
        self.label_info1.setMinimumSize(QSize(80, 0))

        self.verticalLayout_2.addWidget(self.label_info1)

        self.label_info2 = QLabel(self.groupBox_pasteCfg)
        self.label_info2.setObjectName(u"label_info2")
        sizePolicy2.setHeightForWidth(self.label_info2.sizePolicy().hasHeightForWidth())
        self.label_info2.setSizePolicy(sizePolicy2)
        self.label_info2.setMinimumSize(QSize(80, 0))

        self.verticalLayout_2.addWidget(self.label_info2)

        self.label_info3 = QLabel(self.groupBox_pasteCfg)
        self.label_info3.setObjectName(u"label_info3")
        sizePolicy2.setHeightForWidth(self.label_info3.sizePolicy().hasHeightForWidth())
        self.label_info3.setSizePolicy(sizePolicy2)
        self.label_info3.setMinimumSize(QSize(80, 0))

        self.verticalLayout_2.addWidget(self.label_info3)


        self.verticalLayout_4.addWidget(self.groupBox_pasteCfg)

        self.groupBox_EmoMatch = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_EmoMatch.setObjectName(u"groupBox_EmoMatch")
        sizePolicy.setHeightForWidth(self.groupBox_EmoMatch.sizePolicy().hasHeightForWidth())
        self.groupBox_EmoMatch.setSizePolicy(sizePolicy)
        self.groupBox_EmoMatch.setMinimumSize(QSize(0, 250))
        self.formLayout_2 = QFormLayout(self.groupBox_EmoMatch)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setHorizontalSpacing(13)
        self.formLayout_2.setContentsMargins(20, -1, 20, 0)
        self.label_apiKey = QLabel(self.groupBox_EmoMatch)
        self.label_apiKey.setObjectName(u"label_apiKey")

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.LabelRole, self.label_apiKey)

        self.lineEdit_apiKey = QLineEdit(self.groupBox_EmoMatch)
        self.lineEdit_apiKey.setObjectName(u"lineEdit_apiKey")
        self.lineEdit_apiKey.setMinimumSize(QSize(0, 30))

        self.formLayout_2.setWidget(7, QFormLayout.ItemRole.FieldRole, self.lineEdit_apiKey)

        self.label_modelName = QLabel(self.groupBox_EmoMatch)
        self.label_modelName.setObjectName(u"label_modelName")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label_modelName.sizePolicy().hasHeightForWidth())
        self.label_modelName.setSizePolicy(sizePolicy3)

        self.formLayout_2.setWidget(10, QFormLayout.ItemRole.LabelRole, self.label_modelName)

        self.label_apiUrl = QLabel(self.groupBox_EmoMatch)
        self.label_apiUrl.setObjectName(u"label_apiUrl")

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.LabelRole, self.label_apiUrl)

        self.lineEdit_apiUrl = QLineEdit(self.groupBox_EmoMatch)
        self.lineEdit_apiUrl.setObjectName(u"lineEdit_apiUrl")
        self.lineEdit_apiUrl.setMinimumSize(QSize(0, 30))

        self.formLayout_2.setWidget(6, QFormLayout.ItemRole.FieldRole, self.lineEdit_apiUrl)

        self.label_modelSelect = QLabel(self.groupBox_EmoMatch)
        self.label_modelSelect.setObjectName(u"label_modelSelect")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_modelSelect)

        self.widget_2 = QWidget(self.groupBox_EmoMatch)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.comboBox_ModelSelect = QComboBox(self.widget_2)
        self.comboBox_ModelSelect.setObjectName(u"comboBox_ModelSelect")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(4)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.comboBox_ModelSelect.sizePolicy().hasHeightForWidth())
        self.comboBox_ModelSelect.setSizePolicy(sizePolicy4)

        self.horizontalLayout_2.addWidget(self.comboBox_ModelSelect)

        self.pushButton_testConn = QPushButton(self.widget_2)
        self.pushButton_testConn.setObjectName(u"pushButton_testConn")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy5.setHorizontalStretch(1)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.pushButton_testConn.sizePolicy().hasHeightForWidth())
        self.pushButton_testConn.setSizePolicy(sizePolicy5)
        self.pushButton_testConn.setMinimumSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.pushButton_testConn)


        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.widget_2)

        self.widget_4 = QWidget(self.groupBox_EmoMatch)
        self.widget_4.setObjectName(u"widget_4")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.comboBox_modelName = QComboBox(self.widget_4)
        self.comboBox_modelName.setObjectName(u"comboBox_modelName")
        sizePolicy4.setHeightForWidth(self.comboBox_modelName.sizePolicy().hasHeightForWidth())
        self.comboBox_modelName.setSizePolicy(sizePolicy4)

        self.horizontalLayout_4.addWidget(self.comboBox_modelName)

        self.pushButton_query = QPushButton(self.widget_4)
        self.pushButton_query.setObjectName(u"pushButton_query")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(1)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.pushButton_query.sizePolicy().hasHeightForWidth())
        self.pushButton_query.setSizePolicy(sizePolicy6)

        self.horizontalLayout_4.addWidget(self.pushButton_query)


        self.formLayout_2.setWidget(10, QFormLayout.ItemRole.FieldRole, self.widget_4)


        self.verticalLayout_4.addWidget(self.groupBox_EmoMatch)

        self.groupBox_ImgCompression = QGroupBox(self.scrollAreaWidgetContents)
        self.groupBox_ImgCompression.setObjectName(u"groupBox_ImgCompression")
        sizePolicy.setHeightForWidth(self.groupBox_ImgCompression.sizePolicy().hasHeightForWidth())
        self.groupBox_ImgCompression.setSizePolicy(sizePolicy)
        self.groupBox_ImgCompression.setMinimumSize(QSize(0, 125))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_ImgCompression)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(20, 20, 20, -1)
        self.checkBox_enableImgCompression = QCheckBox(self.groupBox_ImgCompression)
        self.checkBox_enableImgCompression.setObjectName(u"checkBox_enableImgCompression")

        self.verticalLayout_5.addWidget(self.checkBox_enableImgCompression)

        self.widget_3 = QWidget(self.groupBox_ImgCompression)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_pixelReductionProps = QLabel(self.widget_3)
        self.label_pixelReductionProps.setObjectName(u"label_pixelReductionProps")
        sizePolicy2.setHeightForWidth(self.label_pixelReductionProps.sizePolicy().hasHeightForWidth())
        self.label_pixelReductionProps.setSizePolicy(sizePolicy2)
        self.label_pixelReductionProps.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.label_pixelReductionProps)

        self.horizontalSlider_ReductionRatio = QSlider(self.widget_3)
        self.horizontalSlider_ReductionRatio.setObjectName(u"horizontalSlider_ReductionRatio")
        self.horizontalSlider_ReductionRatio.setMaximum(90)
        self.horizontalSlider_ReductionRatio.setValue(40)
        self.horizontalSlider_ReductionRatio.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_3.addWidget(self.horizontalSlider_ReductionRatio)

        self.label_ReductRate = QLabel(self.widget_3)
        self.label_ReductRate.setObjectName(u"label_ReductRate")
        sizePolicy2.setHeightForWidth(self.label_ReductRate.sizePolicy().hasHeightForWidth())
        self.label_ReductRate.setSizePolicy(sizePolicy2)
        self.label_ReductRate.setMinimumSize(QSize(20, 0))

        self.horizontalLayout_3.addWidget(self.label_ReductRate)


        self.verticalLayout_5.addWidget(self.widget_3)


        self.verticalLayout_4.addWidget(self.groupBox_ImgCompression)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_3.addWidget(self.scrollArea)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.verticalLayout_6 = QVBoxLayout(self.tab_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_info = QLabel(self.tab_2)
        self.label_info.setObjectName(u"label_info")
        self.label_info.setIndent(10)

        self.verticalLayout_6.addWidget(self.label_info)

        self.textEdit_processList = QTextEdit(self.tab_2)
        self.textEdit_processList.setObjectName(u"textEdit_processList")
        self.textEdit_processList.setFrameShape(QFrame.Shape.WinPanel)

        self.verticalLayout_6.addWidget(self.textEdit_processList)

        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_7 = QVBoxLayout(self.tab_3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.scrollArea_2 = QScrollArea(self.tab_3)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 465, 712))
        self.verticalLayout_8 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.groupBox_ctrlKeys = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_ctrlKeys.setObjectName(u"groupBox_ctrlKeys")
        self.gridLayout = QGridLayout(self.groupBox_ctrlKeys)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setContentsMargins(20, -1, 20, -1)
        self.label_geneTrigger = QLabel(self.groupBox_ctrlKeys)
        self.label_geneTrigger.setObjectName(u"label_geneTrigger")

        self.gridLayout.addWidget(self.label_geneTrigger, 0, 0, 1, 1)

        self.lineEdit_generateImgKey = QLineEdit(self.groupBox_ctrlKeys)
        self.lineEdit_generateImgKey.setObjectName(u"lineEdit_generateImgKey")
        self.lineEdit_generateImgKey.setMinimumSize(QSize(0, 30))

        self.gridLayout.addWidget(self.lineEdit_generateImgKey, 0, 1, 1, 1)

        self.pushButton_modifiy1 = QPushButton(self.groupBox_ctrlKeys)
        self.pushButton_modifiy1.setObjectName(u"pushButton_modifiy1")

        self.gridLayout.addWidget(self.pushButton_modifiy1, 0, 2, 1, 1)

        self.label_listenCtrl = QLabel(self.groupBox_ctrlKeys)
        self.label_listenCtrl.setObjectName(u"label_listenCtrl")

        self.gridLayout.addWidget(self.label_listenCtrl, 1, 0, 1, 1)

        self.lineEdit_listenerCtrlKey = QLineEdit(self.groupBox_ctrlKeys)
        self.lineEdit_listenerCtrlKey.setObjectName(u"lineEdit_listenerCtrlKey")
        self.lineEdit_listenerCtrlKey.setMinimumSize(QSize(0, 30))

        self.gridLayout.addWidget(self.lineEdit_listenerCtrlKey, 1, 1, 1, 1)

        self.pushButton_modify2 = QPushButton(self.groupBox_ctrlKeys)
        self.pushButton_modify2.setObjectName(u"pushButton_modify2")

        self.gridLayout.addWidget(self.pushButton_modify2, 1, 2, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_ctrlKeys)

        self.groupBox_charaSwitch = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_charaSwitch.setObjectName(u"groupBox_charaSwitch")
        self.gridLayout_2 = QGridLayout(self.groupBox_charaSwitch)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setHorizontalSpacing(10)
        self.gridLayout_2.setContentsMargins(20, -1, 20, -1)
        self.label_previChara = QLabel(self.groupBox_charaSwitch)
        self.label_previChara.setObjectName(u"label_previChara")

        self.gridLayout_2.addWidget(self.label_previChara, 0, 0, 1, 1)

        self.lineEdit_previCharaKey = QLineEdit(self.groupBox_charaSwitch)
        self.lineEdit_previCharaKey.setObjectName(u"lineEdit_previCharaKey")
        self.lineEdit_previCharaKey.setMinimumSize(QSize(0, 30))

        self.gridLayout_2.addWidget(self.lineEdit_previCharaKey, 0, 1, 1, 1)

        self.pushButton_modify3 = QPushButton(self.groupBox_charaSwitch)
        self.pushButton_modify3.setObjectName(u"pushButton_modify3")

        self.gridLayout_2.addWidget(self.pushButton_modify3, 0, 2, 1, 1)

        self.label_nextChara = QLabel(self.groupBox_charaSwitch)
        self.label_nextChara.setObjectName(u"label_nextChara")

        self.gridLayout_2.addWidget(self.label_nextChara, 1, 0, 1, 1)

        self.lineEdit_nextCharaKey = QLineEdit(self.groupBox_charaSwitch)
        self.lineEdit_nextCharaKey.setObjectName(u"lineEdit_nextCharaKey")
        self.lineEdit_nextCharaKey.setMinimumSize(QSize(0, 30))

        self.gridLayout_2.addWidget(self.lineEdit_nextCharaKey, 1, 1, 1, 1)

        self.pushButton_modify4 = QPushButton(self.groupBox_charaSwitch)
        self.pushButton_modify4.setObjectName(u"pushButton_modify4")

        self.gridLayout_2.addWidget(self.pushButton_modify4, 1, 2, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_charaSwitch)

        self.groupBox_emoSwitch = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_emoSwitch.setObjectName(u"groupBox_emoSwitch")
        self.gridLayout_3 = QGridLayout(self.groupBox_emoSwitch)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setHorizontalSpacing(10)
        self.gridLayout_3.setContentsMargins(20, -1, 20, -1)
        self.label_previEmo = QLabel(self.groupBox_emoSwitch)
        self.label_previEmo.setObjectName(u"label_previEmo")

        self.gridLayout_3.addWidget(self.label_previEmo, 0, 0, 1, 1)

        self.lineEdit_previEmoKey = QLineEdit(self.groupBox_emoSwitch)
        self.lineEdit_previEmoKey.setObjectName(u"lineEdit_previEmoKey")
        self.lineEdit_previEmoKey.setMinimumSize(QSize(0, 30))

        self.gridLayout_3.addWidget(self.lineEdit_previEmoKey, 0, 1, 1, 1)

        self.pushButton_modify5 = QPushButton(self.groupBox_emoSwitch)
        self.pushButton_modify5.setObjectName(u"pushButton_modify5")

        self.gridLayout_3.addWidget(self.pushButton_modify5, 0, 2, 1, 1)

        self.label_nextEmo = QLabel(self.groupBox_emoSwitch)
        self.label_nextEmo.setObjectName(u"label_nextEmo")

        self.gridLayout_3.addWidget(self.label_nextEmo, 1, 0, 1, 1)

        self.lineEdit_nextEmoKey = QLineEdit(self.groupBox_emoSwitch)
        self.lineEdit_nextEmoKey.setObjectName(u"lineEdit_nextEmoKey")
        self.lineEdit_nextEmoKey.setMinimumSize(QSize(0, 30))

        self.gridLayout_3.addWidget(self.lineEdit_nextEmoKey, 1, 1, 1, 1)

        self.pushButton_modify6 = QPushButton(self.groupBox_emoSwitch)
        self.pushButton_modify6.setObjectName(u"pushButton_modify6")

        self.gridLayout_3.addWidget(self.pushButton_modify6, 1, 2, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_emoSwitch)

        self.groupBox_bgSwitch = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_bgSwitch.setObjectName(u"groupBox_bgSwitch")
        self.gridLayout_4 = QGridLayout(self.groupBox_bgSwitch)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setHorizontalSpacing(10)
        self.gridLayout_4.setContentsMargins(20, -1, 20, -1)
        self.lineEdit_previBgKey = QLineEdit(self.groupBox_bgSwitch)
        self.lineEdit_previBgKey.setObjectName(u"lineEdit_previBgKey")
        self.lineEdit_previBgKey.setMinimumSize(QSize(0, 30))

        self.gridLayout_4.addWidget(self.lineEdit_previBgKey, 0, 1, 1, 1)

        self.lineEdit_nextBgKey = QLineEdit(self.groupBox_bgSwitch)
        self.lineEdit_nextBgKey.setObjectName(u"lineEdit_nextBgKey")
        self.lineEdit_nextBgKey.setMinimumSize(QSize(0, 30))

        self.gridLayout_4.addWidget(self.lineEdit_nextBgKey, 1, 1, 1, 1)

        self.label_previBg = QLabel(self.groupBox_bgSwitch)
        self.label_previBg.setObjectName(u"label_previBg")

        self.gridLayout_4.addWidget(self.label_previBg, 0, 0, 1, 1)

        self.pushButton_modify8 = QPushButton(self.groupBox_bgSwitch)
        self.pushButton_modify8.setObjectName(u"pushButton_modify8")

        self.gridLayout_4.addWidget(self.pushButton_modify8, 1, 2, 1, 1)

        self.pushButton_modify7 = QPushButton(self.groupBox_bgSwitch)
        self.pushButton_modify7.setObjectName(u"pushButton_modify7")

        self.gridLayout_4.addWidget(self.pushButton_modify7, 0, 2, 1, 1)

        self.label_nextBg = QLabel(self.groupBox_bgSwitch)
        self.label_nextBg.setObjectName(u"label_nextBg")

        self.gridLayout_4.addWidget(self.label_nextBg, 1, 0, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_bgSwitch)

        self.groupBox_quickChara = QGroupBox(self.scrollAreaWidgetContents_2)
        self.groupBox_quickChara.setObjectName(u"groupBox_quickChara")
        self.formLayout = QFormLayout(self.groupBox_quickChara)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setHorizontalSpacing(20)
        self.formLayout.setContentsMargins(20, -1, 20, -1)
        self.label_chara1 = QLabel(self.groupBox_quickChara)
        self.label_chara1.setObjectName(u"label_chara1")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_chara1)

        self.comboBox_Chara1 = QComboBox(self.groupBox_quickChara)
        self.comboBox_Chara1.setObjectName(u"comboBox_Chara1")
        self.comboBox_Chara1.setMinimumSize(QSize(0, 30))

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox_Chara1)

        self.label_chara2 = QLabel(self.groupBox_quickChara)
        self.label_chara2.setObjectName(u"label_chara2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_chara2)

        self.comboBox_Chara2 = QComboBox(self.groupBox_quickChara)
        self.comboBox_Chara2.setObjectName(u"comboBox_Chara2")
        self.comboBox_Chara2.setMinimumSize(QSize(0, 30))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBox_Chara2)

        self.label_chara3 = QLabel(self.groupBox_quickChara)
        self.label_chara3.setObjectName(u"label_chara3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_chara3)

        self.label_chara6 = QLabel(self.groupBox_quickChara)
        self.label_chara6.setObjectName(u"label_chara6")

        self.formLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.label_chara6)

        self.label_chara5 = QLabel(self.groupBox_quickChara)
        self.label_chara5.setObjectName(u"label_chara5")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_chara5)

        self.label_chara4 = QLabel(self.groupBox_quickChara)
        self.label_chara4.setObjectName(u"label_chara4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_chara4)

        self.comboBox_Chara3 = QComboBox(self.groupBox_quickChara)
        self.comboBox_Chara3.setObjectName(u"comboBox_Chara3")
        self.comboBox_Chara3.setMinimumSize(QSize(0, 30))

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboBox_Chara3)

        self.comboBox_Chara4 = QComboBox(self.groupBox_quickChara)
        self.comboBox_Chara4.setObjectName(u"comboBox_Chara4")
        self.comboBox_Chara4.setMinimumSize(QSize(0, 30))

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.comboBox_Chara4)

        self.comboBox_Chara5 = QComboBox(self.groupBox_quickChara)
        self.comboBox_Chara5.setObjectName(u"comboBox_Chara5")
        self.comboBox_Chara5.setMinimumSize(QSize(0, 30))

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.comboBox_Chara5)

        self.comboBox_Chara6 = QComboBox(self.groupBox_quickChara)
        self.comboBox_Chara6.setObjectName(u"comboBox_Chara6")
        self.comboBox_Chara6.setMinimumSize(QSize(0, 30))

        self.formLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.comboBox_Chara6)


        self.verticalLayout_8.addWidget(self.groupBox_quickChara)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_7.addWidget(self.scrollArea_2)

        self.tabWidget.addTab(self.tab_3, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(SettingWindow)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(SettingWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SettingWindow)
    # setupUi

    def retranslateUi(self, SettingWindow):
        SettingWindow.setWindowTitle(QCoreApplication.translate("SettingWindow", u"\u8bbe\u7f6e", None))
        self.groupBox_pasteCfg.setTitle(QCoreApplication.translate("SettingWindow", u"\u526a\u5207\u8bbe\u7f6e", None))
        self.label_pasteModeSelect.setText(QCoreApplication.translate("SettingWindow", u"\u526a\u5207\u6a21\u5f0f", None))
        self.label_info1.setText(QCoreApplication.translate("SettingWindow", u"\u5168\u9009\u526a\u5207\uff1a   \u4f7f\u7528Ctrl+A\u4ee5\u53caCtrl+X\u526a\u5207\u8d70\u6240\u6709\u5185\u5bb9", None))
        self.label_info2.setText(QCoreApplication.translate("SettingWindow", u"\u5355\u884c\u526a\u5207\uff1a   \u4f7f\u7528End\u4ee5\u53caShift+Home\u9009\u4e2d\u5e76\u526a\u5207\u8d70\u5f53\u524d\u884c", None))
        self.label_info3.setText(QCoreApplication.translate("SettingWindow", u"\u76f4\u63a5\u526a\u5207\uff1a   \u526a\u5207\u8d70\u5f53\u524d\u624b\u52a8\u9009\u62e9\u7684\u5185\u5bb9", None))
        self.groupBox_EmoMatch.setTitle(QCoreApplication.translate("SettingWindow", u"\u60c5\u611f\u5339\u914d", None))
        self.label_apiKey.setText(QCoreApplication.translate("SettingWindow", u"API Key", None))
        self.label_modelName.setText(QCoreApplication.translate("SettingWindow", u"\u6a21\u578b\u540d\u79f0", None))
        self.label_apiUrl.setText(QCoreApplication.translate("SettingWindow", u"API\u5730\u5740", None))
        self.label_modelSelect.setText(QCoreApplication.translate("SettingWindow", u"\u6a21\u578b\u9009\u62e9", None))
        self.pushButton_testConn.setText(QCoreApplication.translate("SettingWindow", u"\u6d4b\u8bd5\u8fde\u63a5", None))
        self.pushButton_query.setText(QCoreApplication.translate("SettingWindow", u"\u67e5\u8be2", None))
        self.groupBox_ImgCompression.setTitle(QCoreApplication.translate("SettingWindow", u"\u56fe\u7247\u538b\u7f29", None))
        self.checkBox_enableImgCompression.setText(QCoreApplication.translate("SettingWindow", u"\u542f\u7528\u56fe\u50cf\u538b\u7f29", None))
        self.label_pixelReductionProps.setText(QCoreApplication.translate("SettingWindow", u"\u50cf\u7d20\u524a\u51cf\u6bd4\u4f8b", None))
        self.label_ReductRate.setText(QCoreApplication.translate("SettingWindow", u"40%", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("SettingWindow", u"\u5e38\u89c4\u8bbe\u7f6e", None))
        self.label_info.setText(QCoreApplication.translate("SettingWindow", u"\u6bcf\u884c\u4e00\u4e2a\u8fdb\u7a0b\u540d", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("SettingWindow", u"\u8fdb\u7a0b\u767d\u540d\u5355", None))
        self.groupBox_ctrlKeys.setTitle(QCoreApplication.translate("SettingWindow", u"\u63a7\u5236\u6309\u952e", None))
        self.label_geneTrigger.setText(QCoreApplication.translate("SettingWindow", u"\u89e6\u53d1\u56fe\u7247\u751f\u6210", None))
        self.pushButton_modifiy1.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.label_listenCtrl.setText(QCoreApplication.translate("SettingWindow", u"\u542f\u505c\u6309\u952e\u76d1\u542c", None))
        self.pushButton_modify2.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.groupBox_charaSwitch.setTitle(QCoreApplication.translate("SettingWindow", u"\u89d2\u8272\u5207\u6362", None))
        self.label_previChara.setText(QCoreApplication.translate("SettingWindow", u"\u5411\u524d\u5207\u6362\u89d2\u8272", None))
        self.pushButton_modify3.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.label_nextChara.setText(QCoreApplication.translate("SettingWindow", u"\u5411\u540e\u5207\u6362\u89d2\u8272", None))
        self.pushButton_modify4.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.groupBox_emoSwitch.setTitle(QCoreApplication.translate("SettingWindow", u"\u8868\u60c5\u5207\u6362", None))
        self.label_previEmo.setText(QCoreApplication.translate("SettingWindow", u"\u5411\u524d\u5207\u6362\u8868\u60c5", None))
        self.pushButton_modify5.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.label_nextEmo.setText(QCoreApplication.translate("SettingWindow", u"\u5411\u540e\u5207\u6362\u8868\u60c5", None))
        self.pushButton_modify6.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.groupBox_bgSwitch.setTitle(QCoreApplication.translate("SettingWindow", u"\u80cc\u666f\u5207\u6362", None))
        self.label_previBg.setText(QCoreApplication.translate("SettingWindow", u"\u5411\u524d\u5207\u6362\u80cc\u666f", None))
        self.pushButton_modify8.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.pushButton_modify7.setText(QCoreApplication.translate("SettingWindow", u"\u4fee\u6539", None))
        self.label_nextBg.setText(QCoreApplication.translate("SettingWindow", u"\u5411\u540e\u5207\u6362\u80cc\u666f", None))
        self.groupBox_quickChara.setTitle(QCoreApplication.translate("SettingWindow", u"\u89d2\u8272\u5feb\u901f\u5207\u6362", None))
        self.label_chara1.setText(QCoreApplication.translate("SettingWindow", u"\u89d2\u82721", None))
        self.label_chara2.setText(QCoreApplication.translate("SettingWindow", u"\u89d2\u82722", None))
        self.label_chara3.setText(QCoreApplication.translate("SettingWindow", u"\u89d2\u82723", None))
        self.label_chara6.setText(QCoreApplication.translate("SettingWindow", u"\u89d2\u82726", None))
        self.label_chara5.setText(QCoreApplication.translate("SettingWindow", u"\u89d2\u82725", None))
        self.label_chara4.setText(QCoreApplication.translate("SettingWindow", u"\u89d2\u82724", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("SettingWindow", u"\u5feb\u6377\u952e\u7f16\u8f91", None))
    # retranslateUi

