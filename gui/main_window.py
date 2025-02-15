# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/main_window.ui'
#
# Created: Thu May  8 15:57:16 2014
# by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(804, 736)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainTabs = QtGui.QTabWidget(self.centralwidget)
        self.mainTabs.setObjectName("mainTabs")
        self.singleTab = QtGui.QWidget()
        self.singleTab.setObjectName("singleTab")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.singleTab)
        self.verticalLayout_6.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label = QtGui.QLabel(self.singleTab)
        self.label.setObjectName("label")
        self.verticalLayout_6.addWidget(self.label)
        self.file_holder = QtGui.QWidget(self.singleTab)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.file_holder.sizePolicy().hasHeightForWidth())
        self.file_holder.setSizePolicy(sizePolicy)
        self.file_holder.setObjectName("file_holder")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.file_holder)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.input = QtGui.QTextEdit(self.file_holder)
        self.input.setMaximumSize(QtCore.QSize(16777215, 25))
        self.input.setObjectName("input")
        self.horizontalLayout_4.addWidget(self.input)
        self.filechooser = QtGui.QPushButton(self.file_holder)
        self.filechooser.setMaximumSize(QtCore.QSize(16777215, 25))
        self.filechooser.setObjectName("filechooser")
        self.horizontalLayout_4.addWidget(self.filechooser)
        self.verticalLayout_6.addWidget(self.file_holder)
        self.runner = QtGui.QPushButton(self.singleTab)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.runner.sizePolicy().hasHeightForWidth())
        self.runner.setSizePolicy(sizePolicy)
        self.runner.setObjectName("runner")
        self.verticalLayout_6.addWidget(self.runner)
        self.tabs = QtGui.QTabWidget(self.singleTab)
        self.tabs.setObjectName("tabs")
        self.output_tab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.output_tab.sizePolicy().hasHeightForWidth())
        self.output_tab.setSizePolicy(sizePolicy)
        self.output_tab.setAcceptDrops(False)
        self.output_tab.setObjectName("output_tab")
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.output_tab)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.scrollOutput = QtGui.QScrollArea(self.output_tab)
        self.scrollOutput.setWidgetResizable(True)
        self.scrollOutput.setObjectName("scrollOutput")
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 758, 496))
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth()
        )
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.out = QtGui.QTextBrowser(self.scrollAreaWidgetContents)
        self.out.setObjectName("out")
        self.verticalLayout_3.addWidget(self.out)
        self.scrollOutput.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_2.addWidget(self.scrollOutput)
        self.tabs.addTab(self.output_tab, "")
        self.error_tab = QtGui.QWidget()
        self.error_tab.setObjectName("error_tab")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.error_tab)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.scrollArea_2 = QtGui.QScrollArea(self.error_tab)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 758, 496))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.errors = QtGui.QTextBrowser(self.scrollAreaWidgetContents_2)
        self.errors.setObjectName("errors")
        self.verticalLayout_5.addWidget(self.errors)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.verticalLayout_4.addWidget(self.scrollArea_2)
        self.tabs.addTab(self.error_tab, "")
        self.verticalLayout_6.addWidget(self.tabs)
        self.resultsWidget = QtGui.QWidget(self.singleTab)
        self.resultsWidget.setEnabled(False)
        self.resultsWidget.setObjectName("resultsWidget")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.resultsWidget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.openLink = QtGui.QPushButton(self.resultsWidget)
        self.openLink.setObjectName("openLink")
        self.horizontalLayout_3.addWidget(self.openLink)
        self.openFolder = QtGui.QPushButton(self.resultsWidget)
        self.openFolder.setObjectName("openFolder")
        self.horizontalLayout_3.addWidget(self.openFolder)
        self.verticalLayout_6.addWidget(self.resultsWidget)
        self.mainTabs.addTab(self.singleTab, "")
        self.multipleTab = QtGui.QWidget()
        self.multipleTab.setEnabled(True)
        self.multipleTab.setObjectName("multipleTab")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.multipleTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtGui.QLabel(self.multipleTab)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.folder_holder = QtGui.QWidget(self.multipleTab)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.folder_holder.sizePolicy().hasHeightForWidth()
        )
        self.folder_holder.setSizePolicy(sizePolicy)
        self.folder_holder.setObjectName("folder_holder")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.folder_holder)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.input_multiple = QtGui.QTextEdit(self.folder_holder)
        self.input_multiple.setMaximumSize(QtCore.QSize(16777215, 25))
        self.input_multiple.setObjectName("input_multiple")
        self.horizontalLayout_5.addWidget(self.input_multiple)
        self.folderchooser = QtGui.QPushButton(self.folder_holder)
        self.folderchooser.setObjectName("folderchooser")
        self.horizontalLayout_5.addWidget(self.folderchooser)
        self.verticalLayout_2.addWidget(self.folder_holder)
        self.multipleExecute = QtGui.QPushButton(self.multipleTab)
        self.multipleExecute.setObjectName("multipleExecute")
        self.verticalLayout_2.addWidget(self.multipleExecute)
        self.tableWidget = QtGui.QTableWidget(self.multipleTab)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.mainTabs.addTab(self.multipleTab, "")
        self.verticalLayout.addWidget(self.mainTabs)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.mainTabs.setCurrentIndex(0)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QtGui.QApplication.translate(
                "MainWindow", "ScriptLattes", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.label.setText(
            QtGui.QApplication.translate(
                "MainWindow",
                "Escolha um arquivo de configuração",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.filechooser.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Escolher", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.runner.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Executar", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.tabs.setTabText(
            self.tabs.indexOf(self.output_tab),
            QtGui.QApplication.translate(
                "MainWindow", "Saída", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
        self.tabs.setTabText(
            self.tabs.indexOf(self.error_tab),
            QtGui.QApplication.translate(
                "MainWindow", "Erros", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
        self.openLink.setText(
            QtGui.QApplication.translate(
                "MainWindow",
                "Abrir resultados no navegador",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.openFolder.setText(
            QtGui.QApplication.translate(
                "MainWindow",
                "Abrir pasta de saída",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.singleTab),
            QtGui.QApplication.translate(
                "MainWindow", "Arquivo único", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
        self.label_2.setText(
            QtGui.QApplication.translate(
                "MainWindow",
                "Escolha uma pasta com arquivos de configuração (*.config). Os arquivos podem estar em sub-pastas.",
                None,
                QtGui.QApplication.UnicodeUTF8,
            )
        )
        self.folderchooser.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Escolher", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.multipleExecute.setText(
            QtGui.QApplication.translate(
                "MainWindow", "Executar lote", None, QtGui.QApplication.UnicodeUTF8
            )
        )
        self.mainTabs.setTabText(
            self.mainTabs.indexOf(self.multipleTab),
            QtGui.QApplication.translate(
                "MainWindow", "Múltiplos arquivos", None, QtGui.QApplication.UnicodeUTF8
            ),
        )
