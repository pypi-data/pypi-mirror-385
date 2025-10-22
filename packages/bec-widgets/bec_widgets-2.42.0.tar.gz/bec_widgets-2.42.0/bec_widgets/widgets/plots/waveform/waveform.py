from __future__ import annotations

import json
from typing import Literal

import lmfit
import numpy as np
import pyqtgraph as pg
from bec_lib import bec_logger, messages
from bec_lib.endpoints import MessageEndpoints
from bec_lib.scan_data_container import ScanDataContainer
from pydantic import Field, ValidationError, field_validator
from qtpy.QtCore import Qt, QTimer, Signal
from qtpy.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from bec_widgets.utils import ConnectionConfig
from bec_widgets.utils.bec_signal_proxy import BECSignalProxy
from bec_widgets.utils.colors import Colors, set_theme
from bec_widgets.utils.container_utils import WidgetContainerUtils
from bec_widgets.utils.error_popups import SafeProperty, SafeSlot
from bec_widgets.utils.settings_dialog import SettingsDialog
from bec_widgets.utils.toolbars.toolbar import MaterialIconAction
from bec_widgets.widgets.dap.lmfit_dialog.lmfit_dialog import LMFitDialog
from bec_widgets.widgets.plots.plot_base import PlotBase
from bec_widgets.widgets.plots.waveform.curve import Curve, CurveConfig, DeviceSignal
from bec_widgets.widgets.plots.waveform.settings.curve_settings.curve_setting import CurveSetting
from bec_widgets.widgets.plots.waveform.utils.roi_manager import WaveformROIManager
from bec_widgets.widgets.services.scan_history_browser.scan_history_browser import (
    ScanHistoryBrowser,
)

logger = bec_logger.logger


# noinspection PyDataclass
class WaveformConfig(ConnectionConfig):
    color_palette: str | None = Field(
        "plasma", description="The color palette of the figure widget.", validate_default=True
    )
    max_dataset_size_mb: float = Field(
        10,
        description="Maximum dataset size (in MB) permitted when fetching async data from history before prompting the user.",
        validate_default=True,
    )

    model_config: dict = {"validate_assignment": True}
    _validate_color_palette = field_validator("color_palette")(Colors.validate_color_map)


