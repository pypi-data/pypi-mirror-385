"""
Description
===========

Module: ``geocompy.geo.aut``

Definitions for the GeoCOM Automation subsystem.

Types
-----

- ``GeoComAUT``

"""
from __future__ import annotations

from typing import SupportsFloat

from ..data import (
    Angle,
    get_enum,
    get_enum_parser,
    parse_bool
)
from .gcdata import (
    Adjust,
    ATR,
    Position,
    Turn,
    Camera
)
from .gctypes import (
    GeoComSubsystem,
    GeoComResponse
)


class GeoComAUT(GeoComSubsystem):
    """
    Automation subsystem of the GeoCOM protocol.

    This subsystem controls most of the motorized functions of
    a total station, such as positioning of the axes, target search,
    target lock, etc.

    """

    def get_atr_status(self) -> GeoComResponse[bool]:
        """
        RPC 9019, ``AUT_GetATRStatus``

        .. deprecated:: GeoCOM-TPS1100
            The command is still available, but should not be used with
            instruments that support the new `aus.get_user_atr_state`
            command.

        .. versionremoved:: GeoCOM-TPS1200


        Gets whether or not the ATR mode is active.

        Returns
        -------
        GeoComResponse
            Params:
                - `bool`: ATR mode is active.

            Error codes:
                - ``NOT_IMPL``: ATR is not available.

        Notes
        -----
        This command does not indicate if the ATR has acquired a prism.

        See Also
        --------
        switch_atr
        """
        return self._request(
            9019,
            parsers=parse_bool
        )

    def switch_atr(
        self,
        activate: bool
    ) -> GeoComResponse[None]:
        """
        RPC 9018, ``AUT_SetATRStatus``

        .. deprecated:: GeoCOM-TPS1100
            The command is still available, but should not be used with
            instruments that support the new `aus.switch_user_atr`
            command.

        .. versionremoved:: GeoCOM-TPS1200

        Activates or deactivates the ATR mode.

        Parameters
        ----------
        activate : bool
            Set ATR to active.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NOT_IMPL``: ATR is not available.

        Notes
        -----
        If LOCK mode is active when the ATR is activated, then LOCK mode
        changes to ATR mode.

        If the ATR is deactivated, the LOCK mode does not change.

        See Also
        --------
        get_atr_status
        get_lock_status
        switch_lock
        """
        return self._request(9018, [activate])

    def get_lock_status(self) -> GeoComResponse[bool]:
        """
        RPC 9021, ``AUT_GetLockStatus``

        .. deprecated:: GeoCOM-TPS1100
            The command is still available, but should not be used with
            instruments that support the new `aus.get_user_lock_state`
            command.

        .. versionremoved:: GeoCOM-TPS1200

        Gets whether or not the lock mode is active.

        Returns
        -------
        GeoComResponse
            Params:
                - `bool`: Lock mode is active.

            Error codes:
                - ``NOT_IMPL``: ATR is not available.

        See Also
        --------
        switch_lock
        mot.get_lockon_status
        """
        return self._request(
            9021,
            parsers=parse_bool
        )

    def switch_lock(
        self,
        activate: bool
    ) -> GeoComResponse[None]:
        """
        RPC 9020, ``AUT_SetLockStatus``

        .. deprecated:: GeoCOM-TPS1100
            The command is still available, but should not be used with
            instruments that support the new `aus.switch_user_lock`
            command.

        .. versionremoved:: GeoCOM-TPS1200

        Activates or deactivates the LOCK mode.

        Parameters
        ----------
        activate : bool
            LOCK state to set

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NOT_IMPL``: ATR is not available.

        Notes
        -----
        Activating the LOCK mode does not mean that the instrument is
        automatically locked onto a prism.

        See Also
        --------
        get_lock_status
        get_atr_status
        lock_in
        """
        return self._request(
            9020,
            [activate]
        )

    def get_tolerance(self) -> GeoComResponse[tuple[Angle, Angle]]:
        """
        RPC 9008, ``AUT_ReadTol``

        Gets the positioning tolerances on the Hz and V axes.

        Returns
        -------
        GeoComResponse
            Params:
                - `Angle`: Horizontal tolerance.
                - `Angle`: Vertical tolerance.

            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        set_tolerance
        """
        return self._request(
            9008,
            parsers=(Angle.parse, Angle.parse)
        )

    def set_tolerance(
        self,
        hz: SupportsFloat,
        v: SupportsFloat
    ) -> GeoComResponse[None]:
        """
        RPC 9007, ``AUT_SetTol``

        Sets the positioning tolerances on the Hz and V axes.

        Parameters
        ----------
        hz : SupportsFloat
            Horizontal tolerance.
        v : SupportsFloat
            Vertical tolerance.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``IVPARAM``: Tolerances are out of the valid range.
                - ``MOT_UNREADY``: Instrument has no motorization.

        See Also
        --------
        get_tolerance
        """
        return self._request(9007, [float(hz), float(v)])

    def get_timeout(self) -> GeoComResponse[tuple[float, float]]:
        """
        RPC 9012, ``AUT_ReadTimeout``

        Gets the positioning timeout for the Hz and V axes.

        Returns
        -------
        GeoComResponse
            Params:
                - `float`: Horizontal timeout [sec].
                - `float`: Vertical timeout [sec].

            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        set_timeout
        """
        return self._request(
            9012,
            parsers=(float, float)
        )

    def set_timeout(
        self,
        hz: float,
        v: float
    ) -> GeoComResponse[None]:
        """
        RPC 9011, ``AUT_SetTimeout``

        Sets the positioning timeout for the Hz and V axes.

        Parameters
        ----------
        hz : float
            Horizontal timeout [sec].
        v : float
            Vertical timeout [sec]

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``IVPARAM``: Timeout values are not in the [7; 60] range.

        See Also
        --------
        get_timeout
        """
        return self._request(
            9011,
            [hz, v]
        )

    def turn_to(
        self,
        hz: SupportsFloat,
        v: SupportsFloat,
        posmode: Position | str = Position.NORMAL,
        atrmode: ATR | str = ATR.POSITION
    ) -> GeoComResponse[None]:
        """
        RPC 9027, ``AUT_MakePositioning``

        Turns the telescope to the specified angular positions.

        Parameters
        ----------
        hz : SupportsFloat
            Horizontal position.
        v : SupportsFloat
            Vertical position.
        posmode : Position | str, optional
            Positioning precision mode, by default Position.NORMAL
        atrmode : ATR | str, optional
            ATR mode, by default ATR.POSITION

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``IVPARAM``: Invalid parameter
                - ``AUT_TIMEOUT``: Positioning timed out.
                - ``AUT_MOTOR_ERROR``: Instrument has no motorization.
                - ``AUT_ANGLE_ERROR``: Angle measurement error.
                - ``AUT_INACC``: Inexact position.
                - ``ABORT``: Function aborted.
                - ``COM_TIMEDOUT``: Communication timeout.
                - ``AUT_NO_TARGET``: No ATR target found.
                - ``AUT_MULTIPLE_TARGETS``: Multiple ATR targets found.
                - ``AUT_BAD_ENVIRONMENT``: Inadequate environmental
                  conditions.
                - ``AUT_ACCURACY``: Position is not within tolerances.
                  Repeat positioning!
                - ``AUT_DEV_ERROR``: Angle deviation calculation error.
                  Repeat positioning!
                - ``AUT_NOT_ENABLED``: ATR mode is not active.

        See Also
        --------
        get_atr_status
        switch_atr
        get_lock_status
        switch_lock
        get_tolerance
        set_tolerance
        get_timeout
        set_timeout
        com.get_timeout
        com.set_timeout
        """
        _posmode = get_enum(Position, posmode)
        _atrmode = get_enum(ATR, atrmode)
        return self._request(
            9027,
            [float(hz), float(v), _posmode, _atrmode, 0]
        )

    def change_face(
        self,
        posmode: Position | str = Position.NORMAL,
        atrmode: ATR | str = ATR.POSITION
    ) -> GeoComResponse[None]:
        """
        RPC 9028, ``AUT_ChangeFace``

        Turns the telescope to the opposite face.

        Parameters
        ----------
        posmode : Position | str, optional
            Positioning precision mode, by default Position.NORMAL
        atrmode : ATR | str, optional
            ATR mode, by default ATR.POSITION

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``IVPARAM``: Invalid parameter
                - ``AUT_TIMEOUT``: Positioning timed out.
                - ``AUT_MOTOR_ERROR``: Instrument has no motorization.
                - ``AUT_ANGLE_ERROR``: Angle measurement error.
                - ``AUT_INACC``: Inexact position.
                - ``ABORT``: Function aborted.
                - ``COM_TIMEDOUT``: Communication timeout.
                - ``AUT_NO_TARGET``: No ATR target found.
                - ``AUT_MULTIPLE_TARGETS``: Multiple ATR targets found.
                - ``AUT_BAD_ENVIRONMENT``: Inadequate environmental
                  conditions.
                - ``AUT_ACCURACY``: Position is not within tolerances.
                  Repeat positioning!
                - ``AUT_DEV_ERROR``: Angle deviation calculation error.
                  Repeat positioning!
                - ``AUT_NOT_ENABLED``: ATR mode is not active.

        See Also
        --------
        get_atr_status
        switch_atr
        get_lock_status
        switch_lock
        get_tolerance
        set_tolerance
        get_timeout
        set_timeout
        com.get_timeout
        com.set_timeout
        tmc.get_face
        """
        _posmode = get_enum(Position, posmode)
        _atrmode = get_enum(ATR, atrmode)
        return self._request(
            9028,
            [_posmode, _atrmode, 0]
        )

    def fine_adjust(
        self,
        width: SupportsFloat,
        height: SupportsFloat
    ) -> GeoComResponse[None]:
        """
        RPC 9037, ``AUT_FineAdjust``

        Precisely targets a prism. If the prism is not within the view of
        the ATR, a target search is executed in the specified window.

        Parameters
        ----------
        width : SupportsFloat
            Width of target search window.
        height : SupportsFloat
            Heigth of target search window.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``IVPARAM``: Invalid parameter
                - ``AUT_TIMEOUT``: Positioning timed out.
                - ``AUT_MOTOR_ERROR``: Instrument has no motorization.
                - ``FATAL``: Fatal error.
                - ``ABORT``: Function aborted.
                - ``COM_TIMEDOUT``: Communication timeout.
                - ``AUT_NO_TARGET``: No ATR target found.
                - ``AUT_MULTIPLE_TARGETS``: Multiple ATR targets found.
                - ``AUT_BAD_ENVIRONMENT``: Inadequate environmental
                  conditions.
                - ``AUT_DEV_ERROR``: Angle deviation calculation error.
                  Repeat positioning!
                - ``AUT_NOT_ENABLED``: ATR mode is not active.
                - ``AUT_DETECTOR_ERROR``: Error in target acquisition.

        See Also
        --------
        get_atr_status
        switch_atr
        get_fine_adjust_mode
        set_fine_adjust_mode
        """
        return self._request(
            9037,
            [float(width), float(height), 0]
        )

    def search(
        self,
        width: SupportsFloat,
        height: SupportsFloat
    ) -> GeoComResponse[None]:
        """
        RPC 9029, ``AUT_Search``

        Search for target in the specified search window. The search is
        terminated once a prism appears in the view of the ATR. Fine
        adjustment must be executed afterwards.

        Parameters
        ----------
        width : SupportsFloat
            Width of target search window.
        height : SupportsFloat
            Heigth of target search window.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``IVPARAM``: Invalid parameter
                - ``AUT_MOTOR_ERROR``: Instrument has no motorization.
                - ``TMC_NO_FULL_CORRECTION``: Instrument might not be
                  properly levelled.
                - ``FATAL``: Fatal error.
                - ``ABORT``: Function aborted.
                - ``COM_TIMEDOUT``: Communication timeout.
                - ``AUT_NO_TARGET``: No ATR target found.
                - ``AUT_BAD_ENVIRONMENT``: Inadequate environmental
                  conditions.
                - ``AUT_NOT_ENABLED``: ATR mode is not active.
                - ``AUT_DETECTOR_ERROR``: Error in target acquisition.

        See Also
        --------
        get_atr_status
        switch_atr
        fine_adjust
        """
        return self._request(
            9029,
            [float(width), float(height), 0]
        )

    def get_fine_adjust_mode(self) -> GeoComResponse[Adjust]:
        """
        RPC 9030, ``AUT_GetFineAdjustMode``

        Gets the fine adjustment mode.

        Returns
        -------
        GeoComResponse
            Params:
                - `Adjust`: Current fine adjustment mode.

        See Also
        --------
        set_fine_adjust_mode
        """
        return self._request(
            9030,
            parsers=get_enum_parser(Adjust)
        )

    def set_fine_adjust_mode(
        self,
        mode: Adjust | str
    ) -> GeoComResponse[None]:
        """
        RPC 9031, ``AUT_SetFineAdjustMode``

        Sets the fine adjustment mode.

        Parameters
        ----------
        mode : Adjust | str

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``IVPARAM``: Invalid mode

        See Also
        --------
        get_fine_adjust_mode
        """
        _mode = get_enum(Adjust, mode)
        return self._request(
            9031,
            [_mode]
        )

    def lock_in(self) -> GeoComResponse[None]:
        """
        RPC 9013, ``AUT_LockIn``

        Locks onto target prism and starts tracking. LOCK mode must be
        active, and fine adjustment must have been completed, before
        executing this command.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``AUT_NOT_ENABLED``: ATR mode is not active.
                - ``AUT_MOTOR_ERROR``: Instrument has not motorization.
                - ``AUT_DETECTOR_ERROR``: Error in target acquisition.
                - ``AUT_NO_TARGET``: No ATR target found.
                - ``AUT_BAD_ENVIRONMENT``: Inadequate environmental
                  conditions.

        See Also
        --------
        get_lock_status
        switch_lock
        mot.get_lockon_status
        """
        return self._request(9013)

    def get_search_area(
        self
    ) -> GeoComResponse[tuple[Angle, Angle, Angle, Angle, bool]]:
        """
        RPC 9042, ``AUT_GetSearchArea``

        .. versionadded:: GeoCOM-TPS1100

        Gets current position and size of the PowerSearch window.

        Returns
        -------
        GeoComResponse
            Params:
                - `Angle`: Horizontal center of window.
                - `Angle`: Vertical center of window.
                - `Angle`: Width of window.
                - `Angle`: Height of window.
                - `bool`: If window is enabled.

            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        set_search_area
        bap.search_target
        """
        return self._request(
            9042,
            parsers=(
                Angle.parse,
                Angle.parse,
                Angle.parse,
                Angle.parse,
                parse_bool
            )
        )

    def set_search_area(
        self,
        hz: SupportsFloat,
        v: SupportsFloat,
        width: SupportsFloat,
        height: SupportsFloat,
        enabled: bool = True
    ) -> GeoComResponse[None]:
        """
        RPC 9043, ``AUT_SetSearchArea``

        .. versionadded:: GeoCOM-TPS1100

        Sets position and size of the PowerSearch window.

        Parameters
        ----------
        hz : SupportsFloat
            Horizontal center of search window.
        v : SupportsFloat
            Vertical center of search window.
        width : SupportsFloat
            Width of search window.
        height : SupportsFloat
            Height of search window.
        enabled : bool
            Activation state of search window.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        get_search_area
        bap.search_target
        """
        return self._request(
            9043,
            [float(hz), float(v), float(width), float(height), enabled]
        )

    def get_spiral(self) -> GeoComResponse[tuple[Angle, Angle]]:
        """
        RPC 9040, ``AUT_GetUserSpiral``

        .. versionadded:: GeoCOM-TPS1100

        Gets the size of the PowerSearch window.

        Returns
        -------
        GeoComResponse
            Params:
                - `Angle`: Width of window.
                - `Angle`: Height of window.

            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        set_spiral
        bap.search_target
        """
        return self._request(
            9040,
            parsers=(Angle.parse, Angle.parse)
        )

    def set_spiral(
        self,
        width: SupportsFloat,
        height: SupportsFloat
    ) -> GeoComResponse[None]:
        """
        RPC 9041, ``AUT_SetUserSpiral``

        .. versionadded:: GeoCOM-TPS1100

        Sets the size of the PowerSearch window.

        Parameters
        ----------
        width : SupportsFloat
            Width of the search window.
        height : SupportsFloat
            Height of the search window.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        get_spiral
        bap.search_target
        """
        return self._request(
            9041,
            [float(width), float(height)]
        )

    def switch_powersearch_range(
        self,
        enable: bool
    ) -> GeoComResponse[None]:
        """
        RPC 9048, ``AUT_PS_EnableRange``

        Enables or disables the PowerSearch window and range limit.

        Parameters
        ----------
        enable : bool
            Enable predefined PowerSearch window and range limits.
            Defaults to [0; 400] range when disabled.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.

        See Also
        --------
        set_powersearch_range
        set_search_area
        """
        return self._request(
            9048,
            [enable]
        )

    def set_powersearch_range(
        self,
        closest: int,
        farthest: int
    ) -> GeoComResponse[None]:
        """
        RPC 9044, ``AUT_PS_SetRange``

        .. versionadded:: GeoCOM-TPS1200

        Sets the PowerSearch range limits.

        Parameters
        ----------
        closest : int
            Minimum distance to prism [0; ...].
        farthest : int
            Maxmimum distance to prism [closest + 10; 400].

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``IVPARAM``: Invalid parameters.

        See Also
        --------
        switch_powersearch_range
        powersearch_window
        set_search_area
        """
        return self._request(
            9047,
            [closest, farthest]
        )

    def powersearch_window(self) -> GeoComResponse[None]:
        """
        RPC 9052, ``AUT_PS_SearchWindow``

        .. versionadded:: GeoCOM-TPS1200

        Executes PowerSearch in the predefined search window.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``AUT_NO_WORKING_AREA``: Search window is not defined.
                - ``AUT_NO_TARGET``: Target was not found.

        See Also
        --------
        switch_powersearch_range
        set_powersearch_range
        powersearch_next
        set_search_area
        """
        return self._request(9052)

    def powersearch_next(
        self,
        direction: Turn | str,
        swing: bool
    ) -> GeoComResponse[None]:
        """
        RPC 9051, ``AUT_PS_SearchNext``

        .. versionadded:: GeoCOM-TPS1200

        Executes 360° default PowerSearch to find the next target.

        Parameters
        ----------
        direction : Turn | str
            Turning direction during PowerSearch.
        swing : bool
            Search starts -10 GON to the given turn direction.

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: GeoCOM Robotic license not found.
                - ``AUT_NO_TARGET``: Target was not found.
                - ``IVPARAM``: Invalid parameters.

        See Also
        --------
        switch_powersearch_range
        powersearch_window
        """
        _direction = get_enum(Turn, direction)
        return self._request(
            9051,
            [_direction, swing]
        )

    def switch_lock_onthefly(
        self,
        enabled: bool
    ) -> GeoComResponse[None]:
        """
        RPC 9103, ``AUT_SetLockFlyMode``

        .. versionadded:: GeoCOM-VivaTPS

        Sets the state of on-the-fly mode for the lock mode.

        Parameters
        ----------
        enabled : bool
            Enable on-the-fly lock mode.

        Returns
        -------
        GeoComResponse

        See Also
        --------
        get_lock_onthefly_status
        """
        return self._request(
            9103,
            [enabled]
        )

    def get_lock_onthefly_status(self) -> GeoComResponse[bool]:
        """
        RPC 9102, ``AUT_GetLockFlyMode``

        .. versionadded:: GeoCOM-VivaTPS

        Gets the current state of the on-the-fly lock mode.

        Returns
        -------
        GeoComResponse
            Params:
                - `bool`: On-the-fly lock mode is enabled.

        See Also
        --------
        get_lock_onthefly_status
        """
        return self._request(
            9102,
            parsers=parse_bool
        )

    def aim_at_pixel(
        self,
        x: int,
        y: int,
        camera: Camera | str = Camera.OVERVIEW
    ) -> GeoComResponse[None]:
        """
        RPC 9081, ``AUT_CAM_PositToPixelCoord``

        .. versionadded:: GeoCOM-VivaTPS

        Turns the instrument to face the coordinates specified in the
        image coordinates.

        Parameters
        ----------
        x : int
            Horizontal pixel coordinate.
        y : int
            Vertical pixel coordinate.
        camera : Camera, optional
            Camera device, by default OVERVIEW

        Returns
        -------
        GeoComResponse
            Error codes:
                - ``NA``: Imaging license not found.
                - ``AUT_SIDECOVER_ERR``: Sidecover is open.

        """
        _camera = get_enum(Camera, camera)
        return self._request(
            9081,
            [_camera, x, y]
        )
