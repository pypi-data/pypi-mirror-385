import logging
from copy import deepcopy
from ctypes import addressof, c_ulonglong, c_voidp
from typing import List, Optional

import numpy as np

from .exceptions import TILMediaError, TILMediaErrorIncompatibleVectorLength
from .properties import PROPERTY_INFORMATION

_logger_exceptions = {"fatal": True, "info": True}

_handler = logging.StreamHandler()
_formatter = logging.Formatter()
_logger = logging.getLogger("TILMedia")
_logger.setLevel(logging.INFO)
_logger.addHandler(_handler)


class TILMediaSession:
    def __init__(self, logger: Optional[logging.Logger]) -> None:
        self.logger = logger or _logger
        self.identifier = c_ulonglong(id(self))
        "Identifier for logger"
        self.logger.debug("Creating TILMediaSession id=%s", self.identifier)
        self.identifier_p = c_voidp(addressof(self.identifier))
        "Pointer to identifier for logger"
        self.exceptions: List[TILMediaError] = []
        self.medium_id: Optional[int] = None

    def __del__(self) -> None:
        self.logger.debug("Deleting TILMediaSession id=%s", self.identifier)


def tilmedia_message_logger_function(
    timestamp_bytes: bytes, message_bytes: bytes, level: int, session: TILMediaSession
) -> None:
    message = message_bytes.decode("utf8", errors="ignore")
    # datetime.strptime(re.sub(r'\.\d+',lambda x:x.group()[:7], timestamp_bytes.decode('utf8')), "%Y-%m-%dT%H:%M:%S.%fZ")
    logger = session.logger
    if level >= 5:
        logger.fatal(message)
    elif level >= 4:
        logger.error(message)
    elif level >= 3:
        logger.warning(message)
    elif level >= 2:
        logger.info(message)
    else:
        logger.debug(message)

    if _logger_exceptions["info"] and level >= 2 or _logger_exceptions["fatal"] and level >= 5:
        session.exceptions.append(TILMediaError(message))

    return 0


def set_logger(logger: logging.Logger) -> None:
    """
    set the global logger (logging module) instance. The global logger instance is used, if no local one (instance constructor argument) was given.

    Args:
        logger (logging.Logger): logger instance
    """
    if logger is None:
        logger = logging.getLogger("TILMedia")
    globals()["_logger"] = logger


def set_logger_exceptions(log_level, active: bool):
    """
    activate the exceptions of the global logger for a specific log level.

    Args:
        log_level (str): either "fatal" or "info"
        active (bool): activate exceptions
    """

    globals()["_logger_exceptions"][log_level] = active


def var_normalize_inputs(*args) -> tuple:
    """
    align the sizes of all inputs. The last input is expected to be a concentration vector with one additional dimension.

    Raises:
        TILMediaError: incompatible vector lengths

    Returns:
        tuple: same order as args, just aligned sizes
    """
    array_shapes = []
    # var_are_arrays = []
    arrays = []
    for arg in args:
        if isinstance(arg, np.ndarray):
            var = arg
        else:
            var = np.array(arg)
        # if var.shape != ():
        #     var_are_arrays.append(True)
        array_shapes.append(var.shape)
        arrays.append(var)

    # vectorized arguments
    shapes = [v.shape for v in arrays]
    # remove concentration dimension
    shapes_wo_concentration = deepcopy(shapes)
    shapes_wo_concentration[-1] = shapes_wo_concentration[-1][:-1]

    # get the shape with the highest number of dimensions
    highest_dim_shape = sorted(shapes_wo_concentration, key=len)[-1]
    if highest_dim_shape == tuple():
        highest_dim_shape = (1,)

    # missing dimensions at the beginning are filled with highest_dim_shape
    vectorized_shapes_wo_concentration = [
        tuple(list(highest_dim_shape[: len(highest_dim_shape) - len(shape)]) + list(shape))
        for shape in shapes_wo_concentration
    ]
    vectorized_shapes = deepcopy(vectorized_shapes_wo_concentration)
    vectorized_shapes[-1] = tuple(list(vectorized_shapes[-1]) + [arrays[-1].shape[-1]])

    vectorizations = set(vectorized_shapes_wo_concentration)
    if len(vectorizations) > 1:
        raise TILMediaErrorIncompatibleVectorLength("incompatible vector lengths of inputs")

    # missing dimensions at the beginning are filled with highest_dim_shape
    tile_shapes = [
        tuple(list(highest_dim_shape[: len(highest_dim_shape) - len(shape)]) + [1] * len(shape))
        for shape in shapes_wo_concentration
    ]
    # add concentration dimension
    tile_shapes[-1] = tuple(list(tile_shapes[-1]) + [1])

    normalized_arrays = []
    for expected_shape, tile_shape, var in zip(vectorized_shapes, tile_shapes, arrays):
        if var.shape == expected_shape:
            normalized_arrays.append(var)
        else:  # if var.shape == tuple():
            normalized_arrays.append(np.tile(var, tile_shape))
        # else:
        #     raise TILMediaError("unexpected error handling the vector inputs")

    return tuple(normalized_arrays)


def check_vector_size(vector: np.ndarray, expected: int):
    """
    compare the sizes of a vector and with the expected value. If they dont match raise an exception.

    Args:
        vector (np.ndarray): input vector
        expected (int): expected composition length

    Raises:
        TILMediaErrorIncompatibleVectorLength: length mismatch
    """
    if vector.shape[-1] != expected:
        raise TILMediaErrorIncompatibleVectorLength(
            "The composition vector length is " + str(vector.shape[-1]) + " but should be " + str(expected)
        )


def _generate_code(property_list: list):
    code_a = []
    code_b = []
    for name, _, mixture_dim, _ in property_list:
        info = PROPERTY_INFORMATION.get(name, {})
        if mixture_dim is None:
            template_a = "        self.{name} = np.{data_type}(0)\n" "        '{escaped_description} [{unit}]'"
            template_b = "        self._{name}_vector = np.zeros(1, dtype=np.{data_type})"
        else:
            template_a = (
                "        self.{name} = np.zeros((1, {n}), dtype=np.{data_type})\n"
                "        '{escaped_description} [{unit}]'"
            )
            template_b = "        self._{name}_vector = np.zeros((1, {n}), dtype=np.{data_type})"

        args = {
            "name": name,
            "data_type": info.get("numpy_type", ""),
            "unit": info.get("unit", ""),
            "description": info.get("description", ""),
            "escaped_description": info.get("description", "").replace("'", "\\'"),
            "n": max(0, 1 + mixture_dim if mixture_dim is not None else 0),
        }
        code_a.append(template_a.format(**args))
        code_b.append(template_b.format(**args))
    return code_a + [""] + code_b
