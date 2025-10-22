from typing import Literal, Sequence

from bec_lib.logger import bec_logger
from bec_qthemes import material_icon
from qtpy.QtCore import Property, Qt, Signal, Slot
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from bec_widgets.utils.widget_io import WidgetIO
from bec_widgets.widgets.control.device_input.base_classes.device_input_base import BECDeviceFilter
from bec_widgets.widgets.control.device_input.device_line_edit.device_line_edit import (
    DeviceLineEdit,
)

logger = bec_logger.logger


class ScanArgType:
    DEVICE = "device"
    FLOAT = "float"
    INT = "int"
    BOOL = "bool"
    STR = "str"
    DEVICEBASE = "DeviceBase"
    LITERALS_DICT = "dict"  # Used when the type is provided as a dict with Literal key


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        layout = QFormLayout()

        self.precision_spin_box = QSpinBox()
        self.precision_spin_box.setRange(
            -2147483647, 2147483647
        )  # 2147483647 is the largest int which qt allows

        self.step_size_spin_box = QDoubleSpinBox()
        self.step_size_spin_box.setRange(-float("inf"), float("inf"))

        fixed_width = 80
        self.precision_spin_box.setFixedWidth(fixed_width)
        self.step_size_spin_box.setFixedWidth(fixed_width)

        layout.addRow("Decimal Precision:", self.precision_spin_box)
        layout.addRow("Step Size:", self.step_size_spin_box)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def getValues(self):
        return self.precision_spin_box.value(), self.step_size_spin_box.value()


