from bec_lib.callback_handler import EventType
from bec_lib.device import Signal
from bec_lib.logger import bec_logger
from qtpy.QtCore import Property

from bec_widgets.utils import ConnectionConfig
from bec_widgets.utils.bec_widget import BECWidget
from bec_widgets.utils.error_popups import SafeSlot
from bec_widgets.utils.filter_io import FilterIO, LineEditFilterHandler
from bec_widgets.utils.ophyd_kind_util import Kind
from bec_widgets.utils.widget_io import WidgetIO

logger = bec_logger.logger


class DeviceSignalInputBaseConfig(ConnectionConfig):
    """Configuration class for DeviceSignalInputBase."""

    signal_filter: str | list[str] | None = None
    default: str | None = None
    arg_name: str | None = None
    device: str | None = None
    signals: list[str] | None = None


class DeviceSignalInputBase(BECWidget):
    """
    Mixin base class for device signal input widgets.
    Mixin class for device signal input widgets. This class provides methods to get the device signal list and device
    signal object based on the current text of the widget.
    """

    RPC = False
    _filter_handler = {
        Kind.hinted: "include_hinted_signals",
        Kind.normal: "include_normal_signals",
        Kind.config: "include_config_signals",
    }

    def __init__(
        self,
        client=None,
        config: DeviceSignalInputBaseConfig | dict | None = None,
        gui_id: str = None,
        **kwargs,
    ):

        self.config = self._process_config_input(config)
        super().__init__(client=client, config=self.config, gui_id=gui_id, **kwargs)

        self._device = None
        self.get_bec_shortcuts()
        self._signal_filter = set()
        self._signals = []
        self._hinted_signals = []
        self._normal_signals = []
        self._config_signals = []
        self._device_update_register = self.bec_dispatcher.client.callbacks.register(
            EventType.DEVICE_UPDATE, self.update_signals_from_filters
        )

    ### Qt Slots ###

    @SafeSlot(str)
    def set_signal(self, signal: str):
        """
        Set the signal.

        Args:
            signal (str): signal name.
        """
        if self.validate_signal(signal):
            WidgetIO.set_value(widget=self, value=signal)
            self.config.default = signal
        else:
            logger.warning(
                f"Signal {signal} not found for device {self.device} and filtered selection {self.signal_filter}."
            )

    @SafeSlot(str)
    def set_device(self, device: str | None):
        """
        Set the device. If device is not valid, device will be set to None which happens

        Args:
            device(str): device name.
        """
        if self.validate_device(device) is False:
            self._device = None
        else:
            self._device = device
        self.update_signals_from_filters()

    @SafeSlot(dict, dict)
    @SafeSlot()
    def update_signals_from_filters(
        self, content: dict | None = None, metadata: dict | None = None
    ):
        """Update the filters for the device signals based on list in self.signal_filter.
        In addition, store the hinted, normal and config signals in separate lists to allow
        customisation within QLineEdit.

        Note:
        Signal and ComputedSignals have no signals. The naming convention follows the device name.
        """
        self.config.signal_filter = self.signal_filter
        # pylint: disable=protected-access
        if not self.validate_device(self._device):
            self._device = None
            self.config.device = self._device
            self._signals = []
            self._hinted_signals = []
            self._normal_signals = []
            self._config_signals = []
            FilterIO.set_selection(widget=self, selection=self._signals)
            return
        device = self.get_device_object(self._device)
        device_info = device._info.get("signals", {})

        # See above convention for Signals and ComputedSignals
        if isinstance(device, Signal):
            self._signals = [(self._device, {})]
            self._hinted_signals = [(self._device, {})]
            self._normal_signals = []
            self._config_signals = []
            FilterIO.set_selection(widget=self, selection=self._signals)
            return

        def _update(kind: Kind):
            return FilterIO.update_with_kind(
                widget=self,
                kind=kind,
                signal_filter=self.signal_filter,
                device_info=device_info,
                device_name=self._device,
            )

        self._hinted_signals = _update(Kind.hinted)
        self._normal_signals = _update(Kind.normal)
        self._config_signals = _update(Kind.config)

        self._signals = self._hinted_signals + self._normal_signals + self._config_signals
        FilterIO.set_selection(widget=self, selection=self.signals)

    ### Qt Properties ###

    @Property(str)
    def device(self) -> str:
        """Get the selected device."""
        if self._device is None:
            return ""
        return self._device

    @device.setter
    def device(self, value: str):
        """Set the device and update the filters, only allow devices present in the devicemanager."""
        self._device = value
        self.config.device = value
        self.update_signals_from_filters()

    @Property(bool)
    def include_hinted_signals(self):
        """Include hinted signals in filters."""
        return Kind.hinted in self.signal_filter

    @include_hinted_signals.setter
    def include_hinted_signals(self, value: bool):
        if value:
            self._signal_filter.add(Kind.hinted)
        else:
            self._signal_filter.discard(Kind.hinted)
        self.update_signals_from_filters()

    @Property(bool)
    def include_normal_signals(self):
        """Include normal signals in filters."""
        return Kind.normal in self.signal_filter

    @include_normal_signals.setter
    def include_normal_signals(self, value: bool):
        if value:
            self._signal_filter.add(Kind.normal)
        else:
            self._signal_filter.discard(Kind.normal)
        self.update_signals_from_filters()

    @Property(bool)
    def include_config_signals(self):
        """Include config signals in filters."""
        return Kind.config in self.signal_filter

    @include_config_signals.setter
    def include_config_signals(self, value: bool):
        if value:
            self._signal_filter.add(Kind.config)
        else:
            self._signal_filter.discard(Kind.config)
        self.update_signals_from_filters()

    ### Properties and Methods ###

    @property
    def signals(self) -> list[str]:
        """
        Get the list of device signals for the applied filters.

        Returns:
            list[str]: List of device signals.
        """
        return self._signals

    @signals.setter
    def signals(self, value: list[str]):
        self._signals = value
        self.config.signals = value
        FilterIO.set_selection(widget=self, selection=value)

    @property
    def signal_filter(self) -> list[str]:
        """Get the list of filters to apply on the device signals."""
        return self._signal_filter

    def get_available_filters(self) -> list[str]:
        """Get the available filters."""
        return [entry for entry in self._filter_handler]

    def set_filter(self, filter_selection: str | list[str]):
        """
        Set the device filter. If None, all devices are included.

        Args:
            filter_selection (str | list[str]): Device filters from BECDeviceFilter and BECReadoutPriority.
        """
        filters = None
        if isinstance(filter_selection, list):
            filters = [self._filter_handler.get(entry) for entry in filter_selection]
        if isinstance(filter_selection, str):
            filters = [self._filter_handler.get(filter_selection)]
        if filters is None:
            return
        for entry in filters:
            setattr(self, entry, True)

    def get_device_object(self, device: str) -> object | None:
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
            logger.warning(f"Device {device} not found in devicemanager.")
            return None
        return dev

    def validate_device(self, device: str | None, raise_on_false: bool = False) -> bool:
        """
        Validate the device if it is present in current BEC instance.

        Args:
            device(str): Device to validate.
        """
        if device in self.dev:
            return True
        if raise_on_false is True:
            raise ValueError(f"Device {device} not found in devicemanager.")
        return False

    def validate_signal(self, signal: str) -> bool:
        """
        Validate the signal if it is present in the device signals.

        Args:
            signal(str): Signal to validate.
        """
        for entry in self.signals:
            if isinstance(entry, tuple):
                entry = entry[0]
            if entry == signal:
                return True
        return False

    def _process_config_input(self, config: DeviceSignalInputBaseConfig | dict | None):
        if config is None:
            return DeviceSignalInputBaseConfig(widget_class=self.__class__.__name__)
        return DeviceSignalInputBaseConfig.model_validate(config)

    def cleanup(self):
        """
        Cleanup the widget.
        """
        self.bec_dispatcher.client.callbacks.remove(self._device_update_register)
        super().cleanup()
