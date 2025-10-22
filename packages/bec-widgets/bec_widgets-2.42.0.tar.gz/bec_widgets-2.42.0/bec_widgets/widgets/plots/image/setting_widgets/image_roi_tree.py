from __future__ import annotations

import math
from typing import TYPE_CHECKING, Literal

from bec_lib import bec_logger
from bec_qthemes import material_icon
from qtpy.QtCore import QEvent, Qt
from qtpy.QtGui import QColor
from qtpy.QtWidgets import (
    QColorDialog,
    QHBoxLayout,
    QHeaderView,
    QSpinBox,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from bec_widgets import BECWidget
from bec_widgets.utils import BECDispatcher, ConnectionConfig
from bec_widgets.utils.toolbars.actions import WidgetAction
from bec_widgets.utils.toolbars.bundles import ToolbarBundle
from bec_widgets.utils.toolbars.toolbar import MaterialIconAction, ModularToolBar
from bec_widgets.widgets.plots.roi.image_roi import (
    BaseROI,
    CircularROI,
    EllipticalROI,
    RectangularROI,
    ROIController,
)
from bec_widgets.widgets.utility.visual.color_button_native.color_button_native import (
    ColorButtonNative,
)
from bec_widgets.widgets.utility.visual.colormap_widget.colormap_widget import BECColorMapWidget

if TYPE_CHECKING:
    from bec_widgets.widgets.plots.image.image import Image


logger = bec_logger.logger


class ROILockButton(QToolButton):
    """Keeps its icon and checked state in sync with a single ROI."""

    def __init__(self, roi: BaseROI, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self._roi = roi
        self.clicked.connect(self._toggle)
        roi.movableChanged.connect(lambda _: self._sync())
        self._sync()

    def _toggle(self):
        # checked -> locked -> movable = False
        self._roi.movable = not self.isChecked()

    def _sync(self):
        movable = self._roi.movable
        self.setChecked(not movable)
        icon = "lock_open_right" if movable else "lock"
        self.setIcon(material_icon(icon, size=(20, 20), convert_to_pixmap=False))


class ROIPropertyTree(BECWidget, QWidget):
    """
    Two-column tree:  [ROI]  [Properties]

    - Top-level: ROI name (editable) + color button.
    - Children: type, line-width (spin box), coordinates (auto-updating).

    Args:
        parent (QWidget, optional): Parent widget. Defaults to None.
        image_widget (Image): The main Image widget that displays the ImageItem.
            Provides ``plot_item`` and owns an ROIController already.
        controller (ROIController, optional): Optionally pass an external controller.
            If None, the manager uses ``image_widget.roi_controller``.
        compact (bool, optional): If True, use a compact mode with no tree view,
            only a toolbar with draw actions. Defaults to False.
        compact_orientation (str, optional): Orientation of the toolbar in compact mode.
            Either "vertical" or "horizontal". Defaults to "vertical".
        compact_color (str, optional): Color of the single active ROI in compact mode.
    """

    PLUGIN = False
    RPC = False

    COL_ACTION, COL_ROI, COL_PROPS = range(3)
    DELETE_BUTTON_COLOR = "#CC181E"

    def __init__(
        self,
        *,
        parent: QWidget = None,
        image_widget: Image,
        controller: ROIController | None = None,
        compact: bool = False,
        compact_orientation: Literal["vertical", "horizontal"] = "vertical",
        compact_color: str = "#f0f0f0",
    ):

        super().__init__(
            parent=parent, config=ConnectionConfig(widget_class=self.__class__.__name__)
        )
        self.compact = compact
        self.compact_orient = compact_orientation
        self.compact_color = compact_color
        self.single_active_roi: BaseROI | None = None

        if controller is None:
            # Use the controller already belonging to the Image widget
            controller = getattr(image_widget, "roi_controller", None)
            if controller is None:
                controller = ROIController()
                image_widget.roi_controller = controller

        self.image_widget = image_widget
        self.plot = image_widget.plot_item
        self.controller = controller
        self.roi_items: dict[BaseROI, QTreeWidgetItem] = {}

        self.layout = QVBoxLayout(self)
        self._init_toolbar()
        if not self.compact:
            self._init_tree()
        else:
            self.tree = None

        # connect controller
        self.controller.roiAdded.connect(self._on_roi_added)
        self.controller.roiRemoved.connect(self._on_roi_removed)
        if not self.compact:
            self.controller.cleared.connect(self.tree.clear)

        # initial load
        for r in self.controller.rois:
            self._on_roi_added(r)

        if not self.compact:
            self.tree.collapseAll()

    # --------------------------------------------------------------------- UI
    def _init_toolbar(self):
        tb = self.toolbar = ModularToolBar(
            self, orientation=self.compact_orient if self.compact else "horizontal"
        )
        self._draw_actions: dict[str, MaterialIconAction] = {}
        # --- ROI draw actions (toggleable) ---

        tb.components.add_safe(
            "roi_rectangle",
            MaterialIconAction("add_box", "Add Rect ROI", checkable=True, parent=self),
        )
        tb.components.add_safe(
            "roi_circle",
            MaterialIconAction("add_circle", "Add Circle ROI", checkable=True, parent=self),
        )
        tb.components.add_safe(
            "roi_ellipse",
            MaterialIconAction("vignette", "Add Ellipse ROI", checkable=True, parent=self),
        )
        bundle = ToolbarBundle("roi_draw", tb.components)
        bundle.add_action("roi_rectangle")
        bundle.add_action("roi_circle")
        bundle.add_action("roi_ellipse")
        tb.add_bundle(bundle)

        self._draw_actions = {
            "rect": tb.components.get_action("roi_rectangle"),
            "circle": tb.components.get_action("roi_circle"),
            "ellipse": tb.components.get_action("roi_ellipse"),
        }
        for mode, act in self._draw_actions.items():
            act.action.toggled.connect(lambda on, m=mode: self._on_draw_action_toggled(m, on))

        if self.compact:
            tb.components.add_safe(
                "compact_delete",
                MaterialIconAction("delete", "Delete Current Roi", checkable=False, parent=self),
            )
            bundle.add_action("compact_delete")
            tb.components.get_action("compact_delete").action.triggered.connect(
                lambda _: (
                    self.controller.remove_roi(self.single_active_roi)
                    if self.single_active_roi is not None
                    else None
                )
            )
            tb.show_bundles(["roi_draw"])
            self.layout.addWidget(tb)

            # ROI drawing state (needed even in compact mode)
            self._roi_draw_mode = None
            self._roi_start_pos = None
            self._temp_roi = None
            self.plot.scene().installEventFilter(self)
            return

        # Expand/Collapse toggle
        self.expand_toggle = MaterialIconAction(
            "unfold_more", "Expand/Collapse", checkable=True, parent=self  # icon when collapsed
        )
        tb.components.add_safe("expand_toggle", self.expand_toggle)

        def _exp_toggled(on: bool):
            if on:
                # switched to expanded state
                self.tree.expandAll()
                new_icon = material_icon("unfold_less", size=(20, 20), convert_to_pixmap=False)
            else:
                # collapsed state
                self.tree.collapseAll()
                new_icon = material_icon("unfold_more", size=(20, 20), convert_to_pixmap=False)
            self.expand_toggle.action.setIcon(new_icon)

        self.expand_toggle.action.toggled.connect(_exp_toggled)

        self.expand_toggle.action.setChecked(False)

        # Lock/Unlock all ROIs
        self.lock_all_action = MaterialIconAction(
            "lock_open_right", "Lock/Unlock all ROIs", checkable=True, parent=self
        )
        tb.components.add_safe("lock_unlock_all", self.lock_all_action)

        def _lock_all(checked: bool):
            # checked -> everything locked (movable = False)
            for r in self.controller.rois:
                r.movable = not checked
            new_icon = material_icon(
                "lock" if checked else "lock_open_right", size=(20, 20), convert_to_pixmap=False
            )
            self.lock_all_action.action.setIcon(new_icon)

        self.lock_all_action.action.toggled.connect(_lock_all)

        # colormap widget
        self.cmap = BECColorMapWidget(cmap=self.controller.colormap)

        tb.components.add_safe("roi_tree_spacer", WidgetAction(widget=QWidget()))
        tb.components.add_safe("roi_tree_cmap", WidgetAction(widget=self.cmap))

        self.cmap.colormap_changed_signal.connect(self.controller.set_colormap)
        self.layout.addWidget(tb)
        self.controller.paletteChanged.connect(lambda cmap: setattr(self.cmap, "colormap", cmap))

        bundle = ToolbarBundle("roi_tools", tb.components)
        bundle.add_action("expand_toggle")
        bundle.add_action("lock_unlock_all")
        bundle.add_action("roi_tree_spacer")
        bundle.add_action("roi_tree_cmap")
        tb.add_bundle(bundle)

        tb.show_bundles(["roi_draw", "roi_tools"])

        # ROI drawing state
        self._roi_draw_mode = None  # 'rect' | 'circle' | 'ellipse' | None
        self._roi_start_pos = None  # QPointF in image coords
        self._temp_roi = None  # live ROI being resized while dragging
        # capture mouse events on the plot scene
        self.plot.scene().installEventFilter(self)

    def _init_tree(self):
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Actions", "ROI", "Properties"])
        self.tree.header().setSectionResizeMode(self.COL_ACTION, QHeaderView.ResizeToContents)
        self.tree.headerItem().setText(self.COL_ACTION, "Actions")  # blank header text
        self.tree.itemChanged.connect(self._on_item_edited)
        self.layout.addWidget(self.tree)

    ################################################################################
    # Helper functions
    ################################################################################

    # --------------------------------------------------------------------- formatting
    @staticmethod
    def _format_coord_text(value) -> str:
        """
        Consistently format a coordinate value for display.
        """
        if isinstance(value, (tuple, list)):
            return "(" + ", ".join(f"{v:.2f}" for v in value) + ")"
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)

    def _set_roi_draw_mode(self, mode: str | None):
        # Update toolbar actions so that only the selected mode is checked
        for m, act in self._draw_actions.items():
            act.action.blockSignals(True)
            act.action.setChecked(m == mode)
            act.action.blockSignals(False)

        self._roi_draw_mode = mode
        self._roi_start_pos = None
        # remove any unfinished temp ROI
        if self._temp_roi is not None:
            self.plot.removeItem(self._temp_roi)
            self._temp_roi = None

    def _on_draw_action_toggled(self, mode: str, checked: bool):
        if checked:
            # Activate selected mode
            self._set_roi_draw_mode(mode)
        else:
            # If the active mode is being unchecked, clear mode
            if self._roi_draw_mode == mode:
                self._set_roi_draw_mode(None)

    def eventFilter(self, obj, event):
        if self._roi_draw_mode is None:
            return super().eventFilter(obj, event)
        if event.type() == QEvent.GraphicsSceneMousePress and event.button() == Qt.LeftButton:
            self._roi_start_pos = self.plot.vb.mapSceneToView(event.scenePos())
            if self._roi_draw_mode == "rect":
                self._temp_roi = RectangularROI(
                    pos=[self._roi_start_pos.x(), self._roi_start_pos.y()],
                    size=[5, 5],
                    parent_image=self.image_widget,
                    resize_handles=False,
                )
            elif self._roi_draw_mode == "circle":
                self._temp_roi = CircularROI(
                    pos=[self._roi_start_pos.x() - 2.5, self._roi_start_pos.y() - 2.5],
                    size=[5, 5],
                    parent_image=self.image_widget,
                )
            elif self._roi_draw_mode == "ellipse":
                self._temp_roi = EllipticalROI(
                    pos=[self._roi_start_pos.x() - 2.5, self._roi_start_pos.y() - 2.5],
                    size=[5, 5],
                    parent_image=self.image_widget,
                )
            self.plot.addItem(self._temp_roi)
            return True
        elif event.type() == QEvent.GraphicsSceneMouseMove and self._temp_roi is not None:
            pos = self.plot.vb.mapSceneToView(event.scenePos())
            dx = pos.x() - self._roi_start_pos.x()
            dy = pos.y() - self._roi_start_pos.y()

            if self._roi_draw_mode == "rect":
                self._temp_roi.setSize([dx, dy])
            elif self._roi_draw_mode == "circle":
                r = max(
                    1, math.hypot(dx, dy)
                )  # radius never smaller than 1 for safety of handle mapping, otherwise SEGFAULT
                d = 2 * r  # diameter
                self._temp_roi.setPos(self._roi_start_pos.x() - r, self._roi_start_pos.y() - r)
                self._temp_roi.setSize([d, d])
            elif self._roi_draw_mode == "ellipse":
                # Safeguard: enforce a minimum ellipse width/height of 2 px
                min_dim = 2.0
                w = dx if abs(dx) >= min_dim else math.copysign(min_dim, dx or 1.0)
                h = dy if abs(dy) >= min_dim else math.copysign(min_dim, dy or 1.0)
                self._temp_roi.setSize([w, h])
            return True
        elif (
            event.type() == QEvent.GraphicsSceneMouseRelease
            and event.button() == Qt.LeftButton
            and self._temp_roi is not None
        ):
            # finalize ROI
            final_roi = self._temp_roi
            self._temp_roi = None
            self._set_roi_draw_mode(None)
            # register via controller
            self.controller.add_roi(final_roi)
            if self.compact:
                final_roi.line_color = self.compact_color
            return True
        return super().eventFilter(obj, event)

    # --------------------------------------------------------- controller slots
    def _on_roi_added(self, roi: BaseROI):
        if self.compact:
            roi.line_color = self.compact_color
            if self.single_active_roi is not None and self.single_active_roi is not roi:
                self.controller.remove_roi(self.single_active_roi)
            self.single_active_roi = roi
            return
        # check the global setting from the toolbar
        if hasattr(self, "lock_all_action") and self.lock_all_action.action.isChecked():
            roi.movable = False
        # parent row with blank action column, name in ROI column
        parent = QTreeWidgetItem(self.tree, ["", "", ""])
        parent.setText(self.COL_ROI, roi.label)
        parent.setFlags(parent.flags() | Qt.ItemIsEditable)
        # --- actions widget (lock/unlock + delete) ---
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(3)

        # lock / unlock toggle
        lock_btn = ROILockButton(roi, parent=self)
        actions_layout.addWidget(lock_btn)

        # delete button
        del_btn = QToolButton()
        delete_icon = material_icon(
            "delete",
            size=(20, 20),
            convert_to_pixmap=False,
            filled=False,
            color=self.DELETE_BUTTON_COLOR,
        )
        del_btn.setIcon(delete_icon)
        del_btn.clicked.connect(lambda _=None, r=roi: self._delete_roi(r))
        actions_layout.addWidget(del_btn)

        # install composite widget into the tree
        self.tree.setItemWidget(parent, self.COL_ACTION, actions_widget)
        # color button
        color_btn = ColorButtonNative(parent=self, color=roi.line_color)
        self.tree.setItemWidget(parent, self.COL_PROPS, color_btn)
        color_btn.color_changed.connect(
            lambda new_color, r=roi: setattr(r, "line_color", new_color)
        )

        # child rows (3 columns: action, ROI, properties)
        QTreeWidgetItem(parent, ["", "Type", roi.__class__.__name__])
        width_item = QTreeWidgetItem(parent, ["", "Line width", ""])
        width_spin = QSpinBox()
        width_spin.setRange(1, 50)
        width_spin.setValue(roi.line_width)
        self.tree.setItemWidget(width_item, self.COL_PROPS, width_spin)
        width_spin.valueChanged.connect(lambda v, r=roi: setattr(r, "line_width", v))

        # --- Step 2: Insert separate coordinate rows (one per value)
        coord_rows = {}
        coords = roi.get_coordinates(typed=True)

        for key, value in coords.items():
            # Human-readable label: “center x” from “center_x”, etc.
            label = key.replace("_", " ").title()
            val_text = self._format_coord_text(value)
            row = QTreeWidgetItem(parent, ["", label, val_text])
            coord_rows[key] = row

        # keep dict refs
        self.roi_items[roi] = parent

        # --- Step 3: Update coordinates on ROI movement
        def _update_coords():
            c_dict = roi.get_coordinates(typed=True)
            for k, row in coord_rows.items():
                if k in c_dict:
                    val = c_dict[k]
                    row.setText(self.COL_PROPS, self._format_coord_text(val))

        if isinstance(roi, RectangularROI):
            roi.edgesChanged.connect(_update_coords)
        else:
            roi.centerChanged.connect(_update_coords)

        # sync width edits back to spinbox
        roi.penChanged.connect(lambda r=roi, sp=width_spin: sp.setValue(r.line_width))
        roi.nameChanged.connect(lambda n, itm=parent: itm.setText(self.COL_ROI, n))

        # color changes
        roi.penChanged.connect(lambda r=roi, b=color_btn: b.set_color(r.line_color))

        for c in range(3):
            self.tree.resizeColumnToContents(c)

    def _toggle_movable(self, roi: BaseROI):
        """
        Toggle the `movable` property of the given ROI.
        """
        roi.movable = not roi.movable

    def _on_roi_removed(self, roi: BaseROI):
        if self.compact:
            if self.single_active_roi is roi:
                self.single_active_roi = None
            return
        item = self.roi_items.pop(roi, None)
        if item:
            idx = self.tree.indexOfTopLevelItem(item)
            self.tree.takeTopLevelItem(idx)

    # ---------------------------------------------------------- event handlers
    def _pick_color(self, roi: BaseROI, btn: "ColorButtonNative"):
        clr = QColorDialog.getColor(QColor(roi.line_color), self, "Select ROI Color")
        if clr.isValid():
            roi.line_color = clr.name()
            btn.set_color(clr)

    def _on_item_edited(self, item: QTreeWidgetItem, col: int):
        if col != self.COL_ROI:
            return
        # find which roi
        for r, it in self.roi_items.items():
            if it is item:
                r.label = item.text(self.COL_ROI)
                break

    def _delete_roi(self, roi):
        self.controller.remove_roi(roi)

    def cleanup(self):
        if hasattr(self, "cmap"):
            self.cmap.close()
            self.cmap.deleteLater()
        if self.controller and hasattr(self.controller, "rois"):
            for roi in self.controller.rois:  # disconnect all signals from ROIs
                try:
                    if isinstance(roi, RectangularROI):
                        roi.edgesChanged.disconnect()
                    else:
                        roi.centerChanged.disconnect()
                    roi.penChanged.disconnect()
                    roi.nameChanged.disconnect()
                except (RuntimeError, TypeError) as e:
                    logger.error(f"Failed to disconnect roi qt signal: {e}")

        super().cleanup()


# Demo
if __name__ == "__main__":  # pragma: no cover
    import sys

    import numpy as np
    from qtpy.QtWidgets import QApplication

    from bec_widgets.widgets.plots.image.image import Image

    app = QApplication(sys.argv)

    bec_dispatcher = BECDispatcher(gui_id="roi_tree_demo")
    client = bec_dispatcher.client
    client.start()

    image_widget = Image(popups=False)
    image_widget.main_image.set_data(np.random.normal(size=(200, 200)))

    win = QWidget()
    win.setWindowTitle("Modular ROI Demo")
    ml = QHBoxLayout(win)

    # Add the image widget on the left
    ml.addWidget(image_widget)

    # ROI manager linked to that image with compact mode
    mgr = ROIPropertyTree(parent=image_widget, image_widget=image_widget, compact=True)
    mgr.setFixedWidth(350)
    ml.addWidget(mgr)

    win.resize(1500, 600)
    win.show()
    sys.exit(app.exec_())
