from __future__ import annotations

from typing import Literal, Optional

import numpy as np
import pyqtgraph as pg
from bec_lib.logger import bec_logger
from pydantic import Field, ValidationError, field_validator
from qtpy.QtCore import Signal
from qtpy.QtGui import QTransform

from bec_widgets.utils import BECConnector, Colors, ConnectionConfig
from bec_widgets.widgets.plots.image.image_processor import (
    ImageProcessor,
    ImageStats,
    ProcessingConfig,
)

logger = bec_logger.logger


# noinspection PyDataclass
class ImageItemConfig(ConnectionConfig):  # TODO review config
    parent_id: str | None = Field(None, description="The parent plot of the image.")
    color_map: str | None = Field("plasma", description="The color map of the image.")
    downsample: bool | None = Field(True, description="Whether to downsample the image.")
    opacity: float | None = Field(1.0, description="The opacity of the image.")
    v_range: tuple[float | int, float | int] | None = Field(
        None, description="The range of the color bar. If None, the range is automatically set."
    )
    autorange: bool | None = Field(True, description="Whether to autorange the color bar.")
    autorange_mode: Literal["max", "mean"] = Field(
        "mean", description="Whether to use the mean of the image for autoscaling."
    )
    processing: ProcessingConfig = Field(
        default_factory=ProcessingConfig, description="The post processing of the image."
    )

    model_config: dict = {"validate_assignment": True}
    _validate_color_map = field_validator("color_map")(Colors.validate_color_map)


class ImageItem(BECConnector, pg.ImageItem):

    RPC = True
    USER_ACCESS = [
        "color_map",
        "color_map.setter",
        "v_range",
        "v_range.setter",
        "v_min",
        "v_min.setter",
        "v_max",
        "v_max.setter",
        "autorange",
        "autorange.setter",
        "autorange_mode",
        "autorange_mode.setter",
        "fft",
        "fft.setter",
        "log",
        "log.setter",
        "num_rotation_90",
        "num_rotation_90.setter",
        "transpose",
        "transpose.setter",
        "get_data",
    ]

    vRangeChangedManually = Signal(tuple)
    removed = Signal(str)

    def __init__(
        self,
        config: Optional[ImageItemConfig] = None,
        gui_id: Optional[str] = None,
        parent_image=None,  # FIXME: rename to parent
        **kwargs,
    ):
        if config is None:
            config = ImageItemConfig(widget_class=self.__class__.__name__)
            self.config = config
        else:
            self.config = config
        if parent_image is not None:
            self.set_parent(parent_image)
        else:
            self.parent_image = None
        self.image_transform = None
        super().__init__(config=config, gui_id=gui_id, **kwargs)

        self.raw_data = None
        self.buffer = []
        self.max_len = 0

        # Image processor will handle any setting of data
        self._image_processor = ImageProcessor(config=self.config.processing)

    def set_parent(self, parent: BECConnector):
        self.parent_image = parent

    def parent(self):
        return self.parent_image

    def set_data(self, data: np.ndarray, transform: QTransform | None = None):
        self.raw_data = data
        self.image_transform = transform
        self._process_image()

    ################################################################################
    # Properties
    @property
    def color_map(self) -> str:
        """Get the current color map."""
        return self.config.color_map

    @color_map.setter
    def color_map(self, value: str):
        """Set a new color map."""
        try:
            self.config.color_map = value
            self.setColorMap(value)
        except ValidationError:
            logger.error(f"Invalid colormap '{value}' provided.")

    @property
    def v_range(self) -> tuple[float, float]:
        """
        Get the color intensity range of the image.
        """
        if self.levels is not None:
            return tuple(float(x) for x in self.levels)
        return 0.0, 1.0

    @v_range.setter
    def v_range(self, vrange: tuple[float, float]):
        """
        Set the color intensity range of the image.
        """
        self.set_v_range(vrange, disable_autorange=True)

    def set_v_range(self, vrange: tuple[float, float], disable_autorange=True):
        if disable_autorange:
            self.config.autorange = False
            self.vRangeChangedManually.emit(vrange)
        self.setLevels(vrange)
        self.config.v_range = vrange

    @property
    def v_min(self) -> float:
        return self.v_range[0]

    @v_min.setter
    def v_min(self, value: float):
        self.v_range = (value, self.v_range[1])

    @property
    def v_max(self) -> float:
        return self.v_range[1]

    @v_max.setter
    def v_max(self, value: float):
        self.v_range = (self.v_range[0], value)

    ################################################################################
    # Autorange Logic

    @property
    def autorange(self) -> bool:
        return self.config.autorange

    @autorange.setter
    def autorange(self, value: bool):
        self.config.autorange = value
        if value:
            self.apply_autorange()

    @property
    def autorange_mode(self) -> str:
        return self.config.autorange_mode

    @autorange_mode.setter
    def autorange_mode(self, mode: str):
        self.config.autorange_mode = mode
        if self.autorange:
            self.apply_autorange()

    def apply_autorange(self):
        if self.raw_data is None:
            return
        data = self.image
        if data is None:
            data = self.raw_data
        stats = ImageStats.from_data(data)
        self.auto_update_vrange(stats)

    def auto_update_vrange(self, stats: ImageStats) -> None:
        """Update the v_range based on the stats of the image."""
        fumble_factor = 2
        if self.config.autorange_mode == "mean":
            vmin = max(stats.mean - fumble_factor * stats.std, 0)
            vmax = stats.mean + fumble_factor * stats.std
        elif self.config.autorange_mode == "max":
            vmin, vmax = stats.minimum, stats.maximum
        else:
            return
        self.set_v_range(vrange=(vmin, vmax), disable_autorange=False)

    ################################################################################
    # Data Processing Logic

    def _process_image(self):
        """
        Reprocess the current raw data and update the image display.
        """
        if self.raw_data is None:
            return

        if np.all(np.isnan(self.raw_data)):
            return

        autorange = self.config.autorange
        self._image_processor.set_config(self.config.processing)
        processed_data = self._image_processor.process_image(self.raw_data)
        self.setImage(processed_data, autoLevels=False)
        if self.image_transform is not None:
            self.setTransform(self.image_transform)
        self.autorange = autorange

    @property
    def fft(self) -> bool:
        """Get or set whether FFT postprocessing is enabled."""
        return self.config.processing.fft

    @fft.setter
    def fft(self, enable: bool):
        self.config.processing.fft = enable
        self._process_image()

    @property
    def log(self) -> bool:
        """Get or set whether logarithmic scaling is applied."""
        return self.config.processing.log

    @log.setter
    def log(self, enable: bool):
        self.config.processing.log = enable
        self._process_image()

    @property
    def num_rotation_90(self) -> Optional[int]:
        """Get or set the number of 90° rotations to apply."""
        return self.config.processing.num_rotation_90

    @num_rotation_90.setter
    def num_rotation_90(self, value: Optional[int]):
        self.config.processing.num_rotation_90 = value
        self._process_image()

    @property
    def transpose(self) -> bool:
        """Get or set whether the image is transposed."""
        return self.config.processing.transpose

    @transpose.setter
    def transpose(self, enable: bool):
        self.config.processing.transpose = enable
        self._process_image()

    ################################################################################
    # Export
    def get_data(self) -> np.ndarray:
        """
        Get the data of the image.
        Returns:
            np.ndarray: The data of the image.
        """
        return self.image

    def clear(self):
        super().clear()
        self.raw_data = None
        self.buffer = []
        self.max_len = 0

    def remove(self, emit: bool = True):
        self.clear()
        super().remove()
        if emit:
            self.removed.emit(self.objectName())
