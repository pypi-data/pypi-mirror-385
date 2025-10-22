from __future__ import annotations

from typing import Literal, Optional
from weakref import WeakValueDictionary

from bec_lib.logger import bec_logger
from pydantic import Field
from pyqtgraph.dockarea.DockArea import DockArea
from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QPainter, QPaintEvent
from qtpy.QtWidgets import QApplication, QSizePolicy, QVBoxLayout, QWidget

from bec_widgets.cli.rpc.rpc_register import RPCRegister
from bec_widgets.utils import ConnectionConfig, WidgetContainerUtils
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.error_popups import SafeSlot
from bec_widgets.utils.name_utils import pascal_to_snake
from bec_widgets.utils.toolbars.actions import (
    ExpandableMenuAction,
    MaterialIconAction,
    WidgetAction,
)
from bec_widgets.utils.toolbars.bundles import ToolbarBundle
from bec_widgets.utils.toolbars.toolbar import ModularToolBar
from bec_widgets.utils.widget_io import WidgetHierarchy
from bec_widgets.widgets.containers.dock.dock import BECDock, DockConfig
from bec_widgets.widgets.containers.main_window.main_window import BECMainWindow
from bec_widgets.widgets.control.device_control.positioner_box import PositionerBox
from bec_widgets.widgets.control.scan_control.scan_control import ScanControl
from bec_widgets.widgets.editors.vscode.vscode import VSCodeEditor
from bec_widgets.widgets.plots.heatmap.heatmap import Heatmap
from bec_widgets.widgets.plots.image.image import Image
from bec_widgets.widgets.plots.motor_map.motor_map import MotorMap
from bec_widgets.widgets.plots.multi_waveform.multi_waveform import MultiWaveform
from bec_widgets.widgets.plots.scatter_waveform.scatter_waveform import ScatterWaveform
from bec_widgets.widgets.plots.waveform.waveform import Waveform
from bec_widgets.widgets.progress.ring_progress_bar.ring_progress_bar import RingProgressBar
from bec_widgets.widgets.services.bec_queue.bec_queue import BECQueue
from bec_widgets.widgets.services.bec_status_box.bec_status_box import BECStatusBox
from bec_widgets.widgets.utility.logpanel.logpanel import LogPanel
from bec_widgets.widgets.utility.visual.dark_mode_button.dark_mode_button import DarkModeButton

logger = bec_logger.logger


class DockAreaConfig(ConnectionConfig):
    docks: dict[str, DockConfig] = Field({}, description="The docks in the dock area.")
    docks_state: Optional[dict] = Field(
        None, description="The state of the docks in the dock area."
    )


