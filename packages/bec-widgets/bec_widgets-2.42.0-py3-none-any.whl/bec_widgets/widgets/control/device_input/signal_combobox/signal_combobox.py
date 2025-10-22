from __future__ import annotations

from bec_lib.device import Positioner
from qtpy.QtCore import QSize, Signal
from qtpy.QtWidgets import QComboBox, QSizePolicy

from bec_widgets.utils.error_popups import SafeProperty, SafeSlot
from bec_widgets.utils.filter_io import ComboBoxFilterHandler, FilterIO
from bec_widgets.utils.ophyd_kind_util import Kind
from bec_widgets.widgets.control.device_input.base_classes.device_signal_input_base import (
    DeviceSignalInputBase,
    DeviceSignalInputBaseConfig,
)


class SignalComboBox(DeviceSignalInputBase, QComboBox):
    """
    Line edit widget for device input with autocomplete for device names.

    Args:
        parent: Parent widget.
        client: BEC client object.
        config: Device input configuration.
        gui_id: GUI ID.
        device_filter: Device filter, name of the device class from BECDeviceFilter and BECReadoutPriority. Check DeviceInputBase for more details.
        default: Default device name.
        arg_name: Argument name, can be used for the other widgets which has to call some other function in bec using correct argument names.
    """

    USER_ACCESS = ["set_signal", "set_device", "signals"]

    ICON_NAME = "list_alt"
    PLUGIN = True
    RPC = True

    device_signal_changed = Signal(str)

    def __init__(
        self,
        parent=None,
        client=None,
        config: DeviceSignalInputBaseConfig | None = None,
        gui_id: str | None = None,
        device: str | None = None,
        signal_filter: str | list[str] | None = None,
        default: str | None = None,
        arg_name: str | None = None,
        **kwargs,
    ):
        super().__init__(parent=parent, client=client, gui_id=gui_id, config=config, **kwargs)
        if arg_name is not None:
            self.config.arg_name = arg_name
            self.arg_name = arg_name
        if default is not None:
            self.set_device(default)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMinimumSize(QSize(100, 0))
        self._set_first_element_as_empty = True
        # We do not consider the config that is passed here, this produced problems
        # with QtDesigner, since config and input arguments may differ and resolve properly
        # Implementing this logic and config recoverage is postponed.
        self.currentTextChanged.connect(self.on_text_changed)
        if signal_filter is not None:
            self.set_filter(signal_filter)
        else:
            self.set_filter([Kind.hinted, Kind.normal, Kind.config])
        if device is not None:
            self.set_device(device)
        if default is not None:
            self.set_signal(default)

    @SafeSlot()
    @SafeSlot(dict, dict)
    def update_signals_from_filters(
        self, content: dict | None = None, metadata: dict | None = None
    ):
        """Update the filters for the combobox"""
        super().update_signals_from_filters(content, metadata)
        # pylint: disable=protected-access
        if FilterIO._find_handler(self) is ComboBoxFilterHandler:
            if len(self._config_signals) > 0:
                self.insertItem(
                    len(self._hinted_signals) + len(self._normal_signals), "Config Signals"
                )
                self.model().item(len(self._hinted_signals) + len(self._normal_signals)).setEnabled(
                    False
                )
            if len(self._normal_signals) > 0:
                self.insertItem(len(self._hinted_signals), "Normal Signals")
                self.model().item(len(self._hinted_signals)).setEnabled(False)
            if len(self._hinted_signals) > 0:
                self.insertItem(0, "Hinted Signals")
                self.model().item(0).setEnabled(False)

    @SafeProperty(bool)
    def set_first_element_as_empty(self) -> bool:
        """
        Whether the first element in the combobox should be empty.
        This is useful to allow the user to select a device from the list.
        """
        return self._set_first_element_as_empty

    @set_first_element_as_empty.setter
    def set_first_element_as_empty(self, value: bool) -> None:
        """
        Set whether the first element in the combobox should be empty.
        This is useful to allow the user to select a device from the list.

        Args:
            value (bool): True if the first element should be empty, False otherwise.
        """
        self._set_first_element_as_empty = value
        if self._set_first_element_as_empty:
            self.insertItem(0, "")
            self.setCurrentIndex(0)
        else:
            if self.count() > 0 and self.itemText(0) == "":
                self.removeItem(0)

    def set_to_obj_name(self, obj_name: str) -> bool:
        """
        Set the combobox to the object name of the signal.

        Args:
            obj_name (str): Object name of the signal.

        Returns:
            bool: True if the object name was found and set, False otherwise.
        """
        for i in range(self.count()):
            signal_data = self.itemData(i)
            if signal_data and signal_data.get("obj_name") == obj_name:
                self.setCurrentIndex(i)
                return True
        return False

    def set_to_first_enabled(self) -> bool:
        """
        Set the combobox to the first enabled item.

        Returns:
            bool: True if an enabled item was found and set, False otherwise.
        """
        for i in range(self.count()):
            if self.model().item(i).isEnabled():
                self.setCurrentIndex(i)
                return True
        return False

    @SafeSlot()
    def reset_selection(self):
        """Reset the selection of the combobox."""
        self.clear()
        self.setItemText(0, "Select a device")
        self.update_signals_from_filters()
        self.device_signal_changed.emit("")

    @SafeSlot(str)
    def on_text_changed(self, text: str):
        """Slot for text changed. If a device is selected and the signal is changed and valid it emits a signal.
        For a positioner, the readback value has to be renamed to the device name.

        Args:
            text (str): Text in the combobox.
        """
        if self.validate_device(self.device) is False:
            return
        if self.validate_signal(text) is False:
            return
        self.device_signal_changed.emit(text)

    @property
    def selected_signal_comp_name(self) -> str:
        return dict(self.signals).get(self.currentText(), {}).get("component_name", "")


if __name__ == "__main__":  # pragma: no cover
    # pylint: disable=import-outside-toplevel
    from qtpy.QtWidgets import QApplication, QVBoxLayout, QWidget

    from bec_widgets.utils.colors import set_theme

    app = QApplication([])
    set_theme("dark")
    widget = QWidget()
    widget.setFixedSize(200, 200)
    layout = QVBoxLayout()
    widget.setLayout(layout)
    box = SignalComboBox(device="samx")
    layout.addWidget(box)
    widget.show()
    app.exec_()
