"""
TILMedia for Python
===================

`TILMedia Suite`_ provides methods of calculation, which express the thermophysical properties
of incompressible liquids, ideal gases and real fluids containing a vapor liquid equilibrium.
Methods for calculating the properties of mixtures are also included. TILMedia provides a
comprehensive range of different substances, including our own highly efficient and accurate
real-time substance property implementations.

.. _TILMedia Suite: https://www.tlk-thermo.com/en/software/tilmedia-suite
"""

from re import search as re_search

from ._internals import _logger, set_logger, set_logger_exceptions
from .exceptions import (
    TILMediaError,
    TILMediaErrorIncompatibleVectorLength,
    TILMediaErrorInvalidLicense,
    TILMediaErrorInvalidMedium,
    TILMediaErrorInvalidParameter,
)
from .gas import Gas
from .general import (
    clear_medium_name_cache,
    get_all_adsorption_and_absorption_names,
    get_all_condensing_gas_names,
    get_all_gas_names,
    get_all_liquid_mixture_names,
    get_all_liquid_names,
    get_all_vleFluid_names,
    get_closest_vleFluid_dpT,
    get_data_path,
    license_is_valid,
    set_data_path,
)
from .liquid import Liquid
from .moistair import MoistAir
from .properties import PROPERTY_INFORMATION
from .vlefluid import VLEFluid

__version__ = "2025.2"
version_match = re_search(
    r"(\d+\.)+?((?P<final_release>\d+)|\d+(?P<pre_release>a|b|rc)(?P<pre_release_version>\d+)|(?P<dev_release>dev)(?P<dev_release_version>\d+))$",
    __version__,
)
if version_match:
    # pep 440
    if version_match.group("dev_release"):
        release = version_match.group("dev_release")
        version_info = __version__.split(".")
        version_info = tuple(
            [int(i) for i in version_info[:-2]] + ["x", int(version_match.group("dev_release_version"))]
        )
    elif version_match.group("pre_release"):
        release = version_match.group("pre_release")
        version_info = __version__.split(".")
        version_info = tuple(
            [int(i) for i in version_info[:-1]]
            + ["y", version_match.group("pre_release"), int(version_match.group("pre_release_version"))]
        )
    elif version_match.group("final_release"):
        release = version_match.group("final_release")
        version_info = __version__.split(".")
        version_info = tuple([int(i) for i in version_info[:-1]] + ["z", version_match.group("final_release")])
else:
    # TIL version number
    version_info = __version__.split(".")
    release = version_info[-1].split(" ")[-1] if len(version_info[-1].split(" ")) > 1 else "release"
    version_info = tuple([int(i) for i in version_info[:2]] + ["z"] + [int(version_info[-1].split(" ")[0])])

del re_search
