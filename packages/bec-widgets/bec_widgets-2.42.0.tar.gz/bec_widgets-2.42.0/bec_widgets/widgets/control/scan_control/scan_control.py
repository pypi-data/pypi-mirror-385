from collections import defaultdict
from types import NoneType, SimpleNamespace
from typing import Optional

from bec_lib.endpoints import MessageEndpoints
from pydantic import BaseModel, Field
from qtpy.QtCore import Signal
from qtpy.QtGui import QColor
from qtpy.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from bec_widgets.utils import ConnectionConfig
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.colors import get_accent_colors
from bec_widgets.utils.error_popups import SafeProperty, SafeSlot
from bec_widgets.widgets.control.buttons.stop_button.stop_button import StopButton
from bec_widgets.widgets.control.scan_control.scan_group_box import ScanGroupBox
from bec_widgets.widgets.editors.scan_metadata.scan_metadata import ScanMetadata
from bec_widgets.widgets.utility.toggle.toggle import ToggleSwitch


class ScanParameterConfig(BaseModel):
    name: str
    args: Optional[list] = Field(None)
    kwargs: Optional[dict] = Field(None)


class ScanControlConfig(ConnectionConfig):
    default_scan: Optional[str] = Field(None)
    allowed_scans: Optional[list] = Field(None)
    scans: Optional[dict[str, ScanParameterConfig]] = defaultdict(dict)


