from typing import Protocol, overload, runtime_checkable


@runtime_checkable
class ControlInstrument(Protocol):
    """Protocol for control instruments."""

    def set_voltage(self, channel_name: str, voltage: float) -> None:
        """Set the voltage on a specific channel."""
        ...

    def get_voltage(self, channel_name: str) -> float:
        """Get the voltage on a specific channel."""
        ...

    def get_slew_rate(self, channel_name: str) -> float:
        """Get the slew rate on a specific channel."""
        ...


@runtime_checkable
class MeasurementInstrument(Protocol):
    """Protocol for measurement instruments."""

    @overload
    def measure(self, channel_name: str) -> float:
        """Measure the current on a specific channel."""
        ...

    @overload
    def measure(self, channel_name: list[str]) -> list[float]:
        """Optional overload for measuring the current on multiple channels."""
        ...

    def measure(self, channel_name: str | list[str]) -> float | list[float]:
        """Measure the current on a specific channel(s)."""
        ...


class NamedResource(Protocol):
    """Protocol for resources that have a name attribute."""

    name: str
