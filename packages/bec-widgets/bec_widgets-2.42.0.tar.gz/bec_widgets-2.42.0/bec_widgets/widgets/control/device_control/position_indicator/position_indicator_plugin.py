# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

from qtpy.QtDesigner import QDesignerCustomWidgetInterface
from qtpy.QtWidgets import QWidget

from bec_widgets.utils.bec_designer import designer_material_icon
from bec_widgets.widgets.control.device_control.position_indicator.position_indicator import (
    PositionIndicator,
)

DOM_XML = """
<ui language='c++'>
    <widget class='PositionIndicator' name='position_indicator'>
    </widget>
</ui>
"""


class PositionIndicatorPlugin(QDesignerCustomWidgetInterface):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self._form_editor = None

    def createWidget(self, parent):
        if parent is None:
            return QWidget()
        t = PositionIndicator(parent)
        return t

    def domXml(self):
        return DOM_XML

    def group(self):
        return "BEC Utils"

    def icon(self):
        return designer_material_icon(PositionIndicator.ICON_NAME)

    def includeFile(self):
        return "position_indicator"

    def initialize(self, form_editor):
        self._form_editor = form_editor

    def isContainer(self):
        return False

    def isInitialized(self):
        return self._form_editor is not None

    def name(self):
        return "PositionIndicator"

    def toolTip(self):
        return ""

    def whatsThis(self):
        return self.toolTip()