class ScanSpinBox(QSpinBox):
    def __init__(
        self, parent=None, arg_name: str = None, default: int | None = None, *args, **kwargs
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.arg_name = arg_name
        self.setRange(-2147483647, 2147483647)  # 2147483647 is the largest int which qt allows
        if default is not None:
            self.setValue(default)


class ScanLiteralsComboBox(QComboBox):
    def __init__(
        self, parent=None, arg_name: str | None = None, default: str | None = None, *args, **kwargs
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.arg_name = arg_name
        self.default = default
        if default is not None:
            self.setCurrentText(default)

    def set_literals(self, literals: Sequence[str | int | float | None]) -> None:
        """
        Set the list of literals for the combo box.

        Args:
            literals: List of literal values (can be strings, integers, floats or None)
        """
        self.clear()
        literals = set(literals)  # Remove duplicates
        if None in literals:
            literals.remove(None)
            self.addItem("")

        self.addItems([str(value) for value in literals])

        # find index of the default value
        index = max(self.findText(str(self.default)), 0)
        self.setCurrentIndex(index)

    def get_value(self) -> str | None:
        return self.currentText() if self.currentText() else None


class ScanDoubleSpinBox(QDoubleSpinBox):
    def __init__(
        self, parent=None, arg_name: str = None, default: float | None = None, *args, **kwargs
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.arg_name = arg_name
        self.setRange(-float("inf"), float("inf"))
        if default is not None:
            self.setValue(default)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showSettingsDialog)

        self.setToolTip("Right click to open settings dialog for decimal precision and step size.")

    def showSettingsDialog(self):
        dialog = SettingsDialog(self)
        dialog.precision_spin_box.setValue(self.decimals())
        dialog.step_size_spin_box.setValue(self.singleStep())

        if dialog.exec_() == QDialog.Accepted:
            precision, step_size = dialog.getValues()
            self.setDecimals(precision)
            self.setSingleStep(step_size)


class ScanLineEdit(QLineEdit):
    def __init__(
        self, parent=None, arg_name: str = None, default: str | None = None, *args, **kwargs
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.arg_name = arg_name
        if default is not None:
            self.setText(default)


class ScanCheckBox(QCheckBox):
    def __init__(
        self, parent=None, arg_name: str = None, default: bool | None = None, *args, **kwargs
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.arg_name = arg_name
        if default is not None:
            self.setChecked(default)


class ScanGroupBox(QGroupBox):
    WIDGET_HANDLER = {
        ScanArgType.DEVICE: DeviceLineEdit,
        ScanArgType.DEVICEBASE: DeviceLineEdit,
        ScanArgType.FLOAT: ScanDoubleSpinBox,
        ScanArgType.INT: ScanSpinBox,
        ScanArgType.BOOL: ScanCheckBox,
        ScanArgType.STR: ScanLineEdit,
        ScanArgType.LITERALS_DICT: ScanLiteralsComboBox,
    }

    device_selected = Signal(str)

    def __init__(
        self,
        parent=None,
        box_type=Literal["args", "kwargs"],
        config: dict | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(parent=parent, *args, **kwargs)
        self.config = config
        self.box_type = box_type
        self._hide_add_remove_buttons = False

        vbox_layout = QVBoxLayout(self)
        hbox_layout = QHBoxLayout()
        vbox_layout.addLayout(hbox_layout)
        self.layout = QGridLayout(self)
        vbox_layout.addLayout(self.layout)

        # Add bundle button
        self.button_add_bundle = QPushButton(self)
        self.button_add_bundle.setIcon(
            material_icon(icon_name="add", size=(15, 15), convert_to_pixmap=False)
        )
        # Remove bundle button
        self.button_remove_bundle = QPushButton(self)
        self.button_remove_bundle.setIcon(
            material_icon(icon_name="remove", size=(15, 15), convert_to_pixmap=False)
        )
        hbox_layout.addWidget(self.button_add_bundle)
        hbox_layout.addWidget(self.button_remove_bundle)

        self.labels = []
        self.widgets = []
        self.selected_devices = {}

        self.init_box(self.config)

        self.button_add_bundle.clicked.connect(self.add_widget_bundle)
        self.button_remove_bundle.clicked.connect(self.remove_widget_bundle)

    def init_box(self, config: dict):
        box_name = config.get("name", "ScanGroupBox")
        self.inputs = config.get("inputs", {})
        self.setTitle(box_name)

        # Labels
        self.add_input_labels(self.inputs, 0)

        # Widgets
        if self.box_type == "args":
            min_bundle = self.config.get("min", 1)
            for i in range(1, min_bundle + 1):
                self.add_input_widgets(self.inputs, i)
        else:
            self.add_input_widgets(self.inputs, 1)
            self.button_add_bundle.setVisible(False)
            self.button_remove_bundle.setVisible(False)

    def add_input_labels(self, group_inputs: dict, row: int) -> None:
        """
        Adds the given arg_group from arg_bundle to the scan control layout. The input labels are always added to the first row.

        Args:
            group(dict): Dictionary containing the arg_group information.
        """
        for column_index, item in enumerate(group_inputs):
            arg_name = item.get("name", None)
            display_name = item.get("display_name", arg_name)
            label = QLabel(text=display_name)
            self.layout.addWidget(label, row, column_index)
            self.labels.append(label)

    def add_input_widgets(self, group_inputs: dict, row) -> None:
        """
        Adds the given arg_group from arg_bundle to the scan control layout.

        Args:
            group_inputs(dict): Dictionary containing the arg_group information.
            row(int): The row to add the widgets to.
        """
        for column_index, item in enumerate(group_inputs):
            arg_name = item.get("name", None)
            default = item.get("default", None)
            item_type = item.get("type", None)
            if isinstance(item_type, dict) and "Literal" in item_type:
                widget_class = self.WIDGET_HANDLER.get(ScanArgType.LITERALS_DICT, None)
            else:
                widget_class = self.WIDGET_HANDLER.get(item["type"], None)
            if widget_class is None:
                logger.error(
                    f"Unsupported annotation '{item['type']}' for parameter '{item['name']}'"
                )
                continue
            if default == "_empty":
                default = None
            widget = widget_class(parent=self.parent(), arg_name=arg_name, default=default)
            if isinstance(widget, DeviceLineEdit):
                widget.set_device_filter(BECDeviceFilter.DEVICE)
                self.selected_devices[widget] = ""
                widget.device_selected.connect(self.emit_device_selected)
            if isinstance(widget, ScanLiteralsComboBox):
                widget.set_literals(item["type"].get("Literal", []))
            tooltip = item.get("tooltip", None)
            if tooltip is not None:
                widget.setToolTip(item["tooltip"])
            self.layout.addWidget(widget, row, column_index)
            self.widgets.append(widget)

    @Slot(str)
    def emit_device_selected(self, device_name):
        self.selected_devices[self.sender()] = device_name.strip()
        selected_devices_str = " ".join(self.selected_devices.values())
        self.device_selected.emit(selected_devices_str)

    def add_widget_bundle(self):
        """
        Adds a new row of widgets to the scan control layout. Only usable for arg_groups.
        """
        arg_max = self.config.get("max", None)
        row = self.layout.rowCount()
        if arg_max is not None and row >= arg_max:
            return

        self.add_input_widgets(self.inputs, row)

    def remove_widget_bundle(self):
        """
        Removes the last row of widgets from the scan control layout. Only usable for arg_groups.
        """
        arg_min = self.config.get("min", None)
        row = self.count_arg_rows()
        if arg_min is not None and row <= arg_min:
            return

        for widget in self.widgets[-len(self.inputs) :]:
            if isinstance(widget, DeviceLineEdit):
                self.selected_devices[widget] = ""
            widget.close()
            widget.deleteLater()
        self.widgets = self.widgets[: -len(self.inputs)]

        selected_devices_str = " ".join(self.selected_devices.values())
        self.device_selected.emit(selected_devices_str.strip())

    def remove_all_widget_bundles(self):
        """Remove every widget bundle from the scan control layout."""
        for widget in list(self.widgets):
            if isinstance(widget, DeviceLineEdit):
                self.selected_devices.pop(widget, None)
            widget.close()
            widget.deleteLater()
            self.layout.removeWidget(widget)
        self.widgets.clear()
        self.device_selected.emit("")

    @Property(bool)
    def hide_add_remove_buttons(self):
        return self._hide_add_remove_buttons

    @hide_add_remove_buttons.setter
    def hide_add_remove_buttons(self, hide: bool):
        self._hide_add_remove_buttons = hide
        if not hide and self.box_type == "args":
            self.button_add_bundle.show()
            self.button_remove_bundle.show()
            return
        self.button_add_bundle.hide()
        self.button_remove_bundle.hide()

    def get_parameters(self, device_object: bool = True):
        """
        Returns the parameters from the widgets in the scan control layout formated to run scan from BEC.
        """
        if self.box_type == "args":
            return self._get_arg_parameterts(device_object=device_object)
        elif self.box_type == "kwargs":
            return self._get_kwarg_parameters(device_object=device_object)

    def _get_arg_parameterts(self, device_object: bool = True):
        args = []
        for i in range(1, self.layout.rowCount()):
            for j in range(self.layout.columnCount()):
                try:  # In case that the bundle size changes
                    widget = self.layout.itemAtPosition(i, j).widget()
                    if isinstance(widget, DeviceLineEdit) and device_object:
                        value = widget.get_current_device()
                    else:
                        value = WidgetIO.get_value(widget)
                    args.append(value)
                except AttributeError:
                    continue
        return args

    def _get_kwarg_parameters(self, device_object: bool = True):
        kwargs = {}
        for i in range(self.layout.columnCount()):
            widget = self.layout.itemAtPosition(1, i).widget()
            if isinstance(widget, DeviceLineEdit) and device_object:
                value = widget.get_current_device().name
            elif isinstance(widget, ScanLiteralsComboBox):
                value = widget.get_value()
            else:
                value = WidgetIO.get_value(widget)
            kwargs[widget.arg_name] = value
        return kwargs

    def count_arg_rows(self):
        widget_rows = 0
        for row in range(self.layout.rowCount()):
            for col in range(self.layout.columnCount()):
                item = self.layout.itemAtPosition(row, col)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        if isinstance(widget, DeviceLineEdit):
                            widget_rows += 1
        return widget_rows

    def set_parameters(self, parameters: list | dict):
        if self.box_type == "args":
            self._set_arg_parameters(parameters)
        elif self.box_type == "kwargs":
            self._set_kwarg_parameters(parameters)

    def _set_arg_parameters(self, parameters: list):
        self.remove_all_widget_bundles()
        if not parameters:
            return

        inputs_per_bundle = len(self.inputs)
        if inputs_per_bundle == 0:
            return

        bundles_needed = -(-len(parameters) // inputs_per_bundle)

        for row in range(1, bundles_needed + 1):
            self.add_input_widgets(self.inputs, row)

        for i, value in enumerate(parameters):
            WidgetIO.set_value(self.widgets[i], value)

    def _set_kwarg_parameters(self, parameters: dict):
        for widget in self.widgets:
            for key, value in parameters.items():
                if widget.arg_name == key:
                    WidgetIO.set_value(widget, value)
                    break
