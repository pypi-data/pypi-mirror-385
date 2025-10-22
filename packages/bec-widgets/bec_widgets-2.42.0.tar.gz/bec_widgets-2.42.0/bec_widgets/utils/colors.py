from __future__ import annotations

import re
from typing import TYPE_CHECKING, Literal

import bec_qthemes
import numpy as np
import pyqtgraph as pg
from bec_qthemes._os_appearance.listener import OSThemeSwitchListener
from pydantic_core import PydanticCustomError
from qtpy.QtGui import QColor
from qtpy.QtWidgets import QApplication

if TYPE_CHECKING:  # pragma: no cover
    from bec_qthemes._main import AccentColors


def get_theme_name():
    if QApplication.instance() is None or not hasattr(QApplication.instance(), "theme"):
        return "dark"
    else:
        return QApplication.instance().theme.theme


def get_theme_palette():
    return bec_qthemes.load_palette(get_theme_name())


def get_accent_colors() -> AccentColors | None:
    """
    Get the accent colors for the current theme. These colors are extensions of the color palette
    and are used to highlight specific elements in the UI.
    """
    if QApplication.instance() is None or not hasattr(QApplication.instance(), "theme"):
        return None
    return QApplication.instance().theme.accent_colors


def _theme_update_callback():
    """
    Internal callback function to update the theme based on the system theme.
    """
    app = QApplication.instance()
    # pylint: disable=protected-access
    app.theme.theme = app.os_listener._theme.lower()
    app.theme_signal.theme_updated.emit(app.theme.theme)
    apply_theme(app.os_listener._theme.lower())


def set_theme(theme: Literal["dark", "light", "auto"]):
    """
    Set the theme for the application.

    Args:
        theme (Literal["dark", "light", "auto"]): The theme to set. "auto" will automatically switch between dark and light themes based on the system theme.
    """
    app = QApplication.instance()
    bec_qthemes.setup_theme(theme, install_event_filter=False)

    app.theme_signal.theme_updated.emit(theme)
    apply_theme(theme)

    if theme != "auto":
        return

    if not hasattr(app, "os_listener") or app.os_listener is None:
        app.os_listener = OSThemeSwitchListener(_theme_update_callback)
        app.installEventFilter(app.os_listener)


def apply_theme(theme: Literal["dark", "light"]):
    """
    Apply the theme to all pyqtgraph widgets. Do not use this function directly. Use set_theme instead.
    """
    app = QApplication.instance()
    graphic_layouts = [
        child
        for top in app.topLevelWidgets()
        for child in top.findChildren(pg.GraphicsLayoutWidget)
    ]

    plot_items = [
        item
        for gl in graphic_layouts
        for item in gl.ci.items.keys()  # ci is internal pg.GraphicsLayout that hosts all items
        if isinstance(item, pg.PlotItem)
    ]

    histograms = [
        item
        for gl in graphic_layouts
        for item in gl.ci.items.keys()  # ci is internal pg.GraphicsLayout that hosts all items
        if isinstance(item, pg.HistogramLUTItem)
    ]

    # Update background color based on the theme
    if theme == "light":
        background_color = "#e9ecef"  # Subtle contrast for light mode
        foreground_color = "#141414"
        label_color = "#000000"
        axis_color = "#666666"
    else:
        background_color = "#141414"  # Dark mode
        foreground_color = "#e9ecef"
        label_color = "#FFFFFF"
        axis_color = "#CCCCCC"

    # update GraphicsLayoutWidget
    pg.setConfigOptions(foreground=foreground_color, background=background_color)
    for pg_widget in graphic_layouts:
        pg_widget.setBackground(background_color)

    # update PlotItems
    for plot_item in plot_items:
        for axis in ["left", "right", "top", "bottom"]:
            plot_item.getAxis(axis).setPen(pg.mkPen(color=axis_color))
            plot_item.getAxis(axis).setTextPen(pg.mkPen(color=label_color))

        # Change title color
        plot_item.titleLabel.setText(plot_item.titleLabel.text, color=label_color)

        # Change legend color
        if hasattr(plot_item, "legend") and plot_item.legend is not None:
            plot_item.legend.setLabelTextColor(label_color)
            # if legend is in plot item and theme is changed, has to be like that because of pg opt logic
            for sample, label in plot_item.legend.items:
                label_text = label.text
                label.setText(label_text, color=label_color)

    # update HistogramLUTItem
    for histogram in histograms:
        histogram.axis.setPen(pg.mkPen(color=axis_color))
        histogram.axis.setTextPen(pg.mkPen(color=label_color))

    # now define stylesheet according to theme and apply it
    style = bec_qthemes.load_stylesheet(theme)
    app.setStyleSheet(style)


