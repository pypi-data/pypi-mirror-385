import logging
from copy import deepcopy
from threading import Lock
from typing import List, Optional, Union

import numpy as np

from . import _internals as internals
from .batchcaller import BatchFunctionCaller
from .core import (
    ExternalObject,
    Gas_isValid_getInfo_errorInterface,
    Gas_molarMass,
    GasObjectFunctions_freezingPoint,
    getGasInformation_pointer,
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

_gas_lock = Lock()

# _pureComponentProperties = ['p_s', 'delta_hv', 'delta_hd', 'h_i', 'T']
# _additionalProperties = ['cp', 'beta', 'kappa', 's', 'T']
# _transportProperties = ['Pr', 'lambda', 'eta']
# _fullTransportProperties = [('Pr', np.float64, None, None), ('lamb', np.float64, None, None), ('eta', np.float64, None, None), ('sigma', np.float64, None, None)]
_fullProperties = [
    ("d", np.float64, None, None),
    ("h", np.float64, None, None),
    ("p", np.float64, None, None),
    ("s", np.float64, None, None),
    ("T", np.float64, None, None),
    ("xi", np.float64, -1, None),
    ("x", np.float64, -1, None),
    ("xi_dryGas", np.float64, -2, None),
    ("M", np.float64, None, None),
    ("cp", np.float64, None, None),
    ("cv", np.float64, None, None),
    ("beta", np.float64, None, None),
    ("kappa", np.float64, None, None),
    ("w", np.float64, None, None),
    ("drhodh_pxi", np.float64, None, None),
    ("drhodp_hxi", np.float64, None, None),
    ("drhodxi_ph", np.float64, -1, None),
    ("p_i", np.float64, 0, None),
    ("xi_gas", np.float64, None, None),
    ("phi", np.float64, None, None),
    ("p_s", np.float64, None, None),
    ("xi_s", np.float64, None, None),
    ("delta_hv", np.float64, None, None),
    ("delta_hd", np.float64, None, None),
    ("h_i", np.float64, 0, None),
    ("humRatio", np.float64, None, None),
    ("humRatio_s", np.float64, None, None),
    ("h1px", np.float64, None, None),
    ("Y", np.float64, None, None),
    ("Pr", np.float64, None, None),
    ("lamb", np.float64, None, None),
    ("eta", np.float64, None, None),
    ("sigma", np.float64, None, None),
]


class GasInformation(InfoContainer):
    """
    Meta Information about a Gas.
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

    def __repr__(self):
        return "TILMedia.Gas.Info " + self.LibraryName + " " + self.MediumName

    def __str__(self):
        data = dict(self)
        units = {"T_min": " K", "T_max": " K", "T_data_min": " K", "T_data_max": " K"}
        return "\n".join([key + ": " + str(value) + units.get(key, "") for key, value in data.items()])


class Gas(DataContainer):
    """
    This Gas class can calculate the thermopyhsical properties of a pure ideal gas or mixtures of ideal gases, optionally with vapor.

    The following combinations of inputs can be used to calculate properties by calling a set function:

        1. T : temperature (:attr:`set_T`)
        2. T, xi: temperature and mass fraction (:attr:`set_Txi`)
        3. p, h, xi: pressure, specific enthalpy and mass fraction (:attr:`set_phxi`)
        4. p, T, xi: pressure, temperature and mass fraction (:attr:`set_pTxi`)
        5. p, s, xi: pressure, specific entropy and mass fraction (:attr:`set_psxi`)
        6. p, T, phi, xi_dryGas: pressure, temperature, relative humidity and mass fraction of dry gas (:attr:`set_pTphixidg`)
        7. p, T, humRatio, xi_dryGas: pressure, temperature, humidity ratio (humRatio) and mass fraction of dry gas (xi_dryGas) (:attr:`set_pThumRatioxidg`)
        8. p, humRatio, phi, xi_dryGas: pressure, humidity ratio, relative humidity and mass fraction of dry gas (:attr:`set_phumRatiophixidg`)

    Args:
        gas_name (str): complete medium name of the gas
        xi (list or numpy.ndarray, optional): mass faction vector. Always one less than the number of components in mixtures. Defaults to None.
        condensingIndex (int, optional): determines the component in a mixture that can condensate. Zero for none. Defaults to 0.
        fixed_mixing_ratio (bool, optional): if true, the mixture is treated as pure component in this interface. Defaults to False.
        compute_transport_properties (bool, optional): if true, transport properties are calculated. Defaults to True.
        instance_name (str, optional): instance name, appears in error messages. Defaults to "Gas_Python".
        logger (logging.Logger, optional): logger instance for log and error messages of this class instance. If not set, the global setting will be used. Defaults to None.
        session (TILMediaSession, optional): The session can be used to get log messages during instantiation. If not set, a new will be instantiated. Defaults to None.

    Example:
        >>> import tilmedia
        >>> gas = tilmedia.Gas('VDI4670.DryAir')
        >>> gas.set_pTxi(1e5, 300)
        >>> print(round(gas.d, 6))
        1.161034
        >>> gas.set_Txi(300)
        >>> print(round(gas.cp, 6))
        1004.990552
        >>> gas.set(p=1e5, T=300)
        >>> print(round(gas.d, 6))
        1.161034
        >>> gas.set_Txi([300, 350, 400])
        >>> print(gas.cp.round(6))
        [1004.990552 1008.342171 1013.626381]

    """

    # static function call list
    _batch_function_calls = {
        3: [
            (
                "TILMedia_Gas_pureComponentProperties_T",
                lambda self: (self, ["T"], None, ["p_s", "delta_hv", "delta_hd", "h_i"]),
            ),
            (
                "TILMedia_Gas_simpleCondensingProperties_pTxi",
                lambda self: (self, ["p", "T", "xi"], None, ["cp", "cv", "beta", "w"]),
            ),
            (
                "TILMedia_Gas_additionalProperties_pTxi",
                lambda self: (
                    self,
                    ["p", "T", "xi"],
                    None,
                    ["d", "kappa", "drhodp_hxi", "drhodh_pxi", "drhodxi_ph", "p_i", "xi_gas"],
                ),
            ),
            ("TILMedia_GasObjectFunctions_specificEnthalpy_pTxi", lambda self: (self, ["p", "T", "xi"], None, ["h"])),
            (
                "TILMedia_GasObjectFunctions_saturationMassFraction_pTxi",
                lambda self: (self, ["p", "T", "xi"], None, ["xi_s"]),
            ),
            ("TILMedia_GasObjectFunctions_specificEntropy_pTxi", lambda self: (self, ["p", "T", "xi"], None, ["s"])),
            ("TILMedia_GasObjectFunctions_relativeHumidity_pTxi", lambda self: (self, ["p", "T", "xi"], None, ["phi"])),
            (
                "TILMedia_GasObjectFunctions_specificEnthalpy1px_pTxi",
                lambda self: (self, ["p", "T", "xi"], None, ["h1px"]),
            ),
        ],
        2: [
            (
                "TILMedia_Gas_pureComponentProperties_T",
                lambda self: (self, ["T"], None, ["p_s", "delta_hv", "delta_hd", "h_i"]),
            ),
            (
                "TILMedia_Gas_simpleCondensingProperties_pTxi",
                lambda self: (self, ["p", "T", "xi"], None, ["cp", "cv", "beta", "w"]),
            ),
            ("TILMedia_GasObjectFunctions_specificEnthalpy_pTxi", lambda self: (self, ["p", "T", "xi"], None, ["h"])),
        ],
        1: [
            (
                "TILMedia_Gas_pureComponentProperties_T",
                lambda self: (self, ["T"], None, ["p_s", "delta_hv", "delta_hd", "h_i"]),
            ),
        ],
    }
    _Info = GasInformation

    _status = 0
    _property_list = []

    def __init__(
        self,
        gas_name: str,
        xi: Optional[Union[List[float], np.ndarray]] = None,
        condensingIndex=0,
        fixed_mixing_ratio=False,
        compute_transport_properties=True,
        instance_name="Gas_Python",
        logger: Optional[logging.Logger] = None,
        session: Optional[TILMediaSession] = None,
    ) -> None:
        global _gas_lock
        self._property_list = _fullProperties + self._property_list
        # properties of GasObject
        # fmt: off
        #    [[[cog
        # import cog
        # from tilmedia import Gas
        # import numpy as np
        # from tilmedia._internals import _generate_code
        # gas = Gas("DryAir")
        # v = gas._property_list + [("M_i",
        # np.float64, None, None)]
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
        self.x = np.zeros((1, 0), dtype=np.float64)
        'Mole fraction [1]'
        self.xi_dryGas = np.zeros((1, 0), dtype=np.float64)
        'Mass fraction of dry gas [1]'
        self.M = np.float64(0)
        'Average molar mass [kg/mol]'
        self.cp = np.float64(0)
        'Specific isobaric heat capacity cp [J/(kg*K)]'
        self.cv = np.float64(0)
        'Specific isochoric heat capacity cv [J/(kg*K)]'
        self.beta = np.float64(0)
        'Isobaric thermal expansion coefficient [1/K]'
        self.kappa = np.float64(0)
        'Isothermal compressibility [1/Pa]'
        self.w = np.float64(0)
        'Speed of sound [m/s]'
        self.drhodh_pxi = np.float64(0)
        'Derivative of density wrt specific enthalpy at constant pressure and mass fraction [kg^2/(m^3*J)]'
        self.drhodp_hxi = np.float64(0)
        'Derivative of density wrt pressure at specific enthalpy and mass fraction [kg/(N*m)]'
        self.drhodxi_ph = np.zeros((1, 0), dtype=np.float64)
        'Derivative of density wrt mass fraction of water at constant pressure and specific enthalpy [kg/m^3]'
        self.p_i = np.zeros((1, 1), dtype=np.float64)
        'Partial pressure [kg^2/(m^3*J)]'
        self.xi_gas = np.float64(0)
        'Mass fraction of gaseous condensing component [1]'
        self.phi = np.float64(0)
        'Relative humidity [%]'
        self.p_s = np.float64(0)
        'Saturation partial pressure of condensing component [Pa]'
        self.xi_s = np.float64(0)
        'Saturation mass fraction of condensing component [1]'
        self.delta_hv = np.float64(0)
        'Specific enthalpy of vaporisation of condensing component [J/kg]'
        self.delta_hd = np.float64(0)
        'Specific enthalpy of desublimation of condensing component [J/kg]'
        self.h_i = np.zeros((1, 1), dtype=np.float64)
        'Specific enthalpy of theoretical pure component [J/kg]'
        self.humRatio = np.float64(0)
        'Content of condensing component aka humidity ratio [1]'
        self.humRatio_s = np.float64(0)
        'Saturation content of condensing component aka saturation humidity ratio [1]'
        self.h1px = np.float64(0)
        'Specific enthalpy h related to the mass of components that cannot condense [J/kg]'
        self.Y = np.float64(0)
        'Transformed y axis in Mollier\'s hx chart [1]'
        self.Pr = np.float64(0)
        'Prandtl number [1]'
        self.lamb = np.float64(0)
        'Thermal conductivity [W/(m*K)]'
        self.eta = np.float64(0)
        'Dynamic viscosity [Pa*s]'
        self.sigma = np.float64(0)
        'Surface tension [J/m^2]'
        self.M_i = np.float64(0)
        'Molar mass of component i [kg/mol]'

        self._d_vector = np.zeros(1, dtype=np.float64)
        self._h_vector = np.zeros(1, dtype=np.float64)
        self._p_vector = np.zeros(1, dtype=np.float64)
        self._s_vector = np.zeros(1, dtype=np.float64)
        self._T_vector = np.zeros(1, dtype=np.float64)
        self._xi_vector = np.zeros((1, 0), dtype=np.float64)
        self._x_vector = np.zeros((1, 0), dtype=np.float64)
        self._xi_dryGas_vector = np.zeros((1, 0), dtype=np.float64)
        self._M_vector = np.zeros(1, dtype=np.float64)
        self._cp_vector = np.zeros(1, dtype=np.float64)
        self._cv_vector = np.zeros(1, dtype=np.float64)
        self._beta_vector = np.zeros(1, dtype=np.float64)
        self._kappa_vector = np.zeros(1, dtype=np.float64)
        self._w_vector = np.zeros(1, dtype=np.float64)
        self._drhodh_pxi_vector = np.zeros(1, dtype=np.float64)
        self._drhodp_hxi_vector = np.zeros(1, dtype=np.float64)
        self._drhodxi_ph_vector = np.zeros((1, 0), dtype=np.float64)
        self._p_i_vector = np.zeros((1, 1), dtype=np.float64)
        self._xi_gas_vector = np.zeros(1, dtype=np.float64)
        self._phi_vector = np.zeros(1, dtype=np.float64)
        self._p_s_vector = np.zeros(1, dtype=np.float64)
        self._xi_s_vector = np.zeros(1, dtype=np.float64)
        self._delta_hv_vector = np.zeros(1, dtype=np.float64)
        self._delta_hd_vector = np.zeros(1, dtype=np.float64)
        self._h_i_vector = np.zeros((1, 1), dtype=np.float64)
        self._humRatio_vector = np.zeros(1, dtype=np.float64)
        self._humRatio_s_vector = np.zeros(1, dtype=np.float64)
        self._h1px_vector = np.zeros(1, dtype=np.float64)
        self._Y_vector = np.zeros(1, dtype=np.float64)
        self._Pr_vector = np.zeros(1, dtype=np.float64)
        self._lamb_vector = np.zeros(1, dtype=np.float64)
        self._eta_vector = np.zeros(1, dtype=np.float64)
        self._sigma_vector = np.zeros(1, dtype=np.float64)
        self._M_i_vector = np.zeros(1, dtype=np.float64)
        # [[[end]]]
        # fmt: on

        self._xiFixed_vector = np.zeros((1, 0), dtype=np.float64)
        self.T_freeze = np.float64(0)
        "freezing temperature in [K]"

        self._medium: ExternalObject

        self._compute_transport_properties = compute_transport_properties

        if condensingIndex > 0 and fixed_mixing_ratio:
            raise TILMediaErrorInvalidParameter(
                "fixed_mixing_ratio cannot be combined with condensingIndex not equal to zero"
            )

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
        self._condensingIndex = condensingIndex
        self._gas_name = gas_name
        self._nc_internal: int = -1
        _xi_autodetect = np.zeros(20, dtype=np.float64)
        with _gas_lock as locked:
            if locked:
                self._status, self._nc_internal = Gas_isValid_getInfo_errorInterface(
                    gas_name, condensingIndex, _xi_autodetect, True, self._session
                )
        if self._status == 0:
            raise TILMediaErrorInvalidMedium('GasName "' + gas_name + '" not valid. Could not create TILMedia object.')
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
        self.M_i = np.zeros((self._nc), dtype=np.float64)

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
                    _, self._xiFixed_vector = internals.var_normalize_inputs(0, self._xi_autodetect)
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
                    _, self._xi_vector = internals.var_normalize_inputs(0, self._xi_autodetect)
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
        with _gas_lock as locked:
            if locked:
                self._medium = ExternalObject(
                    "Gas", gas_name, flags, _xi_call, self._nc, condensingIndex, instance_name, self._session
                )
        if not hasattr(self, "_medium"):
            if self._session.exceptions:
                exceptions = deepcopy(self._session.exceptions)
                while self._session.exceptions:
                    self._session.exceptions.pop()
                raise exceptions[0]
            else:
                raise TILMediaErrorInvalidMedium(
                    'GasName "' + gas_name + '" not valid. Could not create TILMedia object.'
                )
        self.xi = self._xi_vector[0]

        Gas_molarMass(self._medium, self.M_i)
        self.T_freeze = GasObjectFunctions_freezingPoint(self._medium)

        # initializing Info
        self.info = self._Info()
        "Medium meta information"
        getGasInformation_pointer(self.info, self._medium)

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
            logger.debug("Decoupling external object from gas instance (session = %s)", session_id)
            self._medium = None
            logger.debug("Decoupled external object from gas instance (session = %s)", session_id)

        if hasattr(self, "_session"):
            logger.debug("Decoupling session from gas instance (session = %s)", session_id)
            self._session = None
            logger.debug("Decoupling session from gas instance (session = %s)", session_id)

    def dump(self):
        """Prints the current thermophysical properties of the gas to stdout."""
        print(self.__str__())

    def __repr__(self):
        return 'TILMedia.Gas "' + self._gas_name + '" (nc = ' + str(self._nc) + ")"

    def __str__(self):
        value = []
        value += ["Medium: " + self._gas_name]
        value += [DataContainer.__str__(self)]
        return "\n".join([v for v in value if v])

    def set_T(self, T: Union[float, np.ndarray, List[float]]) -> None:
        """
        Calculates all temperature dependent properties.

        Args:
            T (float, list, or numpy.ndarray): temperature [K]
        """

        T, _ = internals.var_normalize_inputs(T, [])

        shape = T.shape
        self._resize_properties(shape)
        self._T_vector[:] = T

        batch_caller = BatchFunctionCaller()
        for function_name, arguments in self._batch_function_calls[1]:
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
                    + "\nThe error was caused by element %s: T=%s." % (str(failure_index), str(T[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message + "\nThe inputs were T=%s." % (str(T[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_Txi(
        self, T: Union[float, np.ndarray, List[float]], xi: Optional[Union[List[float], np.ndarray]] = None
    ) -> None:
        """
        Calculates temperature and mass fraction dependent properties.

        Args:
            T (float, list, or numpy.ndarray): temperature [K]
            xi (list, or numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if self._condensingIndex > 0:
            raise TILMediaErrorInvalidParameter(
                "If condensingIndex is > 0, then this function must not be called, since some of the properties are pressure dependent"
            )
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        T, xi = internals.var_normalize_inputs(T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        if xi.shape[-1] != self._nc - 1:
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(self._nc - 1))
        shape = T.shape
        self._resize_properties(shape)
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        for function_name, arguments in self._batch_function_calls[2]:
            batch_caller.add_call(function_name, *arguments(self))

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

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

    def set_pTxi(
        self,
        p: Union[float, np.ndarray, List[float]],
        T: Union[float, np.ndarray, List[float]],
        xi: Optional[Union[List[float], np.ndarray]] = None,
    ):
        """
        Calculates all thermophysical properties depending on pressure, temperature and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            T (float, list, or numpy.ndarray): temperature [K]
            xi (list, or numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, T, xi = internals.var_normalize_inputs(p, T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        if xi.shape[-1] != self._nc - 1:
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(self._nc - 1))
        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Gas_transportProperties_pTxi", self, ["p", "T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        if not self.fixed_mixing_ratio:
            batch_caller.add_call("TILMedia_Gas_humRatioxidg_xi_", self, ["xi"], None, ["humRatio", "xi_dryGas"])
            batch_caller.add_call(
                "TILMedia_Gas_saturationHumidityRatio_pTxidg", self, ["p", "T", "xi_dryGas"], None, ["humRatio_s"]
            )

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

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
        Calculates all thermophysical properties depending on pressure, enthalpy and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            h (float, list, or numpy.ndarray): specific entphalpy [J/kg]
            xi (list, or numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, h, xi = internals.var_normalize_inputs(p, h, xi)
        internals.check_vector_size(xi, self._nc - 1)

        if xi.shape[-1] != self._nc - 1:
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(self._nc - 1))
        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._h_vector[:] = h
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_GasObjectFunctions_temperature_phxi", self, ["p", "h", "xi"], None, ["T"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Gas_transportProperties_pTxi", self, ["p", "T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        if not self.fixed_mixing_ratio:
            batch_caller.add_call("TILMedia_Gas_humRatioxidg_xi_", self, ["xi"], None, ["humRatio", "xi_dryGas"])
            batch_caller.add_call(
                "TILMedia_Gas_saturationHumidityRatio_pTxidg", self, ["p", "T", "xi_dryGas"], None, ["humRatio_s"]
            )

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

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

    def set_psxi(
        self,
        p: Union[float, np.ndarray, List[float]],
        s: Union[float, np.ndarray, List[float]],
        xi: Optional[Union[List[float], np.ndarray]] = None,
    ):
        """
        Calculates all thermophysical properties depending on pressure, specific entropy and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            s (float, list, or numpy.ndarray): specific entropy [J/(kg*K)]
            xi (list, or numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, s, xi = internals.var_normalize_inputs(p, s, xi)
        internals.check_vector_size(xi, self._nc - 1)

        if xi.shape[-1] != self._nc - 1:
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(self._nc - 1))
        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._s_vector[:] = s
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_GasObjectFunctions_temperature_psxi", self, ["p", "s", "xi"], None, ["T"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Gas_transportProperties_pTxi", self, ["p", "T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        if not self.fixed_mixing_ratio:
            batch_caller.add_call("TILMedia_Gas_humRatioxidg_xi_", self, ["xi"], None, ["humRatio", "xi_dryGas"])
            batch_caller.add_call(
                "TILMedia_Gas_saturationHumidityRatio_pTxidg", self, ["p", "T", "xi_dryGas"], None, ["humRatio_s"]
            )

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, s=%s, xi=%s."
                    % (str(failure_index), str(p[failure_index]), str(s[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, s=%s, xi=%s."
                    % (str(p[failure_index]), str(s[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_pThumRatioxidg(self, p, T, humRatio, xi_dryGas=None):
        """
        Calculates all thermophysical properties depending on pressure, temperature, humidity ratio and independent mass fractions of dry gas (always two less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            T (float, list, or numpy.ndarray): temperature [K]
            humRatio (float, list, or numpy.ndarray): humidity ratio [1]
            xi_dryGas (list, or numpy.ndarray): mass fraction of dry gas [1] (optional)
        """

        if self.fixed_mixing_ratio:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then this function must not be used")
        if self._condensingIndex <= 0:
            raise TILMediaErrorInvalidParameter("If condensingIndex is = 0, then this function must not be used")
        if xi_dryGas is None:
            xi_dryGas = self._xi_dryGas_vector[tuple([0] * (self._xi_dryGas_vector.ndim - 1))]

        p, T, humRatio, xi_dryGas = internals.var_normalize_inputs(p, T, humRatio, xi_dryGas)
        internals.check_vector_size(xi_dryGas, self._nc - 2)

        if xi_dryGas.shape[-1] != max(0, self._nc - 2):
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(max(0, self._nc - 2)))
        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._T_vector[:] = T
        self._xi_dryGas_vector[:] = xi_dryGas
        self._humRatio_vector[:] = humRatio

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_Gas_xi_humRatioxidg_", self, ["humRatio", "xi_dryGas"], None, ["xi"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Gas_transportProperties_pTxi", self, ["p", "T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        if not self.fixed_mixing_ratio:
            batch_caller.add_call("TILMedia_Gas_humRatioxidg_xi_", self, ["xi"], None, ["humRatio", "xi_dryGas"])
            batch_caller.add_call(
                "TILMedia_Gas_saturationHumidityRatio_pTxidg", self, ["p", "T", "xi_dryGas"], None, ["humRatio_s"]
            )

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, T=%s, humRatio=%s, xi_dryGas=%s."
                    % (
                        str(failure_index),
                        str(p[failure_index]),
                        str(T[failure_index]),
                        str(humRatio[failure_index]),
                        str(xi_dryGas[failure_index]),
                    )
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, T=%s, humRatio=%s, xi_dryGas=%s."
                    % (
                        str(p[failure_index]),
                        str(T[failure_index]),
                        str(humRatio[failure_index]),
                        str(xi_dryGas[failure_index]),
                    )
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_pTphixidg(self, p, T, phi, xi_dryGas=None):
        """
        Calculates all thermophysical properties depending on pressure, temperature, relative humidity and independent mass fractions of dry gas (always two less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            T (float, list, or numpy.ndarray): temperature [K]
            phi (float, list, or numpy.ndarray): relative humidity [%]
            xi_dryGas (list, or numpy.ndarray): mass fraction of dry gas [1] (optional)
        """

        if self.fixed_mixing_ratio:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then this function must not be used")
        if self._condensingIndex <= 0:
            raise TILMediaErrorInvalidParameter("If condensingIndex is = 0, then this function must not be used")
        if xi_dryGas is None:
            xi_dryGas = self._xi_dryGas_vector[tuple([0] * (self._xi_dryGas_vector.ndim - 1))]

        p, T, phi, xi_dryGas = internals.var_normalize_inputs(p, T, phi, xi_dryGas)
        internals.check_vector_size(xi_dryGas, self._nc - 2)

        if xi_dryGas.shape[-1] != max(0, self._nc - 2):
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(max(0, self._nc - 2)))
        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._T_vector[:] = T
        self._xi_dryGas_vector[:] = xi_dryGas
        self._phi_vector[:] = phi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call(
            "TILMedia_MoistAir_humRatio_pTphixidg", self, ["p", "T", "phi", "xi_dryGas"], None, ["humRatio"]
        )
        batch_caller.add_call("TILMedia_Gas_xi_humRatioxidg_", self, ["humRatio", "xi_dryGas"], None, ["xi"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Gas_transportProperties_pTxi", self, ["p", "T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        if not self.fixed_mixing_ratio:
            batch_caller.add_call("TILMedia_Gas_humRatioxidg_xi_", self, ["xi"], None, ["humRatio", "xi_dryGas"])
            batch_caller.add_call(
                "TILMedia_Gas_saturationHumidityRatio_pTxidg", self, ["p", "T", "xi_dryGas"], None, ["humRatio_s"]
            )

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, T=%s, phi=%s, xi_dryGas=%s."
                    % (
                        str(failure_index),
                        str(p[failure_index]),
                        str(T[failure_index]),
                        str(phi[failure_index]),
                        str(xi_dryGas[failure_index]),
                    )
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, T=%s, phi=%s, xi_dryGas=%s."
                    % (
                        str(p[failure_index]),
                        str(T[failure_index]),
                        str(phi[failure_index]),
                        str(xi_dryGas[failure_index]),
                    )
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_phumRatiophixidg(self, p, humRatio, phi, xi_dryGas=None):
        """
        Calculates all thermophysical properties depending on pressure, humidity ratio, relative humidity and independent mass fractions of dry gas (always two less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            humRatio (float, list, or numpy.ndarray): humidity ratio [1]
            phi (float, list, or numpy.ndarray): relative humidity [%]
            xi_dryGas (list, or numpy.ndarray): mass fraction of dry gas [1] (optional)
        """

        if self.fixed_mixing_ratio:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then this function must not be used")
        if self._condensingIndex <= 0:
            raise TILMediaErrorInvalidParameter("If condensingIndex is = 0, then this function must not be used")
        if xi_dryGas is None:
            xi_dryGas = self._xi_dryGas_vector[tuple([0] * (self._xi_dryGas_vector.ndim - 1))]

        p, humRatio, phi, xi_dryGas = internals.var_normalize_inputs(p, humRatio, phi, xi_dryGas)
        internals.check_vector_size(xi_dryGas, self._nc - 2)

        if xi_dryGas.shape[-1] != max(0, self._nc - 2):
            raise TILMediaErrorIncompatibleVectorLength("xi vector length is should be " + str(max(0, self._nc - 2)))
        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._humRatio_vector[:] = humRatio
        self._xi_dryGas_vector[:] = xi_dryGas
        self._phi_vector[:] = phi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call(
            "TILMedia_MoistAir_properties_phumRatiophixidg",
            self,
            ["p", "humRatio", "phi", "xi_dryGas"],
            None,
            ["d", "h", "s", "T", "Y"],
        )
        batch_caller.add_call("TILMedia_Gas_xi_humRatioxidg_", self, ["humRatio", "xi_dryGas"], None, ["xi"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_Gas_transportProperties_pTxi", self, ["p", "T", "xi"], None, ["Pr", "lamb", "eta", "sigma"]
            )
        if not self.fixed_mixing_ratio:
            batch_caller.add_call("TILMedia_Gas_humRatioxidg_xi_", self, ["xi"], None, ["humRatio", "xi_dryGas"])
            batch_caller.add_call(
                "TILMedia_Gas_saturationHumidityRatio_pTxidg", self, ["p", "T", "xi_dryGas"], None, ["humRatio_s"]
            )

        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(self._xi_vector, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties[None])

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, humRatio=%s, phi=%s, xi_dryGas=%s."
                    % (
                        str(failure_index),
                        str(p[failure_index]),
                        str(humRatio[failure_index]),
                        str(phi[failure_index]),
                        str(xi_dryGas[failure_index]),
                    )
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, humRatio=%s, phi=%s, xi_dryGas=%s."
                    % (
                        str(p[failure_index]),
                        str(humRatio[failure_index]),
                        str(phi[failure_index]),
                        str(xi_dryGas[failure_index]),
                    )
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def _molarMass(self, xi, M_i):
        shape = xi.shape[:-1]
        M = np.zeros(shape)
        x = np.zeros(xi.shape)
        if isinstance(M_i, list):
            M_i = np.array(M_i)

        mixingRatio = np.concatenate(
            (xi, (np.ones(shape) - np.sum(xi, xi.ndim - 1)).reshape(shape + (1,))), xi.ndim - 1
        )
        M = 1 / np.sum(mixingRatio / M_i, xi.ndim - 1)
        x = M.reshape(shape + (1,)) * (xi / M_i[:-1])

        return M, x

    def set(self, **kwargs):
        keys = frozenset(kwargs)
        mapping = {
            frozenset({"p", "h"}): self.set_phxi,
            frozenset({"p", "h", "xi"}): self.set_phxi,
            frozenset({"p", "T"}): self.set_pTxi,
            frozenset({"p", "T", "xi"}): self.set_pTxi,
            frozenset({"p", "s"}): self.set_psxi,
            frozenset({"p", "s", "xi"}): self.set_psxi,
            frozenset({"T"}): self.set_T,
            frozenset({"T", "xi"}): self.set_Txi,
            frozenset({"p", "T", "phi"}): self.set_pTphixidg,
            frozenset({"p", "T", "phi", "xi_dryGas"}): self.set_pTphixidg,
            frozenset({"p", "T", "humRatio"}): self.set_pThumRatioxidg,
            frozenset({"p", "T", "humRatio", "xi_dryGas"}): self.set_pThumRatioxidg,
            frozenset({"p", "humRatio", "phi"}): self.set_phumRatiophixidg,
            frozenset({"p", "humRatio", "phi", "xi_dryGas"}): self.set_phumRatiophixidg,
        }
        function = mapping.get(keys)
        if function:
            function(**kwargs)
        else:
            raise TILMediaErrorInvalidParameter(
                f"Properties cannot be computed from the arguments {set(keys)}, only {[set(v) for v in mapping]} are available."
            )
