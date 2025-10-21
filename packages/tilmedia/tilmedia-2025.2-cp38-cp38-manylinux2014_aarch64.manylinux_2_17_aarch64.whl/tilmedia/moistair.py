import logging
from copy import deepcopy
from typing import List, Optional, Union

import numpy as np

from .exceptions import TILMediaErrorInvalidParameter
from .gas import Gas

_moistAirProperties = ["T_wetBulb", "T_iceBulb", "T_dew"]


class MoistAir(Gas):
    """
    This MoistAir class can calculate the thermopyhsical properties of a pure ideal gas or mixtures of ideal gases including vapor. It provides additional variables for wet/ice bulb temperature and dew temperature.

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
        instance_name (str, optional): instance name, appears in error messages. Defaults to "MoistAir_Python".
        logger (logging.Logger, optional): logger instance for log and error messages of this class instance. If not set, the global setting will be used. Defaults to None.

    Example:
        >>> import tilmedia
        >>> moistair = tilmedia.MoistAir('TILMedia.MoistAir', [0.01])
        >>> moistair.set_pTxi(1e5, 300, [0.01])
        >>> print(round(moistair.d, 6))
        1.154025
        >>> moistair.set(p=1e5, T=301, xi=[0.01])
        >>> print(round(moistair.d, 6))
        1.150191

    """

    def __init__(
        self,
        gas_name,
        xi: Optional[Union[List[float], np.ndarray]] = None,
        condensingIndex=1,
        fixed_mixing_ratio=False,
        compute_transport_properties=True,
        instance_name="MoistAir_Python",
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.T_wetBulb = 0
        "wet bulb temperature [K]"
        self.T_iceBulb = 0
        "ice bulb temperature [K]"
        self.T_dew = 0
        "dew temperature [K]"

        self._T_wetBulb_vector = np.zeros((1), dtype=np.float64)
        self._T_iceBulb_vector = np.zeros((1), dtype=np.float64)
        self._T_dew_vector = np.zeros((1), dtype=np.float64)

        self._T_wetBulb = np.ctypeslib.as_ctypes(self._T_wetBulb_vector)
        self._T_iceBulb = np.ctypeslib.as_ctypes(self._T_iceBulb_vector)
        self._T_dew = np.ctypeslib.as_ctypes(self._T_dew_vector)

        self._batch_function_calls = deepcopy(self._batch_function_calls)
        self._batch_function_calls[3] += [
            (
                "TILMedia_GasObjectFunctions_wetBulbTemperature_pTxi",
                lambda self: (self, ["p", "T", "xi"], None, ["T_wetBulb"]),
            ),
            (
                "TILMedia_GasObjectFunctions_iceBulbTemperature_pTxi",
                lambda self: (self, ["p", "T", "xi"], None, ["T_iceBulb"]),
            ),
            (
                "TILMedia_GasObjectFunctions_dewTemperature_pTphixidg",
                lambda self: (self, ["p", "T", "phi", "xi_dryGas"], None, ["T_dew"]),
            ),
        ]
        self._property_list = [
            ("T_wetBulb", np.float64, None, None),
            ("T_iceBulb", np.float64, None, None),
            ("T_dew", np.float64, None, None),
        ]

        Gas.__init__(
            self, gas_name, xi, condensingIndex, fixed_mixing_ratio, compute_transport_properties, instance_name, logger
        )
        if self._nc == 1:
            raise TILMediaErrorInvalidParameter("The MoistAir class should not be used for pure substances.")

    set_pThumRatio = Gas.set_pThumRatioxidg
    set_pTphi = Gas.set_pTphixidg
