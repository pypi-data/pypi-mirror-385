"""
Description
===========

Module: ``geocompy.geo.ctl``

Definitions for the GeoCOM Control task subsystem.

Types
-----

- ``GeoComCTL``

"""
from __future__ import annotations

from .gctypes import (
    GeoComSubsystem,
    GeoComResponse
)


class GeoComCTL(GeoComSubsystem):
    """
    Control task subsystem of the GeoCOM protocol.

    .. versionremoved:: GeoCOM-TPS1200
    """

    def get_wakeup_counter(self) -> GeoComResponse[tuple[int, int]]:
        """
        RPC 12003, ``CTL_GetUpCounter``

        Retrieves how many times has the instrument been switched on, or
        awakened from sleep mode.

        Returns
        -------
        GeoComResponse
            Params:
                - `int`: Switch on count.
                - `int`: Wake up count.

        Note
        ----
        The counters are reset to zero, once the command is executed.

        See Also
        --------
        com.switch_off
        """
        return self._request(
            12003,
            parsers=(
                int,
                int
            )
        )
