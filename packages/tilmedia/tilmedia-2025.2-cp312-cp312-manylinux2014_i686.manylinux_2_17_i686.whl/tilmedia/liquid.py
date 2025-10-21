import logging
from copy import deepcopy
from threading import Lock
from typing import List, Optional, Union

import numpy as np

from . import _internals as internals
from .batchcaller import BatchFunctionCaller
from .core import (
    ExternalObject,
    Liquid_isValid_getInfo_errorInterface,
    Liquid_maximalTemperature_xi_,
    Liquid_minimalTemperature_xi_,
    getLiquidInformation_pointer,
)
from .datacontainer import DataContainer, InfoContainer
from .exceptions import (
    TILMediaErrorIncompatibleVectorLength,
    TILMediaErrorInconsistentLoggers,
    TILMediaErrorInvalidMedium,
    TILMediaErrorInvalidParameter,
    TILMediaErrorReuseOfSession,
)
from .general import TILMediaSession

_liq_lock = Lock()

_fullProperties = [
    ("d", np.float64, None, None),
    ("h", np.float64, None, None),
    ("p", np.float64, None, None),
    ("s", np.float64, None, None),
    ("T", np.float64, None, None),
    ("xi", np.float64, -1, None),
    ("cp", np.float64, None, None),
    ("beta", np.float64, None, None),
    ("Pr", np.float64, None, None),
    ("lamb", np.float64, None, None),
    ("eta", np.float64, None, None),
    ("sigma", np.float64, None, None),
    ("current_T_min", np.float64, None, None),
    ("current_T_max", np.float64, None, None),
]


