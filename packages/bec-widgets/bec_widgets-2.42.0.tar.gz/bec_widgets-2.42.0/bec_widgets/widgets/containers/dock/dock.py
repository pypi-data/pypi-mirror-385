from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Optional, cast

from bec_lib.logger import bec_logger
from pydantic import Field
from pyqtgraph.dockarea import Dock, DockLabel
from qtpy import QtCore, QtGui

from bec_widgets.cli.client_utils import IGNORE_WIDGETS
from bec_widgets.cli.rpc.rpc_widget_handler import widget_handler
from bec_widgets.utils import ConnectionConfig, GridLayoutManager
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.container_utils import WidgetContainerUtils
from bec_widgets.utils.error_popups import SafeSlot

logger = bec_logger.logger

if TYPE_CHECKING:  # pragma: no cover
    from qtpy.QtWidgets import QWidget

    from bec_widgets.widgets.containers.dock.dock_area import BECDockArea


class DockConfig(ConnectionConfig):
    widgets: dict[str, Any] = Field({}, description="The widgets in the dock.")
    position: Literal["bottom", "top", "left", "right", "above", "below"] = Field(
        "bottom", description="The position of the dock."
    )
    parent_dock_area: Optional[str] | None = Field(
        None, description="The GUI ID of parent dock area of the dock."
    )


