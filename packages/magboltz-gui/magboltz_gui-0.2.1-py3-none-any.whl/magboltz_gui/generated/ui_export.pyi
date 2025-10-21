from typing import Any
from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_Dialog:
    Dialog: QtWidgets.QDialog
    buttonBox: QtWidgets.QDialogButtonBox
    groupBox: QtWidgets.QGroupBox
    label: QtWidgets.QLabel
    line: QtWidgets.QFrame
    line_2: QtWidgets.QFrame
    radioButton: QtWidgets.QRadioButton
    radioButton_2: QtWidgets.QRadioButton
    verticalLayout: QtWidgets.QVBoxLayout
    verticalLayout_2: QtWidgets.QVBoxLayout
    verticalLayout_3: QtWidgets.QVBoxLayout
    verticalSpacer: QtWidgets.QSpacerItem
    def setupUi(self, widget: QtWidgets.QDialog) -> None: ...
    def retranslateUi(self, widget: QtWidgets.QDialog) -> None: ...