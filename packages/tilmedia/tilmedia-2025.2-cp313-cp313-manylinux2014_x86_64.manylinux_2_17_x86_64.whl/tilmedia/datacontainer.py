import numpy as np

from .properties import PROPERTY_INFORMATION


class InfoContainer(object):
    """
    Meta Information Base Class.
    """

    _allowed = []

    def keys(self):
        return [member for member in self._allowed if getattr(self, member) is not None]

    def __len__(self):
        return len(self._allowed)

    def __getitem__(self, key):
        if key in self._allowed:
            return getattr(self, key)
        raise KeyError("Invalid parameter requested")

    def dump(self):
        s = str(self)
        if len(s) > 0:
            print(s)

    def items(self):
        return [(name, getattr(self, name)) for name in self._allowed if getattr(self, name) is not None]


class DataContainer(object):
    def __init__(self, nc, shape_property) -> None:
        object.__init__(self)
        if not hasattr(self, "_property_list"):
            self._property_list = []
        self._nc = nc
        self._shape_property = "_" + shape_property + "_vector"

        self._shape_property_mixture_dim = tuple()
        for name, dtype, mixture_dim, default_value in self._property_list:
            if name == shape_property:
                if mixture_dim is None:
                    break
                self._shape_property_mixture_dim = (max(0, self._nc + mixture_dim),)
                break

    def _resize_properties(self, shape):
        old_shape = getattr(self, self._shape_property).shape
        new_shape = shape + self._shape_property_mixture_dim
        if old_shape == new_shape:
            for name, dtype, _, default_value in self._property_list:
                v = getattr(self, "_" + name + "_vector")
                if default_value is not None:
                    v.fill(default_value)
                else:
                    v.fill(0)
        else:
            for name, dtype, mixture_dim, default_value in self._property_list:
                if mixture_dim is not None:
                    additional_dimension = (max(0, self._nc + mixture_dim),)
                else:
                    additional_dimension = tuple()
                if default_value:
                    value = default_value
                else:
                    value = 0
                v = np.full(shape + additional_dimension, value, dtype=dtype)
                setattr(self, "_" + name + "_vector", v)

    def _make_properties_scalar(self, shape, calculated_properties):
        p = calculated_properties
        if shape == (1,):
            for name, dtype, mixture_dim, _ in self._property_list:
                if name not in p:
                    setattr(self, name, None)
                elif dtype == np.int32:
                    setattr(self, name, int(getattr(self, "_" + name + "_vector")[0, ...]))
                else:
                    if mixture_dim is None:
                        setattr(self, name, getattr(self, "_" + name + "_vector")[0])
                    else:
                        setattr(self, name, getattr(self, "_" + name + "_vector")[0, ...])
        else:
            for name, _, _, _ in self._property_list:
                if name not in p:
                    setattr(self, name, None)
                else:
                    setattr(self, name, getattr(self, "_" + name + "_vector"))

    def __str__(self):
        value = []
        for name, _, _, _ in self._property_list:
            v = getattr(self, name)
            if v is not None:
                info = PROPERTY_INFORMATION.get(name, {})
                left_part = name
                description = info.get("description", "")
                unit = info.get("unit", "")
                if description:
                    left_part += " (" + description
                    if unit:
                        left_part += " in " + unit
                    left_part += ")"
                value.append("{left_part}: {property_value}".format(left_part=left_part, property_value=v))
        return "\n".join(value)

    def keys(self):
        return [name for name, _, _, _ in self._property_list if getattr(self, name) is not None]

    def __len__(self):
        return (len(self._property_list) + 1) * 2

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError("Invalid parameter requested")

    def items(self):
        return [(name, getattr(self, name)) for name, _, _, _ in self._property_list if getattr(self, name) is not None]