class Waveform(PlotBase):
    """
    Widget for plotting waveforms.
    """

    PLUGIN = True
    RPC = True
    ICON_NAME = "show_chart"
    USER_ACCESS = [
        # General PlotBase Settings
        "_config_dict",
        "enable_toolbar",
        "enable_toolbar.setter",
        "enable_side_panel",
        "enable_side_panel.setter",
        "enable_fps_monitor",
        "enable_fps_monitor.setter",
        "set",
        "title",
        "title.setter",
        "x_label",
        "x_label.setter",
        "y_label",
        "y_label.setter",
        "x_limits",
        "x_limits.setter",
        "y_limits",
        "y_limits.setter",
        "x_grid",
        "x_grid.setter",
        "y_grid",
        "y_grid.setter",
        "inner_axes",
        "inner_axes.setter",
        "outer_axes",
        "outer_axes.setter",
        "lock_aspect_ratio",
        "lock_aspect_ratio.setter",
        "auto_range_x",
        "auto_range_x.setter",
        "auto_range_y",
        "auto_range_y.setter",
        "auto_range",
        "x_log",
        "x_log.setter",
        "y_log",
        "y_log.setter",
        "legend_label_size",
        "legend_label_size.setter",
        "minimal_crosshair_precision",
        "minimal_crosshair_precision.setter",
        "screenshot",
        # Waveform Specific RPC Access
        "curves",
        "x_mode",
        "x_mode.setter",
        "x_entry",
        "x_entry.setter",
        "color_palette",
        "color_palette.setter",
        "skip_large_dataset_warning",
        "skip_large_dataset_warning.setter",
        "skip_large_dataset_check",
        "skip_large_dataset_check.setter",
        "max_dataset_size_mb",
        "max_dataset_size_mb.setter",
        "plot",
        "add_dap_curve",
        "remove_curve",
        "update_with_scan_history",
        "get_dap_params",
        "get_dap_summary",
        "get_all_data",
        "get_curve",
        "select_roi",
        "clear_all",
    ]

    sync_signal_update = Signal()
    async_signal_update = Signal()
    request_dap_update = Signal()
    unblock_dap_proxy = Signal()
    dap_params_update = Signal(dict, dict)
    dap_summary_update = Signal(dict, dict)
    new_scan = Signal()
    new_scan_id = Signal(str)

    roi_changed = Signal(tuple)
    roi_active = Signal(bool)
    roi_enable = Signal(bool)  # enable toolbar icon

    def __init__(
        self,
        parent: QWidget | None = None,
        config: WaveformConfig | None = None,
        client=None,
        gui_id: str | None = None,
        popups: bool = True,
        **kwargs,
    ):
        if config is None:
            config = WaveformConfig(widget_class=self.__class__.__name__)
        super().__init__(
            parent=parent, config=config, client=client, gui_id=gui_id, popups=popups, **kwargs
        )

        # Curve data
        self._sync_curves = []
        self._async_curves = []
        self._history_curves = []
        self._slice_index = None
        self._dap_curves = []
        self._mode = None

        # Scan data
        self._scan_done = True  # means scan is not running
        self.old_scan_id = None
        self.scan_id = None
        self.scan_item = None
        self.readout_priority = None
        self.x_axis_mode = {
            "name": "auto",
            "entry": None,
            "readout_priority": None,
            "label_suffix": "",
        }
        self._current_x_device: tuple[str, str] | None = None

        # Specific GUI elements
        self._init_roi_manager()
        self.dap_summary = None
        self.dap_summary_dialog = None
        self.scan_history_dialog = None
        self._add_waveform_specific_popup()
        self._enable_roi_toolbar_action(False)  # default state where are no dap curves
        self._init_curve_dialog()
        self.curve_settings_dialog = None

        # Large‑dataset guard
        self._skip_large_dataset_warning = False  # session flag
        self._skip_large_dataset_check = False  # per-plot flag, to skip the warning for this plot

        # Scan status update loop
        self.bec_dispatcher.connect_slot(self.on_scan_status, MessageEndpoints.scan_status())
        self.bec_dispatcher.connect_slot(self.on_scan_progress, MessageEndpoints.scan_progress())

        # Curve update loop
        self.proxy_update_sync = pg.SignalProxy(
            self.sync_signal_update, rateLimit=25, slot=self.update_sync_curves
        )
        self.proxy_update_async = pg.SignalProxy(
            self.async_signal_update, rateLimit=25, slot=self.update_async_curves
        )
        self.proxy_dap_request = BECSignalProxy(
            self.request_dap_update, rateLimit=25, slot=self.request_dap, timeout=10.0
        )
        self.unblock_dap_proxy.connect(self.proxy_dap_request.unblock_proxy)
        self.roi_enable.connect(self._enable_roi_toolbar_action)

        self.update_with_scan_history(-1)

        # for updating a color scheme of curves
        self._connect_to_theme_change()
        # To fix the ViewAll action with clipToView activated
        self._connect_viewbox_menu_actions()

        self.toolbar.show_bundles(["plot_export", "mouse_interaction", "roi", "axis_popup"])

    def _connect_viewbox_menu_actions(self):
        """Connect the viewbox menu action ViewAll to the custom reset_view method."""
        menu = self.plot_item.vb.menu
        # Find and replace "View All" action
        for action in menu.actions():
            if action.text() == "View All":
                # Disconnect the default autoRange action
                action.triggered.disconnect()
                # Connect to the custom reset_view method
                action.triggered.connect(self._reset_view)
                break

    ################################################################################
    # Widget Specific GUI interactions
    ################################################################################
    @SafeSlot(str)
    def apply_theme(self, theme: str):
        """
        Apply the theme to the widget.

        Args:
            theme(str, optional): The theme to be applied.
        """
        self._refresh_colors()
        super().apply_theme(theme)

    def add_side_menus(self):
        """
        Add side menus to the Waveform widget.
        """
        super().add_side_menus()
        self._add_dap_summary_side_menu()

    def _add_waveform_specific_popup(self):
        """
        Add popups to the Waveform widget.
        """
        self.toolbar.components.add_safe(
            "fit_params",
            MaterialIconAction(
                icon_name="monitoring", tooltip="Open Fit Parameters", checkable=True, parent=self
            ),
        )
        self.toolbar.components.add_safe(
            "scan_history",
            MaterialIconAction(
                icon_name="manage_search",
                tooltip="Open Scan History browser",
                checkable=True,
                parent=self,
            ),
        )
        self.toolbar.get_bundle("axis_popup").add_action("fit_params")
        self.toolbar.get_bundle("axis_popup").add_action("scan_history")

        self.toolbar.components.get_action("fit_params").action.triggered.connect(
            self.show_dap_summary_popup
        )
        self.toolbar.components.get_action("scan_history").action.triggered.connect(
            self.show_scan_history_popup
        )

    @SafeSlot()
    def _reset_view(self):
        """
        Custom _reset_view method to fix ViewAll action in toolbar.
        Due to setting clipToView to True on the curves, the autoRange() method
        of the ViewBox does no longer work as expected. This method deactivates the
        setClipToView for all curves, calls autoRange() to circumvent that issue.
        Afterwards, it re-enables the setClipToView for all curves again.

        It is hooked to the ViewAll action in the right-click menu of the pg.PlotItem ViewBox.
        """
        for curve in self._async_curves + self._sync_curves:
            curve.setClipToView(False)
        self.plot_item.vb.autoRange()
        self.auto_range_x = True
        self.auto_range_y = True
        for curve in self._async_curves + self._sync_curves:
            curve.setClipToView(True)

    ################################################################################
    # Roi manager

    def _init_roi_manager(self):
        """
        Initialize the ROI manager for the Waveform widget.
        """
        # Add toolbar icon
        self.toolbar.components.add_safe(
            "roi_linear",
            MaterialIconAction(
                icon_name="align_justify_space_between",
                tooltip="Add ROI region for DAP",
                checkable=True,
                parent=self,
            ),
        )
        self.toolbar.get_bundle("roi").add_action("roi_linear")

        self._roi_manager = WaveformROIManager(self.plot_item, parent=self)

        # Connect manager signals -> forward them via Waveform's own signals
        self._roi_manager.roi_changed.connect(self.roi_changed)
        self._roi_manager.roi_active.connect(self.roi_active)

        # Example: connect ROI changed to re-request DAP
        self.roi_changed.connect(self._on_roi_changed_for_dap)
        self._roi_manager.roi_active.connect(self.request_dap_update)
        self.toolbar.components.get_action("roi_linear").action.toggled.connect(
            self._roi_manager.toggle_roi
        )

    def _init_curve_dialog(self):
        """
        Initializes the Curve dialog within the toolbar.
        """
        self.toolbar.components.add_safe(
            "curve",
            MaterialIconAction(
                icon_name="timeline", tooltip="Show Curve dialog.", checkable=True, parent=self
            ),
        )
        self.toolbar.get_bundle("axis_popup").add_action("curve")
        self.toolbar.components.get_action("curve").action.triggered.connect(
            self.show_curve_settings_popup
        )

    def show_curve_settings_popup(self):
        """
        Displays the curve settings popup to allow users to modify curve-related configurations.
        """
        curve_action = self.toolbar.components.get_action("curve").action

        if self.curve_settings_dialog is None or not self.curve_settings_dialog.isVisible():
            curve_setting = CurveSetting(parent=self, target_widget=self)
            self.curve_settings_dialog = SettingsDialog(
                self, settings_widget=curve_setting, window_title="Curve Settings", modal=False
            )
            # When the dialog is closed, update the toolbar icon and clear the reference
            self.curve_settings_dialog.finished.connect(self._curve_settings_closed)
            self.curve_settings_dialog.show()
            curve_action.setChecked(True)
        else:
            # If already open, bring it to the front
            self.curve_settings_dialog.raise_()
            self.curve_settings_dialog.activateWindow()
            curve_action.setChecked(True)  # keep it toggled

    def _curve_settings_closed(self):
        """
        Slot for when the axis settings dialog is closed.
        """
        self.curve_settings_dialog.close()
        self.curve_settings_dialog.deleteLater()
        self.curve_settings_dialog = None
        self.toolbar.components.get_action("curve").action.setChecked(False)

    @property
    def roi_region(self) -> tuple[float, float] | None:
        """
        Allows external code to get/set the ROI region easily via Waveform.
        """
        return self._roi_manager.roi_region

    @roi_region.setter
    def roi_region(self, value: tuple[float, float] | None):
        """
        Set the ROI region limits.

        Args:
            value(tuple[float, float] | None): The new ROI region limits.
        """
        self._roi_manager.roi_region = value

    def select_roi(self, region: tuple[float, float]):
        """
        Public method if you want the old `select_roi` style.
        """
        self._roi_manager.select_roi(region)

    def toggle_roi(self, enabled: bool):
        """
        Toggle the ROI on or off.

        Args:
            enabled(bool): Whether to enable or disable the ROI.
        """
        self._roi_manager.toggle_roi(enabled)

    def _on_roi_changed_for_dap(self):
        """
        Whenever the ROI changes, you might want to re-request DAP with the new x_min, x_max.
        """
        self.request_dap_update.emit()

    def _enable_roi_toolbar_action(self, enable: bool):
        """
        Enable or disable the ROI toolbar action.

        Args:
            enable(bool): Enable or disable the ROI toolbar action.
        """
        self.toolbar.components.get_action("roi_linear").action.setEnabled(enable)
        if enable is False:
            self.toolbar.components.get_action("roi_linear").action.setChecked(False)
            self._roi_manager.toggle_roi(False)

    ################################################################################
    # Scan History browser popup
    # TODO this is so far quick implementation just as popup, we should make scan history also standalone widget later
    def show_scan_history_popup(self):
        """
        Show the scan history popup.
        """
        scan_history_action = self.toolbar.components.get_action("scan_history").action
        if self.scan_history_dialog is None or not self.scan_history_dialog.isVisible():
            self.scan_history_widget = ScanHistoryBrowser(parent=self)
            self.scan_history_dialog = QDialog(modal=False)
            self.scan_history_dialog.setWindowTitle(f"{self.object_name} - Scan History Browser")
            self.scan_history_dialog.layout = QVBoxLayout(self.scan_history_dialog)
            self.scan_history_dialog.layout.addWidget(self.scan_history_widget)
            self.scan_history_widget.scan_history_device_viewer.request_history_plot.connect(
                lambda scan_id, device_name, signal_name: self.plot(
                    y_name=device_name, y_entry=signal_name, scan_id=scan_id
                )
            )
            self.scan_history_dialog.finished.connect(self._scan_history_closed)
            self.scan_history_dialog.show()
            self.scan_history_dialog.resize(780, 320)
            scan_history_action.setChecked(True)
        else:
            # If already open, bring it to the front
            self.scan_history_dialog.raise_()
            self.scan_history_dialog.activateWindow()
            scan_history_action.setChecked(True)  # keep it toggle

    def _scan_history_closed(self):
        """
        Slot for when the scan history dialog is closed.
        """
        if self.scan_history_dialog is None:
            return
        self.scan_history_widget.close()
        self.scan_history_widget.deleteLater()
        self.scan_history_dialog.deleteLater()
        self.scan_history_dialog = None
        self.toolbar.components.get_action("scan_history").action.setChecked(False)

    ################################################################################
    # Dap Summary

    def _add_dap_summary_side_menu(self):
        """
        Add the DAP summary to the side panel.
        """
        self.dap_summary = LMFitDialog(parent=self)
        self.side_panel.add_menu(
            action_id="fit_params",
            icon_name="monitoring",
            tooltip="Open Fit Parameters",
            widget=self.dap_summary,
            title="Fit Parameters",
        )
        self.dap_summary_update.connect(self.dap_summary.update_summary_tree)

    def show_dap_summary_popup(self):
        """
        Show the DAP summary popup.
        """
        fit_action = self.toolbar.components.get_action("fit_params").action
        if self.dap_summary_dialog is None or not self.dap_summary_dialog.isVisible():
            self.dap_summary = LMFitDialog(parent=self)
            self.dap_summary_dialog = QDialog(modal=False)
            self.dap_summary_dialog.layout = QVBoxLayout(self.dap_summary_dialog)
            self.dap_summary_dialog.layout.addWidget(self.dap_summary)
            self.dap_summary_update.connect(self.dap_summary.update_summary_tree)
            self.dap_summary_dialog.finished.connect(self._dap_summary_closed)
            self.dap_summary_dialog.show()
            self._refresh_dap_signals()  # Get current dap data
            self.dap_summary_dialog.resize(300, 300)
            fit_action.setChecked(True)
        else:
            # If already open, bring it to the front
            self.dap_summary_dialog.raise_()
            self.dap_summary_dialog.activateWindow()
            fit_action.setChecked(True)  # keep it toggle

    def _dap_summary_closed(self):
        """
        Slot for when the axis settings dialog is closed.
        """
        self.dap_summary.close()
        self.dap_summary.deleteLater()
        self.dap_summary_dialog.deleteLater()
        self.dap_summary_dialog = None
        self.toolbar.components.get_action("fit_params").action.setChecked(False)

    def _get_dap_from_target_widget(self) -> None:
        """Get the DAP data from the target widget and update the DAP dialog manually on creation."""
        dap_summary = self.get_dap_summary()
        for curve_id, data in dap_summary.items():
            md = {"curve_id": curve_id}
            self.dap_summary.update_summary_tree(data=data, metadata=md)

    @SafeSlot()
    def get_dap_params(self) -> dict[str, dict]:
        """
        Get the DAP parameters of all DAP curves.

        Returns:
            dict[str, dict]: DAP parameters of all DAP curves.
        """
        return {curve.name(): curve.dap_params for curve in self._dap_curves}

    @SafeSlot()
    def get_dap_summary(self) -> dict[str, dict]:
        """
        Get the DAP summary of all DAP curves.

        Returns:
            dict[str, dict]: DAP summary of all DAP curves.
        """
        return {curve.name(): curve.dap_summary for curve in self._dap_curves}

    ################################################################################
    # Widget Specific Properties
    ################################################################################

    @SafeProperty(str)
    def x_mode(self) -> str:
        return self.x_axis_mode["name"]

    @x_mode.setter
    def x_mode(self, value: str):
        self.x_axis_mode["name"] = value
        if value not in ["timestamp", "index", "auto"]:
            self.x_axis_mode["entry"] = self.entry_validator.validate_signal(value, None)
            self._current_x_device = (value, self.x_axis_mode["entry"])
        self._switch_x_axis_item(mode=value)
        self._current_x_device = None
        self._refresh_history_curves()
        self._update_curve_visibility()
        self.async_signal_update.emit()
        self.sync_signal_update.emit()
        self.plot_item.enableAutoRange(x=True)
        self.round_plot_widget.apply_plot_widget_style()  # To keep the correct theme

    @SafeProperty(str)
    def x_entry(self) -> str | None:
        """
        The x signal name.
        """
        return self.x_axis_mode["entry"]

    @x_entry.setter
    def x_entry(self, value: str | None):
        """
        Set the x signal name.

        Args:
            value(str|None): The x signal name to set.
        """
        if value is None:
            return
        if self.x_axis_mode["name"] in ["auto", "index", "timestamp"]:
            logger.warning("Cannot set x_entry when x_mode is not 'device'.")
            return
        self.x_axis_mode["entry"] = self.entry_validator.validate_signal(self.x_mode, value)
        self._switch_x_axis_item(mode="device")
        self._refresh_history_curves()
        self._update_curve_visibility()
        self.async_signal_update.emit()
        self.sync_signal_update.emit()
        self.plot_item.enableAutoRange(x=True)
        self.round_plot_widget.apply_plot_widget_style()

    @SafeProperty(str)
    def color_palette(self) -> str:
        """
        The color palette of the figure widget.
        """
        return self.config.color_palette

    @color_palette.setter
    def color_palette(self, value: str):
        """
        Set the color palette of the figure widget.

        Args:
            value(str): The color palette to set.
        """
        try:
            self.config.color_palette = value
        except ValidationError:
            return

        colors = Colors.golden_angle_color(
            colormap=self.config.color_palette, num=max(10, len(self.curves) + 1), format="HEX"
        )
        for i, curve in enumerate(self.curves):
            curve.set_color(colors[i])

    @SafeProperty(str, designable=False, popup_error=True)
    def curve_json(self) -> str:
        """
        A JSON string property that serializes all curves' pydantic configs.
        """
        raw_list = []
        for c in self.curves:
            if c.config.source == "custom":  # Do not serialize custom curves
                continue
            cfg_dict = c.config.model_dump()
            raw_list.append(cfg_dict)
        return json.dumps(raw_list, indent=2)

    @curve_json.setter
    def curve_json(self, json_data: str):
        """
        Load curves from a JSON string and add them to the plot, omitting custom source curves.
        """
        try:
            curve_configs = json.loads(json_data)
            self.clear_all()
            for cfg_dict in curve_configs:
                if cfg_dict.get("source") == "custom":
                    logger.warning(f"Custom source curve '{cfg_dict['label']}' not loaded.")
                    continue
                config = CurveConfig(**cfg_dict)
                self._add_curve(config=config)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")

    @property
    def curves(self) -> list[Curve]:
        """
        Get the curves of the plot widget as a list.

        Returns:
            list: List of curves.
        """
        return [item for item in self.plot_item.curves if isinstance(item, Curve)]

    @SafeProperty(bool)
    def skip_large_dataset_check(self) -> bool:
        """
        Whether to skip the large dataset warning when fetching async data.
        """
        return self._skip_large_dataset_check

    @skip_large_dataset_check.setter
    def skip_large_dataset_check(self, value: bool):
        """
        Set whether to skip the large dataset warning when fetching async data.

        Args:
            value(bool): Whether to skip the large dataset warning.
        """
        self._skip_large_dataset_check = value

    @SafeProperty(bool)
    def skip_large_dataset_warning(self) -> bool:
        """
        Whether to skip the large dataset warning when fetching async data.
        """
        return self._skip_large_dataset_warning

    @skip_large_dataset_warning.setter
    def skip_large_dataset_warning(self, value: bool):
        """
        Set whether to skip the large dataset warning when fetching async data.

        Args:
            value(bool): Whether to skip the large dataset warning.
        """
        self._skip_large_dataset_warning = value

    @SafeProperty(float)
    def max_dataset_size_mb(self) -> float:
        """
        The maximum dataset size (in MB) permitted when fetching async data from history before prompting the user.
        """
        return self.config.max_dataset_size_mb

    @max_dataset_size_mb.setter
    def max_dataset_size_mb(self, value: float):
        """
        Set the maximum dataset size (in MB) permitted when fetching async data from history before prompting the user.

        Args:
            value(float): The maximum dataset size in MB.
        """
        if value <= 0:
            raise ValueError("Maximum dataset size must be greater than 0.")
        self.config.max_dataset_size_mb = value

    ################################################################################
    # High Level methods for API
    ################################################################################
    @SafeSlot(popup_error=True)
    def plot(
        self,
        arg1: list | np.ndarray | str | None = None,
        y: list | np.ndarray | None = None,
        x: list | np.ndarray | None = None,
        x_name: str | None = None,
        y_name: str | None = None,
        x_entry: str | None = None,
        y_entry: str | None = None,
        color: str | None = None,
        label: str | None = None,
        dap: str | None = None,
        scan_id: str | None = None,
        scan_number: int | None = None,
        **kwargs,
    ) -> Curve:
        """
        Plot a curve to the plot widget.

        Args:
            arg1(list | np.ndarray | str | None): First argument, which can be x data, y data, or y_name.
            y(list | np.ndarray): Custom y data to plot.
            x(list | np.ndarray): Custom y data to plot.
            x_name(str): Name of the x signal.
                - "auto": Use the best effort signal.
                - "timestamp": Use the timestamp signal.
                - "index": Use the index signal.
                - Custom signal name of a device from BEC.
            y_name(str): The name of the device for the y-axis.
            x_entry(str): The name of the entry for the x-axis.
            y_entry(str): The name of the entry for the y-axis.
            color(str): The color of the curve.
            label(str): The label of the curve.
            dap(str): The dap model to use for the curve, only available for sync devices.
            If not specified, none will be added.
            Use the same string as is the name of the LMFit model.
            scan_id(str):  Optional scan ID. When provided, the curve is treated as a **history** curve and
                the y‑data (and optional x‑data) are fetched from that historical scan. Such curves are
                never cleared by live‑scan resets.
            scan_number(int): Optional scan index. When provided, the curve is treated as a **history** curve and

        Returns:
            Curve: The curve object.
        """
        # 0) preallocate
        source = "custom"
        x_data = None
        y_data = None

        # 1. Custom curve logic
        if x is not None and y is not None:
            source = "custom"
            x_data = np.asarray(x)
            y_data = np.asarray(y)

        if isinstance(arg1, str):
            y_name = arg1
        elif isinstance(arg1, list):
            if isinstance(y, list):
                source = "custom"
                x_data = np.asarray(arg1)
                y_data = np.asarray(y)
            if y is None:
                source = "custom"
                arr = np.asarray(arg1)
                x_data = np.arange(len(arr))
                y_data = arr
        elif isinstance(arg1, np.ndarray) and y is None:
            if arg1.ndim == 1:
                source = "custom"
                x_data = np.arange(len(arg1))
                y_data = arg1
            if arg1.ndim == 2 and arg1.shape[1] == 2:
                source = "custom"
                x_data = arg1[:, 0]
                y_data = arg1[:, 1]

        # If y_name is set => device data
        if y_name is not None and x_data is None and y_data is None:
            source = "device"
            # Validate or obtain entry
            y_entry = self.entry_validator.validate_signal(name=y_name, entry=y_entry)

        # If user gave x_name => store in x_axis_mode, but do not set data here
        if x_name is not None:
            self.x_mode = x_name
            if x_name not in ["timestamp", "index", "auto"]:
                self.x_axis_mode["entry"] = self.entry_validator.validate_signal(x_name, x_entry)

        # Decide label if not provided
        if label is None:
            if source == "custom":
                label = WidgetContainerUtils.generate_unique_name(
                    "Curve", [c.object_name for c in self.curves]
                )
            else:
                label = f"{y_name}-{y_entry}"

        # If color not provided, generate from palette
        if color is None:
            color = self._generate_color_from_palette()

        # Build the config
        config = CurveConfig(
            widget_class="Curve",
            parent_id=self.gui_id,
            label=label,
            color=color,
            source=source,
            scan_id=scan_id,
            scan_number=scan_number,
            **kwargs,
        )

        # If it's device-based, attach DeviceSignal
        if source == "device":
            config.signal = DeviceSignal(name=y_name, entry=y_entry)

        if scan_id is not None or scan_number is not None:
            config.source = "history"

        # CREATE THE CURVE
        curve = self._add_curve(config=config, x_data=x_data, y_data=y_data)

        if dap is not None and source == "device":
            self.add_dap_curve(device_label=curve.name(), dap_name=dap, **kwargs)

        return curve

    ################################################################################
    # Curve Management Methods
    @SafeSlot()
    def add_dap_curve(
        self,
        device_label: str,
        dap_name: str,
        color: str | None = None,
        dap_oversample: int = 1,
        **kwargs,
    ) -> Curve:
        """
        Create a new DAP curve referencing the existing device curve `device_label`,
        with the data processing model `dap_name`.

        Args:
            device_label(str): The label of the device curve to add DAP to.
            dap_name(str): The name of the DAP model to use.
            color(str): The color of the curve.
            dap_oversample(int): The oversampling factor for the DAP curve.
            **kwargs

        Returns:
            Curve: The new DAP curve.
        """

        # 1) Find the existing device curve by label
        device_curve = self._find_curve_by_label(device_label)
        if not device_curve:
            raise ValueError(f"No existing curve found with label '{device_label}'.")
        if device_curve.config.source not in ("device", "history"):
            raise ValueError(
                f"Curve '{device_label}' is not a device curve. Only device curves can have DAP."
            )

        dev_name = device_curve.config.signal.name
        dev_entry = device_curve.config.signal.entry

        # 2) Build a label for the new DAP curve
        dap_label = f"{device_label}-{dap_name}"

        # 3) Possibly raise if the DAP curve already exists
        if self._check_curve_id(dap_label):
            raise ValueError(f"DAP curve '{dap_label}' already exists.")

        if color is None:
            color = self._generate_color_from_palette()

        # Build config for DAP
        config = CurveConfig(
            widget_class="Curve",
            parent_id=self.gui_id,
            label=dap_label,
            color=color,
            source="dap",
            parent_label=device_label,
            symbol="star",
            **kwargs,
        )

        # Attach device signal with DAP
        config.signal = DeviceSignal(
            name=dev_name, entry=dev_entry, dap=dap_name, dap_oversample=dap_oversample
        )

        # 4) Create the DAP curve config using `_add_curve(...)`
        dap_curve = self._add_curve(config=config)

        return dap_curve

    def _add_curve(
        self,
        config: CurveConfig,
        x_data: np.ndarray | None = None,
        y_data: np.ndarray | None = None,
    ) -> Curve:
        """
        Private method to finalize the creation of a new Curve in this Waveform widget
        based on an already-built `CurveConfig`.

        Args:
            config (CurveConfig): A fully populated pydantic model describing how to create and style the curve.
            x_data (np.ndarray | None): If this is a custom curve (config.source == "custom"), optional x data array.
            y_data (np.ndarray | None): If this is a custom curve (config.source == "custom"), optional y data array.

        Returns:
            Curve: The newly created curve object.

        Raises:
            ValueError: If a duplicate curve label/config is found, or if
                        custom data is missing for `source='custom'`.
        """
        scan_item: ScanDataContainer | None = None
        if config.source == "history":
            scan_item = self.get_history_scan_item(
                scan_id=config.scan_id, scan_index=config.scan_number
            )
            if scan_item is None:
                raise ValueError(
                    f"Could not find scan item for history curve '{config.label}' with scan_id='{config.scan_id}' and scan_number='{config.scan_number}'."
                )

            config.scan_id = scan_item.metadata["bec"]["scan_id"]
            config.scan_number = scan_item.metadata["bec"]["scan_number"]

        label = config.label
        if config.source == "history":
            label = f"{config.signal.name}-{config.signal.entry}-scan-{config.scan_number}"
            config.label = label
        if not label:
            # Fallback label
            label = WidgetContainerUtils.generate_unique_name(
                "Curve", [c.object_name for c in self.curves]
            )
            config.label = label

        # Check for duplicates
        if self._check_curve_id(label):
            raise ValueError(f"Curve with ID '{label}' already exists in widget '{self.gui_id}'.")

        # If a user did not provide color in config, pick from palette
        if not config.color:
            config.color = self._generate_color_from_palette()

        # For custom data, ensure x_data, y_data
        if config.source == "custom":
            if x_data is None or y_data is None:
                raise ValueError("For 'custom' curves, x_data and y_data must be provided.")

        # Actually create the Curve item
        curve = self._add_curve_object(name=label, config=config, scan_item=scan_item)

        # If custom => set initial data
        if config.source == "custom" and x_data is not None and y_data is not None:
            curve.setData(x_data, y_data)

        # If device => schedule BEC updates
        if config.source == "device":
            if self.scan_item is None:
                self.update_with_scan_history(-1)
            self.async_signal_update.emit()
            self.sync_signal_update.emit()
        if config.source == "dap":
            self._dap_curves.append(curve)
            self.setup_dap_for_scan()
            self.roi_enable.emit(True)  # Enable the ROI toolbar action
            self.request_dap()  # Request DAP update directly without blocking proxy
        if config.source == "history":
            self._history_curves.append(curve)

        QTimer.singleShot(
            150, self.auto_range
        )  # autorange with a delay to ensure the plot is updated

        return curve

    def _add_curve_object(
        self, name: str, config: CurveConfig, scan_item: ScanDataContainer | None = None
    ) -> Curve | None:
        """
        Low-level creation of the PlotDataItem (Curve) from a `CurveConfig`.

        Args:
            name (str): The name/label of the curve.
            config (CurveConfig): Configuration model describing the curve.
            scan_item (ScanDataContainer | None): Optional scan item for history curves.

        Returns:
            Curve: The newly created curve object, added to the plot.
        """
        curve = Curve(config=config, name=name, parent_item=self)
        self.plot_item.addItem(curve)
        if scan_item is not None:
            self._fetch_history_data_for_curve(curve, scan_item)
        self._categorise_device_curves()
        curve.visibleChanged.connect(self._refresh_crosshair_markers)
        curve.visibleChanged.connect(self.auto_range)
        return curve

    def _fetch_history_data_for_curve(
        self, curve: Curve, scan_item: ScanDataContainer
    ) -> Curve | None:
        # Check if the data are already set
        device = curve.config.signal.name
        entry = curve.config.signal.entry

        all_devices_used = getattr(
            getattr(scan_item, "_msg", None), "stored_data_info", None
        ) or getattr(scan_item, "stored_data_info", None)
        if all_devices_used is None:
            curve.remove()
            raise ValueError(
                f"No stored data info found in scan item ID:{curve.config.scan_id} for curve '{curve.name()}'. "
                f"Upgrade BEC to the latest version."
            )

        # 1. get y data
        x_data, y_data = None, None
        if device not in all_devices_used:
            raise ValueError(f"Device '{device}' not found in scan item ID:{curve.config.scan_id}.")
        if entry not in all_devices_used[device]:
            raise ValueError(
                f"Entry '{entry}' not found in device '{device}' in scan item ID:{curve.config.scan_id}."
            )
        y_shape = all_devices_used.get(device).get(entry).shape[0]

        # Determine X-axis data
        if self.x_axis_mode["name"] == "index":
            x_data = np.arange(y_shape)
            curve.config.current_x_mode = "index"
            self._update_x_label_suffix(" (index)")
        elif self.x_axis_mode["name"] == "timestamp":
            y_device = scan_item.devices.get(device)
            x_data = y_device.get(entry).read().get("timestamp")
            curve.config.current_x_mode = "timestamp"
            self._update_x_label_suffix(" (timestamp)")
        elif self.x_axis_mode["name"] not in ("index", "timestamp", "auto"):  # Custom device mode
            if self.x_axis_mode["name"] not in all_devices_used:
                logger.warning(
                    f"Custom device '{self.x_axis_mode['name']}' not found in scan item of history curve '{curve.name()}'; scan ID: {curve.config.scan_id}."
                )
                curve.setVisible(False)
                return
            x_entry_custom = self.x_axis_mode.get("entry")
            if x_entry_custom is None:
                x_entry_custom = self.entry_validator.validate_signal(
                    self.x_axis_mode["name"], None
                )
            if x_entry_custom not in all_devices_used[self.x_axis_mode["name"]]:
                logger.warning(
                    f"Custom entry '{x_entry_custom}' for device '{self.x_axis_mode['name']}' not found in scan item of history curve '{curve.name()}'; scan ID: {curve.config.scan_id}."
                )
                curve.setVisible(False)
                return
            x_shape = (
                scan_item._msg.stored_data_info.get(self.x_axis_mode["name"])
                .get(x_entry_custom)
                .shape[0]
            )
            if x_shape != y_shape:
                logger.warning(
                    f"Shape mismatch for x data '{x_shape}' and y data '{y_shape}' in history curve '{curve.name()}'; scan ID: {curve.config.scan_id}."
                )
                curve.setVisible(False)
                return
            x_device = scan_item.devices.get(self.x_axis_mode["name"])
            x_data = x_device.get(x_entry_custom).read().get("value")
            curve.config.current_x_mode = self.x_axis_mode["name"]
            self._update_x_label_suffix(f" (custom: {self.x_axis_mode['name']}-{x_entry_custom})")
        elif self.x_axis_mode["name"] == "auto":
            if (
                self._current_x_device is None
            ):  # Scenario where no x device is set yet, because there was no live scan done in this widget yet
                # If no current x device, use the first motor from scan item
                scan_motors = self._ensure_str_list(
                    scan_item.metadata.get("bec").get("scan_report_devices")
                )
                if not scan_motors:  # scan was done without reported motor from whatever reason
                    x_data = np.arange(y_shape)  # Fallback to index
                    y_data = scan_item.devices.get(device).get(entry).read().get("value")
                    curve.set_data(x=x_data, y=y_data)
                    self._update_x_label_suffix(" (auto: index)")
                    return curve
                x_entry = self.entry_validator.validate_signal(scan_motors[0], None)
                if x_entry not in all_devices_used.get(scan_motors[0], {}):
                    logger.warning(
                        f"Auto x entry '{x_entry}' for device '{scan_motors[0]}' not found in scan item of history curve '{curve.name()}'; scan ID: {curve.config.scan_id}."
                    )
                    curve.setVisible(False)
                    return
                if y_shape != all_devices_used.get(scan_motors[0]).get(x_entry, {}).shape[0]:
                    logger.warning(
                        f"Shape mismatch for x data '{all_devices_used.get(scan_motors[0]).get(x_entry, {}).get('shape', [0])[0]}' and y data '{y_shape}' in history curve '{curve.name()}'; scan ID: {curve.config.scan_id}."
                    )
                    curve.setVisible(False)
                    return
                x_data = scan_item.devices.get(scan_motors[0]).get(x_entry).read().get("value")
                self._current_x_device = (scan_motors[0], x_entry)
                self._update_x_label_suffix(f" (auto: {scan_motors[0]}-{x_entry})")
                curve.config.current_x_mode = "auto"
                self._update_x_label_suffix(f" (auto: {scan_motors[0]}-{x_entry})")
            else:  # Scan in auto mode was done and live scan already set the current x device
                if self._current_x_device[0] not in all_devices_used:
                    logger.warning(
                        f"Auto x data for device '{self._current_x_device[0]}' "
                        f"and entry '{self._current_x_device[1]}'"
                        f" not found in scan item of the history curve {curve.name()}."
                    )
                    curve.setVisible(False)
                    return
                x_device = scan_item.devices.get(self._current_x_device[0])
                x_data = x_device.get(self._current_x_device[1]).read().get("value")
                curve.config.current_x_mode = "auto"
                self._update_x_label_suffix(
                    f" (auto: {self._current_x_device[0]}-{self._current_x_device[1]})"
                )
        if x_data is None:
            logger.warning(
                f"X data for curve '{curve.name()}' could not be determined. "
                f"Check if the x_mode '{self.x_axis_mode['name']}' is valid for the scan item."
            )
            curve.setVisible(False)
            return
        if y_data is None:
            y_data = scan_item.devices.get(device).get(entry).read().get("value")
            if y_data is None:
                logger.warning(
                    f"Y data for curve '{curve.name()}' could not be determined. "
                    f"Check if the device '{device}' and entry '{entry}' are valid for the scan item."
                )
                curve.setVisible(False)
                return
        curve.set_data(x=x_data, y=y_data)
        return curve

    def _refresh_history_curves(self):
        for curve in self._history_curves:
            scan_item = self.get_history_scan_item(
                scan_id=curve.config.scan_id, scan_index=curve.config.scan_number
            )
            if scan_item is not None:
                self._fetch_history_data_for_curve(curve, scan_item)
            else:
                logger.warning(f"Scan item for curve {curve.name()} not found.")

    def _refresh_crosshair_markers(self):
        """
        Refresh the crosshair markers when a curve visibility changes.
        """
        if self.crosshair is not None:
            self.crosshair.clear_markers()

    def _generate_color_from_palette(self) -> str:
        """
        Generate a color for the next new curve, based on the current number of curves.
        """
        current_count = len(self.curves)
        color_list = Colors.golden_angle_color(
            colormap=self.config.color_palette, num=max(10, current_count + 1), format="HEX"
        )
        return color_list[current_count]

    def _refresh_colors(self):
        """
        Re-assign colors to all existing curves so they match the new count-based distribution.
        """
        all_curves = self.curves
        # Generate enough colors for the new total
        color_list = Colors.golden_angle_color(
            colormap=self.config.color_palette, num=max(10, len(all_curves)), format="HEX"
        )
        for i, curve in enumerate(all_curves):
            curve.set_color(color_list[i])

    def clear_data(self):
        """
        Clear all data from the plot widget, but keep the curve references.
        """
        for c in self.curves:
            if c.config.source != "history":
                c.clear_data()

    # X-axis compatibility helpers
    def _is_curve_compatible(self, curve: Curve) -> bool:
        """
        Return True when *curve* can be shown with the current x-axis mode.

        - ‘index’, ‘timestamp’ are always compatible.
        - For history curves we check whether the requested motor
          (self.x_axis_mode["name"]) exists in the cached
          history_data_buffer["x"] dictionary.
        - DAP is done by checking if the parent curve is visible.
        - Device curves are fetched by update sync/async curves, which solves the compatibility there.
        """
        mode = self.x_axis_mode.get("name", "index")
        if mode in ("index", "timestamp"):  # always compatible - wild west mode
            return True
        if curve.config.source == "history":
            scan_item = self.get_history_scan_item(
                scan_id=curve.config.scan_id, scan_index=curve.config.scan_number
            )
            curve = self._fetch_history_data_for_curve(curve, scan_item)
            if curve is None:
                return False
        if curve.config.source == "dap":
            parent_curve = self._find_curve_by_label(curve.config.parent_label)
            if parent_curve.isVisible():
                return True
            return False  # DAP curve is not compatible if parent curve is not visible
        return True

    def _update_curve_visibility(self) -> None:
        """Show or hide curves according to `_is_curve_compatible`."""
        for c in self.curves:
            c.setVisible(self._is_curve_compatible(c))

    def clear_all(self):
        """
        Clear all curves from the plot widget.
        """
        curve_list = self.curves
        self._dap_curves = []
        self._sync_curves = []
        self._async_curves = []
        for curve in curve_list:
            self.remove_curve(curve.name())
        if self.crosshair is not None:
            self.crosshair.clear_markers()

    def get_curve(self, curve: int | str) -> Curve | None:
        """
        Get a curve from the plot widget.

        Args:
            curve(int|str): The curve to get. It Can be the order of the curve or the name of the curve.

        Return(Curve|None): The curve object if found, None otherwise.
        """
        if isinstance(curve, int):
            if curve < len(self.curves):
                return self.curves[curve]
        elif isinstance(curve, str):
            for c in self.curves:
                if c.name() == curve:
                    return c
        return None

    @SafeSlot(int, popup_error=True)
    @SafeSlot(str, popup_error=True)
    def remove_curve(self, curve: int | str):
        """
        Remove a curve from the plot widget.

        Args:
            curve(int|str): The curve to remove. It Can be the order of the curve or the name of the curve.
        """
        if isinstance(curve, int):
            self._remove_curve_by_order(curve)
        elif isinstance(curve, str):
            self._remove_curve_by_name(curve)

        self._refresh_colors()
        self._categorise_device_curves()

    def _remove_curve_by_name(self, name: str):
        """
        Remove a curve by its name from the plot widget.

        Args:
            name(str): Name of the curve to be removed.
        """
        for curve in self.curves:
            if curve.name() == name:
                self.plot_item.removeItem(curve)
                self._curve_clean_up(curve)
                return

    def _remove_curve_by_order(self, N: int):
        """
        Remove a curve by its order from the plot widget.

        Args:
            N(int): Order of the curve to be removed.
        """
        if N < len(self.curves):
            curve = self.curves[N]
            self.plot_item.removeItem(curve)
            self._curve_clean_up(curve)

        else:
            logger.error(f"Curve order {N} out of range.")
            raise IndexError(f"Curve order {N} out of range.")

    def _curve_clean_up(self, curve: Curve):
        """
        Clean up the curve by disconnecting the async update signal (even for sync curves).

        Args:
            curve(Curve): The curve to clean up.
        """
        self.bec_dispatcher.disconnect_slot(
            self.on_async_readback,
            MessageEndpoints.device_async_readback(self.scan_id, curve.name()),
        )
        curve.rpc_register.remove_rpc(curve)

        # Remove itself from the DAP summary only for side panels
        if (
            curve.config.source == "dap"
            and self.dap_summary is not None
            and self.enable_side_panel is True
        ):
            self.dap_summary.remove_dap_data(curve.name())

        # find a corresponding dap curve and remove it
        for c in self.curves:
            if c.config.parent_label == curve.name():
                self.plot_item.removeItem(c)
                self._curve_clean_up(c)

    def _check_curve_id(self, curve_id: str) -> bool:
        """
        Check if a curve ID exists in the plot widget.

        Args:
            curve_id(str): The ID of the curve to check.

        Returns:
            bool: True if the curve ID exists, False otherwise.
        """
        curve_ids = [curve.name() for curve in self.curves]
        if curve_id in curve_ids:
            return True
        return False

    def _find_curve_by_label(self, label: str) -> Curve | None:
        """
        Find a curve by its label.

        Args:
            label(str): The label of the curve to find.

        Returns:
            Curve|None: The curve object if found, None otherwise.
        """
        for c in self.curves:
            if c.name() == label:
                return c
        return None

    ################################################################################
    # BEC Update Methods
    ################################################################################
    @SafeSlot(dict, dict)
    def on_scan_status(self, msg: dict, meta: dict):
        """
        Initial scan status message handler, which is triggered at the begging and end of scan.
        Used for triggering the update of the sync and async curves.

        Args:
            msg(dict): The message content.
            meta(dict): The message metadata.
        """
        current_scan_id = msg.get("scan_id", None)
        if current_scan_id is None:
            return

        if current_scan_id != self.scan_id:
            self.reset()
            self.new_scan.emit()
            self.new_scan_id.emit(current_scan_id)
            self.auto_range_x = True
            self.auto_range_y = True
            self.old_scan_id = self.scan_id
            self.scan_id = current_scan_id
            self.scan_item = self.queue.scan_storage.find_scan_by_ID(self.scan_id)  # live scan
            self._slice_index = None  # Reset the slice index
            self._update_curve_visibility()
            self._mode = self._categorise_device_curves()

            # First trigger to sync and async data
            if self._mode == "sync":
                self.sync_signal_update.emit()
                logger.info("Scan status: Sync mode")
            elif self._mode == "async":
                for curve in self._async_curves:
                    self._setup_async_curve(curve)
                self.async_signal_update.emit()
                logger.info("Scan status: Async mode")
            else:
                self.sync_signal_update.emit()
                for curve in self._async_curves:
                    self._setup_async_curve(curve)
                self.async_signal_update.emit()
                logger.info("Scan status: Mixed mode")
                logger.warning("Mixed mode - integrity of x axis cannot be guaranteed.")
        self.setup_dap_for_scan()

    @SafeSlot(dict, dict)
    def on_scan_progress(self, msg: dict, meta: dict):
        """
        Slot for handling scan progress messages. Used for triggering the update of the sync curves.

        Args:
            msg(dict): The message content.
            meta(dict): The message metadata.
        """
        self.sync_signal_update.emit()
        self._scan_done = msg.get("done")
        if self._scan_done:
            QTimer.singleShot(100, self.update_sync_curves)
            QTimer.singleShot(300, self.update_sync_curves)

    def _fetch_scan_data_and_access(self) -> tuple[dict, str] | tuple[None, None]:
        """
        Decide whether the widget is in live or historical mode
        and return the appropriate data dict and access key.

        Returns:
            data_dict (dict): The data structure for the current scan.
            access_key (str): Either 'val' (live) or 'value' (history).
        """
        if self.scan_item is None:
            # Optionally fetch the latest from history if nothing is set
            self.update_with_scan_history(-1)
            if self.scan_item is None:
                logger.info("No scan executed so far; skipping device curves categorisation.")
                return None, None

        if hasattr(self.scan_item, "live_data"):
            # Live scan
            return self.scan_item.live_data, "val"
        else:
            # Historical
            scan_devices = self.scan_item.devices
            return (scan_devices, "value")

    def update_sync_curves(self):
        """
        Update the sync curves with the latest data from the scan.
        """
        if self.scan_item is None:
            logger.info("No scan executed so far; skipping device curves categorisation.")
            return
        data, access_key = self._fetch_scan_data_and_access()
        for curve in self._sync_curves:
            device_name = curve.config.signal.name
            device_entry = curve.config.signal.entry
            if access_key == "val":
                device_data = data.get(device_name, {}).get(device_entry, {}).get(access_key, None)
            else:
                entry_obj = data.get(device_name, {}).get(device_entry)
                device_data = entry_obj.read()["value"] if entry_obj else None
            x_data = self._get_x_data(device_name, device_entry)
            if x_data is not None:
                if np.isscalar(x_data):
                    self.clear_data()
                    return
            if device_data is not None and x_data is not None:
                curve.setData(x_data, device_data)
            if device_data is not None and x_data is None:
                curve.setData(device_data)
        self.request_dap_update.emit()

    def update_async_curves(self):
        """
        Updates asynchronously displayed curves with the latest scan data.

        Fetches the scan data and access key to update each curve in `_async_curves` with
        new values. If the data is available for a specific curve, it sets the x and y
        data for the curve. Emits a signal to request an update once all curves are updated.

        Raises:
            The raised errors are dependent on the internal methods such as
            `_fetch_scan_data_and_access`, `_get_x_data`, or `setData` used in this
            function.

        """
        data, access_key = self._fetch_scan_data_and_access()

        for curve in self._async_curves:
            device_name = curve.config.signal.name
            device_entry = curve.config.signal.entry
            if access_key == "val":  # live access
                device_data = data.get(device_name, {}).get(device_entry, {}).get(access_key, None)
            else:  # history access
                dataset_obj = data.get(device_name, {})
                if self._skip_large_dataset_check is False:
                    if not self._check_dataset_size_and_confirm(dataset_obj, device_entry):
                        continue  # user declined to load; skip this curve
                entry_obj = dataset_obj.get(device_entry, None)
                device_data = entry_obj.read()["value"] if entry_obj else None

            # if shape is 2D cast it into 1D and take the last waveform
            if len(np.shape(device_data)) > 1:
                device_data = device_data[-1, :]

            if device_data is None:
                logger.warning(f"Async data for curve {curve.name()} is None.")
                continue

            # Async curves only support plotting vs index or other device
            if self.x_axis_mode["name"] in ["timestamp", "index", "auto"]:
                device_data_x = np.linspace(0, len(device_data) - 1, len(device_data))
            else:
                # Fetch data from signal instead
                device_data_x = self._get_x_data(device_name, device_entry)

            # Fallback to 'index' in case data is not of equal length
            if len(device_data_x) != len(device_data):
                logger.warning(
                    f"Async data for curve {curve.name()} and x_axis {device_entry} is not of equal length. Falling back to 'index' plotting."
                )
                device_data_x = np.linspace(0, len(device_data) - 1, len(device_data))

            self._auto_adjust_async_curve_settings(curve, len(device_data))
            curve.setData(device_data_x, device_data)

        self.request_dap_update.emit()

    def _check_async_signal_found(self, name: str, signal: str) -> bool:
        """
        Check if the async signal is found in the BEC device manager.

        Args:
            name(str): The name of the async signal.
            signal(str): The entry of the async signal.

        Returns:
            bool: True if the async signal is found, False otherwise.
        """
        bec_async_signals = self.client.device_manager.get_bec_signals("AsyncSignal")
        for entry_name, _, entry_data in bec_async_signals:
            if entry_name == name and entry_data.get("obj_name") == signal:
                return True
        return False

    def _setup_async_curve(self, curve: Curve):
        """
        Setup async curve.

        Args:
            curve(Curve): The curve to set up.
        """
        name = curve.config.signal.name
        signal = curve.config.signal.entry
        async_signal_found = self._check_async_signal_found(name, signal)

        try:
            curve.clear_data()
        except KeyError:
            logger.warning(f"Curve {name} not found in plot item.")
            pass

        # New endpoint for async signals
        if async_signal_found:
            self.bec_dispatcher.disconnect_slot(
                self.on_async_readback,
                MessageEndpoints.device_async_signal(self.old_scan_id, name, signal),
            )
            self.bec_dispatcher.connect_slot(
                self.on_async_readback,
                MessageEndpoints.device_async_signal(self.scan_id, name, signal),
                from_start=True,
                cb_info={"scan_id": self.scan_id},
            )

        # old endpoint
        else:
            self.bec_dispatcher.disconnect_slot(
                self.on_async_readback,
                MessageEndpoints.device_async_readback(self.old_scan_id, name),
            )
            self.bec_dispatcher.connect_slot(
                self.on_async_readback,
                MessageEndpoints.device_async_readback(self.scan_id, name),
                from_start=True,
                cb_info={"scan_id": self.scan_id},
            )
        logger.info(f"Setup async curve {name}")

    @SafeSlot(dict, dict, verify_sender=True)
    def on_async_readback(self, msg, metadata):
        """
        Get async data readback. This code needs to be fast, therefor we try
        to reduce the number of copies in between cycles. Be careful when refactoring
        this part as it will affect the performance of the async readback.

        Async curves support plotting against 'index' or other 'device_signal'. No 'auto' or 'timestamp'.
        The fallback mechanism for 'auto' and 'timestamp' is to use the 'index'.

        Note:
            We create data_plot_x and data_plot_y and modify them within this function
            to avoid creating new arrays. This is important for performance.
            Support update instructions are 'add', 'add_slice', and 'replace'.

        Args:
            msg(dict): Message with the async data.
            metadata(dict): Metadata of the message.
        """
        sender = self.sender()
        if not hasattr(sender, "cb_info"):
            logger.info(f"Sender {sender} has no cb_info.")
            return
        scan_id = sender.cb_info.get("scan_id", None)
        if scan_id != self.scan_id:
            logger.info("Scan ID mismatch, ignoring async readback.")

        instruction = metadata.get("async_update", {}).get("type")
        if instruction not in ["add", "add_slice", "replace"]:
            logger.warning(f"Invalid async update instruction: {instruction}")
            return
        max_shape = metadata.get("async_update", {}).get("max_shape", [])
        plot_mode = self.x_axis_mode["name"]
        for curve in self._async_curves:
            x_data = None  # Reset x_data
            y_data = None  # Reset y_data
            # Get the curve data
            async_data = msg["signals"].get(curve.config.signal.entry, None)
            if async_data is None:
                continue
            # y-data
            data_plot_y = async_data["value"]
            if data_plot_y is None:
                logger.warning(f"Async data for curve {curve.name()} is None.")
                continue
            # Ensure we have numpy array for data_plot_y
            data_plot_y = np.asarray(data_plot_y)
            # Add
            if instruction == "add":
                if len(max_shape) > 1:
                    if len(data_plot_y.shape) > 1:
                        data_plot_y = data_plot_y[-1, :]
                else:
                    x_data, y_data = curve.get_data()
                    if y_data is not None:
                        data_plot_y = np.hstack((y_data, data_plot_y))
            # Add slice
            if instruction == "add_slice":
                current_slice_id = metadata.get("async_update", {}).get("index")
                if current_slice_id != curve.slice_index:
                    curve.slice_index = current_slice_id
                else:
                    x_data, y_data = curve.get_data()
                    if y_data is not None:
                        data_plot_y = np.hstack((y_data, data_plot_y))

            # Replace is trivial, no need to modify data_plot_y

            # Get x data for plotting
            if plot_mode in ["index", "auto", "timestamp"]:
                data_plot_x = np.linspace(0, len(data_plot_y) - 1, len(data_plot_y))
                self._auto_adjust_async_curve_settings(curve, len(data_plot_y))
                curve.setData(data_plot_x, data_plot_y)
                # Move on in the loop
                continue

            # x_axis_mode is device signal
            # Only consider device signals that are async for now, fallback is index
            x_device_entry = self.x_axis_mode["entry"]
            async_data = msg["signals"].get(x_device_entry, None)
            # Make sure the signal exists, otherwise fall back to index
            if async_data is None:
                # Try to grab the data from device signals
                data_plot_x = self._get_x_data(plot_mode, x_device_entry)
            else:
                data_plot_x = np.asarray(async_data["value"])
            if x_data is not None:
                data_plot_x = np.hstack((x_data, data_plot_x))
            # Fallback incase data is not of equal length
            if len(data_plot_x) != len(data_plot_y):
                logger.warning(
                    f"Async data for curve {curve.name()} and x_axis {x_device_entry} is not of equal length. Falling back to 'index' plotting."
                )
                data_plot_x = np.linspace(0, len(data_plot_y) - 1, len(data_plot_y))

            # Plot the data
            self._auto_adjust_async_curve_settings(curve, len(data_plot_y))
            curve.setData(data_plot_x, data_plot_y)

        self.request_dap_update.emit()

    def _auto_adjust_async_curve_settings(
        self,
        curve: Curve,
        data_length: int,
        limit: int = 1000,
        method: Literal["subsample", "mean", "peak"] | None = "peak",
    ) -> None:
        """
        Based on the length of the data this method will adjust the plotting settings of
        Curve items, by deactivating the symbol and activating downsampling auto, method='mean',
        if the data length exceeds N points. If the data length is less than N points, the
        symbol will be activated and downsampling will be deactivated. Maximum points will be
        5x the limit.

        Args:
            curve(Curve): The curve to adjust.
            data_length(int): The length of the data.
            limit(int): The limit of the data length to activate the downsampling.

        """
        if limit <= 1:
            logger.warning("Limit must be greater than 1.")
            return
        if data_length > limit:
            if curve.config.symbol is not None:
                curve.set_symbol(None)
            if curve.config.pen_width > 3:
                curve.set_pen_width(3)
            curve.setDownsampling(ds=None, auto=True, method=method)
            curve.setClipToView(True)
        elif data_length <= limit:
            curve.set_symbol("o")
            curve.set_pen_width(4)
            curve.setDownsampling(ds=1, auto=None, method=method)
            curve.setClipToView(True)

    def setup_dap_for_scan(self):
        """Setup DAP updates for the new scan."""
        self.bec_dispatcher.disconnect_slot(
            self.update_dap_curves,
            MessageEndpoints.dap_response(f"{self.old_scan_id}-{self.gui_id}"),
        )
        if len(self._dap_curves) > 0:
            self.bec_dispatcher.connect_slot(
                self.update_dap_curves,
                MessageEndpoints.dap_response(f"{self.scan_id}-{self.gui_id}"),
            )

    @SafeSlot()
    def request_dap(self, _=None):
        """Request new fit for data"""

        for dap_curve in self._dap_curves:
            parent_label = getattr(dap_curve.config, "parent_label", None)
            if not parent_label:
                continue
            # find the device curve
            parent_curve = self._find_curve_by_label(parent_label)
            if parent_curve is None:
                logger.warning(
                    f"No device curve found for DAP curve '{dap_curve.name()}'!"
                )  # TODO triggerd when DAP curve is removed from the curve dialog, why?
                continue

            x_data, y_data = parent_curve.get_data()
            model_name = dap_curve.config.signal.dap
            model = getattr(self.dap, model_name)
            try:
                x_min, x_max = self.roi_region
                x_data, y_data = self._crop_data(x_data, y_data, x_min, x_max)
            except TypeError:
                x_min = None
                x_max = None

            msg = messages.DAPRequestMessage(
                dap_cls="LmfitService1D",
                dap_type="on_demand",
                config={
                    "args": [],
                    "kwargs": {"data_x": x_data, "data_y": y_data},
                    "class_args": model._plugin_info["class_args"],
                    "class_kwargs": model._plugin_info["class_kwargs"],
                    "curve_label": dap_curve.name(),
                },
                metadata={"RID": f"{self.scan_id}-{self.gui_id}"},
            )
            self.client.connector.set_and_publish(MessageEndpoints.dap_request(), msg)

    @SafeSlot(dict, dict)
    def update_dap_curves(self, msg, metadata):
        """
        Update the DAP curves with the new data.

        Args:
            msg(dict): Message with the DAP data.
            metadata(dict): Metadata of the message.
        """
        self.unblock_dap_proxy.emit()
        # Extract configuration from the message
        msg_config = msg.get("dap_request", None).content.get("config", {})
        curve_id = msg_config.get("curve_label", None)
        curve = self._find_curve_by_label(curve_id)
        if not curve:
            return

        # Get data from the parent (device) curve
        parent_curve = self._find_curve_by_label(curve.config.parent_label)
        if parent_curve is None:
            return
        x_parent, _ = parent_curve.get_data()
        if x_parent is None or len(x_parent) == 0:
            return

        # Retrieve and store the fit parameters and summary from the DAP server response
        try:
            curve.dap_params = msg["data"][1]["fit_parameters"]
            curve.dap_summary = msg["data"][1]["fit_summary"]
        except TypeError:
            logger.warning(f"Failed to retrieve DAP data for curve '{curve.name()}'")
            return

        # Render model according to the DAP model name and parameters
        model_name = curve.config.signal.dap
        model_function = getattr(lmfit.models, model_name)()

        x_min, x_max = x_parent.min(), x_parent.max()
        oversample = curve.dap_oversample
        new_x = np.linspace(x_min, x_max, int(len(x_parent) * oversample))

        # Evaluate the model with the provided parameters to generate the y values
        new_y = model_function.eval(**curve.dap_params, x=new_x)

        # Update the curve with the new data
        curve.setData(new_x, new_y)

        metadata.update({"curve_id": curve_id})
        self.dap_params_update.emit(curve.dap_params, metadata)
        self.dap_summary_update.emit(curve.dap_summary, metadata)

    def _refresh_dap_signals(self):
        """
        Refresh the DAP signals for all curves.
        """
        for curve in self._dap_curves:
            self.dap_params_update.emit(curve.dap_params, {"curve_id": curve.name()})
            self.dap_summary_update.emit(curve.dap_summary, {"curve_id": curve.name()})

    def _get_x_data(self, device_name: str, device_entry: str) -> list | np.ndarray | None:
        """
        Get the x data for the curves with the decision logic based on the widget x mode configuration:
            - If x is called 'timestamp', use the timestamp data from the scan item.
            - If x is called 'index', use the rolling index.
            - If x is a custom signal, use the data from the scan item.
            - If x is not specified, use the first device from the scan report.

        Additionally, checks and updates the x label suffix.

        Args:
            device_name(str): The name of the device.
            device_entry(str): The entry of the device

        Returns:
            list|np.ndarray|None: X data for the curve.
        """
        x_data = None
        new_suffix = None
        data, access_key = self._fetch_scan_data_and_access()

        # 1 User wants custom signal
        if self.x_axis_mode["name"] not in ["timestamp", "index", "auto"]:
            x_name = self.x_axis_mode["name"]
            x_entry = self.x_axis_mode.get("entry", None)
            if x_entry is None:
                x_entry = self.entry_validator.validate_signal(x_name, None)
            # if the motor was not scanned, an empty list is returned and curves are not updated
            if access_key == "val":  # live data
                x_data = data.get(x_name, {}).get(x_entry, {}).get(access_key, [0])
            else:  # history data
                entry_obj = data.get(x_name, {}).get(x_entry)
                x_data = entry_obj.read()["value"] if entry_obj else [0]
            new_suffix = f" (custom: {x_name}-{x_entry})"
            self._current_x_device = (x_name, x_entry)

        # 2 User wants timestamp
        if self.x_axis_mode["name"] == "timestamp":
            if access_key == "val":  # live
                x_data = data.get(device_name, {}).get(device_entry, None)
                if x_data is None:
                    return None
                else:
                    timestamps = x_data.timestamps
            else:  # history data
                entry_obj = data.get(device_name, {}).get(device_entry)
                timestamps = entry_obj.read()["timestamp"] if entry_obj else [0]
            x_data = timestamps
            new_suffix = " (timestamp)"
            self._current_x_device = None

        # 3 User wants index
        if self.x_axis_mode["name"] == "index":
            x_data = None
            new_suffix = " (index)"
            self._current_x_device = None

        # 4 Best effort automatic mode
        if self.x_axis_mode["name"] is None or self.x_axis_mode["name"] == "auto":
            # 4.1 If there are async curves, use index
            if len(self._async_curves) > 0:
                x_data = None
                new_suffix = " (auto: index)"
                self._current_x_device = None
            # 4.2 If there are sync curves, use the first device from the scan report
            else:
                try:
                    scan_report_devices = self._ensure_str_list(
                        self.scan_item.metadata["bec"]["scan_report_devices"]
                    )
                except Exception:
                    scan_report_devices = self.scan_item.status_message.info.get(
                        "scan_report_devices", []
                    )
                if not scan_report_devices:
                    x_data = None
                    new_suffix = " (auto: index)"
                else:
                    x_name = scan_report_devices[0]
                    x_entry = self.entry_validator.validate_signal(x_name, None)
                    if access_key == "val":
                        x_data = data.get(x_name, {}).get(x_entry, {}).get(access_key, None)
                    else:
                        entry_obj = data.get(x_name, {}).get(x_entry)
                        x_data = entry_obj.read()["value"] if entry_obj else None
                    new_suffix = f" (auto: {x_name}-{x_entry})"
                self._current_x_device = (x_name, x_entry)
        self._update_x_label_suffix(new_suffix)
        return x_data

    def _update_x_label_suffix(self, new_suffix: str):
        """
        Update x_label so it ends with `new_suffix`, removing any old suffix.

        Args:
            new_suffix(str): The new suffix to add to the x_label.
        """
        if new_suffix == self.x_axis_mode["label_suffix"]:
            return

        self.x_axis_mode["label_suffix"] = new_suffix
        self.set_x_label_suffix(new_suffix)

    def _switch_x_axis_item(self, mode: str):
        """
        Switch the x-axis mode between timestamp, index, the best effort and custom signal.

        Args:
            mode(str): Mode of the x-axis.
                - "timestamp": Use the timestamp signal.
                - "index": Use the index signal.
                - "best_effort": Use the best effort signal.
                - Custom signal name of a device from BEC.
        """
        logger.info(f'Switching x-axis mode to "{mode}"')
        current_axis = self.plot_item.axes["bottom"]["item"]
        # Only update the axis if the mode change requires it.
        if mode == "timestamp":
            # Only update if the current axis is not a DateAxisItem.
            if not isinstance(current_axis, pg.graphicsItems.DateAxisItem.DateAxisItem):
                date_axis = pg.graphicsItems.DateAxisItem.DateAxisItem(orientation="bottom")
                self.plot_item.setAxisItems({"bottom": date_axis})
        else:
            # For non-timestamp modes, only update if the current axis is a DateAxisItem.
            if isinstance(current_axis, pg.graphicsItems.DateAxisItem.DateAxisItem):
                default_axis = pg.AxisItem(orientation="bottom")
                self.plot_item.setAxisItems({"bottom": default_axis})

        self.set_x_label_suffix(self.x_axis_mode["label_suffix"])

    def _categorise_device_curves(self) -> str:
        """
        Categorise the device curves into sync and async based on the readout priority.
        """
        if self.scan_item is None:
            self.update_with_scan_history(-1)
            if self.scan_item is None:
                logger.info("No scan executed so far; skipping device curves categorisation.")
                return None

        if hasattr(self.scan_item, "live_data"):
            readout_priority = self.scan_item.status_message.info.get(
                "readout_priority"
            )  # live data
        else:
            readout_priority = self.scan_item.metadata["bec"].get("readout_priority")  # history

        if readout_priority is None:
            return None

        # Reset sync/async curve lists
        self._async_curves.clear()
        self._sync_curves.clear()
        found_async = False
        found_sync = False
        mode = "sync"

        readout_priority_async = self._ensure_str_list(readout_priority.get("async", []))
        readout_priority_sync = self._ensure_str_list(readout_priority.get("monitored", []))

        # Iterate over all curves
        for curve in self.curves:
            if curve.config.source != "device":
                continue
            dev_name = curve.config.signal.name
            if dev_name in readout_priority_async:
                self._async_curves.append(curve)
                if hasattr(self.scan_item, "live_data"):
                    self._setup_async_curve(curve)
                found_async = True
            elif dev_name in readout_priority_sync:
                self._sync_curves.append(curve)
                found_sync = True
            else:
                logger.warning("Device {dev_name} not found in readout priority list.")
        # Determine the mode of the scan
        if found_async and found_sync:
            mode = "mixed"
            logger.warning(
                f"Found both async and sync devices in the scan. X-axis integrity cannot be guaranteed."
            )
        elif found_async:
            mode = "async"
        elif found_sync:
            mode = "sync"

        logger.info(f"Scan {self.scan_id} => mode={self._mode}")
        return mode

    def get_history_scan_item(
        self, scan_index: int = None, scan_id: str = None
    ) -> ScanDataContainer | None:
        """
        Get scan item from history based on scan_id or scan_index.
        If both are provided, scan_id takes precedence and the resolved scan_number
        will be read from the fetched item.

        Args:
            scan_id (str, optional): ScanID of the scan to fetch. Defaults to None.
            scan_index (int, optional): Index (scan number) of the scan to fetch. Defaults to None.

        Returns:
            ScanDataContainer | None: The fetched scan item or None if no item was found.
        """
        if scan_index is not None and scan_id is not None:
            scan_index = None  # Prefer scan_id when both are given

        if scan_index is None and scan_id is None:
            logger.warning("Neither scan_id or scan_number was provided, fetching the latest scan")
            scan_index = -1

        if scan_index is None:
            return self.client.history.get_by_scan_id(scan_id)

        if scan_index == -1:
            scan_item = self.client.queue.scan_storage.current_scan
            if scan_item is not None:
                if scan_item.status_message is None:
                    logger.warning(f"Scan item with {scan_item.scan_id} has no status message.")
                    return None
                return scan_item

        if len(self.client.history) == 0:
            logger.info("No scans executed so far. Cannot fetch scan history.")
            return None

        # check if scan_index is negative, then fetch it just from the list from the end
        if int(scan_index) < 0:
            return self.client.history[scan_index]
        scan_item = self.client.history.get_by_scan_number(scan_index)
        if scan_item is None:
            logger.warning(f"Scan with scan_number {scan_index} not found in history.")
            return None
        if isinstance(scan_item, list):
            if len(scan_item) > 1:
                logger.warning(
                    f"Multiple scans found with scan_number {scan_index}. Returning the latest one."
                )
            scan_item = scan_item[-1]
        return scan_item

    @SafeSlot(int)
    @SafeSlot(str)
    @SafeSlot()
    def update_with_scan_history(self, scan_index: int = None, scan_id: str = None):
        """
        Update the scan curves with the data from the scan storage.
        If both arguments are provided, scan_id takes precedence and scan_index is ignored.

        Args:
            scan_id(str, optional): ScanID of the scan to be updated. Defaults to None.
            scan_index(int, optional): Index (scan number) of the scan to be updated. Defaults to None.
        """
        self.scan_item = self.get_history_scan_item(scan_index=scan_index, scan_id=scan_id)

        if self.scan_item is None:
            return

        if scan_id is not None:
            self.scan_id = scan_id
        else:
            # If scan_number was used, set the scan_id from the fetched item
            if hasattr(self.scan_item, "metadata"):
                self.scan_id = self.scan_item.metadata["bec"]["scan_id"]
            else:
                self.scan_id = self.scan_item.scan_id

        self._emit_signal_update()

    def _emit_signal_update(self):
        self._categorise_device_curves()

        self.setup_dap_for_scan()
        self.sync_signal_update.emit()
        self.async_signal_update.emit()

    ################################################################################
    # Utility Methods
    ################################################################################

    # Large dataset handling helpers
    def _check_dataset_size_and_confirm(self, dataset_obj, device_entry: str) -> bool:
        """
        Check the size of the dataset and confirm with the user if it exceeds the limit.

        Args:
            dataset_obj: The dataset object containing the information.
            device_entry( str): The specific device entry to check.

        Returns:
            bool: True if the dataset is within the size limit or user confirmed to load it,
                  False if the dataset exceeds the size limit and user declined to load it.
        """
        try:
            info = dataset_obj._info
            mem_bytes = info.get(device_entry, {}).get("value", {}).get("mem_size", 0)
            # Fallback – grab first entry if lookup failed
            if mem_bytes == 0 and info:
                first_key = next(iter(info))
                mem_bytes = info[first_key]["value"]["mem_size"]
            size_mb = mem_bytes / (1024 * 1024)
            print(f"Dataset size: {size_mb:.1f} MB")
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Unable to evaluate dataset size: {exc}")
            return True

        if size_mb <= self.config.max_dataset_size_mb:
            return True
        logger.warning(
            f"Attempt to load large dataset: {size_mb:.1f} MB "
            f"(limit {self.config.max_dataset_size_mb} MB)"
        )
        if self._skip_large_dataset_warning:
            logger.info("Skipping large dataset warning dialog.")
            return False
        return self._confirm_large_dataset(size_mb)

    def _confirm_large_dataset(self, size_mb: float) -> bool:
        """
        Confirm with the user whether to load a large dataset with dialog popup.
        Also allows the user to adjust the maximum dataset size limit and if user
        wants to see this popup again during session.

        Args:
            size_mb(float): Size of the dataset in MB.

        Returns:
            bool: True if the user confirmed to load the dataset, False otherwise.
        """
        if self._skip_large_dataset_warning:
            return True

        dialog = QDialog(self)
        dialog.setWindowTitle("Large dataset detected")
        main_dialog_layout = QVBoxLayout(dialog)

        # Limit adjustment widgets
        limit_adjustment_layout = QHBoxLayout()
        limit_adjustment_layout.addWidget(QLabel("New limit (MB):"))
        spin = QDoubleSpinBox()
        spin.setRange(0.001, 4096)
        spin.setDecimals(3)
        spin.setSingleStep(0.01)
        spin.setValue(self.config.max_dataset_size_mb)
        spin.valueChanged.connect(lambda value: setattr(self.config, "max_dataset_size_mb", value))
        limit_adjustment_layout.addWidget(spin)

        # Don't show again checkbox
        checkbox = QCheckBox("Don't show this again for this session")

        buttons = QDialogButtonBox(
            QDialogButtonBox.Yes | QDialogButtonBox.No, Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)  # Yes
        buttons.rejected.connect(dialog.reject)  # No

        # widget layout
        main_dialog_layout.addWidget(
            QLabel(
                f"The selected dataset is {size_mb:.1f} MB which exceeds the "
                f"current limit of {self.config.max_dataset_size_mb} MB.\n"
            )
        )
        main_dialog_layout.addLayout(limit_adjustment_layout)
        main_dialog_layout.addWidget(checkbox)
        main_dialog_layout.addWidget(QLabel("Would you like to display dataset anyway?"))
        main_dialog_layout.addWidget(buttons)

        result = dialog.exec()  # modal; waits for user choice

        # Respect the “don't show again” checkbox for *either* choice
        if checkbox.isChecked():
            self._skip_large_dataset_warning = True

        if result == QDialog.Accepted:
            self.config.max_dataset_size_mb = spin.value()
            return True
        return False

    def _ensure_str_list(self, entries: list | tuple | np.ndarray):
        """
        Convert a variety of possible inputs (string, bytes, list/tuple/ndarray of either)
        into a list of Python strings.

        Args:
            entries:

        Returns:
            list[str]: A list of Python strings.
        """

        if isinstance(entries, (list, tuple, np.ndarray)):
            return [self._to_str(e) for e in entries]
        else:
            return [self._to_str(entries)]

    @staticmethod
    def _to_str(x):
        """
        Convert a single object x (which may be a Python string, bytes, or something else)
        into a plain Python string.
        """
        if isinstance(x, bytes):
            return x.decode("utf-8", errors="replace")
        return str(x)

    @staticmethod
    def _crop_data(x_data, y_data, x_min=None, x_max=None):
        """
        Utility function to crop x_data and y_data based on x_min and x_max.

        Args:
            x_data (np.ndarray): The array of x-values.
            y_data (np.ndarray): The array of y-values corresponding to x_data.
            x_min (float, optional): The lower bound for cropping. Defaults to None.
            x_max (float, optional): The upper bound for cropping. Defaults to None.

        Returns:
            tuple: (cropped_x_data, cropped_y_data)
        """
        # If either bound is None, skip cropping
        if x_min is None or x_max is None:
            return x_data, y_data

        # Create a boolean mask to select only those points within [x_min, x_max]
        mask = (x_data >= x_min) & (x_data <= x_max)

        return x_data[mask], y_data[mask]

    ################################################################################
    # Export Methods
    ################################################################################
    def get_all_data(self, output: Literal["dict", "pandas"] = "dict") -> dict:  # | pd.DataFrame:
        """
        Extract all curve data into a dictionary or a pandas DataFrame.

        Args:
            output (Literal["dict", "pandas"]): Format of the output data.

        Returns:
            dict | pd.DataFrame: Data of all curves in the specified format.
        """
        data = {}
        if output == "pandas":  # pragma: no cover
            try:
                import pandas as pd
            except ModuleNotFoundError:
                raise ModuleNotFoundError(
                    "Pandas is not installed. Please install pandas using 'pip install pandas'."
                )

        for curve in self.curves:
            x_data, y_data = curve.get_data()
            if x_data is not None or y_data is not None:
                if output == "dict":
                    data[curve.name()] = {"x": x_data.tolist(), "y": y_data.tolist()}
                elif output == "pandas" and pd is not None:
                    data[curve.name()] = pd.DataFrame({"x": x_data, "y": y_data})

        if output == "pandas" and pd is not None:  # pragma: no cover
            combined_data = pd.concat(
                [data[curve.name()] for curve in self.curves],
                axis=1,
                keys=[curve.name() for curve in self.curves],
            )
            return combined_data
        return data

    def export_to_matplotlib(self):  # pragma: no cover
        """
        Export current waveform to matplotlib gui. Available only if matplotlib is installed in the environment.

        """
        try:
            import matplotlib as mpl
            from pyqtgraph.exporters import MatplotlibExporter

            MatplotlibExporter(self.plot_item).export()
        except ModuleNotFoundError:
            logger.error("Matplotlib is not installed in the environment.")

    ################################################################################
    # Cleanup
    ################################################################################
    def cleanup(self):
        """
        Cleanup the widget by disconnecting signals and closing dialogs.
        """
        self.proxy_dap_request.cleanup()
        self.clear_all()
        if self.curve_settings_dialog is not None:
            self.curve_settings_dialog.reject()
            self.curve_settings_dialog = None
        if self.dap_summary_dialog is not None:
            self.dap_summary_dialog.reject()
            self.dap_summary_dialog = None
        if self.scan_history_dialog is not None:
            self.scan_history_dialog.reject()
            self.scan_history_dialog = None
        super().cleanup()


class DemoApp(QMainWindow):  # pragma: no cover
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Waveform Demo")
        self.resize(800, 600)
        self.main_widget = QWidget(self)
        self.layout = QHBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        self.waveform_popup = Waveform(popups=True)
        self.waveform_popup.plot(y_name="waveform")

        self.waveform_side = Waveform(popups=False)
        self.waveform_side.plot(y_name="bpm4i", y_entry="bpm4i", dap="GaussianModel")
        self.waveform_side.plot(y_name="bpm3a", y_entry="bpm3a")

        self.layout.addWidget(self.waveform_side)
        self.layout.addWidget(self.waveform_popup)


if __name__ == "__main__":  # pragma: no cover
    import sys

    app = QApplication(sys.argv)
    set_theme("dark")
    widget = DemoApp()
    widget.show()
    widget.resize(1400, 600)
    sys.exit(app.exec_())