class LiquidInformation(InfoContainer):
    """
    Meta Information about a Liquid.
    """

    _allowed = [
        "MediumName",
        "LibraryName",
        "LibraryLiteratureReference",
        "Description",
        "LiteratureReference",
        "T_min",
        "T_max",
        "T_data_min",
        "T_data_max",
        "xi_min",
        "xi_max",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.MediumName: Optional[str] = None
        "Name of the medium"
        self.LibraryName: Optional[str] = None
        "Name of the medium library"
        self.LibraryLiteratureReference: Optional[str] = None
        "Literature reference of the medium library"
        self.Description: Optional[str] = None
        "Medium description"
        self.LiteratureReference: Optional[str] = None
        "Literature reference of the medium data"
        self.T_min: Optional[float] = None
        "Minimum usable temperature"
        self.T_max: Optional[float] = None
        "Maximum usable temperature"
        self.T_data_min: Optional[float] = None
        "Minimum temperature of the original reference"
        self.T_data_max: Optional[float] = None
        "Maximum temperature of the original reference"
        self.xi_min: Optional[float] = None
        "Minimum usable composition"
        self.xi_max: Optional[float] = None
        "Maximum usable composition"

    def __repr__(self):
        return "TILMedia.Liquid.Info " + self.LibraryName + " " + self.MediumName

    def __str__(self):
        data = dict(self)
        units = {"T_min": " K", "T_max": " K", "T_data_min": " K", "T_data_max": " K"}
        return "\n".join([key + ": " + str(value) + units.get(key, "") for key, value in data.items()])


class Liquid(DataContainer):
    """
    This Liquid class can calculate the thermopyhsical properties of a pure or mixture of incompressible liquids.

    The following combinations of inputs can be used to calculate properties by calling a set function:

    1. xi: mass fraction (:attr:`set_xi`)
    2. h, xi: specific enthalpy and mass fraction (:attr:`set_hxi`)
    3. T, xi: temperature and mass fraction (:attr:`set_Txi`)
    4. p, h, xi: pressure, specific enthalpy and mass fraction (:attr:`set_phxi`)
    5. p, T, xi: pressure, temperature and mass fraction (:attr:`set_pTxi`)

    Args:
        liquid_name (str): complete name of the liquid
        xi (list or numpy.ndarray, optional): mass faction vector. Always one less than the number of components in mixtures. Defaults to None.
        fixed_mixing_ratio (bool, optional): if true, the mixture is treated as pure component in this interface. Defaults to False.
        compute_transport_properties (bool, optional): if true, transport properties are calculated. Defaults to True.
        instance_name (str, optional): instance name, appears in error messages. Defaults to "Liquid_Python".
        logger (logging.Logger, optional): logger instance for log and error messages of this class instance. If not set, the global setting will be used. Defaults to None.
        session (TILMediaSession, optional): The session can be used to get log messages during instantiation. If not set, a new will be instantiated. Defaults to None.

    Example:
        >>> import tilmedia
        >>> liquid = tilmedia.Liquid('TILMedia.Water')
        >>> liquid.set_Txi(300)
        >>> print(round(liquid.d, 6))
        996.425346
        >>> liquid.set_pTxi(1e5, 300)
        >>> print(round(liquid.s, 6))
        394.977757
        >>> liquid.set(p=liquid.p, T=300)
        >>> print(round(liquid.s, 6))
        394.977757
        >>> liquid.set_Txi([300, 310, 320])
        >>> print(liquid.cp.round(6))
        [4180.308149 4177.312533 4177.805418]

    """

    # static function call list
    _batch_function_calls = {
        1: [
            ("TILMedia_Liquid_minimalTemperature_xi_", lambda self: (self, ["xi"], None, ["current_T_min"])),
            ("TILMedia_Liquid_maximalTemperature_xi_", lambda self: (self, ["xi"], None, ["current_T_max"])),
        ],
        2: [
            ("TILMedia_Liquid_minimalTemperature_xi_", lambda self: (self, ["xi"], None, ["current_T_min"])),
            ("TILMedia_Liquid_maximalTemperature_xi_", lambda self: (self, ["xi"], None, ["current_T_max"])),
        ],
        3: [
            ("TILMedia_Liquid_minimalTemperature_xi_", lambda self: (self, ["xi"], None, ["current_T_min"])),
            ("TILMedia_Liquid_maximalTemperature_xi_", lambda self: (self, ["xi"], None, ["current_T_max"])),
            ("TILMedia_Liquid_specificEntropy_pTxi", lambda self: (self, ["p", "T", "xi"], None, ["s"])),
        ],
    }
    _Info = LiquidInformation

    _status = 0
    _property_list = []

    def __init__(
        self,
        liquid_name,
        xi: Optional[Union[List[float], np.ndarray]] = None,
        fixed_mixing_ratio=False,
        compute_transport_properties=True,
        instance_name="Liquid_Python",
        logger: Optional[logging.Logger] = None,
        session: Optional[TILMediaSession] = None,
    ) -> None:
        global _liq_lock
        self._property_list = _fullProperties + self._property_list
        # properties of liquidObject
        # fmt: off
        #    [[[cog
        # import cog
        # from tilmedia import Liquid
        # import numpy as np
        # from tilmedia._internals import _generate_code
        # gas = Liquid("Water")
        # v = gas._property_list
        # cog.outl("\n".join(_generate_code(v)))
        # ]]]
        self.d = np.float64(0)
        'Density [kg/m^3]'
        self.h = np.float64(0)
        'Specific enthalpy [J/kg]'
        self.p = np.float64(0)
        'Pressure [Pa]'
        self.s = np.float64(0)
        'Specific entropy [J/(kg*K)]'
        self.T = np.float64(0)
        'Temperature [K]'
        self.xi = np.zeros((1, 0), dtype=np.float64)
        'Water Mass fraction [1]'
        self.cp = np.float64(0)
        'Specific isobaric heat capacity cp [J/(kg*K)]'
        self.beta = np.float64(0)
        'Isobaric thermal expansion coefficient [1/K]'
        self.Pr = np.float64(0)
        'Prandtl number [1]'
        self.lamb = np.float64(0)
        'Thermal conductivity [W/(m*K)]'
        self.eta = np.float64(0)
        'Dynamic viscosity [Pa*s]'
        self.sigma = np.float64(0)
        'Surface tension [J/m^2]'
        self.current_T_min = np.float64(0)
        'Minimal temperature of the valid region [K]'
        self.current_T_max = np.float64(0)
        'Maximal temperature of the valid region [K]'

        self._d_vector = np.zeros(1, dtype=np.float64)
        self._h_vector = np.zeros(1, dtype=np.float64)
        self._p_vector = np.zeros(1, dtype=np.float64)
        self._s_vector = np.zeros(1, dtype=np.float64)
        self._T_vector = np.zeros(1, dtype=np.float64)
        self._xi_vector = np.zeros((1, 0), dtype=np.float64)
        self._cp_vector = np.zeros(1, dtype=np.float64)
        self._beta_vector = np.zeros(1, dtype=np.float64)
        self._Pr_vector = np.zeros(1, dtype=np.float64)
        self._lamb_vector = np.zeros(1, dtype=np.float64)
        self._eta_vector = np.zeros(1, dtype=np.float64)
        self._sigma_vector = np.zeros(1, dtype=np.float64)
        self._current_T_min_vector = np.zeros(1, dtype=np.float64)
        self._current_T_max_vector = np.zeros(1, dtype=np.float64)
        # [[[end]]]
        # fmt: on
        self._xiFixed_vector = np.zeros((1, 0), dtype=np.float64)

        self._medium: ExternalObject

        self._compute_transport_properties = compute_transport_properties

        # prepare error function pointer
        if logger is None:
            logger = internals._logger
        if session is not None:
            if session.logger is not logger:
                raise TILMediaErrorInconsistentLoggers("The logger is not the same as in the session")
            self._session = session
        else:
            self._session = TILMediaSession(logger)
        if self._session.medium_id is not None and self._session.medium_id != id(self):
            raise TILMediaErrorReuseOfSession("The session has be used with another medium instance!")
        self._session.medium_id = id(self)

        # Check if name is valid and calculate number of components
        self.fixed_mixing_ratio = fixed_mixing_ratio
        "Mixture is treated as pure component"
        self._liquid_name = liquid_name
        self._nc_internal: int = -1
        _xi_autodetect = np.zeros(20, dtype=np.float64)
        with _liq_lock as locked:
            if locked:
                self._status, self._nc_internal = Liquid_isValid_getInfo_errorInterface(
                    liquid_name + "", _xi_autodetect, True, self._session
                )
        if self._status == 0:
            raise TILMediaErrorInvalidMedium(
                'LiquidName "' + liquid_name + '" not valid. Could not create TILMedia object.'
            )
        self._xi_autodetect = np.zeros(self._nc_internal - 1)

        # forwarding information to other classes
        if fixed_mixing_ratio:
            self._nc = 1
        else:
            self._nc = self._nc_internal
        DataContainer.__init__(self, self._nc, "xi")

        # update to new nc
        self._resize_properties((1,))
        self._make_properties_scalar((1,), {None: []})

        # evaluate concentration
        if self._nc_internal > 1:
            # it is a mixture
            if fixed_mixing_ratio:
                if xi is not None:
                    _, self._xiFixed_vector = internals.var_normalize_inputs(0, xi)
                    # xi is given
                    if self._xiFixed_vector.shape[-1] != self._nc_internal - 1:
                        # but has the wrong length
                        raise TILMediaErrorIncompatibleVectorLength(
                            "length of xi vector should be {nc} but is {length}".format(
                                nc=self._nc_internal - 1, length=self._xiFixed_vector.shape[-1]
                            )
                        )
                else:
                    # xi is not given
                    if _xi_autodetect[0] < -1e200:
                        # and autodetection failed (should work for e.g. Refprop.R407c.mix)
                        raise TILMediaErrorInvalidParameter(
                            "xi vector with length {nc} expected, but none was given".format(nc=self._nc_internal - 1)
                        )
                    # and autodetection was successful
                    for i in range(self._nc_internal - 1):
                        self._xi_autodetect[i] = _xi_autodetect[i]
            else:
                # variable concentration
                if xi is None:
                    if _xi_autodetect[0] < -1e200:
                        # and autodetection failed (should work for e.g. Refprop.R407c.mix)
                        raise TILMediaErrorInvalidParameter(
                            "xi vector with length {nc} expected, but none was given".format(nc=self._nc_internal - 1)
                        )
                    # and autodetection was successful
                    for i in range(self._nc_internal - 1):
                        self._xi_autodetect[i] = _xi_autodetect[i]
                else:
                    _, self._xi_vector = internals.var_normalize_inputs(0, xi)
                    if self._xi_vector.shape[-1] != self._nc_internal - 1:
                        # but the concentration vector has the wrong length
                        raise TILMediaErrorIncompatibleVectorLength(
                            "Length of xi vector should be {nc} but is {length}".format(
                                nc=self._nc_internal - 1, length=self._xi_vector.shape[-1]
                            )
                        )
        else:
            if xi is not None:
                _, xi = internals.var_normalize_inputs(0, xi)
                internals.check_vector_size(xi, self._nc_internal - 1)
        if xi is None:
            xi = self._xi_autodetect

        # creating TILMediaObject
        flags = 0
        if self._compute_transport_properties:
            flags = 1
        if self.fixed_mixing_ratio:
            _xi_call = self._xiFixed_vector[0]
        else:
            _xi_call = self._xi_vector[0]
        with _liq_lock as locked:
            if locked:
                self._medium = ExternalObject(
                    "Liquid", liquid_name, flags, _xi_call, self._nc, -1, instance_name, self._session
                )
        if not hasattr(self, "_medium"):
            if self._session.exceptions:
                exceptions = deepcopy(self._session.exceptions)
                while self._session.exceptions:
                    self._session.exceptions.pop()
                raise exceptions[0]
            else:
                raise TILMediaErrorInvalidMedium(
                    'LiquidName "' + liquid_name + '" not valid. Could not create TILMedia object.'
                )
        self.xi = self._xi_vector[0]

        # initializing Info
        self.info = self._Info()
        "Medium meta information"
        getLiquidInformation_pointer(self.info, self._medium)

        if self._nc == 1:
            self.current_T_min = Liquid_minimalTemperature_xi_(self.xi, self._medium)
            self.current_T_max = Liquid_maximalTemperature_xi_(self.xi, self._medium)

        if self._session.exceptions:
            exceptions = deepcopy(self._session.exceptions)
            while self._session.exceptions:
                self._session.exceptions.pop()
            raise exceptions[0]

    def __del__(self):
        if hasattr(self, "_session"):
            session_id = self._session.identifier.value
            logger = self._session.logger

        if self._status != 0:
            logger.debug("Decoupling external object from liquid instance (session = %s)", session_id)
            self._medium = None
            logger.debug("Decoupled external object from liquid instance (session = %s)", session_id)

        if hasattr(self, "_session"):
            logger.debug("Decoupling session from liquid instance (session = %s)", session_id)
            self._session = None
            logger.debug("Decoupling session from liquid instance (session = %s)", session_id)

    def dump(self):
        """Prints the current thermophysical properties of the liquid to stdout."""

        s = "---------------------------------"
        s += str(self)
        s += "---------------------------------"
        print(s)

    def __str__(self):
        value = []
        value += ["Medium: " + self._liquid_name]
        value += [DataContainer.__str__(self)]
        return "\n".join([v for v in value if v])

    def __repr__(self):
        return 'TILMedia.Liquid "' + self._liquid_name + '" (nc = ' + str(self._nc) + ")"

    def set_xi(self, xi: Optional[Union[List[float], np.ndarray]] = None) -> None:
        """
        Calculates all thermophysical properties depending on the concentration.

        Args:
            xi (list, numpy.ndarray): mass fraction [1]
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        (xi,) = internals.var_normalize_inputs(xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = xi.shape[:-1]
        self._resize_properties(shape)
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        for function_name, arguments in self._batch_function_calls[1]:
            batch_caller.add_call(function_name, *arguments(self))

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))
        self._s_vector[:] = 0

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: xi=%s." % (str(failure_index), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message + "\nThe inputs were xi=%s." % (str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_Txi(
        self, T: Union[float, np.ndarray, List[float]], xi: Optional[Union[List[float], np.ndarray]] = None
    ) -> None:
        """
        Calculates all thermophysical properties depending on temperature and independent mass fractions (always one less than the number of components in mixtures).
        Pressure and specific entropy are set to 0.

        Args:
            T (float, list, numpy.ndarray): temperature [K]
            xi (list, numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        T, xi = internals.var_normalize_inputs(T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = T.shape
        self._resize_properties(shape)
        self._p_vector[:] = 0
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_Liquid_properties_Txi", self, ["T", "xi"], None, ["d", "cp", "beta"])
        batch_caller.add_call("TILMedia_LiquidObjectFunctions_specificEnthalpy_Txi", self, ["T", "xi"], None, ["h"])
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Liquid_transportProperties_Txi", self, ["T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        for function_name, arguments in self._batch_function_calls[2]:
            batch_caller.add_call(function_name, *arguments(self))

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))
        self._s_vector[:] = 0

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: T=%s, xi=%s."
                    % (str(failure_index), str(T[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were T=%s, xi=%s." % (str(T[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_hxi(
        self, h: Union[float, np.ndarray, List[float]], xi: Optional[Union[List[float], np.ndarray]] = None
    ) -> None:
        """
        Calculates all thermophysical properties depending on specific enthalpy and independent mass fractions (always one less than the number of components in mixtures).
        Pressure and specific entropy are set to 0.

        Args:
            h (float, list, numpy.ndarray): specific entphalpy [J/kg]
            xi (list, numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        h, xi = internals.var_normalize_inputs(h, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = h.shape
        self._resize_properties(shape)
        self._p_vector[:] = 0
        self._h_vector[:] = h
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_Liquid_properties_hxi", self, ["h", "xi"], None, ["d", "cp", "beta"])
        batch_caller.add_call("TILMedia_LiquidObjectFunctions_temperature_hxi", self, ["h", "xi"], None, ["T"])
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Liquid_transportProperties_Txi", self, ["T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        for function_name, arguments in self._batch_function_calls[2]:
            batch_caller.add_call(function_name, *arguments(self))

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))
        self._s_vector[:] = 0

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: h=%s, xi=%s."
                    % (str(failure_index), str(h[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were h=%s, xi=%s." % (str(h[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_pTxi(
        self,
        p: Union[float, np.ndarray, List[float]],
        T: Union[float, np.ndarray, List[float]],
        xi: Optional[Union[List[float], np.ndarray]] = None,
    ):
        """
        Calculates all thermophysical properties depending on pressure, temperature and independent mass fractions
        (always one less than the number of components in mixtures).

        Args:
            p (float, list, numpy.ndarray): pressure [Pa]
            T (float, list, numpy.ndarray): temperature [K]
            xi (list, numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, T, xi = internals.var_normalize_inputs(p, T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_Liquid_properties_Txi", self, ["T", "xi"], None, ["d", "cp", "beta"])
        batch_caller.add_call("TILMedia_LiquidObjectFunctions_specificEnthalpy_Txi", self, ["T", "xi"], None, ["h"])
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Liquid_transportProperties_Txi", self, ["T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, T=%s, xi=%s."
                    % (str(failure_index), str(p[failure_index]), str(T[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, T=%s, xi=%s."
                    % (str(p[failure_index]), str(T[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_phxi(
        self,
        p: Union[float, np.ndarray, List[float]],
        h: Union[float, np.ndarray, List[float]],
        xi: Optional[Union[List[float], np.ndarray]] = None,
    ):
        """
        Calculates all thermophysical properties depending on pressure, specific enthalpy and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            p (float, list, numpy.ndarray): pressure [Pa]
            h (float, list, numpy.ndarray): specific entphalpy [J/kg]
            xi (list, numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, h, xi = internals.var_normalize_inputs(p, h, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._h_vector[:] = h
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_Liquid_properties_hxi", self, ["h", "xi"], None, ["d", "cp", "beta"])
        batch_caller.add_call("TILMedia_LiquidObjectFunctions_temperature_hxi", self, ["h", "xi"], None, ["T"])
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Liquid_transportProperties_Txi", self, ["T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, h=%s, xi=%s."
                    % (str(failure_index), str(p[failure_index]), str(h[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, h=%s, xi=%s."
                    % (str(p[failure_index]), str(h[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set(self, **kwargs):
        keys = frozenset(kwargs)
        mapping = {
            frozenset({"p", "h"}): self.set_phxi,
            frozenset({"p", "h", "xi"}): self.set_phxi,
            frozenset({"p", "T"}): self.set_pTxi,
            frozenset({"p", "T", "xi"}): self.set_pTxi,
            frozenset({"h"}): self.set_hxi,
            frozenset({"h", "xi"}): self.set_hxi,
            frozenset({"T"}): self.set_Txi,
            frozenset({"T", "xi"}): self.set_Txi,
            frozenset({"xi"}): self.set_xi,
        }
        function = mapping.get(keys)
        if function:
            function(**kwargs)
        else:
            raise TILMediaErrorInvalidParameter(
                f"Properties cannot be computed from the arguments {set(keys)}, only {[set(v) for v in mapping]} are available."
            )