class Colors:

    @staticmethod
    def golden_ratio(num: int) -> list:
        """Calculate the golden ratio for a given number of angles.

        Args:
            num (int): Number of angles

        Returns:
            list: List of angles calculated using the golden ratio.
        """
        phi = 2 * np.pi * ((1 + np.sqrt(5)) / 2)
        angles = []
        for ii in range(num):
            x = np.cos(ii * phi)
            y = np.sin(ii * phi)
            angle = np.arctan2(y, x)
            angles.append(angle)
        return angles

    @staticmethod
    def set_theme_offset(theme: Literal["light", "dark"] | None = None, offset=0.2) -> tuple:
        """
        Set the theme offset to avoid colors too close to white or black with light or dark theme respectively for pyqtgraph plot background.

        Args:
            theme(str): The theme to be applied.
            offset(float): Offset to avoid colors too close to white or black with light or dark theme respectively for pyqtgraph plot background.

        Returns:
            tuple: Tuple of min_pos and max_pos.

        Raises:
            ValueError: If theme_offset is not between 0 and 1.
        """

        if offset < 0 or offset > 1:
            raise ValueError("theme_offset must be between 0 and 1")

        if theme is None:
            app = QApplication.instance()
            if hasattr(app, "theme"):
                theme = app.theme.theme

        if theme == "light":
            min_pos = 0.0
            max_pos = 1 - offset
        else:
            min_pos = 0.0 + offset
            max_pos = 1.0

        return min_pos, max_pos

    @staticmethod
    def evenly_spaced_colors(
        colormap: str,
        num: int,
        format: Literal["QColor", "HEX", "RGB"] = "QColor",
        theme_offset=0.2,
        theme: Literal["light", "dark"] | None = None,
    ) -> list:
        """
        Extract `num` colors from the specified colormap, evenly spaced along its range,
        and return them in the specified format.

        Args:
            colormap (str): Name of the colormap.
            num (int): Number of requested colors.
            format (Literal["QColor","HEX","RGB"]): The format of the returned colors ('RGB', 'HEX', 'QColor').
            theme_offset (float): Has to be between 0-1. Offset to avoid colors too close to white or black with light or dark theme respectively for pyqtgraph plot background.
            theme (Literal['light', 'dark'] | None): The theme to be applied. Overrides the QApplication theme if specified.

        Returns:
            list: List of colors in the specified format.

        Raises:
            ValueError: If theme_offset is not between 0 and 1.
        """
        if theme_offset < 0 or theme_offset > 1:
            raise ValueError("theme_offset must be between 0 and 1")

        cmap = pg.colormap.get(colormap)
        min_pos, max_pos = Colors.set_theme_offset(theme, theme_offset)

        # Generate positions that are evenly spaced within the acceptable range
        if num == 1:
            positions = np.array([(min_pos + max_pos) / 2])
        else:
            positions = np.linspace(min_pos, max_pos, num)

        # Sample colors from the colormap at the calculated positions
        colors = cmap.map(positions, mode="float")
        color_list = []

        for color in colors:
            if format.upper() == "HEX":
                color_list.append(QColor.fromRgbF(*color).name())
            elif format.upper() == "RGB":
                color_list.append(tuple((np.array(color) * 255).astype(int)))
            elif format.upper() == "QCOLOR":
                color_list.append(QColor.fromRgbF(*color))
            else:
                raise ValueError("Unsupported format. Please choose 'RGB', 'HEX', or 'QColor'.")
        return color_list

    @staticmethod
    def golden_angle_color(
        colormap: str,
        num: int,
        format: Literal["QColor", "HEX", "RGB"] = "QColor",
        theme_offset=0.2,
        theme: Literal["dark", "light"] | None = None,
    ) -> list:
        """
        Extract num colors from the specified colormap following golden angle distribution and return them in the specified format.

        Args:
            colormap (str): Name of the colormap.
            num (int): Number of requested colors.
            format (Literal["QColor","HEX","RGB"]): The format of the returned colors ('RGB', 'HEX', 'QColor').
            theme_offset (float): Has to be between 0-1. Offset to avoid colors too close to white or black with light or dark theme respectively for pyqtgraph plot background.

        Returns:
            list: List of colors in the specified format.

        Raises:
            ValueError: If theme_offset is not between 0 and 1.
        """

        cmap = pg.colormap.get(colormap)
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        golden_angle_conjugate = 1 - (1 / phi)  # Approximately 0.38196601125

        min_pos, max_pos = Colors.set_theme_offset(theme, theme_offset)

        # Generate positions within the acceptable range
        positions = np.mod(np.arange(num) * golden_angle_conjugate, 1)
        positions = min_pos + positions * (max_pos - min_pos)

        # Sample colors from the colormap at the calculated positions
        colors = cmap.map(positions, mode="float")
        color_list = []

        for color in colors:
            if format.upper() == "HEX":
                color_list.append(QColor.fromRgbF(*color).name())
            elif format.upper() == "RGB":
                color_list.append(tuple((np.array(color) * 255).astype(int)))
            elif format.upper() == "QCOLOR":
                color_list.append(QColor.fromRgbF(*color))
            else:
                raise ValueError("Unsupported format. Please choose 'RGB', 'HEX', or 'QColor'.")
        return color_list

    @staticmethod
    def hex_to_rgba(hex_color: str, alpha=255) -> tuple:
        """
        Convert HEX color to RGBA.

        Args:
            hex_color(str): HEX color string.
            alpha(int): Alpha value (0-255). Default is 255 (opaque).

        Returns:
            tuple: RGBA color tuple (r, g, b, a).
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 6:
            r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
        elif len(hex_color) == 8:
            r, g, b, a = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4, 6))
            return (r, g, b, a)
        else:
            raise ValueError("HEX color must be 6 or 8 characters long.")
        return (r, g, b, alpha)

    @staticmethod
    def rgba_to_hex(r: int, g: int, b: int, a: int = 255) -> str:
        """
        Convert RGBA color to HEX.

        Args:
            r(int): Red value (0-255).
            g(int): Green value (0-255).
            b(int): Blue value (0-255).
            a(int): Alpha value (0-255). Default is 255 (opaque).

        Returns:
            hec_color(str): HEX color string.
        """
        return "#{:02X}{:02X}{:02X}{:02X}".format(r, g, b, a)

    @staticmethod
    def validate_color(color: tuple | str) -> tuple | str:
        """
        Validate the color input if it is HEX or RGBA compatible. Can be used in any pydantic model as a field validator.

        Args:
            color(tuple|str): The color to be validated. Can be a tuple of RGBA values or a HEX string.

        Returns:
            tuple|str: The validated color.
        """
        CSS_COLOR_NAMES = {
            "aliceblue",
            "antiquewhite",
            "aqua",
            "aquamarine",
            "azure",
            "beige",
            "bisque",
            "black",
            "blanchedalmond",
            "blue",
            "blueviolet",
            "brown",
            "burlywood",
            "cadetblue",
            "chartreuse",
            "chocolate",
            "coral",
            "cornflowerblue",
            "cornsilk",
            "crimson",
            "cyan",
            "darkblue",
            "darkcyan",
            "darkgoldenrod",
            "darkgray",
            "darkgreen",
            "darkgrey",
            "darkkhaki",
            "darkmagenta",
            "darkolivegreen",
            "darkorange",
            "darkorchid",
            "darkred",
            "darksalmon",
            "darkseagreen",
            "darkslateblue",
            "darkslategray",
            "darkslategrey",
            "darkturquoise",
            "darkviolet",
            "deeppink",
            "deepskyblue",
            "dimgray",
            "dimgrey",
            "dodgerblue",
            "firebrick",
            "floralwhite",
            "forestgreen",
            "fuchsia",
            "gainsboro",
            "ghostwhite",
            "gold",
            "goldenrod",
            "gray",
            "green",
            "greenyellow",
            "grey",
            "honeydew",
            "hotpink",
            "indianred",
            "indigo",
            "ivory",
            "khaki",
            "lavender",
            "lavenderblush",
            "lawngreen",
            "lemonchiffon",
            "lightblue",
            "lightcoral",
            "lightcyan",
            "lightgoldenrodyellow",
            "lightgray",
            "lightgreen",
            "lightgrey",
            "lightpink",
            "lightsalmon",
            "lightseagreen",
            "lightskyblue",
            "lightslategray",
            "lightslategrey",
            "lightsteelblue",
            "lightyellow",
            "lime",
            "limegreen",
            "linen",
            "magenta",
            "maroon",
            "mediumaquamarine",
            "mediumblue",
            "mediumorchid",
            "mediumpurple",
            "mediumseagreen",
            "mediumslateblue",
            "mediumspringgreen",
            "mediumturquoise",
            "mediumvioletred",
            "midnightblue",
            "mintcream",
            "mistyrose",
            "moccasin",
            "navajowhite",
            "navy",
            "oldlace",
            "olive",
            "olivedrab",
            "orange",
            "orangered",
            "orchid",
            "palegoldenrod",
            "palegreen",
            "paleturquoise",
            "palevioletred",
            "papayawhip",
            "peachpuff",
            "peru",
            "pink",
            "plum",
            "powderblue",
            "purple",
            "red",
            "rosybrown",
            "royalblue",
            "saddlebrown",
            "salmon",
            "sandybrown",
            "seagreen",
            "seashell",
            "sienna",
            "silver",
            "skyblue",
            "slateblue",
            "slategray",
            "slategrey",
            "snow",
            "springgreen",
            "steelblue",
            "tan",
            "teal",
            "thistle",
            "tomato",
            "turquoise",
            "violet",
            "wheat",
            "white",
            "whitesmoke",
            "yellow",
            "yellowgreen",
        }
        if isinstance(color, str):
            hex_pattern = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")
            if hex_pattern.match(color):
                return color
            elif color.lower() in CSS_COLOR_NAMES:
                return color
            else:
                raise PydanticCustomError(
                    "unsupported color",
                    "The color must be a valid HEX string or CSS Color.",
                    {"wrong_value": color},
                )
        elif isinstance(color, tuple):
            if len(color) != 4:
                raise PydanticCustomError(
                    "unsupported color",
                    "The color must be a tuple of 4 elements (R, G, B, A).",
                    {"wrong_value": color},
                )
            for value in color:
                if not 0 <= value <= 255:
                    raise PydanticCustomError(
                        "unsupported color",
                        f"The color values must be between 0 and 255 in RGBA format (R,G,B,A)",
                        {"wrong_value": color},
                    )
            return color

    @staticmethod
    def validate_color_map(color_map: str, return_error: bool = True) -> str | bool:
        """
        Validate the colormap input if it is supported by pyqtgraph. Can be used in any pydantic model as a field validator. If validation fails it prints all available colormaps from pyqtgraph instance.

        Args:
            color_map(str): The colormap to be validated.

        Returns:
            str: The validated colormap, if colormap is valid.
            bool: False, if colormap is invalid.

        Raises:
            PydanticCustomError: If colormap is invalid.
        """
        available_pg_maps = pg.colormap.listMaps()
        available_mpl_maps = pg.colormap.listMaps("matplotlib")
        available_mpl_colorcet = pg.colormap.listMaps("colorcet")

        available_colormaps = available_pg_maps + available_mpl_maps + available_mpl_colorcet
        if color_map not in available_colormaps:
            if return_error:
                raise PydanticCustomError(
                    "unsupported colormap",
                    f"Colormap '{color_map}' not found in the current installation of pyqtgraph. Choose on the following: {available_colormaps}.",
                    {"wrong_value": color_map},
                )
            else:
                return False
        return color_map
