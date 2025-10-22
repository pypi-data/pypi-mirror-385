from __future__ import annotations

import os

from bec_lib.endpoints import MessageEndpoints
from qtpy.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QSize, Qt, QTimer
from qtpy.QtGui import QAction, QActionGroup, QIcon
from qtpy.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStyle,
    QVBoxLayout,
    QWidget,
)

import bec_widgets
from bec_widgets.utils import UILoader
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.colors import apply_theme, set_theme
from bec_widgets.utils.error_popups import SafeSlot
from bec_widgets.utils.widget_io import WidgetHierarchy
from bec_widgets.widgets.containers.main_window.addons.hover_widget import HoverWidget
from bec_widgets.widgets.containers.main_window.addons.notification_center.notification_banner import (
    BECNotificationBroker,
    NotificationCentre,
    NotificationIndicator,
)
from bec_widgets.widgets.containers.main_window.addons.scroll_label import ScrollLabel
from bec_widgets.widgets.containers.main_window.addons.web_links import BECWebLinksMixin
from bec_widgets.widgets.progress.scan_progressbar.scan_progressbar import ScanProgressBar

MODULE_PATH = os.path.dirname(bec_widgets.__file__)

# Ensure the application does not use the native menu bar on macOS to be consistent with linux development.
QApplication.setAttribute(Qt.AA_DontUseNativeMenuBar, True)


