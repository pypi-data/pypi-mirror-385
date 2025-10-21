from typing import Any
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_Form:
    Form: QtWidgets.QWidget
    buttonBox: QtWidgets.QDialogButtonBox
    gridLayout: QtWidgets.QGridLayout
    groupBox: QtWidgets.QGroupBox
    label: QtWidgets.QLabel
    lineEdit: QtWidgets.QLineEdit
    toolButton: QtWidgets.QToolButton
    verticalLayout: QtWidgets.QVBoxLayout
    def setupUi(self, widget: QtWidgets.QWidget) -> None: ...
    def retranslateUi(self, widget: QtWidgets.QWidget) -> None: ...