class ScanControl(BECWidget, QWidget):
    """
    Widget to submit new scans to the queue.
    """

    USER_ACCESS = ["remove", "screenshot"]
    PLUGIN = True
    ICON_NAME = "tune"
    ARG_BOX_POSITION: int = 2

    scan_started = Signal()
    scan_selected = Signal(str)
    device_selected = Signal(str)
    scan_args = Signal(list)

    def __init__(
        self,
        parent=None,
        client=None,
        config: ScanControlConfig | dict | None = None,
        gui_id: str | None = None,
        allowed_scans: list | None = None,
        default_scan: str | None = None,
        **kwargs,
    ):
        if config is None:
            config = ScanControlConfig(
                widget_class=self.__class__.__name__, allowed_scans=allowed_scans
            )
        super().__init__(parent=parent, client=client, gui_id=gui_id, config=config, **kwargs)

        self._hide_add_remove_buttons = False

        # Client from BEC + shortcuts to device manager and scans
        self.get_bec_shortcuts()

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.arg_box = None
        self.kwarg_boxes = []
        self.expert_mode = False  # TODO implement in the future versions
        self.previous_scan = None
        self.last_scan_found = None

        # Widget Default Parameters
        self.config.default_scan = default_scan
        self.config.allowed_scans = allowed_scans

        self._scan_metadata: dict | None = None
        self._metadata_form = ScanMetadata(parent=self)

        # Create and set main layout
        self._init_UI()

    def _init_UI(self):
        """
        Initializes the UI of the scan control widget. Create the top box for scan selection and populate scans to main combobox.
        """
        palette = get_accent_colors()
        if palette is None:
            palette = SimpleNamespace(
                default=QColor("blue"),
                success=QColor("green"),
                warning=QColor("orange"),
                emergency=QColor("red"),
            )
        # Scan selection box
        self.scan_selection_group = QWidget(self)
        QVBoxLayout(self.scan_selection_group)
        scan_selection_layout = QHBoxLayout()
        self.comboBox_scan_selection_label = QLabel("Scan:", self.scan_selection_group)
        self.comboBox_scan_selection = QComboBox(self.scan_selection_group)
        scan_selection_layout.addWidget(self.comboBox_scan_selection_label, 0)
        scan_selection_layout.addWidget(self.comboBox_scan_selection, 1)
        self.scan_selection_group.layout().addLayout(scan_selection_layout)

        # Label to reload the last scan parameters within scan selection group box
        self.toggle_layout = QHBoxLayout()
        self.toggle_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed)
        )
        self.last_scan_label = QLabel("Restore last scan parameters", self.scan_selection_group)
        self.toggle = ToggleSwitch(parent=self.scan_selection_group, checked=False)
        self.toggle.enabled.connect(self.request_last_executed_scan_parameters)
        self.toggle_layout.addWidget(self.last_scan_label)
        self.toggle_layout.addWidget(self.toggle)
        self.scan_selection_group.layout().addLayout(self.toggle_layout)
        self.scan_selection_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.layout.addWidget(self.scan_selection_group)

        # Scan control (Run/Stop) buttons
        self.scan_control_group = QWidget(self)
        self.scan_control_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.button_layout = QHBoxLayout(self.scan_control_group)
        self.button_run_scan = QPushButton("Start", self.scan_control_group)
        self.button_run_scan.setStyleSheet(
            f"background-color: {palette.success.name()}; color: white"
        )
        self.button_stop_scan = StopButton(parent=self.scan_control_group)
        self.button_stop_scan.setStyleSheet(
            f"background-color: {palette.emergency.name()}; color: white"
        )
        self.button_layout.addWidget(self.button_run_scan)
        self.button_layout.addWidget(self.button_stop_scan)
        self.layout.addWidget(self.scan_control_group)

        # Default scan from config
        if self.config.default_scan is not None:
            self.comboBox_scan_selection.setCurrentText(self.config.default_scan)

        # Connect signals
        self.comboBox_scan_selection.view().pressed.connect(self.save_current_scan_parameters)
        self.comboBox_scan_selection.currentIndexChanged.connect(self.on_scan_selection_changed)
        self.button_run_scan.clicked.connect(self.run_scan)

        self.scan_selected.connect(self.scan_select)

        # Initialize scan selection
        self.populate_scans()

        # Append metadata form
        self._add_metadata_form()

        self.layout.addStretch()

    def _add_metadata_form(self):
        self.layout.addWidget(self._metadata_form)
        self._metadata_form.update_with_new_scan(self.comboBox_scan_selection.currentText())
        self.scan_selected.connect(self._metadata_form.update_with_new_scan)
        self._metadata_form.form_data_updated.connect(self.update_scan_metadata)
        self._metadata_form.form_data_cleared.connect(self.update_scan_metadata)
        self._metadata_form.validate_form()

    def populate_scans(self):
        """Populates the scan selection combo box with available scans from BEC session."""
        self.available_scans = self.client.connector.get(
            MessageEndpoints.available_scans()
        ).resource
        if self.config.allowed_scans is None:
            supported_scans = ["ScanBase", "SyncFlyScanBase", "AsyncFlyScanBase"]
            allowed_scans = [
                scan_name
                for scan_name, scan_info in self.available_scans.items()
                if scan_info["base_class"] in supported_scans and len(scan_info["gui_config"]) > 0
            ]

        else:
            allowed_scans = self.config.allowed_scans
        self.comboBox_scan_selection.addItems(allowed_scans)

    def on_scan_selection_changed(self, index: int):
        """Callback for scan selection combo box"""
        selected_scan_name = self.comboBox_scan_selection.currentText()
        self.scan_selected.emit(selected_scan_name)
        self.request_last_executed_scan_parameters()
        self.restore_scan_parameters(selected_scan_name)

    @SafeSlot()
    @SafeSlot(bool)
    def request_last_executed_scan_parameters(self, *_):
        """
        Requests the last executed scan parameters from BEC and restores them to the scan control widget.
        """
        self.last_scan_found = False
        if not self.toggle.checked:
            return

        current_scan = self.comboBox_scan_selection.currentText()
        history = (
            self.client.connector.xread(
                MessageEndpoints.scan_history(), from_start=True, user_id=self.object_name
            )
            or []
        )

        for scan in reversed(history):
            scan_data = scan.get("data")
            if not scan_data:
                continue

            if scan_data.scan_name != current_scan:
                continue

            ri = getattr(scan_data, "request_inputs", {}) or {}
            args_list = ri.get("arg_bundle", [])
            if args_list and self.arg_box:
                self.arg_box.set_parameters(args_list)

            inputs = ri.get("inputs", {})
            kwargs = ri.get("kwargs", {})
            merged = {**inputs, **kwargs}
            if merged and self.kwarg_boxes:
                for box in self.kwarg_boxes:
                    box.set_parameters(merged)

            self.last_scan_found = True
            break

    @SafeProperty(str)
    def current_scan(self):
        """Returns the scan name for the currently selected scan."""
        return self.comboBox_scan_selection.currentText()

    @current_scan.setter
    def current_scan(self, scan_name: str):
        """Sets the current scan to the given scan name.

        Args:
            scan_name(str): Name of the scan to set as current.
        """
        if scan_name not in self.available_scans:
            return
        self.comboBox_scan_selection.setCurrentText(scan_name)

    @SafeSlot(str)
    def set_current_scan(self, scan_name: str):
        """Slot for setting the current scan to the given scan name.

        Args:
            scan_name(str): Name of the scan to set as current.
        """
        self.current_scan = scan_name

    @SafeProperty(bool)
    def hide_arg_box(self):
        """Property to hide the argument box."""
        if self.arg_box is None:
            return True
        return not self.arg_box.isVisible()

    @hide_arg_box.setter
    def hide_arg_box(self, hide: bool):
        """Setter for the hide_arg_box property.

        Args:
            hide(bool): Hide or show the argument box.
        """
        if self.arg_box is not None:
            self.arg_box.setVisible(not hide)

    @SafeProperty(bool)
    def hide_kwarg_boxes(self):
        """Property to hide the keyword argument boxes."""
        if len(self.kwarg_boxes) == 0:
            return True

        for box in self.kwarg_boxes:
            if box is not None:
                return not box.isVisible()

    @hide_kwarg_boxes.setter
    def hide_kwarg_boxes(self, hide: bool):
        """Setter for the hide_kwarg_boxes property.

        Args:
            hide(bool): Hide or show the keyword argument boxes.
        """
        if len(self.kwarg_boxes) > 0:
            for box in self.kwarg_boxes:
                box.setVisible(not hide)

    @SafeProperty(bool)
    def hide_scan_control_buttons(self):
        """Property to hide the scan control buttons."""
        return not self.button_run_scan.isVisible()

    @hide_scan_control_buttons.setter
    def hide_scan_control_buttons(self, hide: bool):
        """Setter for the hide_scan_control_buttons property.

        Args:
            hide(bool): Hide or show the scan control buttons.
        """
        self.show_scan_control_buttons(not hide)

    @SafeProperty(bool)
    def hide_metadata(self):
        """Property to hide the metadata form."""
        return not self._metadata_form.isVisible()

    @hide_metadata.setter
    def hide_metadata(self, hide: bool):
        """Setter for the hide_metadata property.

        Args:
            hide(bool): Hide or show the metadata form.
        """
        self._metadata_form.setVisible(not hide)

    @SafeProperty(bool)
    def hide_optional_metadata(self):
        """Property to hide the optional metadata form."""
        return self._metadata_form.hide_optional_metadata

    @hide_optional_metadata.setter
    def hide_optional_metadata(self, hide: bool):
        """Setter for the hide_optional_metadata property.

        Args:
            hide(bool): Hide or show the optional metadata form.
        """
        self._metadata_form.hide_optional_metadata = hide

    @SafeSlot(bool)
    def show_scan_control_buttons(self, show: bool):
        """Shows or hides the scan control buttons."""
        self.scan_control_group.setVisible(show)

    @SafeProperty(bool)
    def hide_scan_selection_combobox(self):
        """Property to hide the scan selection combobox."""
        return not self.comboBox_scan_selection.isVisible()

    @hide_scan_selection_combobox.setter
    def hide_scan_selection_combobox(self, hide: bool):
        """Setter for the hide_scan_selection_combobox property.

        Args:
            hide(bool): Hide or show the scan selection combobox.
        """
        self.show_scan_selection_combobox(not hide)

    @SafeSlot(bool)
    def show_scan_selection_combobox(self, show: bool):
        """Shows or hides the scan selection combobox."""
        self.scan_selection_group.setVisible(show)

    @SafeSlot(str)
    def scan_select(self, scan_name: str):
        """
        Slot for scan selection. Updates the scan control layout based on the selected scan.

        Args:
            scan_name(str): Name of the selected scan.
        """
        self.reset_layout()
        selected_scan_info = self.available_scans.get(scan_name, {})

        gui_config = selected_scan_info.get("gui_config", {})
        self.arg_group = gui_config.get("arg_group", None)
        self.kwarg_groups = gui_config.get("kwarg_groups", None)

        if bool(self.arg_group["arg_inputs"]):
            self.add_arg_group(self.arg_group)
        if len(self.kwarg_groups) > 0:
            self.add_kwargs_boxes(self.kwarg_groups)

        self.update()
        self.adjustSize()

    @SafeProperty(bool)
    def hide_add_remove_buttons(self):
        """Property to hide the add_remove buttons."""
        return self._hide_add_remove_buttons

    @hide_add_remove_buttons.setter
    def hide_add_remove_buttons(self, hide: bool):
        """Setter for the hide_add_remove_buttons property.

        Args:
            hide(bool): Hide or show the add_remove buttons.
        """
        self._hide_add_remove_buttons = hide
        if self.arg_box is not None:
            self.arg_box.hide_add_remove_buttons = hide

    def add_kwargs_boxes(self, groups: list):
        """
        Adds the given gui_groups to the scan control layout.

        Args:
            groups(list): List of dictionaries containing the gui_group information.
        """
        position = self.ARG_BOX_POSITION + (1 if self.arg_box is not None else 0)
        for group in groups:
            box = ScanGroupBox(box_type="kwargs", config=group)
            box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            self.layout.insertWidget(position + len(self.kwarg_boxes), box)
            self.kwarg_boxes.append(box)

    def add_arg_group(self, group: dict):
        """
        Adds the given gui_groups to the scan control layout.

        Args:
        """
        self.arg_box = ScanGroupBox(box_type="args", config=group)
        self.arg_box.device_selected.connect(self.emit_device_selected)
        self.arg_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.arg_box.hide_add_remove_buttons = self._hide_add_remove_buttons
        self.layout.insertWidget(self.ARG_BOX_POSITION, self.arg_box)

    @SafeSlot(str)
    def emit_device_selected(self, dev_names):
        """
        Emit the signal to inform about selected device(s)

        "dev_names" is a string separated by space, in case of multiple devices
        """
        self._selected_devices = dev_names
        self.device_selected.emit(dev_names)

    def reset_layout(self):
        """Clears the scan control layout from GuiGroups and ArgGroups boxes."""
        if self.arg_box is not None:
            self.layout.removeWidget(self.arg_box)
            self.arg_box.deleteLater()
            self.arg_box = None
        if self.kwarg_boxes != []:
            self.remove_kwarg_boxes()

    def remove_kwarg_boxes(self):
        for box in self.kwarg_boxes:
            self.layout.removeWidget(box)
            box.deleteLater()
        self.kwarg_boxes = []

    def get_scan_parameters(self, bec_object: bool = True):
        """
        Returns the scan parameters for the selected scan.

        Args:
            bec_object(bool): If True, returns the BEC object for the scan parameters such as device objects.
        """
        args = []
        kwargs = {}
        if self.arg_box is not None:
            args = self.arg_box.get_parameters(bec_object)
        for box in self.kwarg_boxes:
            box_kwargs = box.get_parameters(bec_object)
            kwargs.update(box_kwargs)
        return args, kwargs

    def restore_scan_parameters(self, scan_name: str):
        """
        Restores the scan parameters for the given scan name

        Args:
            scan_name(str): Name of the scan to restore the parameters for.
        """
        if self.last_scan_found is True:
            return
        scan_params = self.config.scans.get(scan_name, None)
        if scan_params is None and self.previous_scan is None:
            return

        if scan_params is None and self.previous_scan is not None:
            previous_scan_params = self.config.scans.get(self.previous_scan, None)
            self._restore_kwargs(previous_scan_params.kwargs)
            return

        if scan_params.args is not None and self.arg_box is not None:
            self.arg_box.set_parameters(scan_params.args)

        self._restore_kwargs(scan_params.kwargs)

    def _restore_kwargs(self, scan_kwargs: dict):
        """Restores the kwargs for the given scan parameters."""
        if scan_kwargs is not None and self.kwarg_boxes is not None:
            for box in self.kwarg_boxes:
                box.set_parameters(scan_kwargs)

    def save_current_scan_parameters(self):
        """Saves the current scan parameters to the scan control config for further use."""
        scan_name = self.comboBox_scan_selection.currentText()
        self.previous_scan = scan_name
        args, kwargs = self.get_scan_parameters(False)
        scan_params = ScanParameterConfig(name=scan_name, args=args, kwargs=kwargs)
        self.config.scans[scan_name] = scan_params

    @SafeSlot(dict)
    @SafeSlot(NoneType)
    def update_scan_metadata(self, md: dict | None):
        self._scan_metadata = md
        if md is None:
            self.button_run_scan.setEnabled(False)
        else:
            self.button_run_scan.setEnabled(True)

    @SafeSlot(popup_error=True)
    def run_scan(self):
        """Starts the selected scan with the given parameters."""
        args, kwargs = self.get_scan_parameters()
        kwargs["metadata"] = self._scan_metadata
        self.scan_args.emit(args)
        scan_function = getattr(self.scans, self.comboBox_scan_selection.currentText())
        if callable(scan_function):
            self.scan_started.emit()
            scan_function(*args, **kwargs)

    def cleanup(self):
        """Cleanup the scan control widget."""
        self.button_stop_scan.cleanup()
        if self.arg_box:
            for widget in self.arg_box.widgets:
                if hasattr(widget, "cleanup"):
                    widget.cleanup()
        for kwarg_box in self.kwarg_boxes:
            for widget in kwarg_box.widgets:
                if hasattr(widget, "cleanup"):
                    widget.cleanup()
        super().cleanup()


# Application example
if __name__ == "__main__":  # pragma: no cover
    from bec_widgets.utils.colors import set_theme

    app = QApplication([])
    scan_control = ScanControl()

    set_theme("auto")
    window = scan_control
    window.show()
    app.exec()