class CustomDockLabel(DockLabel):
    def __init__(self, text: str, closable: bool = True):
        super().__init__(text, closable)
        if closable:
            red_icon = QtGui.QIcon()
            pixmap = QtGui.QPixmap(32, 32)
            pixmap.fill(QtCore.Qt.GlobalColor.red)
            painter = QtGui.QPainter(pixmap)
            pen = QtGui.QPen(QtCore.Qt.GlobalColor.white)
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(8, 8, 24, 24)
            painter.drawLine(24, 8, 8, 24)
            painter.end()
            red_icon.addPixmap(pixmap)

            self.closeButton.setIcon(red_icon)

    def updateStyle(self):
        r = "3px"
        if self.dim:
            fg = "#aaa"
            bg = "#44a"
            border = "#339"
        else:
            fg = "#fff"
            bg = "#3f4042"
            border = "#3f4042"

        if self.orientation == "vertical":
            self.vStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: 0px;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: %s;
                border-width: 0px;
                border-right: 2px solid %s;
                padding-top: 3px;
                padding-bottom: 3px;
                font-size: %s;
            }""" % (
                bg,
                fg,
                r,
                r,
                border,
                self.fontSize,
            )
            self.setStyleSheet(self.vStyle)
        else:
            self.hStyle = """DockLabel {
                background-color : %s;
                color : %s;
                border-top-right-radius: %s;
                border-top-left-radius: %s;
                border-bottom-right-radius: 0px;
                border-bottom-left-radius: 0px;
                border-width: 0px;
                border-bottom: 2px solid %s;
                padding-left: 3px;
                padding-right: 3px;
                font-size: %s;
            }""" % (
                bg,
                fg,
                r,
                r,
                border,
                self.fontSize,
            )
            self.setStyleSheet(self.hStyle)


class BECDock(BECWidget, Dock):
    ICON_NAME = "widgets"
    USER_ACCESS = [
        "_config_dict",
        "element_list",
        "elements",
        "new",
        "show",
        "hide",
        "show_title_bar",
        "set_title",
        "hide_title_bar",
        "available_widgets",
        "delete",
        "delete_all",
        "remove",
        "attach",
        "detach",
    ]

    def __init__(
        self,
        parent: QWidget | None = None,
        parent_dock_area: BECDockArea | None = None,
        config: DockConfig | None = None,
        name: str | None = None,
        object_name: str | None = None,
        client=None,
        gui_id: str | None = None,
        closable: bool = True,
        **kwargs,
    ) -> None:

        if config is None:
            config = DockConfig(
                widget_class=self.__class__.__name__,
                parent_dock_area=parent_dock_area.gui_id if parent_dock_area else None,
            )
        else:
            if isinstance(config, dict):
                config = DockConfig(**config)
            self.config = config
        label = CustomDockLabel(text=name, closable=closable)
        super().__init__(
            parent=parent_dock_area,
            name=name,
            object_name=object_name,
            client=client,
            gui_id=gui_id,
            config=config,
            label=label,
            **kwargs,
        )

        self.parent_dock_area = parent_dock_area
        # Layout Manager
        self.layout_manager = GridLayoutManager(self.layout)

    def dropEvent(self, event):
        source = event.source()
        old_area = source.area
        self.setOrientation("horizontal", force=True)
        super().dropEvent(event)
        if old_area in self.orig_area.tempAreas and old_area != self.orig_area:
            self.orig_area.removeTempArea(old_area)
            old_area.window().deleteLater()

    def float(self):
        """
        Float the dock.
        Overwrites the default pyqtgraph dock float.
        """

        # need to check if the dock is temporary and if it is the only dock in the area
        # fixes bug in pyqtgraph detaching
        if self.area.temporary == True and len(self.area.docks) <= 1:
            return
        elif self.area.temporary == True and len(self.area.docks) > 1:
            self.area.docks.pop(self.name(), None)
            super().float()
        else:
            super().float()

    @property
    def elements(self) -> dict[str, BECWidget]:
        """
        Get the widgets in the dock.

        Returns:
            widgets(dict): The widgets in the dock.
        """
        # pylint: disable=protected-access
        return dict((widget.object_name, widget) for widget in self.element_list)

    @property
    def element_list(self) -> list[BECWidget]:
        """
        Get the widgets in the dock.

        Returns:
            widgets(list): The widgets in the dock.
        """
        return self.widgets

    def hide_title_bar(self):
        """
        Hide the title bar of the dock.
        """
        # self.hideTitleBar() #TODO pyqtgraph looks bugged ATM, doing my implementation
        self.label.hide()
        self.labelHidden = True

    def show(self):
        """
        Show the dock.
        """
        super().show()
        self.show_title_bar()

    def hide(self):
        """
        Hide the dock.
        """
        self.hide_title_bar()
        super().hide()

    def show_title_bar(self):
        """
        Hide the title bar of the dock.
        """
        # self.showTitleBar() #TODO pyqtgraph looks bugged ATM, doing my implementation
        self.label.show()
        self.labelHidden = False

    def set_title(self, title: str):
        """
        Set the title of the dock.

        Args:
            title(str): The title of the dock.
        """
        self.orig_area.docks[title] = self.orig_area.docks.pop(self.name())
        self.setTitle(title)

    def get_widgets_positions(self) -> dict:
        """
        Get the positions of the widgets in the dock.

        Returns:
            dict: The positions of the widgets in the dock as dict -> {(row, col, rowspan, colspan):widget}
        """
        return self.layout_manager.get_widgets_positions()

    def available_widgets(
        self,
    ) -> list:  # TODO can be moved to some util mixin like container class for rpc widgets
        """
        List all widgets that can be added to the dock.

        Returns:
            list: The list of eligible widgets.
        """
        return list(widget_handler.widget_classes.keys())

    def _get_list_of_widget_name_of_parent_dock_area(self) -> list[str]:
        if (docks := self.parent_dock_area.panel_list) is None:
            return []
        widgets = []
        for dock in docks:
            widgets.extend(dock.elements.keys())
        return widgets

    @SafeSlot(popup_error=True)
    def new(
        self,
        widget: BECWidget | str,
        name: str | None = None,
        row: int | None = None,
        col: int = 0,
        rowspan: int = 1,
        colspan: int = 1,
        shift: Literal["down", "up", "left", "right"] = "down",
    ) -> BECWidget:
        """
        Add a widget to the dock.

        Args:
            widget(QWidget): The widget to add. It can not be BECDock or BECDockArea.
            name(str): The name of the widget.
            row(int): The row to add the widget to. If None, the widget will be added to the next available row.
            col(int): The column to add the widget to.
            rowspan(int): The number of rows the widget should span.
            colspan(int): The number of columns the widget should span.
            shift(Literal["down", "up", "left", "right"]): The direction to shift the widgets if the position is occupied.
        """
        if name is not None:
            WidgetContainerUtils.raise_for_invalid_name(name, container=self)

        if row is None:
            row = self.layout.rowCount()

        if self.layout_manager.is_position_occupied(row, col):
            self.layout_manager.shift_widgets(shift, start_row=row)

        # Check that Widget is not BECDock or BECDockArea
        widget_class_name = widget if isinstance(widget, str) else widget.__class__.__name__
        if widget_class_name in IGNORE_WIDGETS:
            raise ValueError(f"Widget {widget} can not be added to dock.")

        if isinstance(widget, str):
            widget = cast(
                BECWidget,
                widget_handler.create_widget(
                    widget_type=widget, object_name=name, parent_dock=self, parent=self
                ),
            )
        else:
            widget.object_name = name

        self.addWidget(widget, row=row, col=col, rowspan=rowspan, colspan=colspan)
        if hasattr(widget, "config"):
            widget.config.gui_id = widget.gui_id
            self.config.widgets[widget.object_name] = widget.config
        return widget

    def move_widget(self, widget: QWidget, new_row: int, new_col: int):
        """
        Move a widget to a new position in the layout.

        Args:
            widget(QWidget): The widget to move.
            new_row(int): The new row to move the widget to.
            new_col(int): The new column to move the widget to.
        """
        self.layout_manager.move_widget(widget, new_row, new_col)

    def attach(self):
        """
        Attach the dock to the parent dock area.
        """
        self.parent_dock_area.remove_temp_area(self.area)

    def detach(self):
        """
        Detach the dock from the parent dock area.
        """
        self.float()

    def remove(self):
        """
        Remove the dock from the parent dock area.
        """
        self.parent_dock_area.delete(self.object_name)

    def delete(self, widget_name: str) -> None:
        """
        Remove a widget from the dock.

        Args:
            widget_name(str): Delete the widget with the given name.
        """
        # pylint: disable=protected-access
        widgets = [widget for widget in self.widgets if widget.object_name == widget_name]
        if len(widgets) == 0:
            logger.warning(
                f"Widget with name {widget_name} not found in dock {self.name()}. "
                f"Checking if gui_id was passed as widget_name."
            )
            # Try to find the widget in the RPC register, maybe the gui_id was passed as widget_name
            widget = self.rpc_register.get_rpc_by_id(widget_name)
            if widget is None:
                logger.warning(
                    f"Widget not found for name or gui_id: {widget_name} in dock {self.name()}"
                )
                return
        else:
            widget = widgets[0]
        self.layout.removeWidget(widget)
        self.config.widgets.pop(widget.object_name, None)
        if widget in self.widgets:
            self.widgets.remove(widget)
        widget.close()
        widget.deleteLater()

    def delete_all(self):
        """
        Remove all widgets from the dock.
        """
        for widget in self.widgets:
            self.delete(widget.object_name)

    def cleanup(self):
        """
        Clean up the dock, including all its widgets.
        """
        # # FIXME Cleanup might be called twice
        try:
            logger.info(f"Cleaning up dock {self.name()}")
            self.label.close()
            self.label.deleteLater()
        except Exception as e:
            logger.error(f"Error while closing dock label: {e}")

        # Remove the dock from the parent dock area
        if self.parent_dock_area:
            self.parent_dock_area.dock_area.docks.pop(self.name(), None)
            self.parent_dock_area.config.docks.pop(self.name(), None)
        self.delete_all()
        self.widgets.clear()
        super().cleanup()
        self.deleteLater()

    def close(self):
        """
        Close the dock area and cleanup.
        Has to be implemented to overwrite pyqtgraph event accept in Container close.
        """
        self.cleanup()
        super().close()


if __name__ == "__main__":  # pragma: no cover
    import sys

    from qtpy.QtWidgets import QApplication

    app = QApplication([])
    dock = BECDock(name="dock")
    dock.show()
    app.exec_()
    sys.exit(app.exec_())