class BECMainWindow(BECWidget, QMainWindow):
    RPC = True
    PLUGIN = True
    SCAN_PROGRESS_WIDTH = 100  # px
    STATUS_BAR_WIDGETS_EXPIRE_TIME = 60_000  # milliseconds

    def __init__(
        self,
        parent=None,
        gui_id: str = None,
        client=None,
        window_title: str = "BEC",
        *args,
        **kwargs,
    ):
        super().__init__(parent=parent, gui_id=gui_id, **kwargs)

        self.app = QApplication.instance()
        self.status_bar = self.statusBar()
        self.setWindowTitle(window_title)

        # Notification Centre overlay
        self.notification_centre = NotificationCentre(parent=self)  # Notification layer
        self.notification_broker = BECNotificationBroker()
        self._nc_margin = 16
        self._position_notification_centre()

        # Init ui
        self._init_ui()
        self._connect_to_theme_change()

        # Connections to BEC Notifications
        self.bec_dispatcher.connect_slot(
            self.display_client_message, MessageEndpoints.client_info()
        )

    def setCentralWidget(self, widget: QWidget, qt_default: bool = False):  # type: ignore[override]
        """
        Re‑implement QMainWindow.setCentralWidget so that the *main content*
        widget always lives on the lower layer of the stacked layout that
        hosts our notification overlays.

        Args:
            widget: The widget that should become the new central content.
            qt_default: When *True* the call is forwarded to the base class so
                that Qt behaves exactly as the original implementation (used
                during __init__ when we first install ``self._full_content``).
        """
        super().setCentralWidget(widget)
        self.notification_centre.raise_()
        self.statusBar().raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_notification_centre()

    def _position_notification_centre(self):
        """Keep the notification panel at a fixed margin top-right."""
        if not hasattr(self, "notification_centre"):
            return
        margin = getattr(self, "_nc_margin", 16)  # px
        nc = self.notification_centre
        nc.move(self.width() - nc.width() - margin, margin)

    ################################################################################
    # MainWindow Elements Initialization
    ################################################################################
    def _init_ui(self):

        # Set the icon
        self._init_bec_icon()

        # Set Menu and Status bar
        self._setup_menu_bar()
        self._init_status_bar_widgets()

        # BEC Specific UI
        self.display_app_id()

    def _init_status_bar_widgets(self):
        """
        Prepare the BEC specific widgets in the status bar.
        """

        # Left: App‑ID label
        self._app_id_label = QLabel()
        self._app_id_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.status_bar.addWidget(self._app_id_label)

        # Add a separator after the app ID label
        self._add_separator()

        # Centre: Client‑info label (stretch=1 so it expands)
        self._add_client_info_label()

        # Add scan_progress bar with display logic
        self._add_scan_progress_bar()

        # Setup NotificationIndicator to bottom right of the status bar
        self._add_notification_indicator()

    ################################################################################
    # Notification indicator and Notification Centre helpers

    def _add_notification_indicator(self):
        """
        Add the notification indicator to the status bar and hook the signals.
        """
        # Add the notification indicator to the status bar
        self.notification_indicator = NotificationIndicator(self)
        self.status_bar.addPermanentWidget(self.notification_indicator)

        # Connect the notification broker to the indicator
        self.notification_centre.counts_updated.connect(self.notification_indicator.update_counts)
        self.notification_indicator.filter_changed.connect(self.notification_centre.apply_filter)
        self.notification_indicator.show_all_requested.connect(self.notification_centre.show_all)
        self.notification_indicator.hide_all_requested.connect(self.notification_centre.hide_all)

    ################################################################################
    # Client message status bar widget helpers

    def _add_client_info_label(self):
        """
        Add a client info label to the status bar.
        This label will display messages from the BEC dispatcher.
        """

        # Scroll label for client info in Status Bar
        self._client_info_label = ScrollLabel(self)
        self._client_info_label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        # Full label used in the hover widget
        self._client_info_label_full = QLabel(self)
        self._client_info_label_full.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        # Hover widget to show the full client info label
        self._client_info_hover = HoverWidget(
            self, simple=self._client_info_label, full=self._client_info_label_full
        )
        self.status_bar.addWidget(self._client_info_hover, 1)

        # Timer to automatically clear client messages once they expire
        self._client_info_expire_timer = QTimer(self)
        self._client_info_expire_timer.setSingleShot(True)
        self._client_info_expire_timer.timeout.connect(lambda: self._client_info_label.setText(""))
        self._client_info_expire_timer.timeout.connect(
            lambda: self._client_info_label_full.setText("")
        )

    ################################################################################
    # Progress‑bar helpers
    def _add_scan_progress_bar(self):

        # Setting HoverWidget for the scan progress bar - minimal and full version
        self._scan_progress_bar_simple = ScanProgressBar(self, one_line_design=True)
        self._scan_progress_bar_simple.show_elapsed_time = False
        self._scan_progress_bar_simple.show_remaining_time = False
        self._scan_progress_bar_simple.show_source_label = False
        self._scan_progress_bar_simple.progressbar.label_template = ""
        self._scan_progress_bar_simple.progressbar.setFixedHeight(8)
        self._scan_progress_bar_simple.progressbar.setFixedWidth(80)
        self._scan_progress_bar_full = ScanProgressBar(self)
        self._scan_progress_hover = HoverWidget(
            self, simple=self._scan_progress_bar_simple, full=self._scan_progress_bar_full
        )

        # Bundle the progress bar with a separator
        separator = self._add_separator(separate_object=True)
        self._scan_progress_bar_with_separator = QWidget()
        self._scan_progress_bar_with_separator.layout = QHBoxLayout(
            self._scan_progress_bar_with_separator
        )
        self._scan_progress_bar_with_separator.layout.setContentsMargins(0, 0, 0, 0)
        self._scan_progress_bar_with_separator.layout.setSpacing(0)
        self._scan_progress_bar_with_separator.layout.addWidget(separator)
        self._scan_progress_bar_with_separator.layout.addWidget(self._scan_progress_hover)

        # Set Size
        self._scan_progress_bar_target_width = self.SCAN_PROGRESS_WIDTH
        self._scan_progress_bar_with_separator.setMaximumWidth(self._scan_progress_bar_target_width)

        self.status_bar.addWidget(self._scan_progress_bar_with_separator)

        # Visibility logic
        self._scan_progress_bar_with_separator.hide()
        self._scan_progress_bar_with_separator.setMaximumWidth(0)

        # Timer for hiding logic
        self._scan_progress_hide_timer = QTimer(self)
        self._scan_progress_hide_timer.setSingleShot(True)
        self._scan_progress_hide_timer.setInterval(self.STATUS_BAR_WIDGETS_EXPIRE_TIME)
        self._scan_progress_hide_timer.timeout.connect(self._animate_hide_scan_progress_bar)

        # Show / hide behaviour
        self._scan_progress_bar_simple.progress_started.connect(self._show_scan_progress_bar)
        self._scan_progress_bar_simple.progress_finished.connect(self._delay_hide_scan_progress_bar)

    def _show_scan_progress_bar(self):
        if self._scan_progress_hide_timer.isActive():
            self._scan_progress_hide_timer.stop()
        if self._scan_progress_bar_with_separator.isVisible():
            return

        # Make visible and reset width
        self._scan_progress_bar_with_separator.show()
        self._scan_progress_bar_with_separator.setMaximumWidth(0)

        self._show_container_anim = QPropertyAnimation(
            self._scan_progress_bar_with_separator, b"maximumWidth", self
        )
        self._show_container_anim.setDuration(300)
        self._show_container_anim.setStartValue(0)
        self._show_container_anim.setEndValue(self._scan_progress_bar_target_width)
        self._show_container_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._show_container_anim.start()

    def _delay_hide_scan_progress_bar(self):
        """Start the countdown to hide the scan progress bar."""
        if hasattr(self, "_scan_progress_hide_timer"):
            self._scan_progress_hide_timer.start()

    def _animate_hide_scan_progress_bar(self):
        """Shrink container to the right, then hide."""
        self._hide_container_anim = QPropertyAnimation(
            self._scan_progress_bar_with_separator, b"maximumWidth", self
        )
        self._hide_container_anim.setDuration(300)
        self._hide_container_anim.setStartValue(self._scan_progress_bar_with_separator.width())
        self._hide_container_anim.setEndValue(0)
        self._hide_container_anim.setEasingCurve(QEasingCurve.InCubic)
        self._hide_container_anim.finished.connect(self._scan_progress_bar_with_separator.hide)
        self._hide_container_anim.start()

    def _add_separator(self, separate_object: bool = False) -> QWidget | None:
        """
        Add a vertically centred separator to the status bar or just return it as a separate object.
        """
        status_bar = self.statusBar()

        # The actual line
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFixedHeight(status_bar.sizeHint().height() - 2)

        # Wrapper to center the line vertically -> work around for QFrame not being able to center itself
        wrapper = QWidget()
        vbox = QVBoxLayout(wrapper)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addStretch()
        vbox.addWidget(line, alignment=Qt.AlignHCenter)
        vbox.addStretch()
        wrapper.setFixedWidth(line.sizeHint().width())

        if separate_object:
            return wrapper
        status_bar.addWidget(wrapper)

    def _init_bec_icon(self):
        icon = self.app.windowIcon()
        if icon.isNull():
            icon = QIcon()
            icon.addFile(
                os.path.join(MODULE_PATH, "assets", "app_icons", "bec_widgets_icon.png"),
                size=QSize(48, 48),
            )
            self.app.setWindowIcon(icon)

    def load_ui(self, ui_file):
        loader = UILoader(self)
        self.ui = loader.loader(ui_file)
        self.setCentralWidget(self.ui)

    def _fetch_theme(self) -> str:
        return self.app.theme.theme

    def _get_launcher_from_qapp(self):
        """
        Get the launcher from the QApplication instance.
        """
        from bec_widgets.applications.launch_window import LaunchWindow

        qapp = QApplication.instance()
        widgets = qapp.topLevelWidgets()
        widgets = [w for w in widgets if isinstance(w, LaunchWindow)]
        if widgets:
            return widgets[0]
        return None

    def _show_launcher(self):
        """
        Show the launcher if it exists.
        """
        launcher = self._get_launcher_from_qapp()
        if launcher:
            launcher.show()
            launcher.activateWindow()
            launcher.raise_()

    def _setup_menu_bar(self):
        """
        Setup the menu bar for the main window.
        """
        menu_bar = self.menuBar()

        ##########################################
        # Launch menu
        launch_menu = menu_bar.addMenu("New")

        open_launcher_action = QAction("Open Launcher", self)
        launch_menu.addAction(open_launcher_action)
        open_launcher_action.triggered.connect(self._show_launcher)

        ########################################
        # Theme menu
        theme_menu = menu_bar.addMenu("Theme")

        theme_group = QActionGroup(self)
        light_theme_action = QAction("Light Theme", self, checkable=True)
        dark_theme_action = QAction("Dark Theme", self, checkable=True)
        theme_group.addAction(light_theme_action)
        theme_group.addAction(dark_theme_action)
        theme_group.setExclusive(True)

        theme_menu.addAction(light_theme_action)
        theme_menu.addAction(dark_theme_action)

        # Connect theme actions
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))

        # Set the default theme
        theme = self.app.theme.theme
        if theme == "light":
            light_theme_action.setChecked(True)
        elif theme == "dark":
            dark_theme_action.setChecked(True)

        ########################################
        # Help menu
        help_menu = menu_bar.addMenu("Help")

        help_icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxQuestion)
        bug_icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)

        bec_docs = QAction("BEC Docs", self)
        bec_docs.setIcon(help_icon)
        widgets_docs = QAction("BEC Widgets Docs", self)
        widgets_docs.setIcon(help_icon)
        bug_report = QAction("Bug Report", self)
        bug_report.setIcon(bug_icon)

        bec_docs.triggered.connect(BECWebLinksMixin.open_bec_docs)
        widgets_docs.triggered.connect(BECWebLinksMixin.open_bec_widgets_docs)
        bug_report.triggered.connect(BECWebLinksMixin.open_bec_bug_report)

        help_menu.addAction(bec_docs)
        help_menu.addAction(widgets_docs)
        help_menu.addAction(bug_report)

    ################################################################################
    # Status Bar Addons
    ################################################################################
    def display_app_id(self):
        """
        Display the app ID in the status bar.
        """
        if self.bec_dispatcher.cli_server is None:
            status_message = "Not connected"
        else:
            # Get the server ID from the dispatcher
            server_id = self.bec_dispatcher.cli_server.gui_id
            status_message = f"App ID: {server_id}"
        self._app_id_label.setText(status_message)

    @SafeSlot(dict, dict)
    def display_client_message(self, msg: dict, meta: dict):
        """
        Display a client message in the status bar.

        Args:
            msg(dict): The message to display, should contain:
            meta(dict): Metadata about the message, usually empty.
        """
        message = msg.get("message", "")
        expiration = msg.get("expire", 0)  # 0 → never expire
        self._client_info_label.setText(message)
        self._client_info_label_full.setText(message)

        # Restart the expiration timer if necessary
        if hasattr(self, "_client_info_expire_timer") and self._client_info_expire_timer.isActive():
            self._client_info_expire_timer.stop()
        if expiration and expiration > 0:
            self._client_info_expire_timer.start(int(expiration * 1000))

    ################################################################################
    # General and Cleanup Methods
    ################################################################################
    @SafeSlot(str)
    def change_theme(self, theme: str):
        """
        Change the theme of the application and propagate it to widgets.

        Args:
            theme(str): Either "light" or "dark".
        """
        set_theme(theme)  # emits theme_updated and applies palette globally

    def event(self, event):
        if event.type() == QEvent.Type.StatusTip:
            return True
        return super().event(event)

    def cleanup(self):
        central_widget = self.centralWidget()
        if central_widget is not None:
            central_widget.close()
            central_widget.deleteLater()
        if not isinstance(central_widget, BECWidget):
            # if the central widget is not a BECWidget, we need to call the cleanup method
            # of all widgets whose parent is the current BECMainWindow
            children = self.findChildren(BECWidget)
            for child in children:
                ancestor = WidgetHierarchy._get_becwidget_ancestor(child)
                if ancestor is self:
                    child.cleanup()
                    child.close()
                    child.deleteLater()

        # Timer cleanup
        if hasattr(self, "_client_info_expire_timer") and self._client_info_expire_timer.isActive():
            self._client_info_expire_timer.stop()
        if hasattr(self, "_scan_progress_hide_timer") and self._scan_progress_hide_timer.isActive():
            self._scan_progress_hide_timer.stop()

        ########################################
        # Status bar widgets cleanup

        # Client info label cleanup
        self._client_info_label.cleanup()
        self._client_info_hover.close()
        self._client_info_hover.deleteLater()
        # Scan progress bar cleanup
        self._scan_progress_bar_simple.close()
        self._scan_progress_bar_simple.deleteLater()
        self._scan_progress_bar_full.close()
        self._scan_progress_bar_full.deleteLater()
        self._scan_progress_hover.close()
        self._scan_progress_hover.deleteLater()
        super().cleanup()


class BECMainWindowNoRPC(BECMainWindow):
    RPC = False
    PLUGIN = False


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = BECMainWindow()
    main_window.show()
    main_window.resize(800, 600)
    sys.exit(app.exec())
