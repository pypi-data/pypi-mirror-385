from __future__ import annotations

from enum import Enum

import numpy as np
import pyqtgraph as pg
from bec_lib import bec_logger
from qtpy.QtCore import QPoint, QPointF, Qt, Signal
from qtpy.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

from bec_widgets.utils import ConnectionConfig, Crosshair, EntryValidator
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.error_popups import SafeProperty, SafeSlot
from bec_widgets.utils.fps_counter import FPSCounter
from bec_widgets.utils.plot_indicator_items import BECArrowItem, BECTickItem
from bec_widgets.utils.round_frame import RoundedFrame
from bec_widgets.utils.side_panel import SidePanel
from bec_widgets.utils.toolbars.performance import PerformanceConnection, performance_bundle
from bec_widgets.utils.toolbars.toolbar import ModularToolBar
from bec_widgets.utils.widget_state_manager import WidgetStateManager
from bec_widgets.widgets.containers.layout_manager.layout_manager import LayoutManagerWidget
from bec_widgets.widgets.plots.setting_menus.axis_settings import AxisSettings
from bec_widgets.widgets.plots.toolbar_components.axis_settings_popup import (
    AxisSettingsPopupConnection,
    axis_popup_bundle,
)
from bec_widgets.widgets.plots.toolbar_components.mouse_interactions import (
    MouseInteractionConnection,
    mouse_interaction_bundle,
)
from bec_widgets.widgets.plots.toolbar_components.plot_export import (
    PlotExportConnection,
    plot_export_bundle,
)
from bec_widgets.widgets.plots.toolbar_components.roi import RoiConnection, roi_bundle

logger = bec_logger.logger


class BECViewBox(pg.ViewBox):
    sigPaint = Signal()

    def paint(self, painter, opt, widget):
        super().paint(painter, opt, widget)
        self.sigPaint.emit()

    def itemBoundsChanged(self, item):
        self._itemBoundsCache.pop(item, None)
        if (self.state["autoRange"][0] is not False) or (self.state["autoRange"][1] is not False):
            # check if the call is coming from a mouse-move event
            if hasattr(item, "skip_auto_range") and item.skip_auto_range:
                return
            self._autoRangeNeedsUpdate = True
            self.update()


class UIMode(Enum):
    NONE = 0
    POPUP = 1
    SIDE = 2


