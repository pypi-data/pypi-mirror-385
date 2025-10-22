from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING, Any, Sequence

import numpy as np
from bec_lib.device import Device, Signal
from bec_lib.endpoints import MessageEndpoints
from bec_qthemes import material_icon
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal as QSignal
from qtpy.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.colors import get_accent_colors
from bec_widgets.utils.error_popups import SafeProperty, SafeSlot
from bec_widgets.utils.ophyd_kind_util import Kind
from bec_widgets.widgets.control.device_input.device_line_edit.device_line_edit import (
    DeviceLineEdit,
)
from bec_widgets.widgets.control.device_input.signal_combobox.signal_combobox import SignalComboBox

if TYPE_CHECKING:
    from bec_lib.client import BECClient


class ChoiceDialog(QDialog):
    accepted_output = QSignal(str, str)

    CONNECTION_ERROR_STR = "Error: client is not connected!"

    def __init__(
        self,
        parent: QWidget | None = None,
        client: BECClient | None = None,
        device: str | None = None,
        signal: str | None = None,
        show_hinted: bool = True,
        show_normal: bool = False,
        show_config: bool = False,
    ):
        if not client or not client.started:
            self._display_error()
            return
        super().__init__(parent=parent)
        self.setWindowTitle("Choose device and signal...")
        self._accent_colors = get_accent_colors()

        layout = QHBoxLayout()

        self._device_field = DeviceLineEdit(parent=parent, client=client)
        self._signal_field = SignalComboBox(parent=parent, client=client)
        layout.addWidget(self._device_field)
        layout.addWidget(self._signal_field)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self._signal_field.include_hinted_signals = show_hinted
        self._signal_field.include_normal_signals = show_normal
        self._signal_field.include_config_signals = show_config

        self.setLayout(layout)
        self._device_field.textChanged.connect(self._update_device)
        if device:
            self._device_field.set_device(device)
        if signal and signal in set(s[0] for s in self._signal_field.signals):
            self._signal_field.set_signal(signal)

    def _display_error(self):
        try:
            super().__init__()
        except Exception:
            ...
        layout = QHBoxLayout()
        layout.addWidget(QLabel(self.CONNECTION_ERROR_STR))
        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    @SafeSlot(str)
    def _update_device(self, device: str):
        if device in self._device_field.dev:
            self._device_field.set_device(device)
            self._signal_field.set_device(device)
            self._device_field.setStyleSheet(
                f"QLineEdit {{ border-style: solid; border-width: 2px; border-color: {self._accent_colors.success.name() if self._accent_colors else 'green'}}}"
            )
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self._device_field.setStyleSheet(
                f"QLineEdit {{ border-style: solid; border-width: 2px; border-color: {self._accent_colors.emergency.name() if self._accent_colors else 'red'}}}"
            )
            self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
            self._signal_field.clear()

    def accept(self):
        self.accepted_output.emit(
            self._device_field.text(), self._signal_field.selected_signal_comp_name
        )
        self.cleanup()
        return super().accept()

    def reject(self):
        self.cleanup()
        return super().reject()

    def cleanup(self):
        self._device_field.close()
        self._signal_field.close()


