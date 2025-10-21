from collections import defaultdict
from typing import List

from ._internals import _logger_exceptions
from .core import BatchFunctionCaller_execute, ExternalObject, logger_flush_messages


class BatchFunctionCaller:
    """
    Preparing and executing TILMedia function calls for an array of inputs
    """

    def __init__(self) -> None:
        self.current_index = None
        "progress information in batch call"

        self._function_names = []
        "functions to be called"

        self._function_input_arguments = {"d": [], "i": []}
        "all input numpy arrays of the functions to be called"

        self._function_input_argument_index = []
        "for each function in :attr:`_function_names` this contains the index of the input arguments in :attr:`_function_input_arguments`"

        self._double_arguments = []
        "all output numpy arrays of doubles"

        self._int_arguments = []
        "all output numpy arrays of ints"

        self._calculated_property_list = defaultdict(list)
        "properties which are correct now"

    def add_call(
        self,
        function_name,
        input_argument_instance,
        input_argument_names,
        output_argument_instance_name,
        output_argument_names,
    ):
        """
        Add a function call to the sequence of calls per input value set.

        Args:
            function_name (str): name of the function to be called
            input_argument_instance (object): parent instance were the input ctypes property instances can be found
            input_argument_names (list): list of input argument property names (None means creating a new one which contains -1)
            output_argument_instance_name (object): member name of input parent instance were the ouput ctypes property instances can be found (None means self)
            output_argument_names (list): list of output argument property names
        """
        self._function_names.append(function_name)
        self._calculated_property_list[None] += [
            n for n in input_argument_names if n not in self._calculated_property_list[None]
        ]
        self._calculated_property_list[output_argument_instance_name] += [
            n for n in output_argument_names if n not in self._calculated_property_list[output_argument_instance_name]
        ]
        indices = []

        for arg_name in input_argument_names:
            if arg_name is None:
                arg = None
            else:
                arg = getattr(input_argument_instance, "_" + arg_name + "_vector")
            argument_type_letter = self.__get_argument_letter(arg)

            # use the same array if the input variable is reused
            array_is_identical = [arg is item for item in self._function_input_arguments[argument_type_letter]]
            if any(array_is_identical):
                index = array_is_identical.index(True)
            else:
                self._function_input_arguments[argument_type_letter].append(arg)
                index = len(self._function_input_arguments[argument_type_letter]) - 1
            indices.append(index)

        self._function_input_argument_index.append(indices)
        for arg_name in output_argument_names:
            if output_argument_instance_name is None:
                output_argument_instance = input_argument_instance
            else:
                output_argument_instance = getattr(input_argument_instance, output_argument_instance_name)
            arg = getattr(output_argument_instance, "_" + arg_name + "_vector")
            if self._is_double_argument(arg):
                self._double_arguments.append(arg)
            elif self._is_integer_argument(arg):
                self._int_arguments.append(arg)
            else:
                raise RuntimeError("Argument type not recognized")

    @staticmethod
    def _is_integer_argument(input_argument):
        return input_argument is not None and input_argument.dtype.name == "int32"

    @staticmethod
    def _is_double_argument(input_argument):
        return input_argument is not None and input_argument.dtype.name == "float64"

    @staticmethod
    def __get_argument_letter(input_argument):
        if BatchFunctionCaller._is_double_argument(input_argument):
            return "d"
        elif BatchFunctionCaller._is_integer_argument(input_argument):
            return "i"
        elif input_argument is None:
            return "d"
        raise RuntimeError("Unknown input argument type")

    def execute(self, eo: ExternalObject, length: int, *args) -> List[str]:
        temp = BatchFunctionCaller_execute(self, eo, length, *args)
        logger_flush_messages(eo.py_session)
        return temp
