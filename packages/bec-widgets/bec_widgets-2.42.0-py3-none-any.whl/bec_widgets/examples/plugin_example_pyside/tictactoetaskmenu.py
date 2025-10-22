# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from qtpy.QtDesigner import QExtensionFactory, QPyDesignerTaskMenuExtension
from qtpy.QtGui import QAction
from qtpy.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from bec_widgets.examples.plugin_example_pyside.tictactoe import TicTacToe
from bec_widgets.utils.error_popups import SafeSlot as Slot


class TicTacToeDialog(QDialog):  # pragma: no cover
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._ticTacToe = TicTacToe(self)
        layout.addWidget(self._ticTacToe)
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        reset_button = button_box.button(QDialogButtonBox.Reset)
        reset_button.clicked.connect(self._ticTacToe.clear_board)
        layout.addWidget(button_box)

    def set_state(self, new_state):
        self._ticTacToe.setState(new_state)

    def state(self):
        return self._ticTacToe.state


class TicTacToeTaskMenu(QPyDesignerTaskMenuExtension):
    def __init__(self, ticTacToe, parent):
        super().__init__(parent)
        self._ticTacToe = ticTacToe
        self._edit_state_action = QAction("Edit State...", None)
        self._edit_state_action.triggered.connect(self._edit_state)

    def taskActions(self):
        return [self._edit_state_action]

    def preferredEditAction(self):
        return self._edit_state_action

    @Slot()
    def _edit_state(self):
        dialog = TicTacToeDialog(self._ticTacToe)
        dialog.set_state(self._ticTacToe.state)
        if dialog.exec() == QDialog.Accepted:
            self._ticTacToe.state = dialog.state()


class TicTacToeTaskMenuFactory(QExtensionFactory):
    def __init__(self, extension_manager):
        super().__init__(extension_manager)

    @staticmethod
    def task_menu_iid():
        return "org.qt-project.Qt.Designer.TaskMenu"

    def createExtension(self, object, iid, parent):
        if iid != TicTacToeTaskMenuFactory.task_menu_iid():
            return None
        if object.__class__.__name__ != "TicTacToe":
            return None
        return TicTacToeTaskMenu(object, parent)
