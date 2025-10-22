from __future__ import annotations

import enum

from bec_lib.device import ComputedSignal, Device, Positioner, ReadoutPriority
from bec_lib.device import Signal as BECSignal
from bec_lib.logger import bec_logger
from pydantic import field_validator

from bec_widgets.utils import ConnectionConfig
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.error_popups import SafeProperty, SafeSlot
from bec_widgets.utils.filter_io import FilterIO
from bec_widgets.utils.widget_io import WidgetIO

logger = bec_logger.logger


class BECDeviceFilter(enum.Enum):
    """Filter for the device classes."""

    DEVICE = "Device"
    POSITIONER = "Positioner"
    SIGNAL = "Signal"
    COMPUTED_SIGNAL = "ComputedSignal"


class DeviceInputConfig(ConnectionConfig):
    device_filter: list[str] = []
    readout_filter: list[str] = []
    devices: list[str] = []
    default: str | None = None
    arg_name: str | None = None
    apply_filter: bool = True

    @field_validator("device_filter")
    @classmethod
    def check_device_filter(cls, v, values):
        valid_device_filters = [entry.value for entry in BECDeviceFilter]
        for filt in v:
            if filt not in valid_device_filters:
                raise ValueError(
                    f"Device filter {filt} is not a valid device filter {valid_device_filters}."
                )
        return v

    @field_validator("readout_filter")
    @classmethod
    def check_readout_filter(cls, v, values):
        valid_device_filters = [entry.value for entry in ReadoutPriority]
        for filt in v:
            if filt not in valid_device_filters:
                raise ValueError(
                    f"Device filter {filt} is not a valid device filter {valid_device_filters}."
                )
        return v


