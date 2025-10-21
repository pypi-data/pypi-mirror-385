"""Type stubs for dive_deco_py"""

from typing import List

class BuhlmannModel:
    """Buhlmann decompression model for dive planning."""

    def __init__(self) -> None:
        """Initialize a new BuhlmannModel with default configuration (GF 30/70)."""
        ...

    def record(self, depth: float, time: float, gas: Gas) -> None:
        """
        Record a dive segment at a specific depth with a gas mixture.

        Args:
            depth: Depth in meters
            time: Time duration in minutes
            gas: Gas mixture used during this segment
        """
        ...

    def ndl(self) -> float:
        """
        Calculate the No Decompression Limit (NDL) in minutes.

        Returns:
            float: The NDL time in minutes.
        """
        ...

    def deco(self, gas_mixes: List[Gas]) -> Deco:
        """
        Calculate decompression schedule for the recorded dive profile.

        Args:
            gas_mixes: List of gas mixtures available for decompression

        Returns:
            Deco: Decompression information including total time to surface
        """
        ...

    def ceiling(self) -> int:
        """
        Calculate the current ceiling depth in meters.

        Returns:
            int: Ceiling depth in meters
        """
        ...

    def supersaturation(self) -> Supersaturation:
        """
        Get current tissue supersaturation information.

        Returns:
            Supersaturation: GF99 and surface GF values
        """
        ...

    def tissues(self) -> List[Compartment]:
        """
        Get all tissue compartments with their current state.

        Returns:
            List[Compartment]: List of 16 tissue compartments
        """
        ...

class Gas:
    """Breathing gas mixture for diving."""

    def __init__(self, o2: float, he: float) -> None:
        """
        Initialize a new Gas mixture.

        Args:
            o2: Oxygen fraction (0.0 to 1.0)
            he: Helium fraction (0.0 to 1.0)
        """
        ...

    @staticmethod
    def air() -> "Gas":
        """
        Create a standard air mixture (21% O2, 79% N2).

        Returns:
            Gas: Air gas mixture.
        """
        ...

class Compartment:
    """Tissue compartment with inert gas saturation data."""

    @property
    def no(self) -> int:
        """Tissue compartment number (1-16)."""
        ...

    @property
    def he_ip(self) -> float:
        """Helium inert pressure in the compartment."""
        ...

    @property
    def n2_ip(self) -> float:
        """Nitrogen inert pressure in the compartment."""
        ...

    @property
    def total_ip(self) -> float:
        """Total inert pressure (He + N2) in the compartment."""
        ...

    @property
    def m_value_raw(self) -> float:
        """Raw M-value (original Buhlmann value)."""
        ...

    @property
    def m_value_calc(self) -> float:
        """Calculated M-value considering gradient factors."""
        ...

    @property
    def min_tolerable_amb_pressure(self) -> float:
        """Minimum tolerable ambient pressure for this compartment."""
        ...

class Deco:
    """Decompression calculation result."""

    tts: float
    """Total Time to Surface in minutes."""

    tts_at_5: float
    """Time to surface at 5m depth in minutes."""

    tts_delta_at_5: float
    """Delta time at 5m depth in minutes."""

class Supersaturation:
    """Tissue supersaturation information."""

    gf_99: float
    """Gradient factor at 99% (current supersaturation)."""

    gf_surf: float
    """Gradient factor at surface."""
