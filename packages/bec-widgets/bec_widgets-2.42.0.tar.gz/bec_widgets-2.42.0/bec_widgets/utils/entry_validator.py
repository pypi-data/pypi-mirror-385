class EntryValidator:
    def __init__(self, devices):
        self.devices = devices

    def validate_signal(self, name: str, entry: str = None) -> str:
        """
        Validate a signal entry for a given device. If the entry is not provided, the first signal entry will be used from the device hints.

        Args:
            name(str): Device name
            entry(str): Signal entry

        Returns:
            str: Signal entry
        """
        if name not in self.devices:
            raise ValueError(f"Device '{name}' not found in current BEC session")

        device = self.devices[name]

        # Build list of available signal entries from device._info['signals']
        signals_dict = getattr(device, "_info", {}).get("signals", {})
        available_entries = [
            sig.get("obj_name") for sig in signals_dict.values() if sig.get("obj_name")
        ]

        # If no signals are found, means device is a signal, use the device name as the entry
        if not available_entries:
            available_entries = [name]

        # edge case for if name is passed instead of full_name, should not happen
        if entry in signals_dict:
            entry = signals_dict[entry].get("obj_name", entry)

        if entry is None or entry == "":
            entry = next(iter(device._hints), name) if hasattr(device, "_hints") else name
        if entry not in available_entries:
            raise ValueError(
                f"Entry '{entry}' not found in device '{name}' signals. "
                f"Available signals: '{available_entries}'"
            )

        return entry

    def validate_monitor(self, monitor: str) -> str:
        """
        Validate a monitor entry for a given device.

        Args:
            monitor(str): Monitor entry

        Returns:
            str: Monitor entry
        """
        if monitor not in self.devices:
            raise ValueError(f"Device '{monitor}' not found in current BEC session")

        return monitor