class SignalLabel(BECWidget, QWidget):
    ICON_NAME = "scoreboard"
    RPC = True
    PLUGIN = True

    USER_ACCESS = [
        "custom_label",
        "custom_units",
        "custom_label.setter",
        "custom_units.setter",
        "decimal_places",
        "decimal_places.setter",
        "show_default_units",
        "show_default_units.setter",
        "show_select_button",
        "show_select_button.setter",
        "show_hinted_signals",
        "show_hinted_signals.setter",
        "show_normal_signals",
        "show_normal_signals.setter",
        "show_config_signals",
        "show_config_signals.setter",
        "display_array_data",
        "display_array_data.setter",
        "max_list_display_len",
        "max_list_display_len.setter",
    ]

    def __init__(
        self,
        parent: QWidget | None = None,
        client: BECClient | None = None,
        device: str | None = None,
        signal: str | None = None,
        show_select_button: bool = True,
        show_default_units: bool = False,
        custom_label: str = "",
        custom_units: str = "",
        **kwargs,
    ):
        """Initialize the SignalLabel widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            client (BECClient, optional): The BEC client. Defaults to None.
            device (str, optional): The device name. Defaults to None.
            signal (str, optional): The signal name. Defaults to None.
            selection_dialog_config (DeviceSignalInputBaseConfig | dict, optional): Configuration for the signal selection dialog.
            show_select_button (bool, optional): Whether to show the select button. Defaults to True.
            show_default_units (bool, optional): Whether to show default units. Defaults to False.
            custom_label (str, optional): Custom label for the widget. Defaults to "".
            custom_units (str, optional): Custom units for the widget. Defaults to "".
        """
        super().__init__(parent=parent, client=client, **kwargs)

        self._device = device
        self._signal = signal

        self._custom_label: str = custom_label
        self._custom_units: str = custom_units
        self._show_default_units: bool = show_default_units
        self._decimal_places = 3
        self._dtype = None
        self._max_list_display_len = 5

        self._show_hinted_signals: bool = True
        self._show_normal_signals: bool = True
        self._show_config_signals: bool = True
        self._display_array_data: bool = False

        self._outer_layout = QHBoxLayout()
        self._layout = QHBoxLayout()
        self._outer_layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._outer_layout)

        self._label = QGroupBox(custom_label)
        self._outer_layout.addWidget(self._label)
        self._update_label()
        self._label.setLayout(self._layout)

        self._value: Any = ""
        self._display = QLabel()
        self._layout.addWidget(self._display)

        self._select_button = QToolButton()
        self._select_button.setIcon(material_icon(icon_name="settings", size=(20, 20)))
        self._show_select_button: bool = show_select_button
        self._layout.addWidget(self._select_button)
        self._display.setMinimumHeight(self._select_button.sizeHint().height())
        self.show_select_button = self._show_select_button

        self._select_button.clicked.connect(self.show_choice_dialog)
        self.get_bec_shortcuts()
        self._device_obj = self.dev.get(self._device)
        self._signal_key, self._signal_info = "", {}

        self._connected: bool = False
        self.connect_device()

    def _create_dialog(self):
        return ChoiceDialog(
            parent=self,
            client=self.client,
            device=self.device,
            signal=self._signal_key,
            show_config=self.show_config_signals,
            show_normal=self.show_normal_signals,
            show_hinted=self.show_hinted_signals,
        )

    @SafeSlot()
    def _process_dialog(self, device: str, signal: str):
        signal = signal or device
        self.disconnect_device()
        self.device = device
        self.signal = signal
        self._update_label()
        self.connect_device()

    def show_choice_dialog(self):
        dialog = self._create_dialog()
        dialog.accepted_output.connect(self._process_dialog)
        dialog.open()
        return dialog

    def connect_device(self):
        """Subscribe to the Redis topic for the device to display"""
        if not self._connected and self._device and self._device in self.dev:
            self._signal_key, self._signal_info = self._signal_key_and_info()
            self._manual_read()
            self._read_endpoint = MessageEndpoints.device_readback(self._device)
            self._read_config_endpoint = MessageEndpoints.device_read_configuration(self._device)
            self.bec_dispatcher.connect_slot(self.on_device_readback, self._read_endpoint)
            self.bec_dispatcher.connect_slot(self.on_device_readback, self._read_config_endpoint)
            self._connected = True
            self.set_display_value(self._value)

    def disconnect_device(self):
        """Unsubscribe from the Redis topic for the device to display"""
        if self._connected:
            self.bec_dispatcher.disconnect_slot(self.on_device_readback, self._read_endpoint)
            self.bec_dispatcher.disconnect_slot(self.on_device_readback, self._read_config_endpoint)
            self._connected = False

    def _manual_read(self):
        if not isinstance(self._device_obj, Device | Signal):
            self._value, self._units = "__", ""
            return
        reading = (self._device_obj.read(cached=True) or {}) | (
            self._device_obj.read_configuration(cached=True) or {}
        )
        value = reading.get(self._signal_key, {}).get("value")
        if value is None:
            self._value, self._units = "__", ""
            return
        self._value = value
        self._units = self._signal_info.get("egu", "")
        self._dtype = self._signal_info.get("dtype")

    @SafeSlot(dict, dict)
    def on_device_readback(self, msg: dict, metadata: dict) -> None:
        """
        Update the display with the new value.
        """
        try:
            _value = msg["signals"].get(self._signal_key, {}).get("value")
            if _value is not None:
                self._value = _value
                self.set_display_value(self._value)
        except Exception as e:
            self._display.setText("ERROR!")
            self._display.setToolTip(
                f"Error processing incoming reading: {msg}, handled with exception: {''.join(traceback.format_exception(e))}"
            )

    def _signal_key_and_info(self) -> tuple[str, dict]:
        if isinstance(self._device_obj, Device):
            try:
                signal_info = self._device_obj._info["signals"][self._signal]
            except KeyError:
                return "", {}
            if signal_info["kind_str"] == Kind.hinted.name:
                return signal_info["obj_name"], signal_info.get("describe", {})
            else:
                return f"{self._device}_{self._signal}", signal_info.get("describe", {})
        elif isinstance(self._device_obj, Signal):
            info = self._device_obj._info["describe_configuration"][self._device]
            info["egu"] = self._device_obj._info["describe_configuration"].get("egu")
            return (self._device, info)
        return "", {}

    @SafeProperty(str)
    def device(self) -> str:
        """The device from which to select a signal"""
        return self._device or "Not set!"

    @device.setter
    def device(self, value: str) -> None:
        self.disconnect_device()
        self._device = value
        self._device_obj = self.dev.get(self._device)
        self.connect_device()
        self._update_label()

    @SafeProperty(str)
    def signal(self) -> str:
        """The signal to display"""
        return self._signal or "Not set!"

    @signal.setter
    def signal(self, value: str) -> None:
        self.disconnect_device()
        self._signal = value
        self.connect_device()
        self._update_label()

    @SafeProperty(bool)
    def show_select_button(self) -> bool:
        """Show the button to select the signal to display"""
        return self._show_select_button

    @show_select_button.setter
    def show_select_button(self, value: bool) -> None:
        self._show_select_button = value
        self._select_button.setVisible(value)

    @SafeProperty(bool)
    def show_default_units(self) -> bool:
        """Show default units obtained from the signal alongside it"""
        return self._show_default_units

    @show_default_units.setter
    def show_default_units(self, value: bool) -> None:
        self._show_default_units = value
        self.set_display_value(self._value)

    @SafeProperty(str)
    def custom_label(self) -> str:
        """Use a cusom label rather than the signal name"""
        return self._custom_label

    @custom_label.setter
    def custom_label(self, value: str) -> None:
        self._custom_label = value
        self._update_label()

    @SafeProperty(str)
    def max_list_display_len(self) -> int:
        """For small lists, the max length to display"""
        return self._max_list_display_len

    @max_list_display_len.setter
    def max_list_display_len(self, value: int) -> None:
        self._max_list_display_len = value
        self.set_display_value(self._value)

    @SafeProperty(str)
    def custom_units(self) -> str:
        """Use a custom unit string"""
        return self._custom_units

    @custom_units.setter
    def custom_units(self, value: str) -> None:
        self._custom_units = value
        self.set_display_value(self._value)

    @SafeProperty(int)
    def decimal_places(self) -> int:
        """Format to a given number of decimal_places. Set to 0 to disable."""
        return self._decimal_places

    @decimal_places.setter
    def decimal_places(self, value: int) -> None:
        self._decimal_places = value
        self._update_label()

    @SafeProperty(bool)
    def display_array_data(self) -> bool:
        """Displays the full data from array signals if set to True."""
        return self._display_array_data

    @display_array_data.setter
    def display_array_data(self, value: bool) -> None:
        self._display_array_data = value
        self.set_display_value(self._value)

    @SafeProperty(bool)
    def show_hinted_signals(self) -> bool:
        """In the signal selection menu, show hinted signals"""
        return self._show_hinted_signals

    @show_hinted_signals.setter
    def show_hinted_signals(self, value: bool) -> None:
        self._show_hinted_signals = value

    @SafeProperty(bool)
    def show_config_signals(self) -> bool:
        """In the signal selection menu, show config signals"""
        return self._show_config_signals

    @show_config_signals.setter
    def show_config_signals(self, value: bool) -> None:
        self._show_config_signals = value

    @SafeProperty(bool)
    def show_normal_signals(self) -> bool:
        """In the signal selection menu, show normal signals"""
        return self._show_normal_signals

    @show_normal_signals.setter
    def show_normal_signals(self, value: bool) -> None:
        self._show_normal_signals = value

    def _format_value(self, value: Any):
        if self._dtype == "array" and not self.display_array_data:
            return "ARRAY DATA"
        if not isinstance(value, str) and isinstance(value, (Sequence, np.ndarray)):
            if len(value) < self._max_list_display_len:
                return str(value)
            else:
                return "ARRAY DATA"
        if self._decimal_places == 0:
            return value
        try:
            if self._dtype in ("integer", "float"):
                return f"{float(value):0.{self._decimal_places}f}"
            else:
                return str(value)
        except ValueError:
            return value

    @SafeSlot(str)
    def set_display_value(self, value: str):
        """Set the display to a given value, appending the units if specified"""
        self._display.setText(f"{self._format_value(value)}{self._units_string}")
        self._display.setToolTip("")

    @property
    def _units_string(self):
        if self.custom_units or self._show_default_units:
            return f" {self.custom_units or self._default_units or ''}"
        return ""

    @property
    def _default_units(self) -> str:
        return self._units

    @property
    def _default_label(self) -> str:
        return (
            str(self._signal) if self._device == self._signal else f"{self._device} {self._signal}"
        )

    def _update_label(self):
        self._label.setTitle(
            self._custom_label if self._custom_label else f"{self._default_label}:"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = QWidget()
    w.setLayout(QVBoxLayout())
    w.layout().addWidget(
        SignalLabel(
            device="samx",
            signal="readback",
            custom_label="custom label:",
            custom_units=" m/s/s",
            show_select_button=False,
        )
    )
    w.layout().addWidget(SignalLabel(device="samy", signal="readback", show_default_units=True))
    l = SignalLabel()
    l.device = "bpm4i"
    l.signal = "bpm4i"
    w.layout().addWidget(l)
    w.show()
    sys.exit(app.exec_())