class PlotBase(BECWidget, QWidget):
    PLUGIN = False
    RPC = False

    # Custom Signals
    property_changed = Signal(str, object)
    crosshair_position_changed = Signal(tuple)
    crosshair_position_clicked = Signal(tuple)
    crosshair_coordinates_changed = Signal(tuple)
    crosshair_coordinates_clicked = Signal(tuple)

    def __init__(
        self,
        parent: QWidget | None = None,
        config: ConnectionConfig | None = None,
        client=None,
        gui_id: str | None = None,
        popups: bool = True,
        **kwargs,
    ) -> None:
        if config is None:
            config = ConnectionConfig(widget_class=self.__class__.__name__)
        super().__init__(parent=parent, client=client, gui_id=gui_id, config=config, **kwargs)

        # For PropertyManager identification
        self.get_bec_shortcuts()

        # Layout Management
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout_manager = LayoutManagerWidget(parent=self)
        self.layout_manager.layout.setContentsMargins(0, 0, 0, 0)
        self.layout_manager.layout.setSpacing(0)

        # Property Manager
        self.state_manager = WidgetStateManager(self)

        # Entry Validator
        self.entry_validator = EntryValidator(self.dev)

        # Base widgets elements
        self._popups = popups
        self._ui_mode = UIMode.POPUP if popups else UIMode.SIDE
        self.axis_settings_dialog = None
        self.plot_widget = pg.GraphicsLayoutWidget(parent=self)
        self.plot_widget.ci.setContentsMargins(0, 0, 0, 0)
        self.plot_item = pg.PlotItem(viewBox=BECViewBox(enableMenu=True))
        self.plot_widget.addItem(self.plot_item)
        self.plot_item.visible_items = lambda: self.visible_items
        self.side_panel = SidePanel(self, orientation="left", panel_max_width=280)

        # PlotItem Addons
        self.plot_item.addLegend()
        self.crosshair = None
        self.fps_monitor = None
        self.fps_label = QLabel(alignment=Qt.AlignmentFlag.AlignRight)
        self._user_x_label = ""
        self._x_label_suffix = ""
        self._x_axis_units = ""
        self._user_y_label = ""
        self._y_label_suffix = ""
        self._y_axis_units = ""
        self._minimal_crosshair_precision = 3

        # Plot Indicator Items
        self.tick_item = BECTickItem(parent=self, plot_item=self.plot_item)
        self.arrow_item = BECArrowItem(parent=self, plot_item=self.plot_item)

        self.toolbar = ModularToolBar(parent=self, orientation="horizontal")
        self._init_toolbar()

        self._init_ui()

        self._connect_to_theme_change()
        self._update_theme()

    def apply_theme(self, theme: str):
        self.round_plot_widget.apply_theme(theme)

    def _init_ui(self):
        self.layout.addWidget(self.layout_manager)
        self.round_plot_widget = RoundedFrame(parent=self, content_widget=self.plot_widget)

        self.layout_manager.add_widget(self.round_plot_widget)
        self.layout_manager.add_widget_relative(self.fps_label, self.round_plot_widget, "top")
        self.fps_label.hide()
        self.layout_manager.add_widget_relative(self.side_panel, self.round_plot_widget, "left")
        self.layout_manager.add_widget_relative(self.toolbar, self.fps_label, "top")

        self.ui_mode = self._ui_mode  # to initiate the first time

        # PlotItem ViewBox Signals
        self.plot_item.vb.sigStateChanged.connect(self.viewbox_state_changed)

    def _init_toolbar(self):
        self.toolbar.add_bundle(performance_bundle(self.toolbar.components))
        self.toolbar.add_bundle(plot_export_bundle(self.toolbar.components))
        self.toolbar.add_bundle(mouse_interaction_bundle(self.toolbar.components))
        self.toolbar.add_bundle(roi_bundle(self.toolbar.components))
        self.toolbar.add_bundle(axis_popup_bundle(self.toolbar.components))

        self.toolbar.connect_bundle(
            "plot_base", PlotExportConnection(self.toolbar.components, self)
        )
        self.toolbar.connect_bundle(
            "plot_base", PerformanceConnection(self.toolbar.components, self)
        )
        self.toolbar.connect_bundle(
            "plot_base", MouseInteractionConnection(self.toolbar.components, self)
        )
        self.toolbar.connect_bundle("plot_base", RoiConnection(self.toolbar.components, self))
        self.toolbar.connect_bundle(
            "plot_base", AxisSettingsPopupConnection(self.toolbar.components, self)
        )

        # hide some options by default
        self.toolbar.toggle_action_visibility("fps_monitor", False)

        # Get default viewbox state
        self.toolbar.show_bundles(
            ["plot_export", "mouse_interaction", "roi", "performance", "axis_popup"]
        )

    def add_side_menus(self):
        """Adds multiple menus to the side panel."""
        # Setting Axis Widget
        try:
            axis_setting = AxisSettings(parent=self, target_widget=self)
            self.side_panel.add_menu(
                action_id="axis",
                icon_name="settings",
                tooltip="Show Axis Settings",
                widget=axis_setting,
                title="Axis Settings",
            )
        except ValueError:
            return

    def reset_legend(self):
        """In the case that the legend is not visible, reset it to be visible to top left corner"""
        self.plot_item.legend.autoAnchor(50)

    ################################################################################
    # Toggle UI Elements
    ################################################################################
    @property
    def ui_mode(self) -> UIMode:
        """
        Get the UI mode.
        """
        return self._ui_mode

    @ui_mode.setter
    def ui_mode(self, mode: UIMode):
        """
        Set the UI mode.

        Args:
            mode(UIMode): The UI mode to set.
        """
        if not isinstance(mode, UIMode):
            raise ValueError("ui_mode must be an instance of UIMode")
        self._ui_mode = mode

        # Now, apply the new mode:
        if mode == UIMode.POPUP:
            shown_bundles = self.toolbar.shown_bundles
            if "axis_popup" not in shown_bundles:
                shown_bundles.append("axis_popup")
            self.toolbar.show_bundles(shown_bundles)
            self.side_panel.hide()

        elif mode == UIMode.SIDE:
            shown_bundles = self.toolbar.shown_bundles
            if "axis_popup" in shown_bundles:
                shown_bundles.remove("axis_popup")
            self.toolbar.show_bundles(shown_bundles)
            pb_connection = self.toolbar.bundles["axis_popup"].get_connection("plot_base")
            if pb_connection.axis_settings_dialog is not None:
                pb_connection.axis_settings_dialog.close()
                pb_connection.axis_settings_dialog = None
            self.add_side_menus()
            self.side_panel.show()

    @SafeProperty(bool, doc="Enable popups setting dialogs for the plot widget.")
    def enable_popups(self):
        """
        Enable popups setting dialogs for the plot widget.
        """
        return self.ui_mode == UIMode.POPUP

    @enable_popups.setter
    def enable_popups(self, value: bool):
        """
        Set the popups setting dialogs for the plot widget.

        Args:
            value(bool): The value to set.
        """
        if value:
            self.ui_mode = UIMode.POPUP
        else:
            if self.ui_mode == UIMode.POPUP:
                self.ui_mode = UIMode.NONE

    @SafeProperty(bool, doc="Show Side Panel")
    def enable_side_panel(self) -> bool:
        """
        Show Side Panel
        """
        return self.ui_mode == UIMode.SIDE

    @enable_side_panel.setter
    def enable_side_panel(self, value: bool):
        """
        Show Side Panel

        Args:
            value(bool): The value to set.
        """
        if value:
            self.ui_mode = UIMode.SIDE
        else:
            if self.ui_mode == UIMode.SIDE:
                self.ui_mode = UIMode.NONE

    @SafeProperty(bool, doc="Show Toolbar")
    def enable_toolbar(self) -> bool:
        """
        Show Toolbar.
        """
        return self.toolbar.isVisible()

    @enable_toolbar.setter
    def enable_toolbar(self, value: bool):
        """
        Show Toolbar.

        Args:
            value(bool): The value to set.
        """
        self.toolbar.setVisible(value)

    @SafeProperty(bool, doc="Enable the FPS monitor.")
    def enable_fps_monitor(self) -> bool:
        """
        Enable the FPS monitor.
        """
        return self.fps_label.isVisible()

    @enable_fps_monitor.setter
    def enable_fps_monitor(self, value: bool):
        """
        Enable the FPS monitor.

        Args:
            value(bool): The value to set.
        """
        if value and self.fps_monitor is None:
            self.hook_fps_monitor()
        elif not value and self.fps_monitor is not None:
            self.unhook_fps_monitor()

    ################################################################################
    # ViewBox State Signals
    ################################################################################

    def viewbox_state_changed(self):
        """
        Emit a signal when the state of the viewbox has changed.
        Merges the default pyqtgraphs signal states and also CTRL menu toggles.
        """

        viewbox_state = self.plot_item.vb.getState()
        # Range Limits
        x_min, x_max = viewbox_state["targetRange"][0]
        y_min, y_max = viewbox_state["targetRange"][1]
        self.property_changed.emit("x_min", x_min)
        self.property_changed.emit("x_max", x_max)
        self.property_changed.emit("y_min", y_min)
        self.property_changed.emit("y_max", y_max)

        # Grid Toggles

    ################################################################################
    # Plot Properties
    ################################################################################

    def set(self, **kwargs):
        """
        Set the properties of the plot widget.

        Args:
            **kwargs: Keyword arguments for the properties to be set.

        Possible properties:
            - title: str
            - x_label: str
            - y_label: str
            - x_scale: Literal["linear", "log"]
            - y_scale: Literal["linear", "log"]
            - x_lim: tuple
            - y_lim: tuple
            - legend_label_size: int

        """
        property_map = {
            "title": self.title,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "x_limits": self.x_limits,
            "y_limits": self.y_limits,
            "x_grid": self.x_grid,
            "y_grid": self.y_grid,
            "inner_axes": self.inner_axes,
            "outer_axes": self.outer_axes,
            "lock_aspect_ratio": self.lock_aspect_ratio,
            "auto_range_x": self.auto_range_x,
            "auto_range_y": self.auto_range_y,
            "x_log": self.x_log,
            "y_log": self.y_log,
            "legend_label_size": self.legend_label_size,
        }

        for key, value in kwargs.items():
            if key in property_map:
                setattr(self, key, value)
            else:
                logger.warning(f"Property {key} not found.")

    @SafeProperty(str, doc="The title of the axes.")
    def title(self) -> str:
        """
        Set title of the plot.
        """
        return self.plot_item.titleLabel.text

    @title.setter
    def title(self, value: str):
        """
        Set title of the plot.

        Args:
            value(str): The title to set.
        """
        self.plot_item.setTitle(value)
        self.property_changed.emit("title", value)

    @SafeProperty(str, doc="The text of the x label")
    def x_label(self) -> str:
        """
        The set label for the x-axis.
        """
        return self._user_x_label

    @x_label.setter
    def x_label(self, value: str):
        """
        The set label for the x-axis.

        Args:
            value(str): The label to set.
        """
        self._user_x_label = value
        self._apply_x_label()
        self.property_changed.emit("x_label", self._user_x_label)

    @property
    def x_label_suffix(self) -> str:
        """
        A read-only (or internal) suffix automatically appended to the user label.
        Not settable by the user directly from the UI.
        """
        return self._x_label_suffix

    def set_x_label_suffix(self, suffix: str):
        """
        Public or protected method to update the suffix.
        The user code or subclass (Waveform) can call this
        when x_mode changes, but the AxisSettings won't show it.
        """
        self._x_label_suffix = suffix
        self._apply_x_label()

    @property
    def x_label_units(self) -> str:
        """
        The units of the x-axis.
        """
        return self._x_axis_units

    @x_label_units.setter
    def x_label_units(self, units: str):
        """
        The units of the x-axis.

        Args:
            units(str): The units to set.
        """
        self._x_axis_units = units
        self._apply_x_label()

    @property
    def x_label_combined(self) -> str:
        """
        The final label shown on the axis = user portion + suffix + [units].
        """
        units = f" [{self._x_axis_units}]" if self._x_axis_units else ""
        return self._user_x_label + self._x_label_suffix + units

    def _apply_x_label(self):
        """
        Actually updates the pyqtgraph axis label text to
        the combined label. Called whenever user label or suffix changes.
        """
        final_label = self.x_label_combined
        if self.plot_item.getAxis("bottom").isVisible():
            self.plot_item.setLabel("bottom", text=final_label)

    @SafeProperty(str, doc="The text of the y label")
    def y_label(self) -> str:
        """
        The set label for the y-axis.
        """
        return self._user_y_label

    @y_label.setter
    def y_label(self, value: str):
        """
        The set label for the y-axis.
        Args:
            value(str): The label to set.
        """
        self._user_y_label = value
        self._apply_y_label()
        self.property_changed.emit("y_label", value)

    @property
    def y_label_suffix(self) -> str:
        """
        A read-only suffix automatically appended to the y label.
        """
        return self._y_label_suffix

    def set_y_label_suffix(self, suffix: str):
        """
        Public method to update the y label suffix.
        """
        self._y_label_suffix = suffix
        self._apply_y_label()

    @property
    def y_label_units(self) -> str:
        """
        The units of the y-axis.
        """
        return self._y_axis_units

    @y_label_units.setter
    def y_label_units(self, units: str):
        """
        The units of the y-axis.

        Args:
            units(str): The units to set.
        """
        self._y_axis_units = units
        self._apply_y_label()

    @property
    def y_label_combined(self) -> str:
        """
        The final y label shown on the axis = user portion + suffix + [units].
        """
        units = f" [{self._y_axis_units}]" if self._y_axis_units else ""
        return self._user_y_label + self._y_label_suffix + units

    def _apply_y_label(self):
        """
        Actually updates the pyqtgraph y axis label text to
        the combined y label. Called whenever y label or suffix changes.
        """
        final_label = self.y_label_combined
        if self.plot_item.getAxis("bottom").isVisible():
            self.plot_item.setLabel("left", text=final_label)

    def _tuple_to_qpointf(self, tuple: tuple | list):
        """
        Helper function to convert a tuple to a QPointF.

        Args:
            tuple(tuple|list): Tuple or list of two numbers.

        Returns:
            QPointF: The tuple converted to a QPointF.
        """
        if len(tuple) != 2:
            raise ValueError("Limits must be a tuple or list of two numbers.")
        min_val, max_val = tuple
        if not isinstance(min_val, (int, float)) or not isinstance(max_val, (int, float)):
            raise TypeError("Limits must be numbers.")
        if min_val > max_val:
            raise ValueError("Minimum limit cannot be greater than maximum limit.")
        return QPoint(*tuple)

    ################################################################################
    # X limits, has to be SaveProperty("QPointF") because of the tuple conversion for designer,
    # the python properties are used for CLI and API for context dialog settings.

    @SafeProperty("QPointF")
    def x_limits(self) -> QPointF:
        """
        Get the x limits of the plot.
        """
        current_lim = self.plot_item.vb.viewRange()[0]
        return QPointF(current_lim[0], current_lim[1])

    @x_limits.setter
    def x_limits(self, value):
        """
        Set the x limits of the plot.

        Args:
            value(QPointF|tuple|list): The x limits to set.
        """
        if isinstance(value, (tuple, list)):
            value = self._tuple_to_qpointf(value)
        self.plot_item.vb.setXRange(value.x(), value.y(), padding=0)

    @property
    def x_lim(self) -> tuple:
        """
        Get the x limits of the plot.
        """
        return (self.x_limits.x(), self.x_limits.y())

    @x_lim.setter
    def x_lim(self, value):
        """
        Set the x limits of the plot.

        Args:
            value(tuple): The x limits to set.
        """
        self.x_limits = value

    @property
    def x_min(self) -> float:
        """
        Get the minimum x limit of the plot.

        """
        return self.x_limits.x()

    @x_min.setter
    def x_min(self, value: float):
        """
        Set the minimum x limit of the plot.

        Args:
            value(float): The minimum x limit to set.
        """
        self.x_limits = (value, self.x_lim[1])

    @property
    def x_max(self) -> float:
        """
        Get the maximum x limit of the plot.
        """
        return self.x_limits.y()

    @x_max.setter
    def x_max(self, value: float):
        """
        Set the maximum x limit of the plot.

        Args:
            value(float): The maximum x limit to set.
        """
        self.x_limits = (self.x_lim[0], value)

    ################################################################################
    # Y limits, has to be SaveProperty("QPointF") because of the tuple conversion for designer,
    # the python properties are used for CLI and API for context dialog settings.

    @SafeProperty("QPointF")
    def y_limits(self) -> QPointF:
        """
        Get the y limits of the plot.
        """
        current_lim = self.plot_item.vb.viewRange()[1]
        return QPointF(current_lim[0], current_lim[1])

    @y_limits.setter
    def y_limits(self, value):
        """
        Set the y limits of the plot.

        Args:
            value(QPointF|tuple|list): The y limits to set.
        """
        if isinstance(value, (tuple, list)):
            value = self._tuple_to_qpointf(value)
        self.plot_item.vb.setYRange(value.x(), value.y(), padding=0)

    @property
    def y_lim(self) -> tuple:
        """
        Get the y limits of the plot.
        """
        return (self.y_limits.x(), self.y_limits.y())

    @y_lim.setter
    def y_lim(self, value):
        """
        Set the y limits of the plot.

        Args:
            value(tuple): The y limits to set.
        """
        self.y_limits = value

    @property
    def y_min(self) -> float:
        """
        Get the minimum y limit of the plot.
        """
        return self.y_limits.x()

    @y_min.setter
    def y_min(self, value: float):
        """
        Set the minimum y limit of the plot.

        Args:
            value(float): The minimum y limit to set.
        """
        self.y_limits = (value, self.y_lim[1])

    @property
    def y_max(self) -> float:
        """
        Get the maximum y limit of the plot.
        """
        return self.y_limits.y()

    @y_max.setter
    def y_max(self, value: float):
        """
        Set the maximum y limit of the plot.

        Args:
            value(float): The maximum y limit to set.
        """
        self.y_limits = (self.y_lim[0], value)

    @SafeProperty(bool, doc="Show grid on the x-axis.")
    def x_grid(self) -> bool:
        """
        Show grid on the x-axis.
        """
        return self.plot_item.ctrl.xGridCheck.isChecked()

    @x_grid.setter
    def x_grid(self, value: bool):
        """
        Show grid on the x-axis.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.showGrid(x=value)
        self.property_changed.emit("x_grid", value)

    @SafeProperty(bool, doc="Show grid on the y-axis.")
    def y_grid(self) -> bool:
        """
        Show grid on the y-axis.
        """
        return self.plot_item.ctrl.yGridCheck.isChecked()

    @y_grid.setter
    def y_grid(self, value: bool):
        """
        Show grid on the y-axis.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.showGrid(y=value)
        self.property_changed.emit("y_grid", value)

    @SafeProperty(bool, doc="Set X-axis to log scale if True, linear if False.")
    def x_log(self) -> bool:
        """
        Set X-axis to log scale if True, linear if False.
        """
        return bool(self.plot_item.vb.state.get("logMode", [False, False])[0])

    @x_log.setter
    def x_log(self, value: bool):
        """
        Set X-axis to log scale if True, linear if False.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.setLogMode(x=value)
        self.property_changed.emit("x_log", value)

    @SafeProperty(bool, doc="Set Y-axis to log scale if True, linear if False.")
    def y_log(self) -> bool:
        """
        Set Y-axis to log scale if True, linear if False.
        """
        return bool(self.plot_item.vb.state.get("logMode", [False, False])[1])

    @y_log.setter
    def y_log(self, value: bool):
        """
        Set Y-axis to log scale if True, linear if False.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.setLogMode(y=value)
        self.property_changed.emit("y_log", value)

    @SafeProperty(bool, doc="Show the outer axes of the plot widget.")
    def outer_axes(self) -> bool:
        """
        Show the outer axes of the plot widget.
        """
        return self.plot_item.getAxis("top").isVisible()

    @outer_axes.setter
    def outer_axes(self, value: bool):
        """
        Show the outer axes of the plot widget.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.showAxis("top", value)
        self.plot_item.showAxis("right", value)

        self.property_changed.emit("outer_axes", value)

    @SafeProperty(bool, doc="Show inner axes of the plot widget.")
    def inner_axes(self) -> bool:
        """
        Show inner axes of the plot widget.
        """
        return self.plot_item.getAxis("bottom").isVisible()

    @inner_axes.setter
    def inner_axes(self, value: bool):
        """
        Show inner axes of the plot widget.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.showAxis("bottom", value)
        self.plot_item.showAxis("left", value)

        self._apply_x_label()
        self._apply_y_label()
        self.property_changed.emit("inner_axes", value)

    @SafeProperty(bool, doc="Lock aspect ratio of the plot widget.")
    def lock_aspect_ratio(self) -> bool:
        """
        Lock aspect ratio of the plot widget.
        """
        return bool(self.plot_item.vb.getState()["aspectLocked"])

    @lock_aspect_ratio.setter
    def lock_aspect_ratio(self, value: bool):
        """
        Lock aspect ratio of the plot widget.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.setAspectLocked(value)

    @SafeProperty(bool, doc="Set auto range for the x-axis.")
    def auto_range_x(self) -> bool:
        """
        Set auto range for the x-axis.
        """
        return bool(self.plot_item.vb.getState()["autoRange"][0])

    @auto_range_x.setter
    def auto_range_x(self, value: bool):
        """
        Set auto range for the x-axis.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.enableAutoRange(x=value)

    @SafeProperty(bool, doc="Set auto range for the y-axis.")
    def auto_range_y(self) -> bool:
        """
        Set auto range for the y-axis.
        """
        return bool(self.plot_item.vb.getState()["autoRange"][1])

    @auto_range_y.setter
    def auto_range_y(self, value: bool):
        """
        Set auto range for the y-axis.

        Args:
            value(bool): The value to set.
        """
        self.plot_item.enableAutoRange(y=value)

    def auto_range(self, value: bool = True):
        """
        On demand apply autorange to the plot item based on the visible curves.

        Args:
            value(bool): If True, apply autorange to the visible curves.
        """
        if not value:
            self.plot_item.enableAutoRange(x=False, y=False)
            return
        self._apply_autorange_only_visible_curves()

    @property
    def visible_items(self):
        crosshair_items = []
        if self.crosshair:
            crosshair_items = [
                self.crosshair.v_line,
                self.crosshair.h_line,
                self.crosshair.coord_label,
            ]
        return [
            item
            for item in self.plot_item.items
            if item.isVisible() and item not in crosshair_items
        ]

    def _apply_autorange_only_visible_curves(self):
        """
        Apply autorange to the plot item based on the provided curves.

        Args:
            curves (list): List of curves to apply autorange to.
        """
        visible_items = self.visible_items

        self.plot_item.autoRange(items=visible_items if visible_items else None)

    @SafeProperty(int, doc="The font size of the legend font.")
    def legend_label_size(self) -> int:
        """
        The font size of the legend font.
        """
        if not self.plot_item.legend:
            return
        scale = self.plot_item.legend.scale() * 9
        return scale

    @legend_label_size.setter
    def legend_label_size(self, value: int):
        """
        The font size of the legend font.

        Args:
            value(int): The font size to set.
        """
        if not self.plot_item.legend:
            return
        scale = (
            value / 9
        )  # 9 is the default font size of the legend, so we always scale it against 9
        self.plot_item.legend.setScale(scale)

    ################################################################################
    # FPS Counter
    ################################################################################

    def update_fps_label(self, fps: float) -> None:
        """
        Update the FPS label.

        Args:
            fps(float): The frames per second.
        """
        if self.fps_label:
            self.fps_label.setText(f"FPS: {fps:.2f}")

    def hook_fps_monitor(self):
        """Hook the FPS monitor to the plot."""
        if self.fps_monitor is None:
            self.fps_monitor = FPSCounter(self.plot_item.vb)
            self.fps_label.show()

            self.fps_monitor.sigFpsUpdate.connect(self.update_fps_label)
            self.update_fps_label(0)

    def unhook_fps_monitor(self, delete_label=True):
        """Unhook the FPS monitor from the plot."""
        if self.fps_monitor is not None and delete_label:
            # Remove Monitor
            self.fps_monitor.cleanup()
            self.fps_monitor.deleteLater()
            self.fps_monitor = None
        if self.fps_label is not None:
            # Hide Label
            self.fps_label.hide()

    ################################################################################
    # Crosshair
    ################################################################################

    def hook_crosshair(self) -> None:
        """Hook the crosshair to all plots."""
        if self.crosshair is None:
            self.crosshair = Crosshair(
                self.plot_item, min_precision=self._minimal_crosshair_precision
            )
            self.crosshair.crosshairChanged.connect(self.crosshair_position_changed)
            self.crosshair.crosshairClicked.connect(self.crosshair_position_clicked)
            self.crosshair.coordinatesChanged1D.connect(self.crosshair_coordinates_changed)
            self.crosshair.coordinatesClicked1D.connect(self.crosshair_coordinates_clicked)
            self.crosshair.coordinatesChanged2D.connect(self.crosshair_coordinates_changed)
            self.crosshair.coordinatesClicked2D.connect(self.crosshair_coordinates_clicked)

    def unhook_crosshair(self) -> None:
        """Unhook the crosshair from all plots."""
        if self.crosshair is not None:
            self.crosshair.crosshairChanged.disconnect(self.crosshair_position_changed)
            self.crosshair.crosshairClicked.disconnect(self.crosshair_position_clicked)
            self.crosshair.coordinatesChanged1D.disconnect(self.crosshair_coordinates_changed)
            self.crosshair.coordinatesClicked1D.disconnect(self.crosshair_coordinates_clicked)
            self.crosshair.coordinatesChanged2D.disconnect(self.crosshair_coordinates_changed)
            self.crosshair.coordinatesClicked2D.disconnect(self.crosshair_coordinates_clicked)
            self.crosshair.cleanup()
            self.crosshair.deleteLater()
            self.crosshair = None

    def toggle_crosshair(self) -> None:
        """Toggle the crosshair on all plots."""
        if self.crosshair is None:
            return self.hook_crosshair()

        self.unhook_crosshair()

    @SafeProperty(
        int, doc="Minimum decimal places for crosshair when dynamic precision is enabled."
    )
    def minimal_crosshair_precision(self) -> int:
        """
        Minimum decimal places for crosshair when dynamic precision is enabled.
        """
        return self._minimal_crosshair_precision

    @minimal_crosshair_precision.setter
    def minimal_crosshair_precision(self, value: int):
        """
        Set the minimum decimal places for crosshair when dynamic precision is enabled.

        Args:
            value(int): The minimum decimal places to set.
        """
        value_int = max(0, int(value))
        self._minimal_crosshair_precision = value_int
        if self.crosshair is not None:
            self.crosshair.min_precision = value_int
        self.property_changed.emit("minimal_crosshair_precision", value_int)

    @SafeSlot()
    def reset(self) -> None:
        """Reset the plot widget."""
        if self.crosshair is not None:
            self.crosshair.clear_markers()
            self.crosshair.update_markers()

    def cleanup(self):
        self.toolbar.cleanup()
        self.unhook_crosshair()
        self.unhook_fps_monitor(delete_label=True)
        self.tick_item.cleanup()
        self.arrow_item.cleanup()
        if self.axis_settings_dialog is not None:
            self.axis_settings_dialog.close()
            self.axis_settings_dialog = None
        self.cleanup_pyqtgraph()
        self.round_plot_widget.close()
        super().cleanup()

    def cleanup_pyqtgraph(self, item: pg.PlotItem | None = None):
        """Cleanup pyqtgraph items."""
        if item is None:
            item = self.plot_item
        item.vb.menu.close()
        item.vb.menu.deleteLater()
        item.ctrlMenu.close()
        item.ctrlMenu.deleteLater()


class DemoPlotBase(QMainWindow):  # pragma: no cover:
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_widget.layout = QHBoxLayout(self.main_widget)

        self.plot_popup = PlotBase(popups=True)
        self.plot_popup.title = "PlotBase with popups"
        self.plot_side_panels = PlotBase(popups=False)
        self.plot_side_panels.title = "PlotBase with side panels"

        self.plot_popup.plot_item.plot(np.random.rand(100), pen=(255, 0, 0))
        self.plot_side_panels.plot_item.plot(np.random.rand(100), pen=(0, 255, 0))

        self.main_widget.layout.addWidget(self.plot_side_panels)
        self.main_widget.layout.addWidget(self.plot_popup)

        self.resize(1400, 600)


if __name__ == "__main__":  # pragma: no cover:
    import sys

    from qtpy.QtWidgets import QApplication

    from bec_widgets.widgets.containers.main_window.main_window import BECMainWindow

    app = QApplication(sys.argv)
    launch_window = BECMainWindow()
    pb = PlotBase(popups=False)
    launch_window.setCentralWidget(pb)
    launch_window.show()

    sys.exit(app.exec_())
