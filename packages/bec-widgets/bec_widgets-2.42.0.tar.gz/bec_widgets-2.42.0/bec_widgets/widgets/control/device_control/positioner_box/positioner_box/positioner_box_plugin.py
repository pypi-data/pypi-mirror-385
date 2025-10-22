# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from qtpy.QtDesigner import QDesignerCustomWidgetInterface
from qtpy.QtWidgets import QWidget

from bec_widgets.utils.bec_designer import designer_material_icon
from bec_widgets.widgets.control.device_control.positioner_box.positioner_box.positioner_box import (
    PositionerBox,
)

DOM_XML = """
<ui language='c++'>
    <widget class='PositionerBox' name='positioner_box'>
    </widget>
</ui>
"""


class PositionerBoxPlugin(QDesignerCustomWidgetInterface):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        if parent is None:
            return QWidget()
        t = PositionerBox(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return "BEC Device Control"

    def icon(self):
        return designer_material_icon(PositionerBox.ICON_NAME)

    def includeFile(self):
        return "positioner_box"

    def initialize(self, form_editor):
        self._form_editor = form_editor

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return "PositionerBox"

    def toolTip(self):
        return "Simple Widget to control a positioner in box form"

    def whatsThis(self):
        return self.toolTip()