class DeviceInputBase(BECWidget):
    """
    Mixin base class for device input widgets.
    It allows to filter devices from BEC based on
    device class and readout priority.
    """

    _device_handler = {
        BECDeviceFilter.DEVICE: Device,
        BECDeviceFilter.POSITIONER: Positioner,
        BECDeviceFilter.SIGNAL: BECSignal,
        BECDeviceFilter.COMPUTED_SIGNAL: ComputedSignal,
    }

    _filter_handler = {
        BECDeviceFilter.DEVICE: "filter_to_device",
        BECDeviceFilter.POSITIONER: "filter_to_positioner",
        BECDeviceFilter.SIGNAL: "filter_to_signal",
        BECDeviceFilter.COMPUTED_SIGNAL: "filter_to_computed_signal",
        ReadoutPriority.MONITORED: "readout_monitored",
        ReadoutPriority.BASELINE: "readout_baseline",
        ReadoutPriority.ASYNC: "readout_async",
        ReadoutPriority.CONTINUOUS: "readout_continuous",
        ReadoutPriority.ON_REQUEST: "readout_on_request",
    }

    def __init__(self, parent=None, client=None, config=None, gui_id: str | None = None, **kwargs):

        if config is None:
            config = DeviceInputConfig(widget_class=self.__class__.__name__)
        else:
            if isinstance(config, dict):
                config = DeviceInputConfig(**config)
            self.config = config
        super().__init__(
            parent=parent, client=client, config=config, gui_id=gui_id, theme_update=True, **kwargs
        )
        self.get_bec_shortcuts()
        self._device_filter = []
        self._readout_filter = []
        self._devices = []

    ### QtSlots ###

    @SafeSlot(str)
    def set_device(self, device: str):
        """
        Set the device.

        Args:
            device (str): Default name.
        """
        if self.validate_device(device) is True:
            WidgetIO.set_value(widget=self, value=device)
            self.config.default = device
        else:
            logger.warning(
                f"Device {device} is not in the filtered selection of {self}: {self.devices}."
            )

    @SafeSlot()
    def update_devices_from_filters(self):
        """Update the devices based on the current filter selection
        in self.device_filter and self.readout_filter. If apply_filter is False,
        it will not apply the filters, store the filter settings and return.
        """
        current_device = WidgetIO.get_value(widget=self, as_string=True)
        self.config.device_filter = self.device_filter
        self.config.readout_filter = self.readout_filter
        if self.apply_filter is False:
            return
        all_dev = self.dev.enabled_devices
        # Filter based on device class
        devs = [dev for dev in all_dev if self._check_device_filter(dev)]
        # Filter based on readout priority
        devs = [dev for dev in devs if self._check_readout_filter(dev)]
        self.devices = [device.name for device in devs]
        if current_device != "":
            self.set_device(current_device)

    @SafeSlot(list)
    def set_available_devices(self, devices: list[str]):
        """
        Set the devices. If a device in the list is not valid, it will not be considered.

        Args:
            devices (list[str]): List of devices.
        """
        self.apply_filter = False
        self.devices = devices

    ### QtProperties ###

    @SafeProperty(
        "QStringList",
        doc="List of devices. If updated, it will disable the apply filters property.",
    )
    def devices(self) -> list[str]:
        """
        Get the list of devices for the applied filters.

        Returns:
            list[str]: List of devices.
        """
        return self._devices

    @devices.setter
    def devices(self, value: list):
        self._devices = value
        self.config.devices = value
        FilterIO.set_selection(widget=self, selection=value)

    @SafeProperty(str)
    def default(self):
        """Get the default device name. If set through this property, it will update only if the device is within the filtered selection."""
        return self.config.default

    @default.setter
    def default(self, value: str):
        if self.validate_device(value) is False:
            return
        self.config.default = value
        WidgetIO.set_value(widget=self, value=value)

    @SafeProperty(bool)
    def apply_filter(self):
        """Apply the filters on the devices."""
        return self.config.apply_filter

    @apply_filter.setter
    def apply_filter(self, value: bool):
        self.config.apply_filter = value
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def filter_to_device(self):
        """Include devices in filters."""
        return BECDeviceFilter.DEVICE in self.device_filter

    @filter_to_device.setter
    def filter_to_device(self, value: bool):
        if value is True and BECDeviceFilter.DEVICE not in self.device_filter:
            self._device_filter.append(BECDeviceFilter.DEVICE)
        if value is False and BECDeviceFilter.DEVICE in self.device_filter:
            self._device_filter.remove(BECDeviceFilter.DEVICE)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def filter_to_positioner(self):
        """Include devices of type Positioner in filters."""
        return BECDeviceFilter.POSITIONER in self.device_filter

    @filter_to_positioner.setter
    def filter_to_positioner(self, value: bool):
        if value is True and BECDeviceFilter.POSITIONER not in self.device_filter:
            self._device_filter.append(BECDeviceFilter.POSITIONER)
        if value is False and BECDeviceFilter.POSITIONER in self.device_filter:
            self._device_filter.remove(BECDeviceFilter.POSITIONER)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def filter_to_signal(self):
        """Include devices of type Signal in filters."""
        return BECDeviceFilter.SIGNAL in self.device_filter

    @filter_to_signal.setter
    def filter_to_signal(self, value: bool):
        if value is True and BECDeviceFilter.SIGNAL not in self.device_filter:
            self._device_filter.append(BECDeviceFilter.SIGNAL)
        if value is False and BECDeviceFilter.SIGNAL in self.device_filter:
            self._device_filter.remove(BECDeviceFilter.SIGNAL)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def filter_to_computed_signal(self):
        """Include devices of type ComputedSignal in filters."""
        return BECDeviceFilter.COMPUTED_SIGNAL in self.device_filter

    @filter_to_computed_signal.setter
    def filter_to_computed_signal(self, value: bool):
        if value is True and BECDeviceFilter.COMPUTED_SIGNAL not in self.device_filter:
            self._device_filter.append(BECDeviceFilter.COMPUTED_SIGNAL)
        if value is False and BECDeviceFilter.COMPUTED_SIGNAL in self.device_filter:
            self._device_filter.remove(BECDeviceFilter.COMPUTED_SIGNAL)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def readout_monitored(self):
        """Include devices with readout priority Monitored in filters."""
        return ReadoutPriority.MONITORED in self.readout_filter

    @readout_monitored.setter
    def readout_monitored(self, value: bool):
        if value is True and ReadoutPriority.MONITORED not in self.readout_filter:
            self._readout_filter.append(ReadoutPriority.MONITORED)
        if value is False and ReadoutPriority.MONITORED in self.readout_filter:
            self._readout_filter.remove(ReadoutPriority.MONITORED)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def readout_baseline(self):
        """Include devices with readout priority Baseline in filters."""
        return ReadoutPriority.BASELINE in self.readout_filter

    @readout_baseline.setter
    def readout_baseline(self, value: bool):
        if value is True and ReadoutPriority.BASELINE not in self.readout_filter:
            self._readout_filter.append(ReadoutPriority.BASELINE)
        if value is False and ReadoutPriority.BASELINE in self.readout_filter:
            self._readout_filter.remove(ReadoutPriority.BASELINE)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def readout_async(self):
        """Include devices with readout priority Async in filters."""
        return ReadoutPriority.ASYNC in self.readout_filter

    @readout_async.setter
    def readout_async(self, value: bool):
        if value is True and ReadoutPriority.ASYNC not in self.readout_filter:
            self._readout_filter.append(ReadoutPriority.ASYNC)
        if value is False and ReadoutPriority.ASYNC in self.readout_filter:
            self._readout_filter.remove(ReadoutPriority.ASYNC)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def readout_continuous(self):
        """Include devices with readout priority continuous in filters."""
        return ReadoutPriority.CONTINUOUS in self.readout_filter

    @readout_continuous.setter
    def readout_continuous(self, value: bool):
        if value is True and ReadoutPriority.CONTINUOUS not in self.readout_filter:
            self._readout_filter.append(ReadoutPriority.CONTINUOUS)
        if value is False and ReadoutPriority.CONTINUOUS in self.readout_filter:
            self._readout_filter.remove(ReadoutPriority.CONTINUOUS)
        self.update_devices_from_filters()

    @SafeProperty(bool)
    def readout_on_request(self):
        """Include devices with readout priority OnRequest in filters."""
        return ReadoutPriority.ON_REQUEST in self.readout_filter

    @readout_on_request.setter
    def readout_on_request(self, value: bool):
        if value is True and ReadoutPriority.ON_REQUEST not in self.readout_filter:
            self._readout_filter.append(ReadoutPriority.ON_REQUEST)
        if value is False and ReadoutPriority.ON_REQUEST in self.readout_filter:
            self._readout_filter.remove(ReadoutPriority.ON_REQUEST)
        self.update_devices_from_filters()

    ### Python Methods and Properties ###

    @property
    def device_filter(self) -> list[object]:
        """Get the list of filters to apply on the devices."""
        return self._device_filter

    @property
    def readout_filter(self) -> list[str]:
        """Get the list of filters to apply on the devices"""
        return self._readout_filter

    def get_available_filters(self) -> list:
        """Get the available filters."""
        return [entry for entry in BECDeviceFilter]

    def get_readout_priority_filters(self) -> list:
        """Get the available readout priority filters."""
        return [entry for entry in ReadoutPriority]

    def set_device_filter(
        self, filter_selection: str | BECDeviceFilter | list[str] | list[BECDeviceFilter]
    ):
        """
        Set the device filter. If None is passed, no filters are applied and all devices included.

        Args:
            filter_selection (str | list[str]): Device filters. It is recommended to make an enum for the filters.
        """
        filters = None
        if isinstance(filter_selection, list):
            filters = [self._filter_handler.get(entry) for entry in filter_selection]
        if isinstance(filter_selection, str) or isinstance(filter_selection, BECDeviceFilter):
            filters = [self._filter_handler.get(filter_selection)]
        if filters is None or any([entry is None for entry in filters]):
            logger.warning(f"Device filter {filter_selection} is not in the device filter list.")
            return
        for entry in filters:
            setattr(self, entry, True)

    def set_readout_priority_filter(
        self, filter_selection: str | ReadoutPriority | list[str] | list[ReadoutPriority]
    ):
        """
        Set the readout priority filter. If None is passed, all filters are included.

        Args:
            filter_selection (str | list[str]): Readout priority filters.
        """
        filters = None
        if isinstance(filter_selection, list):
            filters = [self._filter_handler.get(entry) for entry in filter_selection]
        if isinstance(filter_selection, str) or isinstance(filter_selection, ReadoutPriority):
            filters = [self._filter_handler.get(filter_selection)]
        if filters is None or any([entry is None for entry in filters]):
            logger.warning(
                f"Readout priority filter {filter_selection} is not in the readout priority list."
            )
            return
        for entry in filters:
            setattr(self, entry, True)

    def _check_device_filter(
        self, device: Device | BECSignal | ComputedSignal | Positioner
    ) -> bool:
        """Check if filter for device type is applied or not.

        Args:
            device(Device | Signal | ComputedSignal | Positioner): Device object.
        """
        return all(isinstance(device, self._device_handler[entry]) for entry in self.device_filter)

    def _check_readout_filter(
        self, device: Device | BECSignal | ComputedSignal | Positioner
    ) -> bool:
        """Check if filter for readout priority is applied or not.

        Args:
            device(Device | Signal | ComputedSignal | Positioner): Device object.
        """
        return device.readout_priority in self.readout_filter

    def get_device_object(self, device: str) -> object:
        """
        Get the device object based on the device name.

        Args:
            device(str): Device name.

        Returns:
            object: Device object, can be device of type Device, Positioner, Signal or ComputedSignal.
        """
        self.validate_device(device)
        dev = getattr(self.dev, device, None)
        if dev is None:
            raise ValueError(
                f"Device {device} is not found in the device manager {self.dev} as enabled device."
            )
        return dev

    def validate_device(self, device: str) -> bool:
        """
        Validate the device if it is present in the filtered device selection.

        Args:
            device(str): Device to validate.
        """
        all_devs = [dev.name for dev in self.dev.enabled_devices]
        if device in self.devices and device in all_devs:
            return True
        return False