class BECDockArea(BECWidget, QWidget):
    """
    Container for other widgets. Widgets can be added to the dock area and arranged in a grid layout.
    """

    PLUGIN = True
    USER_ACCESS = [
        "_rpc_id",
        "_config_dict",
        "_get_all_rpc",
        "new",
        "show",
        "hide",
        "panels",
        "panel_list",
        "delete",
        "delete_all",
        "remove",
        "detach_dock",
        "attach_all",
        "save_state",
        "screenshot",
        "restore_state",
    ]

    def __init__(
        self,
        parent: QWidget | None = None,
        config: DockAreaConfig | None = None,
        client=None,
        gui_id: str = None,
        object_name: str = None,
        **kwargs,
    ) -> None:
        if config is None:
            config = DockAreaConfig(widget_class=self.__class__.__name__)
        else:
            if isinstance(config, dict):
                config = DockAreaConfig(**config)
            self.config = config
        super().__init__(
            parent=parent,
            object_name=object_name,
            client=client,
            gui_id=gui_id,
            config=config,
            **kwargs,
        )
        self._parent = parent  # TODO probably not needed
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self._instructions_visible = True

        self.dark_mode_button = DarkModeButton(parent=self, toolbar=True)
        self.dock_area = DockArea(parent=self)
        self.toolbar = ModularToolBar(parent=self)
        self._setup_toolbar()

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.dock_area)

        self._hook_toolbar()
        self.toolbar.show_bundles(
            ["menu_plots", "menu_devices", "menu_utils", "dock_actions", "dark_mode"]
        )

    def minimumSizeHint(self):
        return QSize(800, 600)

    def _setup_toolbar(self):

        # Add plot menu
        self.toolbar.components.add_safe(
            "menu_plots",
            ExpandableMenuAction(
                label="Add Plot ",
                actions={
                    "waveform": MaterialIconAction(
                        icon_name=Waveform.ICON_NAME,
                        tooltip="Add Waveform",
                        filled=True,
                        parent=self,
                    ),
                    "scatter_waveform": MaterialIconAction(
                        icon_name=ScatterWaveform.ICON_NAME,
                        tooltip="Add Scatter Waveform",
                        filled=True,
                        parent=self,
                    ),
                    "multi_waveform": MaterialIconAction(
                        icon_name=MultiWaveform.ICON_NAME,
                        tooltip="Add Multi Waveform",
                        filled=True,
                        parent=self,
                    ),
                    "image": MaterialIconAction(
                        icon_name=Image.ICON_NAME, tooltip="Add Image", filled=True, parent=self
                    ),
                    "motor_map": MaterialIconAction(
                        icon_name=MotorMap.ICON_NAME,
                        tooltip="Add Motor Map",
                        filled=True,
                        parent=self,
                    ),
                    "heatmap": MaterialIconAction(
                        icon_name=Heatmap.ICON_NAME, tooltip="Add Heatmap", filled=True, parent=self
                    ),
                },
            ),
        )

        bundle = ToolbarBundle("menu_plots", self.toolbar.components)
        bundle.add_action("menu_plots")
        self.toolbar.add_bundle(bundle)

        # Add control menu
        self.toolbar.components.add_safe(
            "menu_devices",
            ExpandableMenuAction(
                label="Add Device Control ",
                actions={
                    "scan_control": MaterialIconAction(
                        icon_name=ScanControl.ICON_NAME,
                        tooltip="Add Scan Control",
                        filled=True,
                        parent=self,
                    ),
                    "positioner_box": MaterialIconAction(
                        icon_name=PositionerBox.ICON_NAME,
                        tooltip="Add Device Box",
                        filled=True,
                        parent=self,
                    ),
                },
            ),
        )
        bundle = ToolbarBundle("menu_devices", self.toolbar.components)
        bundle.add_action("menu_devices")
        self.toolbar.add_bundle(bundle)

        # Add utils menu
        self.toolbar.components.add_safe(
            "menu_utils",
            ExpandableMenuAction(
                label="Add Utils ",
                actions={
                    "queue": MaterialIconAction(
                        icon_name=BECQueue.ICON_NAME,
                        tooltip="Add Scan Queue",
                        filled=True,
                        parent=self,
                    ),
                    "vs_code": MaterialIconAction(
                        icon_name=VSCodeEditor.ICON_NAME,
                        tooltip="Add VS Code",
                        filled=True,
                        parent=self,
                    ),
                    "status": MaterialIconAction(
                        icon_name=BECStatusBox.ICON_NAME,
                        tooltip="Add BEC Status Box",
                        filled=True,
                        parent=self,
                    ),
                    "progress_bar": MaterialIconAction(
                        icon_name=RingProgressBar.ICON_NAME,
                        tooltip="Add Circular ProgressBar",
                        filled=True,
                        parent=self,
                    ),
                    # FIXME temporarily disabled -> issue #644
                    "log_panel": MaterialIconAction(
                        icon_name=LogPanel.ICON_NAME,
                        tooltip="Add LogPanel - Disabled",
                        filled=True,
                        parent=self,
                    ),
                    "sbb_monitor": MaterialIconAction(
                        icon_name="train", tooltip="Add SBB Monitor", filled=True, parent=self
                    ),
                },
            ),
        )
        bundle = ToolbarBundle("menu_utils", self.toolbar.components)
        bundle.add_action("menu_utils")
        self.toolbar.add_bundle(bundle)

        ########## Dock Actions ##########
        spacer = QWidget(parent=self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.components.add_safe("spacer", WidgetAction(widget=spacer, adjust_size=False))

        self.toolbar.components.add_safe(
            "dark_mode", WidgetAction(widget=self.dark_mode_button, adjust_size=False)
        )

        bundle = ToolbarBundle("dark_mode", self.toolbar.components)
        bundle.add_action("spacer")
        bundle.add_action("dark_mode")
        self.toolbar.add_bundle(bundle)

        self.toolbar.components.add_safe(
            "attach_all",
            MaterialIconAction(
                icon_name="zoom_in_map", tooltip="Attach all floating docks", parent=self
            ),
        )

        self.toolbar.components.add_safe(
            "save_state",
            MaterialIconAction(icon_name="bookmark", tooltip="Save Dock State", parent=self),
        )
        self.toolbar.components.add_safe(
            "restore_state",
            MaterialIconAction(icon_name="frame_reload", tooltip="Restore Dock State", parent=self),
        )
        self.toolbar.components.add_safe(
            "screenshot",
            MaterialIconAction(icon_name="photo_camera", tooltip="Take Screenshot", parent=self),
        )

        bundle = ToolbarBundle("dock_actions", self.toolbar.components)
        bundle.add_action("attach_all")
        bundle.add_action("save_state")
        bundle.add_action("restore_state")
        bundle.add_action("screenshot")
        self.toolbar.add_bundle(bundle)

    def _hook_toolbar(self):
        menu_plots = self.toolbar.components.get_action("menu_plots")
        menu_devices = self.toolbar.components.get_action("menu_devices")
        menu_utils = self.toolbar.components.get_action("menu_utils")

        menu_plots.actions["waveform"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="Waveform")
        )

        menu_plots.actions["scatter_waveform"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="ScatterWaveform")
        )
        menu_plots.actions["multi_waveform"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="MultiWaveform")
        )
        menu_plots.actions["image"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="Image")
        )
        menu_plots.actions["motor_map"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="MotorMap")
        )
        menu_plots.actions["heatmap"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="Heatmap")
        )

        # Menu Devices
        menu_devices.actions["scan_control"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="ScanControl")
        )
        menu_devices.actions["positioner_box"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="PositionerBox")
        )

        # Menu Utils
        menu_utils.actions["queue"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="BECQueue")
        )
        menu_utils.actions["status"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="BECStatusBox")
        )
        menu_utils.actions["vs_code"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="VSCodeEditor")
        )
        menu_utils.actions["progress_bar"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="RingProgressBar")
        )
        # FIXME temporarily disabled -> issue #644
        menu_utils.actions["log_panel"].action.setEnabled(False)

        menu_utils.actions["sbb_monitor"].action.triggered.connect(
            lambda: self._create_widget_from_toolbar(widget_name="SBBMonitor")
        )

        # Icons
        self.toolbar.components.get_action("attach_all").action.triggered.connect(self.attach_all)
        self.toolbar.components.get_action("save_state").action.triggered.connect(self.save_state)
        self.toolbar.components.get_action("restore_state").action.triggered.connect(
            self.restore_state
        )
        self.toolbar.components.get_action("screenshot").action.triggered.connect(self.screenshot)

    @SafeSlot()
    def _create_widget_from_toolbar(self, widget_name: str) -> None:
        # Run with RPC broadcast to namespace of all widgets
        with RPCRegister.delayed_broadcast():
            name = pascal_to_snake(widget_name)
            dock_name = WidgetContainerUtils.generate_unique_name(name, self.panels.keys())
            self.new(name=dock_name, widget=widget_name)

    def paintEvent(self, event: QPaintEvent):  # TODO decide if we want any default instructions
        super().paintEvent(event)
        if self._instructions_visible:
            painter = QPainter(self)
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "Add docks using 'new' method from CLI\n or \n Add widget docks using the toolbar",
            )

    @property
    def panels(self) -> dict[str, BECDock]:
        """
        Get the docks in the dock area.
        Returns:
            dock_dict(dict): The docks in the dock area.
        """
        return dict(self.dock_area.docks)

    @panels.setter
    def panels(self, value: dict[str, BECDock]):
        self.dock_area.docks = WeakValueDictionary(value)  # This can not work can it?

    @property
    def panel_list(self) -> list[BECDock]:
        """
        Get the docks in the dock area.

        Returns:
            list: The docks in the dock area.
        """
        return list(self.dock_area.docks.values())

    @property
    def temp_areas(self) -> list:
        """
        Get the temporary areas in the dock area.

        Returns:
            list: The temporary areas in the dock area.
        """
        return list(map(str, self.dock_area.tempAreas))

    @temp_areas.setter
    def temp_areas(self, value: list):
        self.dock_area.tempAreas = list(map(str, value))

    @SafeSlot()
    def restore_state(
        self, state: dict = None, missing: Literal["ignore", "error"] = "ignore", extra="bottom"
    ):
        """
        Restore the state of the dock area. If no state is provided, the last state is restored.

        Args:
            state(dict): The state to restore.
            missing(Literal['ignore','error']): What to do if a dock is missing.
            extra(str): Extra docks that are in the dockarea but that are not mentioned in state will be added to the bottom of the dockarea, unless otherwise specified by the extra argument.
        """
        if state is None:
            state = self.config.docks_state
        if state is None:
            return
        self.dock_area.restoreState(state, missing=missing, extra=extra)

    @SafeSlot()
    def save_state(self) -> dict:
        """
        Save the state of the dock area.

        Returns:
            dict: The state of the dock area.
        """
        last_state = self.dock_area.saveState()
        self.config.docks_state = last_state
        return last_state

    @SafeSlot(popup_error=True)
    def new(
        self,
        name: str | None = None,
        widget: str | QWidget | None = None,
        widget_name: str | None = None,
        position: Literal["bottom", "top", "left", "right", "above", "below"] = "bottom",
        relative_to: BECDock | None = None,
        closable: bool = True,
        floating: bool = False,
        row: int | None = None,
        col: int = 0,
        rowspan: int = 1,
        colspan: int = 1,
    ) -> BECDock:
        """
        Add a dock to the dock area. Dock has QGridLayout as layout manager by default.

        Args:
            name(str): The name of the dock to be displayed and for further references. Has to be unique.
            widget(str|QWidget|None): The widget to be added to the dock. While using RPC, only BEC RPC widgets from RPCWidgetHandler are allowed.
            position(Literal["bottom", "top", "left", "right", "above", "below"]): The position of the dock.
            relative_to(BECDock): The dock to which the new dock should be added relative to.
            closable(bool): Whether the dock is closable.
            floating(bool): Whether the dock is detached after creating.
            row(int): The row of the added widget.
            col(int): The column of the added widget.
            rowspan(int): The rowspan of the added widget.
            colspan(int): The colspan of the added widget.

        Returns:
            BECDock: The created dock.
        """
        dock_names = [
            dock.object_name for dock in self.panel_list
        ]  # pylint: disable=protected-access
        if name is not None:  # Name is provided
            if name in dock_names:
                raise ValueError(
                    f"Name {name} must be unique for docks, but already exists in DockArea "
                    f"with name: {self.object_name} and id {self.gui_id}."
                )
            WidgetContainerUtils.raise_for_invalid_name(name, container=self)

        else:  # Name is not provided
            name = WidgetContainerUtils.generate_unique_name(name="dock", list_of_names=dock_names)

        dock = BECDock(
            parent=self,
            name=name,  # this is dock name pyqtgraph property, this is displayed on label
            object_name=name,  # this is a real qt object name passed to BECConnector
            parent_dock_area=self,
            closable=closable,
        )
        dock.config.position = position
        self.config.docks[dock.name()] = dock.config
        # The dock.name is equal to the name passed to BECDock
        self.dock_area.addDock(dock=dock, position=position, relativeTo=relative_to)

        if len(self.dock_area.docks) <= 1:
            dock.hide_title_bar()
        elif len(self.dock_area.docks) > 1:
            for dock in self.dock_area.docks.values():
                dock.show_title_bar()

        if widget is not None:
            # Check if widget name exists.
            dock.new(
                widget=widget, name=widget_name, row=row, col=col, rowspan=rowspan, colspan=colspan
            )
        if (
            self._instructions_visible
        ):  # TODO still decide how initial instructions should be handled
            self._instructions_visible = False
            self.update()
        if floating:
            dock.detach()
        return dock

    def detach_dock(self, dock_name: str) -> BECDock:
        """
        Undock a dock from the dock area.

        Args:
            dock_name(str): The dock to undock.

        Returns:
            BECDock: The undocked dock.
        """
        dock = self.dock_area.docks[dock_name]
        dock.detach()
        return dock

    @SafeSlot()
    def attach_all(self):
        """
        Return all floating docks to the dock area.
        """
        while self.dock_area.tempAreas:
            for temp_area in self.dock_area.tempAreas:
                self.remove_temp_area(temp_area)

    def remove_temp_area(self, area):
        """
        Remove a temporary area from the dock area.
        This is a patched method of pyqtgraph's removeTempArea
        """
        if area not in self.dock_area.tempAreas:
            # FIXME add some context for the logging, I am not sure which object is passed.
            # It looks like a pyqtgraph.DockArea
            logger.info(f"Attempted to remove dock_area, but was not floating.")
            return
        self.dock_area.tempAreas.remove(area)
        area.window().close()
        area.window().deleteLater()

    def cleanup(self):
        """
        Cleanup the dock area.
        """
        self.delete_all()
        self.dark_mode_button.close()
        self.dark_mode_button.deleteLater()
        super().cleanup()

    def show(self):
        """Show all windows including floating docks."""
        super().show()
        for docks in self.panels.values():
            if docks.window() is self:
                # avoid recursion
                continue
            docks.window().show()

    def hide(self):
        """Hide all windows including floating docks."""
        super().hide()
        for docks in self.panels.values():
            if docks.window() is self:
                # avoid recursion
                continue
            docks.window().hide()

    def delete_all(self) -> None:
        """
        Delete all docks.
        """
        self.attach_all()
        for dock_name in self.panels.keys():
            self.delete(dock_name)

    def delete(self, dock_name: str):
        """
        Delete a dock by name.

        Args:
            dock_name(str): The name of the dock to delete.
        """
        dock = self.dock_area.docks.pop(dock_name, None)
        self.config.docks.pop(dock_name, None)
        if dock:
            dock.close()
            dock.deleteLater()
            if len(self.dock_area.docks) <= 1:
                for dock in self.dock_area.docks.values():
                    dock.hide_title_bar()
        else:
            raise ValueError(f"Dock with name {dock_name} does not exist.")
        # self._broadcast_update()

    def remove(self) -> None:
        """
        Remove the dock area. If the dock area is embedded in a BECMainWindow and
        is set as the central widget, the main window will be closed.
        """
        parent = self.parent()
        if isinstance(parent, BECMainWindow):
            central_widget = parent.centralWidget()
            if central_widget is self:
                # Closing the parent will also close the dock area
                parent.close()
                return

        self.close()


if __name__ == "__main__":  # pragma: no cover

    import sys

    from bec_widgets.utils.colors import set_theme

    app = QApplication([])
    set_theme("auto")
    dock_area = BECDockArea()
    dock_1 = dock_area.new(name="dock_0", widget="DarkModeButton")
    dock_1.new(widget="DarkModeButton")
    # dock_1 = dock_area.new(name="dock_0", widget="Waveform")
    dock_area.new(widget="DarkModeButton")
    dock_area.show()
    dock_area.setGeometry(100, 100, 800, 600)
    app.topLevelWidgets()
    WidgetHierarchy.print_becconnector_hierarchy_from_app()
    app.exec_()
    sys.exit(app.exec_())
