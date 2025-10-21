import logging
from copy import deepcopy
from threading import Lock
from typing import List, Optional, Union

import numpy as np

from . import _internals as internals
from .batchcaller import BatchFunctionCaller
from .core import (
    ExternalObject,
    VLEFluid_Cached_molarMass,
    VLEFluid_isValid_getInfo_errorInterface,
    getVLEFluidInformation_pointer,
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

_vle_lock = Lock()

_properties = [
    ("d", np.float64, None, None),
    ("h", np.float64, None, None),
    ("p", np.float64, None, None),
    ("s", np.float64, None, None),
    ("T", np.float64, None, None),
]
_additionalProperties = [
    ("cp", np.float64, None, None),
    ("beta", np.float64, None, None),
    ("kappa", np.float64, None, None),
]
_transportProperties = [
    ("Pr", np.float64, None, None),
    ("lambda", np.float64, None, None),
    ("eta", np.float64, None, None),
]
_fullProperties = [
    ("p", np.float64, None, None),
    ("h", np.float64, None, None),
    ("d", np.float64, None, None),
    ("s", np.float64, None, None),
    ("T", np.float64, None, None),
    ("xi", np.float64, -1, None),
    ("x", np.float64, -1, None),
    ("M", np.float64, None, None),
    ("phase", np.int32, None, None),
    ("q", np.float64, None, None),
    ("cp", np.float64, None, None),
    ("cv", np.float64, None, None),
    ("beta", np.float64, None, None),
    ("kappa", np.float64, None, None),
    ("w", np.float64, None, None),
    ("drhodh_pxi", np.float64, None, None),
    ("drhodp_hxi", np.float64, None, None),
    ("drhodxi_ph", np.float64, -1, None),
    ("gamma", np.float64, None, None),
]
_fullTransportProperties = [
    ("Pr", np.float64, None, None),
    ("lamb", np.float64, None, None),
    ("eta", np.float64, None, None),
    ("sigma", np.float64, None, None),
]
_saturationProperties = [
    ("T_bubble", np.float64, None, None),
    ("T_dew", np.float64, None, None),
    ("p_bubble", np.float64, None, None),
    ("p_dew", np.float64, None, None),
    ("dl_bubble", np.float64, None, None),
    ("dv_dew", np.float64, None, None),
    ("dv_bubble", np.float64, None, None),
    ("dl_dew", np.float64, None, None),
    ("hl_bubble", np.float64, None, None),
    ("hv_dew", np.float64, None, None),
    ("sl_bubble", np.float64, None, None),
    ("sv_dew", np.float64, None, None),
]
_saturationMixtureProperties = [("xiv_bubble", np.float64, -1, None), ("xil_dew", np.float64, -1, None)]


class VLEFluidVLEProperties(DataContainer):
    """Vapour Liquid Equilibrium Properties"""

    def __init__(self, nc=1) -> None:
        self._property_list = []
        for p in _properties + [("xi", np.float64, -1, None)] + _additionalProperties + _transportProperties:
            self._property_list.append((p[0] + "_l",) + p[1:])
            self._property_list.append((p[0] + "_v",) + p[1:])

        # fmt: off
        #    [[[cog
        # import cog
        # from tilmedia import VLEFluid
        # import numpy as np
        # from tilmedia._internals import _generate_code
        # vle = VLEFluid("Refprop.R410A.mix")
        # v = vle.vle._property_list
        # cog.outl("\n".join(_generate_code(v)))
        # ]]]
        self.d_l = np.float64(0)
        'Density of liquid phase [kg/m^3]'
        self.d_v = np.float64(0)
        'Density of vapour phase [kg/m^3]'
        self.h_l = np.float64(0)
        'Specific enthalpy of liquid phase [J/kg]'
        self.h_v = np.float64(0)
        'Specific enthalpy of vapour phase [J/kg]'
        self.p_l = np.float64(0)
        'Pressure of liquid phase [Pa]'
        self.p_v = np.float64(0)
        'Pressure of vapour phase [Pa]'
        self.s_l = np.float64(0)
        'Specific entropy of liquid phase [J/(kg*K)]'
        self.s_v = np.float64(0)
        'Specific entropy of vapour phase [J/(kg*K)]'
        self.T_l = np.float64(0)
        'Temperature of liquid phase [K]'
        self.T_v = np.float64(0)
        'Temperature of vapour phase [K]'
        self.xi_l = np.zeros((1, 0), dtype=np.float64)
        'Mass fraction of liquid phase [1]'
        self.xi_v = np.zeros((1, 0), dtype=np.float64)
        'Mass fraction of vapour phase [1]'
        self.cp_l = np.float64(0)
        'Specific heat capacity cp of liquid phase [J/(kg*K)]'
        self.cp_v = np.float64(0)
        'Specific heat capacity cp of vapour phase [J/(kg*K)]'
        self.beta_l = np.float64(0)
        'Isobaric expansion coefficient of liquid phase [1/K]'
        self.beta_v = np.float64(0)
        'Isobaric expansion coefficient of vapour phase [1/K]'
        self.kappa_l = np.float64(0)
        'Isothermal compressibility of liquid phase [1/Pa]'
        self.kappa_v = np.float64(0)
        'Isothermal compressibility of vapour phase [1/Pa]'
        self.Pr_l = np.float64(0)
        'Prandtl number of liquid phase [1]'
        self.Pr_v = np.float64(0)
        'Prandtl number of vapour phase [1]'
        self.lambda_l = np.float64(0)
        'Thermal conductivity of liquid phase [W/(m*K)]'
        self.lambda_v = np.float64(0)
        'Thermal conductivity of vapour phase [W/(m*K)]'
        self.eta_l = np.float64(0)
        'Dynamic viscosity of liquid phase [Pa*s]'
        self.eta_v = np.float64(0)
        'Dynamic viscosity of vapour phase [Pa*s]'

        self._d_l_vector = np.zeros(1, dtype=np.float64)
        self._d_v_vector = np.zeros(1, dtype=np.float64)
        self._h_l_vector = np.zeros(1, dtype=np.float64)
        self._h_v_vector = np.zeros(1, dtype=np.float64)
        self._p_l_vector = np.zeros(1, dtype=np.float64)
        self._p_v_vector = np.zeros(1, dtype=np.float64)
        self._s_l_vector = np.zeros(1, dtype=np.float64)
        self._s_v_vector = np.zeros(1, dtype=np.float64)
        self._T_l_vector = np.zeros(1, dtype=np.float64)
        self._T_v_vector = np.zeros(1, dtype=np.float64)
        self._xi_l_vector = np.zeros((1, 0), dtype=np.float64)
        self._xi_v_vector = np.zeros((1, 0), dtype=np.float64)
        self._cp_l_vector = np.zeros(1, dtype=np.float64)
        self._cp_v_vector = np.zeros(1, dtype=np.float64)
        self._beta_l_vector = np.zeros(1, dtype=np.float64)
        self._beta_v_vector = np.zeros(1, dtype=np.float64)
        self._kappa_l_vector = np.zeros(1, dtype=np.float64)
        self._kappa_v_vector = np.zeros(1, dtype=np.float64)
        self._Pr_l_vector = np.zeros(1, dtype=np.float64)
        self._Pr_v_vector = np.zeros(1, dtype=np.float64)
        self._lambda_l_vector = np.zeros(1, dtype=np.float64)
        self._lambda_v_vector = np.zeros(1, dtype=np.float64)
        self._eta_l_vector = np.zeros(1, dtype=np.float64)
        self._eta_v_vector = np.zeros(1, dtype=np.float64)
        # [[[end]]]
        # fmt: on

        DataContainer.__init__(self, nc, "xi_l")

    def resize_properties(self, shape):
        return self._resize_properties(shape)

    def __repr__(self):
        return "VLEProperties()"


class VLEFluidSaturationProperties(DataContainer):
    """Dew and Bubble Point Properties"""

    def __init__(self, nc=1) -> None:
        self._property_list = _saturationProperties + _saturationMixtureProperties

        # fmt: off
        #    [[[cog
        # import cog
        # from tilmedia import VLEFluid
        # import numpy as np
        # from tilmedia._internals import _generate_code
        # vle = VLEFluid("Refprop.R410A.mix")
        # v = vle.sat._property_list
        # cog.outl("\n".join(_generate_code(v)))
        # ]]]
        self.T_bubble = np.float64(0)
        'bubble point temperature [K]'
        self.T_dew = np.float64(0)
        'dew point temperature [K]'
        self.p_bubble = np.float64(0)
        'bubble point pressure [Pa]'
        self.p_dew = np.float64(0)
        'dew point pressure [Pa]'
        self.dl_bubble = np.float64(0)
        'bubble point liquid density [kg/m^3]'
        self.dv_dew = np.float64(0)
        'dew point vapour density [kg/m^3]'
        self.dv_bubble = np.float64(0)
        'bubble point vapour density [kg/m^3]'
        self.dl_dew = np.float64(0)
        'dew point liquid density [kg/m^3]'
        self.hl_bubble = np.float64(0)
        'bubble point liquid specific enthalpy [J/kg]'
        self.hv_dew = np.float64(0)
        'dew point vapour specific enthalpy [J/kg]'
        self.sl_bubble = np.float64(0)
        'bubble point liquid specific entropy [J/(kg*K)]'
        self.sv_dew = np.float64(0)
        'dew point vapour specific entropy [J/(kg*K)]'
        self.xiv_bubble = np.zeros((1, 0), dtype=np.float64)
        'bubble point vapour mass fraction [1]'
        self.xil_dew = np.zeros((1, 0), dtype=np.float64)
        'dew point liquid mass fraction [1]'

        self._T_bubble_vector = np.zeros(1, dtype=np.float64)
        self._T_dew_vector = np.zeros(1, dtype=np.float64)
        self._p_bubble_vector = np.zeros(1, dtype=np.float64)
        self._p_dew_vector = np.zeros(1, dtype=np.float64)
        self._dl_bubble_vector = np.zeros(1, dtype=np.float64)
        self._dv_dew_vector = np.zeros(1, dtype=np.float64)
        self._dv_bubble_vector = np.zeros(1, dtype=np.float64)
        self._dl_dew_vector = np.zeros(1, dtype=np.float64)
        self._hl_bubble_vector = np.zeros(1, dtype=np.float64)
        self._hv_dew_vector = np.zeros(1, dtype=np.float64)
        self._sl_bubble_vector = np.zeros(1, dtype=np.float64)
        self._sv_dew_vector = np.zeros(1, dtype=np.float64)
        self._xiv_bubble_vector = np.zeros((1, 0), dtype=np.float64)
        self._xil_dew_vector = np.zeros((1, 0), dtype=np.float64)
        # [[[end]]]
        # fmt: on

        DataContainer.__init__(self, nc, "xil_dew")

    def resize_properties(self, shape):
        return self._resize_properties(shape)

    def __repr__(self):
        return "SaturationProperties()"


class VLEFluidCriticalProperties(DataContainer):
    """Critical Properties"""

    def __init__(self, nc=1) -> None:
        self._property_list = [(n[0] + "c",) + n[1:] for n in _properties]
        DataContainer.__init__(self, nc, "Tc")
        # fmt: off
        #    [[[cog
        # import cog
        # from tilmedia import VLEFluid
        # import numpy as np
        # from tilmedia._internals import _generate_code
        # vle = VLEFluid("Refprop.R410A.mix")
        # v = vle.crit._property_list
        # cog.outl("\n".join(_generate_code(v)))
        # ]]]
        self.dc = np.float64(0)
        'Critical density [kg/m^3]'
        self.hc = np.float64(0)
        'Critical specific enthalpy [J/kg]'
        self.pc = np.float64(0)
        'Critical pressure [Pa]'
        self.sc = np.float64(0)
        'Critical specific entropy [J/(kg*K)]'
        self.Tc = np.float64(0)
        'Critical temperature [K]'

        self._dc_vector = np.zeros(1, dtype=np.float64)
        self._hc_vector = np.zeros(1, dtype=np.float64)
        self._pc_vector = np.zeros(1, dtype=np.float64)
        self._sc_vector = np.zeros(1, dtype=np.float64)
        self._Tc_vector = np.zeros(1, dtype=np.float64)
        # [[[end]]]
        # fmt: on

    def resize_properties(self, shape):
        return self._resize_properties(shape)

    def __repr__(self):
        return "CriticalProperties()"


class VLEFluidInformation(InfoContainer):
    """
    Meta Information about a VLEFluid.
    """

    _allowed = [
        "MediumName",
        "LibraryName",
        "LibraryLiteratureReference",
        "EOS_type",
        "EOS_models",
        "EOS_selected_model",
        "CASnumber",
        "Fullname",
        "ChemicalFormula",
        "Synonym",
        "MolarMass",
        "TripleTemperature",
        "NormalBoilingPoint",
        "criticalTemperature",
        "criticalPressure",
        "criticalDensity",
        "AcentricFactor",
        "DipoleMoment",
        "DefaultReferenceState",
        "UNNumber",
        "Family",
        "HeatingValue",
        "GWP",
        "ODP",
        "RCL",
        "SafetyGroup",
        "IdealPart_name",
        "IdealPart_literatureReference",
        "IdealPart_precisionComment",
        "IdealPart_Tmin",
        "IdealPart_Tmax",
        "RealPart_name",
        "RealPart_literatureReference",
        "RealPart_precisionComment",
        "RealPart_Tmin",
        "RealPart_Tmax",
        "RealPart_pmax",
        "RealPart_rhomax",
        "ThermalConductivity_models",
        "ThermalConductivity_name",
        "ThermalConductivity_literatureReference",
        "ThermalConductivity_precisionComment",
        "ThermalConductivity_Tmin",
        "ThermalConductivity_Tmax",
        "ThermalConductivity_pmax",
        "ThermalConductivity_rhomax",
        "Viscosity_models",
        "Viscosity_name",
        "Viscosity_literatureReference",
        "Viscosity_precisionComment",
        "Viscosity_Tmin",
        "Viscosity_Tmax",
        "Viscosity_pmax",
        "Viscosity_rhomax",
    ]

    def __init__(self) -> None:
        super().__init__()
        self.MediumName: Optional[str] = None
        "Name of the medium"
        self.LibraryName: Optional[str] = None
        "Name of the medium library"
        self.LibraryLiteratureReference: Optional[str] = None
        "Literature reference of the medium library"
        self.EOS_type: Optional[str] = None
        "Type of selected equation of state"
        self.EOS_models: Optional[str] = None
        "Identifiers of available equations of state"
        self.EOS_selected_model: Optional[str] = None
        "Identifier of selected equation of state"
        self.CASnumber: Optional[str] = None
        "CAS number of medium"
        self.Fullname: Optional[str] = None
        "Full name of medium"
        self.ChemicalFormula: Optional[str] = None
        "Chemical formula"
        self.Synonym: Optional[str] = None
        "Synonym of medium"
        self.MolarMass: Optional[float] = None
        "Molar mass"
        self.TripleTemperature: Optional[float] = None
        "Triple point temperature"
        self.NormalBoilingPoint: Optional[float] = None
        "Normal boiling point"
        self.criticalTemperature: Optional[float] = None
        "Critical temperature"
        self.criticalPressure: Optional[float] = None
        "Critical pressure"
        self.criticalDensity: Optional[float] = None
        "Critical density"
        self.AcentricFactor: Optional[float] = None
        "Acentric factor"
        self.DipoleMoment: Optional[float] = None
        "Dipole moment"
        self.DefaultReferenceState: Optional[str] = None
        "Default reference state"
        self.UNNumber: Optional[str] = None
        "UN number"
        self.Family: Optional[str] = None
        "Medium family"
        self.HeatingValue: Optional[float] = None
        "Heating value (upper)"
        self.GWP: Optional[float] = None
        "Global warming potential"
        self.ODP: Optional[float] = None
        "Ozone depletion potential"
        self.RCL: Optional[float] = None
        "Refrigerant concentration limit"
        self.SafetyGroup: Optional[str] = None
        "Safety Group"
        self.IdealPart_name: Optional[str] = None
        "Identifier of the ideal part of the equation of state (REFPROP naming)"
        self.IdealPart_literatureReference: Optional[str] = None
        "Literature reference of the ideal part of the equation of state"
        self.IdealPart_precisionComment: Optional[str] = None
        "Precision comment of the ideal part of the equation of state"
        self.IdealPart_Tmin: Optional[float] = None
        "Minimum temperature of the ideal part of the equation of state"
        self.IdealPart_Tmax: Optional[float] = None
        "Maximum temperature of the ideal part of the equation of state"
        self.RealPart_name: Optional[str] = None
        "Identifier of the real part of the equation of state (REFPROP naming)"
        self.RealPart_literatureReference: Optional[str] = None
        "Literature reference of the real part of the equation of state"
        self.RealPart_precisionComment: Optional[str] = None
        "Precision comment of the real part of the equation of state"
        self.RealPart_Tmin: Optional[float] = None
        "Minimum temperature of the real part of the equation of state"
        self.RealPart_Tmax: Optional[float] = None
        "Maximum temperature of the real part of the equation of state"
        self.RealPart_pmax: Optional[float] = None
        "Maximum pressure of the real part of the equation of state"
        self.RealPart_rhomax: Optional[float] = None
        "Maximum density of the real part of the equation of state"
        self.ThermalConductivity_models: Optional[str] = None
        "Identifiers of the available thermal conductivity equations (REFPROP naming)"
        self.ThermalConductivity_name: Optional[str] = None
        "Identifier of the selected thermal conductivity equation (REFPROP naming)"
        self.ThermalConductivity_literatureReference: Optional[str] = None
        "Literature reference of the thermal conductivity equation"
        self.ThermalConductivity_precisionComment: Optional[str] = None
        "Precision comment of the thermal conductivity equation"
        self.ThermalConductivity_Tmin: Optional[float] = None
        "Minimum temperature of the thermal conductivity equation"
        self.ThermalConductivity_Tmax: Optional[float] = None
        "Maximum temperature of the thermal conductivity equation"
        self.ThermalConductivity_pmax: Optional[float] = None
        "Maximum pressure of the thermal conductivity equation"
        self.ThermalConductivity_rhomax: Optional[float] = None
        "Maximum density of the thermal conductivity equation"
        self.Viscosity_models: Optional[str] = None
        "Identifiers of the available viscosity equations (REFPROP naming)"
        self.Viscosity_name: Optional[str] = None
        "Identifier of the selected viscosity equation (REFPROP naming)"
        self.Viscosity_literatureReference: Optional[str] = None
        "Literature reference of the viscosity equation"
        self.Viscosity_precisionComment: Optional[str] = None
        "Precision comment of the viscosity equation"
        self.Viscosity_Tmin: Optional[float] = None
        "Minimum temperature of the viscosity equation"
        self.Viscosity_Tmax: Optional[float] = None
        "Maximum temperature of the viscosity equation"
        self.Viscosity_pmax: Optional[float] = None
        "Maximum pressure of the viscosity equation"
        self.Viscosity_rhomax: Optional[float] = None
        "Maximum density of the viscosity equation"

    def __repr__(self):
        return "TILMedia.VLEFluid.Info " + self.LibraryName + " " + self.MediumName

    def __str__(self):
        data = dict(self)
        units = {
            "MolarMass": " kg/mol",
            "IdealPart_Tmin": " K",
            "IdealPart_Tmax": " K",
            "RealPart_Tmin": " K",
            "RealPart_Tmax": " K",
            "Viscosity_Tmin": " K",
            "Viscosity_Tmax": " K",
            "ThermalConductivity_Tmin": " K",
            "ThermalConductivity_Tmax": " K",
            "TripleTemperature": " K",
            "NormalBoilingPoint": " K",
            "criticalTemperature": " K",
            "criticalPressure": " Pa",
            "criticalDensity": " kg/m^3",
            "RealPart_pmax": " Pa",
            "RealPart_rhomax": " kg/m^3",
        }
        return "\n".join([key + ": " + str(value) + units.get(key, "") for key, value in data.items()])


class VLEFluid(DataContainer):
    """
    This VLEFluid class can calculate the thermopyhsical properties of a pure real fluid or real fluid mixture.

        1. xi: mass fraction (:attr:`set_xi`)
        2. p, xi: pressure and mass fraction (:attr:`set_xi`)
        3. T, xi: temperature and mass fraction (:attr:`set_Txi`)
        4. p, h, xi: pressure, specific enthalpy and mass fraction (:attr:`set_phxi`)
        5. p, s, xi: pressure, specific entropy and mass fraction (:attr:`set_psxi`)
        6. p, T, xi: pressure, temperature and mass fraction (:attr:`set_pTxi`)
        7. d, T, xi: density, temperature and mass fraction (:attr:`set_dTxi`)

    Additional experimental implementations are available for:

        1. p, d, xi: pressure, density and mass fraction (:attr:`set_pdxi`)
        2. T, h, xi: temperature, specific enthalpy and mass fraction (:attr:`set_Thxi`)
        3. T, s, xi: temperature, specific entropy and mass fraction (:attr:`set_Tsxi`)

    Args:
        vleFluid_name (str): complete name of the vleFluid
        xi (list or numpy.ndarray, optional): mass faction vector. Always one less than the number of components in mixtures. Defaults to None.
        fixed_mixing_ratio (bool, optional): if true, the mixture is treated as pure component in this interface. Defaults to False.
        compute_transport_properties (bool, optional): if true, transport properties are calculated. Defaults to False.
        compute_vle_transport_properties (bool, optional): if true, transport property variables are available in the VLEProperties. Defaults to False.
        compute_vle_additional_properties (bool, optional): if true, additional information such as the specific heat capacity are available in the VLEProperties. Defaults to False.
        deactivate_density_derivatives (bool, optional): if true, derivatives of the density are not calculated. Defaults to False.
        deactivate_two_phase_region (bool, optional): if true, derivatives of the density are not calculated. Defaults to False.
        instance_name (str, optional): instance name, appears in error messages. Defaults to "VLEFluid_Python".
        logger (logging.Logger, optional): logger instance for log and error messages of this class instance. If not set, the global setting will be used. Defaults to None.
        session (TILMediaSession, optional): The session can be used to get log messages during instantiation. If not set, a new will be instantiated. Defaults to None.

    Example:
        >>> import tilmedia
        >>> vleFluid = tilmedia.VLEFluid('TILMedia.R134a')
        >>> vleFluid.set_pTxi(1e5, 300)
        >>> print(round(vleFluid.d, 6))
        4.173095
        >>> print(round(vleFluid.vle.T_l, 6))
        246.788812
        >>> vleFluid.set_pxi(2e5)
        >>> print(round(vleFluid.vle.T_l, 6))
        263.073728
        >>> vleFluid.set(T=vleFluid.sat.T_dew)
        >>> print(round(vleFluid.sat.p_dew, 1))
        200000.0
        >>> vleFluid.set_phxi(1e5, [350e3, 360e3, 370e3])
        >>> print(vleFluid.d.round(6))
        [6.106462 5.79392  5.511813]

    """

    # static function call list
    _batch_function_calls = {
        4: [
            (
                "TILMedia_VLEFluid_criticalDataRecord_xi",
                lambda self: (self, ["xi"], "crit", ["dc", "hc", "pc", "sc", "Tc"]),
            ),
            ("TILMedia_VLEFluid_Cached_phase_dTxi", lambda self: (self, ["d", "T", "xi"], None, ["phase"])),
            (
                "TILMedia_VLEFluid_additionalProperties_dTxi",
                lambda self: (
                    self,
                    ["d", "T", "xi"],
                    None,
                    ["q", "cp", "cv", "beta", "kappa", "drhodp_hxi", "drhodh_pxi", "drhodxi_ph", "w", "gamma"],
                ),
            ),
            (
                "TILMedia_VLEFluid_VLEProperties_dTxi",
                lambda self: (
                    self,
                    ["d", "T", "xi"],
                    "vle",
                    ["d_l", "h_l", "p_l", "s_l", "T_l", "xi_l", "d_v", "h_v", "p_v", "s_v", "T_v", "xi_v"],
                ),
            ),
        ],
        3: [
            (
                "TILMedia_VLEFluid_criticalDataRecord_xi",
                lambda self: (self, ["xi"], "crit", ["dc", "hc", "pc", "sc", "Tc"]),
            ),
            ("TILMedia_VLEFluid_Cached_phase_phxi", lambda self: (self, ["p", "h", "xi"], None, ["phase"])),
            (
                "TILMedia_VLEFluid_additionalProperties_phxi",
                lambda self: (
                    self,
                    ["p", "h", "xi"],
                    None,
                    ["q", "cp", "cv", "beta", "kappa", "drhodp_hxi", "drhodh_pxi", "drhodxi_ph", "w", "gamma"],
                ),
            ),
            (
                "TILMedia_VLEFluid_VLEProperties_phxi",
                lambda self: (
                    self,
                    ["p", "h", "xi"],
                    "vle",
                    ["d_l", "h_l", "p_l", "s_l", "T_l", "xi_l", "d_v", "h_v", "p_v", "s_v", "T_v", "xi_v"],
                ),
            ),
        ],
        2: [],
        1: [
            (
                "TILMedia_VLEFluid_criticalDataRecord_xi",
                lambda self: (self, ["xi"], "crit", ["dc", "hc", "pc", "sc", "Tc"]),
            )
        ],
    }

    _VLEProperties = VLEFluidVLEProperties
    _CriticalProperties = VLEFluidCriticalProperties
    _SaturationProperties = VLEFluidSaturationProperties
    _Info = VLEFluidInformation

    _status = 0
    _property_list = []

    def __init__(
        self,
        vleFluid_name: str,
        xi: Optional[Union[List[float], np.ndarray]] = None,
        fixed_mixing_ratio=False,
        compute_transport_properties=False,
        compute_vle_transport_properties=False,
        compute_vle_additional_properties=False,
        deactivate_density_derivatives=False,
        deactivate_two_phase_region=False,
        instance_name="VLEFluid_Python",
        logger: Optional[logging.Logger] = None,
        session: Optional[TILMediaSession] = None,
    ) -> None:
        global _vle_lock
        self._property_list = _fullProperties + _fullTransportProperties + self._property_list
        # fmt: off
        #    [[[cog
        # import cog
        # from tilmedia import VLEFluid
        # import numpy as np
        # from tilmedia._internals import _generate_code
        # vle = VLEFluid("Refprop.R410A.mix")
        # v = vle._property_list + [("M_i", np.float64, 0, None)]
        # cog.outl("\n".join(_generate_code(v)))
        # ]]]
        self.p = np.float64(0)
        'Pressure [Pa]'
        self.h = np.float64(0)
        'Specific enthalpy [J/kg]'
        self.d = np.float64(0)
        'Density [kg/m^3]'
        self.s = np.float64(0)
        'Specific entropy [J/(kg*K)]'
        self.T = np.float64(0)
        'Temperature [K]'
        self.xi = np.zeros((1, 0), dtype=np.float64)
        'Water Mass fraction [1]'
        self.x = np.zeros((1, 0), dtype=np.float64)
        'Mole fraction [1]'
        self.M = np.float64(0)
        'Average molar mass [kg/mol]'
        self.phase = np.int32(0)
        '0=subcooled, 1=two phase, 2=superheated [1]'
        self.q = np.float64(0)
        'Vapor quality (steam mass fraction) [1]'
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
        self.gamma = np.float64(0)
        'Heat capacity ratio aka isentropic expansion factor [1]'
        self.Pr = np.float64(0)
        'Prandtl number [1]'
        self.lamb = np.float64(0)
        'Thermal conductivity [W/(m*K)]'
        self.eta = np.float64(0)
        'Dynamic viscosity [Pa*s]'
        self.sigma = np.float64(0)
        'Surface tension [J/m^2]'
        self.M_i = np.zeros((1, 1), dtype=np.float64)
        'Molar mass of component i [kg/mol]'

        self._p_vector = np.zeros(1, dtype=np.float64)
        self._h_vector = np.zeros(1, dtype=np.float64)
        self._d_vector = np.zeros(1, dtype=np.float64)
        self._s_vector = np.zeros(1, dtype=np.float64)
        self._T_vector = np.zeros(1, dtype=np.float64)
        self._xi_vector = np.zeros((1, 0), dtype=np.float64)
        self._x_vector = np.zeros((1, 0), dtype=np.float64)
        self._M_vector = np.zeros(1, dtype=np.float64)
        self._phase_vector = np.zeros(1, dtype=np.int32)
        self._q_vector = np.zeros(1, dtype=np.float64)
        self._cp_vector = np.zeros(1, dtype=np.float64)
        self._cv_vector = np.zeros(1, dtype=np.float64)
        self._beta_vector = np.zeros(1, dtype=np.float64)
        self._kappa_vector = np.zeros(1, dtype=np.float64)
        self._w_vector = np.zeros(1, dtype=np.float64)
        self._drhodh_pxi_vector = np.zeros(1, dtype=np.float64)
        self._drhodp_hxi_vector = np.zeros(1, dtype=np.float64)
        self._drhodxi_ph_vector = np.zeros((1, 0), dtype=np.float64)
        self._gamma_vector = np.zeros(1, dtype=np.float64)
        self._Pr_vector = np.zeros(1, dtype=np.float64)
        self._lamb_vector = np.zeros(1, dtype=np.float64)
        self._eta_vector = np.zeros(1, dtype=np.float64)
        self._sigma_vector = np.zeros(1, dtype=np.float64)
        self._M_i_vector = np.zeros((1, 1), dtype=np.float64)
        # [[[end]]]
        # fmt: on

        self._xiFixed_vector = np.zeros((1, 0), dtype=np.float64)
        self._medium: ExternalObject

        # Library functions

        self._compute_transport_properties = compute_transport_properties
        self._compute_vle_transport_properties = compute_vle_transport_properties
        self._compute_vle_additional_properties = compute_vle_additional_properties
        self._deactivate_density_derivatives = deactivate_density_derivatives
        self._deactivate_two_phase_region = deactivate_two_phase_region

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
        self._vleFluid_name = vleFluid_name
        self._nc_internal: int = 0
        _xi_autodetect = np.zeros(20, dtype=np.float64)
        with _vle_lock as locked:
            if locked:
                self._status, self._nc_internal = VLEFluid_isValid_getInfo_errorInterface(
                    vleFluid_name, _xi_autodetect, True, self._session
                )
        if self._status == 0:
            raise TILMediaErrorInvalidMedium(
                'VLEFluidName "' + vleFluid_name + '" not valid. Could not create TILMedia object.'
            )
        self._xi_autodetect = np.zeros(self._nc_internal - 1)

        # forwarding information to other classes
        if fixed_mixing_ratio:
            self._nc = 1
        else:
            self._nc = self._nc_internal
        DataContainer.__init__(self, self._nc, "drhodxi_ph")
        self.vle = self._VLEProperties(self._nc)
        "Vapour Liquid Equilibrium Properties"
        self.sat = self._SaturationProperties(self._nc)
        "Dew and Bubble Point Properties"
        self.crit = self._CriticalProperties(self._nc)
        "Critical Properties"

        # update to new nc
        self._resize_properties((1,))
        self._make_properties_scalar((1,), {None: [], "sat": [], "vle": [], "crit": []})
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
        flags = 6
        if self._compute_transport_properties:
            flags = flags | 1
        if self._deactivate_density_derivatives:
            flags = flags | 16
        if self._deactivate_two_phase_region:
            flags = flags | 8
        if self.fixed_mixing_ratio:
            _xi_call = self._xiFixed_vector[0]
        else:
            _xi_call = self._xi_vector[0]
        with _vle_lock as locked:
            if locked:
                self._medium = ExternalObject(
                    "VLEFluid", vleFluid_name, flags, _xi_call, self._nc, -1, instance_name, self._session
                )
        if not hasattr(self, "_medium"):
            if self._session.exceptions:
                exceptions = deepcopy(self._session.exceptions)
                while self._session.exceptions:
                    self._session.exceptions.pop()
                raise exceptions[0]
            else:
                raise TILMediaErrorInvalidMedium(
                    'VLEFluidName "' + vleFluid_name + '" not valid. Could not create TILMedia object.'
                )
        self.xi = self._xi_vector[0]

        VLEFluid_Cached_molarMass(self._medium, self.M_i)
        if fixed_mixing_ratio:
            self.set_xi()
        else:
            self.set_xi(self.xi)

        # initializing Info
        self.info = self._Info()
        "Medium meta information"
        getVLEFluidInformation_pointer(self.info, self._medium)

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
            logger.debug("Decoupling external object from vlefluid instance (session = %s)", session_id)
            self._medium = None
            logger.debug("Decoupled external object from vlefluid instance (session = %s)", session_id)

        if hasattr(self, "_session"):
            logger.debug("Decoupling session from vlefluid instance (session = %s)", session_id)
            self._session = None
            logger.debug("Decoupling session from vlefluid instance (session = %s)", session_id)

    def dump(self):
        """Prints the current thermophysical properties of the VLEFluid to stdout."""
        print(self)

    def __str__(self):
        value = []
        value += ["Medium: " + self._vleFluid_name]
        value += [DataContainer.__str__(self)]
        value += [str(self.crit)]
        value += [str(self.vle)]
        value += [str(self.sat)]
        return "\n".join([v for v in value if v])

    def __repr__(self):
        return 'TILMedia.VLEFluid "' + self._vleFluid_name + '" (nc = ' + str(self._nc) + ")"

    def set_pxi(
        self, p: Union[float, np.ndarray, List[float]], xi: Optional[Union[List[float], np.ndarray]] = None
    ) -> None:
        """
        Calculates the saturated properties depending on pressure and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            xi (float, list, or numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, xi = internals.var_normalize_inputs(p, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call(
            "TILMedia_VLEFluid_criticalDataRecord_xi", self, ["xi"], "crit", ["dc", "hc", "pc", "sc", "Tc"]
        )
        if self._nc == 1:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEProperties_phxi",
                self,
                ["p", None, "xi"],
                "vle",
                ["d_l", "h_l", "p_l", "s_l", "T_l", "xi_l", "d_v", "h_v", "p_v", "s_v", "T_v", "xi_v"],
            )
            if self._compute_vle_transport_properties:
                batch_caller.add_call(
                    "TILMedia_VLEFluid_VLETransportProperties_phxi",
                    self,
                    ["p", None, "xi"],
                    "vle",
                    ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
                )
            if self._compute_vle_additional_properties:
                batch_caller.add_call(
                    "TILMedia_VLEFluid_VLEAdditionalProperties_phxi",
                    self,
                    ["p", None, "xi"],
                    "vle",
                    ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
                )
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_pxi",
            self,
            ["p", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        for function_name, arguments in self._batch_function_calls[2]:
            batch_caller.add_call(function_name, *arguments(self))
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, xi=%s."
                    % (str(failure_index), str(p[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, xi=%s." % (str(p[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_Txi(
        self, T: Union[float, np.ndarray, List[float]], xi: Optional[Union[List[float], np.ndarray]] = None
    ) -> None:
        """
        Calculates the saturated properties depending on temperature and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            T (float, list, or numpy.ndarray): temperature [K]
            xi (float, list, or numpy.ndarray): mass fraction [1] (optional)
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        T, xi = internals.var_normalize_inputs(T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = T.shape
        self._resize_properties(shape)
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call(
            "TILMedia_VLEFluid_criticalDataRecord_xi", self, ["xi"], "crit", ["dc", "hc", "pc", "sc", "Tc"]
        )
        if self._nc == 1:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEProperties_dTxi",
                self,
                [None, "T", "xi"],
                "vle",
                ["d_l", "h_l", "p_l", "s_l", "T_l", "xi_l", "d_v", "h_v", "p_v", "s_v", "T_v", "xi_v"],
            )
            if self._compute_vle_transport_properties:
                batch_caller.add_call(
                    "TILMedia_VLEFluid_VLETransportProperties_dTxi",
                    self,
                    [None, "T", "xi"],
                    "vle",
                    ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
                )
            if self._compute_vle_additional_properties:
                batch_caller.add_call(
                    "TILMedia_VLEFluid_VLEAdditionalProperties_dTxi",
                    self,
                    [None, "T", "xi"],
                    "vle",
                    ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
                )
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_Txi",
            self,
            ["T", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        for function_name, arguments in self._batch_function_calls[2]:
            batch_caller.add_call(function_name, *arguments(self))
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

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

    def set_xi(self, xi: Optional[Union[List[float], np.ndarray]] = None):
        """
        Calculates critical properties depending on independent mass fractions (always one less than the number of components in mixtures).

        Args:
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
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

        self.crit.resize_properties(shape)
        batch_caller = BatchFunctionCaller()
        for function_name, arguments in self._batch_function_calls[1]:
            batch_caller.add_call(function_name, *arguments(self))
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

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
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, T, xi = internals.var_normalize_inputs(p, T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = T.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_pTxi", self, ["p", "T", "xi"], None, ["d", "h", "s"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_pxi",
            self,
            ["p", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_phxi",
                self,
                ["p", "h", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

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
            p (float, list, or numpy.ndarray): pressure [Pa]
            h (float, list, or numpy.ndarray): specific enthalpy [J/kg]
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, h, xi = internals.var_normalize_inputs(p, h, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = h.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._h_vector[:] = h
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_phxi", self, ["p", "h", "xi"], None, ["d", "s", "T"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_pxi",
            self,
            ["p", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_phxi",
                self,
                ["p", "h", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

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
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, s, xi = internals.var_normalize_inputs(p, s, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = s.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._s_vector[:] = s
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_psxi", self, ["p", "s", "xi"], None, ["d", "h", "T"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_pxi",
            self,
            ["p", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_phxi",
                self,
                ["p", "h", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

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

    def set_pdxi(self, p, d, xi=None):
        """
        Calculates all thermophysical properties depending on pressure, specific entropy and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            p (float, list, or numpy.ndarray): pressure [Pa]
            d (float, list, or numpy.ndarray): density [kg/m3]
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        p, d, xi = internals.var_normalize_inputs(p, d, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = p.shape
        self._resize_properties(shape)
        self._p_vector[:] = p
        self._d_vector[:] = d
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_pdxi", self, ["p", "d", "xi"], None, ["h", "s", "T"])
        for function_name, arguments in self._batch_function_calls[3]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_pxi",
            self,
            ["p", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_phxi",
                self,
                ["p", "h", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_phxi",
                self,
                ["p", "h", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: p=%s, d=%s, xi=%s."
                    % (str(failure_index), str(p[failure_index]), str(d[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were p=%s, d=%s, xi=%s."
                    % (str(p[failure_index]), str(d[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_Thxi(self, T, h, xi=None):
        """
        Calculates all thermophysical properties depending on pressure, specific entropy and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            T (float, list, or numpy.ndarray): pressure [K]
            h (float, list, or numpy.ndarray): specific enthalpy [J/kg]
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        T, h, xi = internals.var_normalize_inputs(T, h, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = T.shape
        self._resize_properties(shape)
        self._T_vector[:] = T
        self._h_vector[:] = h
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_Thxi", self, ["T", "h", "xi"], None, ["d", "p", "s"])
        for function_name, arguments in self._batch_function_calls[4]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_Txi",
            self,
            ["T", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_dTxi",
                self,
                ["d", "T", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_dTxi",
                self,
                ["d", "T", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_dTxi",
                self,
                ["d", "T", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: T=%s, h=%s, xi=%s."
                    % (str(failure_index), str(T[failure_index]), str(h[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were T=%s, h=%s, xi=%s."
                    % (str(T[failure_index]), str(h[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_Tsxi(self, T, s, xi=None):
        """
        Calculates all thermophysical properties depending on pressure, specific entropy and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            T (float, list, or numpy.ndarray): pressure [K]
            s (float, list, or numpy.ndarray): specific entropy [J/(kg*K)]
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        T, s, xi = internals.var_normalize_inputs(T, s, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = T.shape
        self._resize_properties(shape)
        self._T_vector[:] = T
        self._s_vector[:] = s
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_Tsxi", self, ["T", "s", "xi"], None, ["d", "h", "p"])
        for function_name, arguments in self._batch_function_calls[4]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_Txi",
            self,
            ["T", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_dTxi",
                self,
                ["d", "T", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_dTxi",
                self,
                ["d", "T", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_dTxi",
                self,
                ["d", "T", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: T=%s, s=%s, xi=%s."
                    % (str(failure_index), str(T[failure_index]), str(s[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were T=%s, s=%s, xi=%s."
                    % (str(T[failure_index]), str(s[failure_index]), str(xi[failure_index]))
                )
            while self._session.exceptions:
                self._session.exceptions.pop()

            raise exception

    def set_dTxi(
        self,
        d: Union[float, np.ndarray, List[float]],
        T: Union[float, np.ndarray, List[float]],
        xi: Optional[Union[List[float], np.ndarray]] = None,
    ):
        """
        Calculates all thermophysical properties depending on density, temperature and independent mass fractions (always one less than the number of components in mixtures).

        Args:
            d (float, list, or numpy.ndarray): density [kg/m^3]
            T (float, list, or numpy.ndarray): temperature [K]
            xi (list or numpy.ndarray, optional): mass fraction [1]. Defaults to None.
        """

        if self.fixed_mixing_ratio and xi is not None:
            raise TILMediaErrorInvalidParameter("If fixed_mixing_ratio is True, then xi input must not be used")
        if xi is None:
            xi = self._xi_vector[tuple([0] * (self._xi_vector.ndim - 1))]

        d, T, xi = internals.var_normalize_inputs(d, T, xi)
        internals.check_vector_size(xi, self._nc - 1)

        shape = d.shape
        self._resize_properties(shape)
        self._d_vector[:] = d
        self._T_vector[:] = T
        self._xi_vector[:] = xi

        batch_caller = BatchFunctionCaller()
        batch_caller.add_call("TILMedia_VLEFluid_properties_dTxi", self, ["d", "T", "xi"], None, ["h", "p", "s"])
        for function_name, arguments in self._batch_function_calls[4]:
            batch_caller.add_call(function_name, *arguments(self))
        batch_caller.add_call(
            "_TILMedia_VLEFluid_saturationProperties_Txi",
            self,
            ["T", "xi"],
            "sat",
            [
                "dl_bubble",
                "dv_bubble",
                "xiv_bubble",
                "hl_bubble",
                "p_bubble",
                "sl_bubble",
                "T_bubble",
                "dv_dew",
                "dl_dew",
                "xil_dew",
                "hv_dew",
                "p_dew",
                "sv_dew",
                "T_dew",
            ],
        )
        if self._compute_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_transportProperties_dTxi",
                self,
                ["d", "T", "xi"],
                None,
                ["Pr", "lamb", "eta", "sigma"],
            )
        if self._compute_vle_transport_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLETransportProperties_dTxi",
                self,
                ["d", "T", "xi"],
                "vle",
                ["Pr_l", "Pr_v", "lambda_l", "lambda_v", "eta_l", "eta_v"],
            )
        if self._compute_vle_additional_properties:
            batch_caller.add_call(
                "TILMedia_VLEFluid_VLEAdditionalProperties_dTxi",
                self,
                ["d", "T", "xi"],
                "vle",
                ["cp_l", "beta_l", "kappa_l", "cp_v", "beta_v", "kappa_v"],
            )
        calculated_properties = batch_caller.execute(self._medium, np.prod(shape))

        self._M_vector[:], self._x_vector[:] = self._molarMass(xi, self.M_i)
        calculated_properties[None] += ["x", "M"]

        self._make_properties_scalar(shape, calculated_properties)

        if self._session.exceptions:
            if len(shape) > 1 or max(shape) > 1:
                failure_index = np.unravel_index(batch_caller.current_index, shape)
                if len(failure_index) == 1:
                    failure_index = failure_index[0]
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe error was caused by element %s: d=%s, T=%s, xi=%s."
                    % (str(failure_index), str(d[failure_index]), str(T[failure_index]), str(xi[failure_index]))
                )
            else:
                failure_index = 0
                exception = self._session.exceptions[0].__class__(
                    self._session.exceptions[0].message
                    + "\nThe inputs were d=%s, T=%s, xi=%s."
                    % (str(d[failure_index]), str(T[failure_index]), str(xi[failure_index]))
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
        M = 1 / np.sum(mixingRatio / np.maximum(1e-20, M_i), xi.ndim - 1)
        x = M.reshape(shape + (1,)) * (xi / M_i[:-1])

        return M, x

    def _make_properties_scalar(self, shape, calculated_properties):
        DataContainer._make_properties_scalar(self, shape, calculated_properties[None])
        self.vle._make_properties_scalar(shape, calculated_properties.get("vle", []))
        self.sat._make_properties_scalar(shape, calculated_properties.get("sat", []))
        self.crit._make_properties_scalar(shape, calculated_properties.get("crit", []))

    def _resize_properties(self, shape):
        DataContainer._resize_properties(self, shape)
        self.vle.resize_properties(shape)
        self.sat.resize_properties(shape)
        self.crit.resize_properties(shape)

    def set(self, **kwargs):
        keys = frozenset(kwargs)
        mapping = {
            frozenset({"p", "h"}): self.set_phxi,
            frozenset({"p", "h", "xi"}): self.set_phxi,
            frozenset({"p", "T"}): self.set_pTxi,
            frozenset({"p", "T", "xi"}): self.set_pTxi,
            frozenset({"p", "s"}): self.set_psxi,
            frozenset({"p", "s", "xi"}): self.set_psxi,
            frozenset({"d", "T"}): self.set_dTxi,
            frozenset({"d", "T", "xi"}): self.set_dTxi,
            frozenset({"xi"}): self.set_xi,
            frozenset({"p"}): self.set_pxi,
            frozenset({"p", "xi"}): self.set_pxi,
            frozenset({"T"}): self.set_Txi,
            frozenset({"T", "xi"}): self.set_Txi,
            frozenset({"p", "d"}): self.set_pdxi,
            frozenset({"p", "d", "xi"}): self.set_pdxi,
            frozenset({"T", "h"}): self.set_Thxi,
            frozenset({"T", "h", "xi"}): self.set_Thxi,
            frozenset({"T", "s"}): self.set_Tsxi,
            frozenset({"T", "s", "xi"}): self.set_Tsxi,
        }
        function = mapping.get(keys)
        if function:
            function(**kwargs)
        else:
            raise TILMediaErrorInvalidParameter(
                f"Properties cannot be computed from the arguments {set(keys)}, only {[set(v) for v in mapping]} are available."
            )
